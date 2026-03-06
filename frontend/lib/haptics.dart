// DiceIQ — Haptics Service
// Controls Apple Watch vibrations and iPhone haptics.
// One short pulse = recorded
// Long vibration  = seven out
// Triple tap      = point made!

import 'package:flutter/services.dart';

class HapticsService {

  // Single short pulse — roll recorded, all good
  static Future<void> single() async {
    await HapticFeedback.lightImpact();
  }

  // Long strong vibration — SEVEN OUT
  static Future<void> long() async {
    await HapticFeedback.heavyImpact();
    await Future.delayed(const Duration(milliseconds: 100));
    await HapticFeedback.heavyImpact();
  }

  // Triple tap — POINT MADE!
  static Future<void> triple() async {
    for (int i = 0; i < 3; i++) {
      await HapticFeedback.mediumImpact();
      await Future.delayed(const Duration(milliseconds: 120));
    }
  }

  // Double pulse — error, couldn't understand
  static Future<void> error() async {
    await HapticFeedback.mediumImpact();
    await Future.delayed(const Duration(milliseconds: 80));
    await HapticFeedback.mediumImpact();
  }

  // Route haptic from Flask response string
  static Future<void> fromResponse(String? haptic) async {
    switch (haptic) {
      case 'single': await single(); break;
      case 'long':   await long();   break;
      case 'triple': await triple(); break;
      case 'double': await error();  break;
      default:       await single(); break;
    }
  }
}
