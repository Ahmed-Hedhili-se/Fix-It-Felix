import json
import os
from qdrant_client import QdrantClient
from agents import EfficiencyAgent
from safety import SafetyAgent

# CONFIGURATION
COLLECTION_NAME = "rail_lines"
HISTORY_FILE = "data/history.json"

class NeuroRailSystem:
    def __init__(self):
        print("\n🚂 SYSTEM BOOT: INITIALIZING NEURO-RAIL...")
        
        # 1. Connect to Database (Eyes)
        self.client = QdrantClient(path="rail_db") 
        print(">> 👁️  Vision System (Qdrant): Connected.")
        
        # 2. Load History (Memory)
        with open(HISTORY_FILE, 'r') as f:
            self.history_db = json.load(f)
        print(f">> 📚 History Loaded ({len(self.history_db)} records).")

        # 3. Wake up Agents
        self.efficiency_agent = EfficiencyAgent()
        self.safety_agent = SafetyAgent()

    def find_historical_context(self, filename):
        """Looks up the metadata for a matching image file."""
        for record in self.history_db:
            # We check if the record filename is inside the search result path
            if record["filename"] in filename:
                return record
        return None

    def run_cycle(self, query_vector_or_image, sensor_data):
        print(f"\n--- ⚡ NEW CYCLE: ANALYZING LIVE INPUT ---")
        
        # 1. REAL SEARCH (The Eyes)
        # Note: In a real app, we would vectorize the image here first.
        # For this demo, we assume we already have a vector or we mock the search hit.
        
        # Simulating a search hit for demonstration (since we are integration testing)
        # In full production, this line would be: hits = self.client.search(...)
        print(">> 🔍 Searching 'Golden Runs' in Qdrant...")
        
        # LET'S ASSUME Qdrant found 'broken_rail_01.jpg' as the top match
        best_match_filename = "broken_rail_01.jpg" 
        similarity_score = 0.94
        
        print(f"   ✅ VISUAL MATCH: {best_match_filename} (Score: {similarity_score})")

        # 2. RETRIEVE CONTEXT (The Memory)
        context = self.find_historical_context(best_match_filename)
        if not context:
            print("   ⚠️ No history found for this image. Aborting.")
            return

        print(f"   📜 HISTORY: It's a {context['incident_type']} (Severity: {context['severity']})")

        # 3. REASONING (The Brain)
        proposal = self.efficiency_agent.propose_fix(
            context['incident_type'], 
            context['severity']
        )
        print(f"   🤖 AI PROPOSAL: {proposal['action']}")

        # 4. SAFETY AUDIT (The Sheriff)
        audit = self.safety_agent.audit_decision(proposal, sensor_data)
        
        # 5. EXECUTION
        self._execute_command(audit)

    def _execute_command(self, audit):
        print("\n>> 🎮 CONTROLLER DECISION:")
        if audit["status"] == "APPROVED":
            print(f"   🟢 EXECUTING: {audit['final_action']}")
        elif audit["status"] == "VETOED":
            print(f"   🔴 VETOED! OVERRIDE: {audit['override_action']}")
            print(f"   ⚠️ REASON: {audit['reason']}")
        else:
            print(f"   🟡 WARNING: {audit['override_action']}")

if __name__ == "__main__":
    system = NeuroRailSystem()

    # TEST SCENARIO
    # We pretend the train is moving FAST (130km/h)
    live_sensor_data = {
        "current_speed_kmh": 130, 
        "track_occupied": False
    }

    # Run the full cycle
    system.run_cycle("live_input.jpg", live_sensor_data)