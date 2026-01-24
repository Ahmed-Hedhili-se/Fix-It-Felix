import os
import json

from src.perception import PerceptionEngine
from src.search import MemoryBank
from src.agents import EfficiencyAgent
from src.safety import SafetyAgent

HISTORY_FILE = "data/history.json"

class NeuroRailSystem:
    def __init__(self):
        print("\nSYSTEM BOOT: INITIALIZING NEURO-RAIL...")
        
        self.vision = PerceptionEngine()
        self.memory = MemoryBank()
        self.efficiency_agent = EfficiencyAgent()
        self.safety_agent = SafetyAgent()
        
    def run_cycle(self, image_path, sensor_data):
        pass

if __name__ == "__main__":
    system = NeuroRailSystem()
    
    live_sensor_data = {"current_speed_kmh": 130, "track_occupied": False}
    
    if os.path.exists("data/broken_rail.jpg"):
        system.run_cycle("data/broken_rail.jpg", live_sensor_data)
    else:
        print("Please add an image to ./data/ to test.")