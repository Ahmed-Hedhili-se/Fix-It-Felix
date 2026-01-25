import json
class SafetyAgent:
    def __init__(self):
        print("Safety Agent (Symbolic Logic): Online.")
    def audit_decision(self, ai_proposal, sensor_data):
        action = ai_proposal.get("action")
        reason = ai_proposal.get("reason")
        print(f"\n    AUDITING ACTION: '{action}'")
        if action == "STOP_TRAIN" and sensor_data["current_speed_kmh"] > 120:
            return {
                : "VETOED",
                : "EMERGENCY_BRAKE",
                : "Train speed (120+) too high for standard stop. Physics violation."
            }
        if action == "SWITCH_TRACK" and sensor_data["track_occupied"] == True:
            return {
                : "VETOED",
                : "STOP_TRAIN",
                : "Target track is occupied. Collision detected."
            }
        if action == "PROCEED" and ai_proposal.get("confidence", 1.0) < 0.8:
             return {
                : "WARNING",
                : "SLOW_DOWN",
                : "AI Confidence too low (<80%) to authorize full speed."
            }
        return {
            : "APPROVED",
            : action,
            : "Safety checks passed."
        }
if __name__ == "__main__":
    safety = SafetyAgent()
    dumb_ai_proposal = {"action": "SWITCH_TRACK", "reason": "Faster route found", "confidence": 0.99}
    hard_sensor_data = {"current_speed_kmh": 80, "track_occupied": True}
    result = safety.audit_decision(dumb_ai_proposal, hard_sensor_data)
    print("\n   FINAL AUDIT RESULT:")
    print(json.dumps(result, indent=2))