from qdrant_client import QdrantClient, models
COLLECTION_NAME = "rail_safety_logs"
VECTOR_SIZE = 768
from qdrant_client import QdrantClient, models
class MemorySystem:
    def __init__(self, path="qdrant_db"):
        self.client = QdrantClient(path=path)
        self.collection = "rail_safety_logs"
    def save_incident(self, vector, mode, payload):
        lane = "offline_lane" if mode == 3 else "fast_lane"
        self.client.upsert(
            collection_name=self.collection,
            points=[
                models.PointStruct(
                    id=payload.get("id"),
                    vector={lane: vector},
                    payload=payload
                )
            ]
        )
    def search_similar(self, query_vector, mode, limit=5):
        lane = "offline_lane" if mode == 3 else "fast_lane"
        return self.client.search(
            collection_name=self.collection,
            query_vector=(lane, query_vector),
            limit=limit,
            search_params=models.SearchParams(
                quantization=models.QuantizationSearchParams(
                    rescore=True
                )
            )
        )