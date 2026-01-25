from qdrant_client import QdrantClient

COLLECTION_NAME = "rail_safety_logs"

class MemoryBank:
    def __init__(self):
        self.client = QdrantClient(path="qdrant_db")
        print("Memory Bank (Qdrant): Connected.")

    def search_by_vector(self, vector):
        results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=vector,
            limit=1
        ).points

        if results:
            best = results[0]
            return {
                "found": True,
                "filename": best.payload['filename'],
                "status": best.payload['status'],
                "score": best.score
            }
        else:
            return {"found": False}