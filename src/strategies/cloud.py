import os
import base64
import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from abc import ABC, abstractmethod
load_dotenv()
ai_client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ.get("GITHUB_TOKEN") 
)
def matryoshka_slice(vector, target_dim):
    sliced = np.array(vector[:target_dim])
    norm = np.linalg.norm(sliced)
    if norm > 0:
        sliced = sliced / norm
    return sliced.tolist()
class InferenceStrategy(ABC):
    @abstractmethod
    def process(self, image_path: str, incident_id: str):
        pass
class CloudMatryoshkaStrategy(InferenceStrategy):
    def process(self, image_path: str, incident_id: str):
        print(f" Processing {incident_id} in Cloud Tier 1...")
        with open(image_path, "rb") as f:
            encoded_image = base64.b64encode(f.read()).decode("utf-8")
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
            response_format={"type": "json_object"} 
        )
        analysis_json = response.choices[0].message.content
        emb_response = ai_client.embeddings.create(
            input=analysis_json,
            model="text-embedding-3-small"
        )
        original_vector = emb_response.data[0].embedding
        mrl_vector = matryoshka_slice(original_vector, target_dim=256)
        return {
            "mode": "Cloud Matryoshka (256)",
            "vector_preview": mrl_vector[:5],
            "vector_full": mrl_vector,   
            "analysis": analysis_json,   
            "status": "Processed (Waiting for Save)"
        }