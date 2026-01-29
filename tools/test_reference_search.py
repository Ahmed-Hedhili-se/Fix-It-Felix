import numpy as np
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.memory import MemorySystem
import uuid

def test_kb_flow():
    print("--- Test du Flux Base de Connaissances ---")
    memory = MemorySystem()

    knowledge_id = str(uuid.uuid4())
    knowledge_vector = np.random.randn(768).tolist()
    knowledge_payload = {
        "id": knowledge_id,
        "status": "Fissure Longitudinale Type-A",
        "analysis": "Défaut de structure critique détecté sur le rail gauche.",
        "solution": "Mise en place d'un manchon de sécurité et soudure à froid sous 24h.",
        "rules": "Règlement SNCF-R24 : Interdiction de circulation > 40km/h.",
        "timetable": "Retards attendus sur la ligne Paris-Lyon."
    }

    print("Ingestion d'un cas de référence...")
    memory.save_incident(knowledge_vector, mode=3, payload=knowledge_payload)

    query_vector = (np.array(knowledge_vector) + np.random.normal(0, 0.05, 768)).tolist()

    print("Recherche d'un cas similaire dans Qdrant...")
    ref_case = memory.get_reference_case(query_vector, mode=3)

    if ref_case:
        print(f" Match Trouvé ! Score: {ref_case['score']:.4f}")
        print(f"📍 Type de Problème: {ref_case['problem_type']}")
        print(f" Solution: {ref_case['solution']}")
        print(f"📜 Règlement: {ref_case['rules']}")
        print(f"⏳ Impact Planning: {ref_case['timetable']}")
    else:
        print("❌ Aucun cas de référence trouvé.")

if __name__ == "__main__":
    test_kb_flow()
