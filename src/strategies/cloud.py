import os
import base64
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from abc import ABC, abstractmethod

load_dotenv()

# --- SETUP CLIENTS ---
# 1. AI Client (GitHub Models)
ai_client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ.get("GITHUB_TOKEN") 
)

# --- HELPER: MATRYOSHKA MATH ---
def matryoshka_slice(vector, target_dim):
    """
    Slices a vector to 'target_dim' and re-normalizes it.
    Crucial for maintaining cosine similarity accuracy.
    """
    sliced = np.array(vector[:target_dim])
    norm = np.linalg.norm(sliced)
    if norm > 0:
        sliced = sliced / norm
    return sliced.tolist()

class InferenceStrategy(ABC):
    @abstractmethod
    def process(self, image_path: str, incident_id: str):
        pass

# --- MODE 1: CLOUD MATRYOSHKA (Tier 1) ---
class CloudMatryoshkaStrategy(InferenceStrategy):
    def process(self, image_path: str, incident_id: str):
        print(f"☁️ Processing {incident_id} in Cloud Tier 1...")

        # 1. Encode Image
        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")

        # 2. Antigravity Analysis (The Reasoning Core)
        response = ai_client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "You are the Fix-It Felix Antigravity Engine. Analyze rail images. Output technical JSON. Use dense keywords (e.g., 'fissure', 'spalling') at the start of your summary for 256-dim Matryoshka optimization."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this rail segment:"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}}
                    ]
                }
            ],
            model="gpt-4o", 
            temperature=0,
            response_format={"type": "json_object"} # Fast JSON mode
        )
        analysis_json = response.choices[0].message.content

        # 3. Generate Embedding (Using text-embedding-3-small)
        # We embed the JSON/Text to get the raw 1536 vector
        emb_response = ai_client.embeddings.create(
            input=analysis_json,
            model="text-embedding-3-small"
        )
        original_vector = emb_response.data[0].embedding
        
        # 4. Matryoshka Slicing (1536 -> 256)
        mrl_vector = matryoshka_slice(original_vector, target_dim=256)

        # 5. Return Data for centralized saving (Fixes Qdrant Lock Issue)
        return {
            "mode": "Cloud Matryoshka (256)",
            "vector_preview": mrl_vector[:5],
            "vector_full": mrl_vector,   # Return the sliced vector for saving
            "analysis": analysis_json,   # Return the analysis for saving
            "status": "Processed (Waiting for Save)"
        }