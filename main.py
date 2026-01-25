# In main.py
from src.strategies.cloud import HighPrecisionStrategy, FastCloudStrategy
from src.strategies.local import PrivateStrategy, OfflineStrategy

# 1. Initialize Strategies
strategies = {
    1: HighPrecisionStrategy(), # GitHub GPT-4o
    2: FastCloudStrategy(),     # GitHub GPT-4o-mini
    3: PrivateStrategy(),       # Local YOLO + Slicing
    4: OfflineStrategy()        # Local YOLO + Binary
}

# 2. The Function Your UI Calls
def run_analysis_engine(mode_selection, image_file_path):
    print(f"--- Starting Engine: Mode {mode_selection} ---")
    
    if mode_selection not in strategies:
        return "Error: Unknown Mode"
    
    engine = strategies[mode_selection]
    
    # Run the strategy
    try:
        result = engine.process(image_file_path)
        return result
    except Exception as e:
        return f"Error running engine: {e}"