from src.strategies.cloud import HighPrecisionStrategy, FastCloudStrategy
from src.strategies.local import PrivateStrategy, OfflineStrategy
strategies = {
    1: HighPrecisionStrategy(), 
    2: FastCloudStrategy(),     
    3: PrivateStrategy(),       
    4: OfflineStrategy()        
}
def run_analysis_engine(mode_selection, image_file_path):
    print(f"--- Starting Engine: Mode {mode_selection} ---")
    if mode_selection not in strategies:
        return "Error: Unknown Mode"
    engine = strategies[mode_selection]
    try:
        result = engine.process(image_file_path)
        return result
    except Exception as e:
        return f"Error running engine: {e}"