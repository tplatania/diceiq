// DiceIQ — API Service
// Every call the Flutter app makes to the Flask brain lives here.

import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // When running locally — Flask on your Windows machine
  // Flutter on iPhone talks to this IP over WiFi
  // IMPORTANT: Replace with your actual local IP address
  // Find it by running 'ipconfig' in Windows terminal
  static const String baseUrl = 'http://192.168.1.100:5000/api';

  // ─────────────────────────────────────────────
  // HEALTH CHECK
  // ─────────────────────────────────────────────

  static Future<bool> ping() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl/ping'))
          .timeout(const Duration(seconds: 3));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // ─────────────────────────────────────────────
  // SESSION
  // ─────────────────────────────────────────────

  static Future<Map<String, dynamic>> startSession({
    String diceSet = 'Hardway',
    String location = 'Ship Casino',
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/session/start'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'dice_set': diceSet,
        'location': location,
      }),
    );
    return jsonDecode(response.body);
  }

  static Future<Map<String, dynamic>> endSession(int sessionId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/session/$sessionId/end'),
      headers: {'Content-Type': 'application/json'},
    );
    return jsonDecode(response.body);
  }

  // ─────────────────────────────────────────────
  // VOICE — THE MAIN EVENT
  // ─────────────────────────────────────────────

  static Future<Map<String, dynamic>> processVoice({
    required int sessionId,
    required String text,
    required int handId,
    required String phase,
    int? currentPoint,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/session/$sessionId/voice'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'text':          text,
        'hand_id':       handId,
        'phase':         phase,
        'current_point': currentPoint,
      }),
    );
    return jsonDecode(response.body);
  }

  // ─────────────────────────────────────────────
  // ANALYTICS
  // ─────────────────────────────────────────────

  static Future<Map<String, dynamic>> getAnalytics(int sessionId) async {
    final response = await http.get(
      Uri.parse('$baseUrl/session/$sessionId/analytics'),
    );
    return jsonDecode(response.body);
  }

  static Future<Map<String, dynamic>> getLifetimeStats() async {
    final response = await http.get(
      Uri.parse('$baseUrl/lifetime'),
    );
    return jsonDecode(response.body);
  }

  static Future<List<dynamic>> getAllSessions() async {
    final response = await http.get(
      Uri.parse('$baseUrl/sessions'),
    );
    return jsonDecode(response.body);
  }
}
