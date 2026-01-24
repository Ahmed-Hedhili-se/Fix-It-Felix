import os
import requests

DATA_FOLDER = "./data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)
    print(f"Created folder: {DATA_FOLDER}")

images = {
    "clear_track.jpg": "https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?q=80&w=1000&auto=format&fit=crop",
    "snow_switch.jpg": "https://images.unsplash.com/photo-1485739139909-d0d1783a7c80?q=80&w=1000&auto=format&fit=crop",
    "broken_rail.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d3/Broken_rail_at_Wrecclesham_-_geograph.org.uk_-_17894.jpg/640px-Broken_rail_at_Wrecclesham_-_geograph.org.uk_-_17894.jpg"
}

print("Downloading test data...")

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

print("Data ready.")