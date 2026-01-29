import pandas as pd
import json
import os
import glob
BASE_DIR = "datasets/raw_downloads"
OUTPUT_FILE = "datasets/knowledge_base/past_incidents.json"
def process_form_54(file_path):
    print(f" Processing Mechanical Data: {os.path.basename(file_path)}")
    try:
        df = pd.read_csv(file_path, low_memory=False)
        if 'CAUSE' in df.columns:
            dangerous = df[df['CAUSE'].isin(['T202', 'T109', 'T110', 'E50L'])]
        else:
            dangerous = df.head(50)
        cleaned_data = []
        for _, row in dangerous.head(50).iterrows():
            cleaned_data.append({
                "id": f"FRA-MECH-{row.get('INCDTNO', 'UNK')}",
                "type": "Broken Rail" if row.get('CAUSE') == 'T202' else "Track Defect",
                "visual_description": str(row.get('NARR1', 'Mechanical failure detected on track geometry.')).strip(),
                "severity": "CRITICAL",
                "action_taken": "EMERGENCY_STOP",
                "outcome": "Historical Event: Section repaired."
            })
        return cleaned_data
    except Exception as e:
        print(f" Error reading Form 54: {e}")
        return []
def process_form_57(file_path):
    print(f" Processing Crossing Data: {os.path.basename(file_path)}")
    try:
        df = pd.read_csv(file_path, low_memory=False)
        if 'TYPVEH' in df.columns:
            crashes = df[df['TYPVEH'].isin(['A', 'K', 'J'])]
        else:
            crashes = df.head(50)
        cleaned_data = []
        for _, row in crashes.head(50).iterrows():
            cleaned_data.append({
                "id": f"FRA-CROSS-{row.get('INCDTNO', 'UNK')}",
                "type": "Vehicle Collision",
                "visual_description": str(row.get('NARR1', 'Vehicle obstructed grade crossing.')).strip(),
                "severity": "CRITICAL",
                "action_taken": "EMERGENCY_BRAKE",
                "outcome": "Collision recorded. Crossing inspected."
            })
        return cleaned_data
    except Exception as e:
        print(f" Error reading Form 57: {e}")
        return []
def main():
    knowledge_base = []
    if not os.path.exists(BASE_DIR):
        print(f" Error: The folder '{BASE_DIR}' does not exist.")
        print(f"   Please create it and put your CSV files inside.")
        return
    files_54 = glob.glob(os.path.join(BASE_DIR, "Rail_Equipment*.csv"))
    files_57 = glob.glob(os.path.join(BASE_DIR, "Highway-Rail*.csv"))
    if files_54:
        knowledge_base.extend(process_form_54(files_54[0]))
    else:
        print(f" Warning: No 'Rail_Equipment*.csv' found in {BASE_DIR}")
    if files_57:
        knowledge_base.extend(process_form_57(files_57[0]))
    else:
        print(f" Warning: No 'Highway-Rail*.csv' found in {BASE_DIR}")
    if knowledge_base:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, "w") as f:
            json.dump(knowledge_base, f, indent=2)
        print(f" SUCCESS: Generated '{OUTPUT_FILE}' with {len(knowledge_base)} records.")
    else:
        print(" No data processed.")
if __name__ == "__main__":
    main()