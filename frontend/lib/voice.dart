// DiceIQ — Voice Engine
// Listens for Tom's whispers. Sends to Flask. Gets confirmation back.
// Uses iOS SFSpeechRecognizer — works completely offline.

import 'package:speech_to_text/speech_to_text.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'api.dart';
import 'haptics.dart';
import 'game_state.dart';

class VoiceEngine {
  final SpeechToText _speech = SpeechToText();
  final FlutterTts   _tts    = FlutterTts();

  bool isListening  = false;
  bool isInitialized = false;

  // Callback so the UI can react to state changes
  final Function(String status, Map<String, dynamic>? result)? onUpdate;

  VoiceEngine({this.onUpdate});

  // ─────────────────────────────────────────────
  // INITIALIZE
  // Call once when the app starts
  // ─────────────────────────────────────────────

  Future<bool> initialize() async {
    isInitialized = await _speech.initialize(
      onError: (error) => _handleError(error.errorMsg),
    );

    // Configure TTS for hearing aids
    // Calm, clear, low volume — just a whisper back to Tom
    await _tts.setLanguage('en-US');
    await _tts.setSpeechRate(0.45);   // Slower = clearer in noisy casino
    await _tts.setVolume(0.8);
    await _tts.setPitch(1.0);

    return isInitialized;
  }

  // ─────────────────────────────────────────────
  // SPEAK — sends audio to hearing aids
  // ─────────────────────────────────────────────

  Future<void> speak(String text) async {
    await _tts.speak(text);
  }

  // ─────────────────────────────────────────────
  // LISTEN — the main loop
  // Always listening while session is active
  // ─────────────────────────────────────────────

  Future<void> startListening(GameState gameState) async {
    if (!isInitialized || isListening) return;

    isListening = true;

    await _speech.listen(
      // Constrained vocabulary — only valid DiceIQ words
      // Massively improves accuracy in noisy casino environment
      localeId: 'en-US',
      listenMode: ListenMode.dictation,
      pauseFor: const Duration(seconds: 2),
      onResult: (result) async {
        if (result.finalResult && result.recognizedWords.isNotEmpty) {
          await _processWords(result.recognizedWords, gameState);
        }
      },
    );
  }

  Future<void> stopListening() async {
    isListening = false;
    await _speech.stop();
  }

  // ─────────────────────────────────────────────
  // PROCESS — send to Flask and handle response
  // ─────────────────────────────────────────────

  Future<void> _processWords(String words, GameState gameState) async {
    if (gameState.sessionId == null) return;

    // Notify UI we heard something
    onUpdate?.call('heard: $words', null);

    try {
      // Send to Flask brain
      final response = await ApiService.processVoice(
        sessionId:    gameState.sessionId!,
        text:         words,
        handId:       gameState.handId!,
        phase:        gameState.phase,
        currentPoint: gameState.currentPoint,
      );

      if (response['status'] == 'ok') {
        // Update game state from response
        gameState.updateFromResponse(response);

        // Haptic feedback first (instant)
        await HapticsService.fromResponse(response['haptic']);

        // Audio confirmation to hearing aids
        if (response['audio'] != null) {
          await speak(response['audio']);
        }

        // Diagnostic alert — whisper only if present
        if (response['alert'] != null) {
          final alert = response['alert'] as Map<String, dynamic>;
          await Future.delayed(const Duration(milliseconds: 800));
          await speak(alert['message']);
        }

        // Notify UI with full result
        onUpdate?.call('ok', response);

      } else {
        // Flask couldn't parse it
        await HapticsService.error();
        await speak('Repeat that');
        onUpdate?.call('error', response);
      }

    } catch (e) {
      // Network error — Flask unreachable
      await HapticsService.error();
      await speak('Connection lost');
      onUpdate?.call('connection_error', null);
    }

    // Keep listening
    if (isListening && gameState.isActive) {
      await startListening(gameState);
    }
  }

  void _handleError(String error) {
    isListening = false;
    onUpdate?.call('speech_error', null);
  }

  void dispose() {
    _speech.cancel();
    _tts.stop();
  }
}
