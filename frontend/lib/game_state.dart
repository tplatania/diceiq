// DiceIQ — Game State
// Tracks everything that's happening right now at the table.
// Flutter holds this in memory during play.

class GameState {
  int? sessionId;
  int? handId;
  int handNumber;
  String phase;       // 'come_out' or 'point'
  int? currentPoint;  // null on come-out, 4-10 during point phase
  int rollCount;
  bool isActive;

  GameState({
    this.sessionId,
    this.handId,
    this.handNumber  = 1,
    this.phase       = 'come_out',
    this.currentPoint,
    this.rollCount   = 0,
    this.isActive    = false,
  });

  // Called when Flask returns a roll result
  void updateFromResponse(Map<String, dynamic> response) {
    rollCount++;

    // Update phase
    if (response['phase'] != null) {
      phase = response['phase'];
    }

    // Update point
    if (response['new_point'] != null) {
      currentPoint = response['new_point'];
    } else if (phase == 'come_out') {
      currentPoint = null;
    }

    // Update hand if a new one was created
    if (response['new_hand_id'] != null &&
        response['new_hand_id'] != handId) {
      handId = response['new_hand_id'];
      handNumber++;
    }
  }

  void reset() {
    sessionId    = null;
    handId       = null;
    handNumber   = 1;
    phase        = 'come_out';
    currentPoint = null;
    rollCount    = 0;
    isActive     = false;
  }

  String get phaseDisplay =>
      phase == 'come_out' ? 'COME OUT' : 'POINT: $currentPoint';

  @override
  String toString() =>
      'GameState(session:$sessionId hand:$handNumber phase:$phase '
      'point:$currentPoint rolls:$rollCount)';
}
