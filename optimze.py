from qdrant_client import QdrantClient, models

COLLECTION_NAME = "rail_lines"
VECTOR_SIZE = 768

def initialize_optimized_brain():
    print("INITIALIZING NEW OPTIMIZED BRAIN...")
    
    client = QdrantClient(path="rail_db")
    
    client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=VECTOR_SIZE,
            distance=models.Distance.COSINE
        ),
        quantization_config=models.BinaryQuantization(
            binary=models.BinaryQuantizationConfig(
                always_ram=True
            )
        )
    )

    print(f"   Collection '{COLLECTION_NAME}' created.")
    print("   Binary Quantization: ENABLED")
    print("   Status: Ready for Bulk Ingest.")

if __name__ == "__main__":
    initialize_optimized_brain()