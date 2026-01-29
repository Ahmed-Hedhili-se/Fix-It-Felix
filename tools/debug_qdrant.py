import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qdrant_client import QdrantClient

DB_PATH = "qdrant_db"

print(f"--- Qdrant Diagnostic for Windows ---")
print(f"Python Version: {sys.version}")
print(f"Database Path: {os.path.abspath(DB_PATH)}")

try:
    client = QdrantClient(path=DB_PATH)

    collections = client.get_collections().collections
    print(f" Connection Successful.")
    print(f" Active Collections: {[c.name for c in collections]}")

    has_search = hasattr(client, "search")
    print(f"ℹ Client has 'search' method: {has_search}")

    has_query = hasattr(client, "query_points")
    print(f"ℹ Client has 'query_points' method: {has_query}")

    client.close()
    print(" Client closed successfully.")

except Exception as e:
    print(f"❌ Error during diagnostic: {e}")
    if "msvcrt" in str(e).lower():
        print(" TIP: This error is often caused by a stale .lock file or another process holding the database.")