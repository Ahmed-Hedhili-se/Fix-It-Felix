import os
import sys

# Ajouter le dossier parent au système pour trouver le dossier 'src'
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient

DB_PATH = "qdrant_db"

print(f"--- Qdrant Diagnostic for Windows ---")
print(f"Python Version: {sys.version}")
print(f"Database Path: {os.path.abspath(DB_PATH)}")

try:
    # Attempt to initialize client
    client = QdrantClient(path=DB_PATH)
    
    # Check for collection exists instead of hasattr(search)
    # search is a method on the client, but checking functionality is better
    collections = client.get_collections().collections
    print(f"✅ Connection Successful.")
    print(f"✅ Active Collections: {[c.name for c in collections]}")
    
    # Check if 'search' exists (it should in latest qdrant-client)
    has_search = hasattr(client, "search")
    print(f"ℹ️ Client has 'search' method: {has_search}")
    
    # Check if 'query_points' exists (modern API)
    has_query = hasattr(client, "query_points")
    print(f"ℹ️ Client has 'query_points' method: {has_query}")

    client.close()
    print("✅ Client closed successfully.")

except Exception as e:
    print(f"❌ Error during diagnostic: {e}")
    if "msvcrt" in str(e).lower():
        print("💡 TIP: This error is often caused by a stale .lock file or another process holding the database.")