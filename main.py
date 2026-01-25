import uuid
from src.strategies.cloud import CloudMatryoshkaStrategy
from src.strategies.local import PrivateStrategy, OfflineStrategy

strategies = {
    1: CloudMatryoshkaStrategy(), 
    3: PrivateStrategy(),       
    4: OfflineStrategy()        
}

def run_analysis_engine(mode_selection, image_file_path):
    print(f"--- Starting Engine: Mode {mode_selection} ---")
    if mode_selection not in strategies:
        return "Error: Unknown Mode"
    
    incident_id = str(uuid.uuid4())
    engine = strategies[mode_selection]
    try:
        result = engine.process(image_file_path, incident_id)
        return result
    except Exception as e:
        return f"Error running engine: {e}"