import os
import requests

# 1. Setup Data Folder
DATA_FOLDER = "./data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    print(f">> Created folder: {DATA_FOLDER}")

# 2. URLs for Test Images (Real railway scenes)
images = {
    "clear_track.jpg": "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?q=80&w=1000&auto=format&fit=crop", # Sunny track
    "snow_switch.jpg": "https://images.unsplash.com/photo-1485739139909-d0d1783a7c80?q=80&w=1000&auto=format&fit=crop", # Snowy/Winter
    "broken_rail.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Broken_rail_at_Wrecclesham_-_geograph.org.uk_-_17894.jpg/640px-Broken_rail_at_Wrecclesham_-_geograph.org.uk_-_17894.jpg" # Obvious damage
}

print(">> ⬇️  Downloading test data...")

for filename, url in images.items():
    path = os.path.join(DATA_FOLDER, filename)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(path, 'wb') as f:
                f.write(response.content)
            print(f"   [OK] Downloaded {filename}")
        else:
            print(f"   [FAIL] Could not download {filename} (Status: {response.status_code})")
    except Exception as e:
        print(f"   [FAIL] Error downloading {filename}: {e}")

print(">> [DONE] Data ready.")