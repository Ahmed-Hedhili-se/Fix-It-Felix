from memory import MemorySystem  
class RailAgent:
    def __init__(self):
        print(" Initializing Fix-It Felix Agent...")
        self.vision = VisionSystem()
        self.memory = MemorySystem()  
    def evaluate_risk(self, image_path):
        print(f"\n Analyzing Image: {os.path.basename(image_path)}")
        is_defect, vision_msg = self.vision.analyze_image(image_path)
        if not is_defect:
            return {
                "status": "SAFE",
                "action": "Continue Normal Operations",
                "reason": "Vision system confirmed track is clear."
            }
        relevant_case = self.memory.search_similar(vision_msg)
        if relevant_case:
            thought = f"Similar to historical event {relevant_case['id']} "                      f"({relevant_case['type']}). Outcome was: {relevant_case['outcome']}"
        else:
            thought = "New type of anomaly detected. No exact match in database."
        return {
            "status": "DANGER",
            "action": " EMERGENCY STOP & DISPATCH CREW",
            "reason": f"{vision_msg}. Context: {thought}"
        }