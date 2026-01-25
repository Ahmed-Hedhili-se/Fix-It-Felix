from qdrant_client import QdrantClient
client = QdrantClient(path="test_db")
print("SEARCH EXITS:", hasattr(client, "search"))
print("DIR:", dir(client))
