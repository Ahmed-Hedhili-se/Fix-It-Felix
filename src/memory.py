from qdrant_client import QdrantClient, models

class MemorySystem:
    def __init__(self, path="qdrant_db"):
        self.client = QdrantClient(path=path)
        self.collection_images = "rail_safety_logs"
        self.collection_knowledge = "expert_knowledge"

        if not self.client.collection_exists(self.collection_images):
            print(f" Creating collection '{self.collection_images}'...")
            self.client.create_collection(
                collection_name=self.collection_images,
                vectors_config={
                    "fast_lane": models.VectorParams(size=1536, distance=models.Distance.COSINE),
                    "offline_lane": models.VectorParams(size=768, distance=models.Distance.COSINE),
                }
            )

        if not self.client.collection_exists(self.collection_knowledge):
            print(f" Creating collection '{self.collection_knowledge}'...")
            self.client.create_collection(
                collection_name=self.collection_knowledge,
                vectors_config={
                    "text_vector": models.VectorParams(size=384, distance=models.Distance.COSINE)
                }
            )
        
        from fastembed import TextEmbedding
        self.text_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def _pad_vector(self, vector, target_dim):
        current = len(vector)
        if current < target_dim:
            return vector + [0.0] * (target_dim - current)
        return vector[:target_dim]

    def save_incident(self, vector, mode, payload):
        lane = "offline_lane" if mode in [3, 4] else "fast_lane"
        target_dim = 768 if mode in [3, 4] else 1536
        final_vector = self._pad_vector(vector, target_dim)
        self.client.upsert(
            collection_name=self.collection_images,
            points=[
                models.PointStruct(
                    id=payload.get("id"),
                    vector={lane: final_vector},
                    payload=payload
                )
            ]
        )

    def search_similar(self, query_vector, mode, limit=3):
        lane = "offline_lane" if mode in [3, 4] else "fast_lane"
        target_dim = 768 if mode in [3, 4] else 1536
        final_query = self._pad_vector(query_vector, target_dim)

        results = self.client.query_points(
            collection_name=self.collection_images,
            query=final_query,
            using=lane,
            limit=limit,
            with_payload=True,
            search_params=models.SearchParams(
                quantization=models.QuantizationSearchParams(
                    rescore=True
                )
            )
        ).points
        return results

    def search_knowledge(self, query_text, limit=3):
        """Recherche dans les documents techniques et les règlements."""
        query_vector = list(self.text_model.embed([query_text]))[0].tolist()

        results = self.client.query_points(
            collection_name=self.collection_knowledge,
            query=query_vector,
            using="text_vector",
            limit=limit,
            with_payload=True
        ).points
        return results

    def get_reference_case(self, query_vector, mode):
        """Trouve une image similaire et cherche les règlements associés."""
        results = self.search_similar(query_vector, mode, limit=1)
        if results:
            best = results[0]
            p = best.payload

            problem_summary = p.get("analysis") or p.get("status") or "rail defect"

            try:
                docs = self.search_knowledge(problem_summary, limit=2)
                rules_found = [d.payload.get("content") for d in docs if d.score > 0.5]
            except:
                rules_found = []

            return {
                "score": best.score,
                "problem_type": problem_summary,
                "solution": p.get("recommended_action") or p.get("solution") or "Inspection préventive et surveillance thermique recommandées.",
                "rules": rules_found[0] if rules_found else "Protocole standard de sécurité ferroviaire.",
                "all_rules": rules_found,
                "file_ref": p.get("filename")
            }
        return None