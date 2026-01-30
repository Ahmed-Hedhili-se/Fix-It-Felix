import numpy as np
import json
import requests
import torch
from PIL import Image
from transformers import AutoProcessor, AutoModel
from ultralytics import YOLO
from src.strategies.cloud import InferenceStrategy

SIGLIP_MODEL = "google/siglip2-base-patch16-224"

try:
    print("Loading Local YOLO model...")
    model = YOLO("yolo11n.pt")
except Exception as e:
    print(f"Warning: YOLO model not found. Please ensure 'yolo11n.pt' is in root. {e}")
    model = None

try:
    print(f"Loading SigLIP model ({SIGLIP_MODEL})...")
    siglip_processor = AutoProcessor.from_pretrained(SIGLIP_MODEL)
    siglip_model = AutoModel.from_pretrained(SIGLIP_MODEL)
except Exception as e:
    print(f"Warning: SigLIP model could not be loaded. {e}")
    siglip_processor = None
    siglip_model = None

def to_binary(vector):
    return (np.array(vector) > 0).astype(int).tolist()

def get_siglip_embedding(image_path):
    """
    Generates a 768-dim visual embedding using SigLIP.
    """
    if not siglip_model or not siglip_processor:
        return np.random.randn(768).tolist()

    try:
        image = Image.open(image_path).convert("RGB")
        inputs = siglip_processor(images=image, return_tensors="pt")
        with torch.no_grad():
            outputs = siglip_model.get_image_features(**inputs)
        image_vector = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
        return image_vector[0].tolist()
    except Exception as e:
        print(f"Error generating SigLIP embedding: {e}")
        return np.random.randn(768).tolist()

def get_ollama_analysis(detections, user_context=""):
    """
    Communicates with local Ollama 3.2 1B to generate analysis.
    """
    if not detections and not user_context:
        print("DEBUG: No detections/context. Using fallback safety prompt.")
        prompt = """
        You are Fix-It Felix, an expert repair assistant.
        An incident was reported on the railway, but the object detector could not identify specific objects (likely due to smoke, fire, or unique debris).

        Provide a JSON response with:
        - "analysis": "Visual detection inconclusive. Likely ambiguous hazard (smoke/fire/debris).",
        - "severity": "Medium",
        - "advice": "Inspect track manually for heat damage, obstructions, or cracks. Verify signaling systems.",
        - "detected_issues": "Unidentified Anomaly"

        Response MUST be valid JSON.
        """
    else:
        prompt = f"""
        You are Fix-It Felix, an expert repair assistant.
        A user has reported an incident.
        YOLO detections from the scene: {', '.join(detections) if detections else 'None'}
        User provided context: {user_context}

        Based on these detections, provide a JSON response with:
        - "analysis": A brief description of the problem based on the items detected.
        - "severity": "Low", "Medium", or "High".
        - "advice": Specific repair advice or next steps.
        - "detected_issues": A summary of the main issue.

        Response MUST be valid JSON. Do not include markdown formatting.
        """

    print(f"DEBUG: Sending prompt to Ollama: {prompt[:100]}...")

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3.2:1b",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            },
            timeout=90
        )
        if response.status_code == 200:
            result = response.json()
            raw_response = result.get("response", "{}")
            print(f"DEBUG: Ollama Raw Response: {raw_response}")
            return raw_response
        else:
            return json.dumps({
                "analysis": f"Ollama error: {response.status_code}",
                "severity": "Medium",
                "advice": "Please check Ollama service status.",
                "detected_issues": "Local AI Unavailable"
            })
    except Exception as e:
        return json.dumps({
            "analysis": f"Error connecting to Ollama: {str(e)}",
            "severity": "Medium",
            "advice": "Ensure Ollama is running with llama3.2:1b model.",
            "detected_issues": "Connection Error"
        })

class PrivateStrategy(InferenceStrategy):
    def process(self, image_path: str, incident_id: str, user_context: str = ""):
        if not model:
            return {"error": "YOLO model not loaded"}

        local_vector = [0.0] * 768
        detections = []

        if image_path:
            local_vector = get_siglip_embedding(image_path)
            results = model(image_path)
            for r in results:
                for c in r.boxes.cls:
                    detections.append(model.names[int(c)])
        
        ollama_result = get_ollama_analysis(list(set(detections)), user_context)

        optimized_vector = local_vector[:256]

        return {
            "mode": "3-PrivateLocal",
            "source": "Local CPU/GPU (SigLIP -> YOLO -> Ollama 3.2 1B)",
            "privacy": "Secure (No data left device)",
            "detections": list(set(detections)),
            "analysis": ollama_result,
            "vector_preview": optimized_vector[:5],
            "vector_full": local_vector
        }

class OfflineStrategy(InferenceStrategy):
    def process(self, image_path: str, incident_id: str, user_context: str = ""):
        if not model:
            return {"error": "YOLO model not loaded"}

        local_vector = [0.0] * 768
        detections = []

        if image_path:
            local_vector = get_siglip_embedding(image_path)
            results = model(image_path)
            detections = [model.names[int(c)] for r in results for c in r.boxes.cls]

        binary_vector = to_binary(local_vector)

        ollama_result = get_ollama_analysis(list(set(detections)), user_context)

        return {
            "mode": "4-OfflineBinary",
            "source": "Local (Offline - SigLIP -> YOLO -> Ollama 3.2 1B)",
            "storage_type": "Binary (1s and 0s)",
                "detections": list(set(detections)),
                "analysis": ollama_result,
                "vector_preview": binary_vector[:10],
                "vector_full": local_vector
            }