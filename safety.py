import json

class SafetyAgent:
    def __init__(self):
        print(">> 🛡️ Safety Agent (Symbolic Logic): Online.")

    def audit_decision(self, ai_proposal, sensor_data):
        """
        Input: 
            - ai_proposal: The JSON from agents.py (e.g., "GO")
            - sensor_data: Hard facts from the train (e.g., speed=100kmh)
        Output: 
            - "APPROVED" or "VETOED"
        """
        action = ai_proposal.get("action")
        reason = ai_proposal.get("reason")
        
        print(f"\n    AUDITING ACTION: '{action}'")

        # --- RULE 1: THE SPEED LIMIT CHECK ---
        # If the AI says "STOP" but the train is moving too fast to stop instantly,
        # we must change the command to "EMERGENCY_BRAKE" instead of just "STOP".
        if action == "STOP_TRAIN" and sensor_data["current_speed_kmh"] > 120:
            return {
                "status": "VETOED",
                "override_action": "EMERGENCY_BRAKE",
                "reason": "Train speed (120+) too high for standard stop. Physics violation."
            }

        # --- RULE 2: THE OCCUPIED TRACK CHECK ---
        # If AI says "SWITCH_TRACK" but the target track has a train on it -> VETO.
        if action == "SWITCH_TRACK" and sensor_data["track_occupied"] == True:
            return {
                "status": "VETOED",
                "override_action": "STOP_TRAIN",
                "reason": "Target track is occupied. Collision detected."
            }

        # --- RULE 3: THE VISUAL CONFIRMATION CHECK ---
        # If AI says "PROCEED" but our confidence in the image was low -> WARNING.
        if action == "PROCEED" and ai_proposal.get("confidence", 1.0) < 0.8:
             return {
                "status": "WARNING",
                "override_action": "SLOW_DOWN",
                "reason": "AI Confidence too low (<80%) to authorize full speed."
            }

        # If no rules are broken:
        return {
            "status": "APPROVED",
            "final_action": action,
            "reason": "Safety checks passed."
        }

# --- TEST THE VETO ENGINE ---
if __name__ == "__main__":
    safety = SafetyAgent()

    # TEST 1: The AI proposes a dumb move (Switching to a full track)
    dumb_ai_proposal = {"action": "SWITCH_TRACK", "reason": "Faster route found", "confidence": 0.99}
    hard_sensor_data = {"current_speed_kmh": 80, "track_occupied": True} # <--- TRACK IS FULL!

    result = safety.audit_decision(dumb_ai_proposal, hard_sensor_data)
    
    print("\n   👉 FINAL AUDIT RESULT:")
    print(json.dumps(result, indent=2))