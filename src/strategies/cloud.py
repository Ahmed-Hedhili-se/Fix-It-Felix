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
    def process(self, image_path: str, incident_id: str, user_context: str = ""):
        print(f" Processing {incident_id} in Cloud Tier 1...")
        if image_path:
            with open(image_path, "rb") as f:
                encoded_image = base64.b64encode(f.read()).decode("utf-8")
        else:
            encoded_image = None
            print(" Cloud Mode: Text-only request.")

        prompt_text = "Analyze this rail segment:"
        if user_context:
            prompt_text += f"\n\nUser Context/Question: {user_context}"
        
        user_content = [{"type": "text", "text": prompt_text}]
        if encoded_image:
            user_content.append({"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{encoded_image}"}})

        response = ai_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are the Fix-It Felix Expert Engine, specialized in heavy rail maintenance. Analyze rail assessments. Output technical JSON including 'detected_issues', 'severity', 'analysis' (technical summary), and 'advice' (SPECIFIC technical repair steps for engineers). Use dense keywords at the start of the 'analysis' for 256-dim Matryoshka optimization."
                },
                {
                    "role": "user",
                    "content": user_content
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