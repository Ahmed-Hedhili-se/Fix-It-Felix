import json
import os

class EfficiencyAgent:
    def __init__(self):
        print(">> 🧠 Efficiency Agent (Neural Dispatcher): Online.")

    def propose_fix(self, incident_type, status):
        print(f"\n   🤖 AGENT THINKING: 'I see {incident_type}. History says {status}.'")

        if "broken" in incident_type.lower() or status == "CRITICAL":
            return {
                "action": "STOP_TRAIN",
                "reason": "Critical fracture detected. Derailment risk high.",
                "confidence": 0.98
            }
        elif "snow" in incident_type.lower():
            return {
                "action": "SLOW_DOWN",
                "reason": "Visual obstruction. Heater activation recommended.",
                "confidence": 0.85
            }
        else:
            return {
                "action": "PROCEED",
                "reason": "Track matches 'Safe' pattern in memory.",
                "confidence": 0.99
            }

if __name__ == "__main__":
    agent = EfficiencyAgent()
    
    decision = agent.propose_fix("Broken Rail", "CRITICAL")
    
    print("   👉 JSON OUTPUT TO CONTROLLER:")
    print(json.dumps(decision, indent=2))