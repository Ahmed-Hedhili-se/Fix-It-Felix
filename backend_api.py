from fastapi import FastAPI, UploadFile, File, Form, Request
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
import json
from src.memory import MemorySystem
from src.strategies.cloud import CloudMatryoshkaStrategy
from src.strategies.local import PrivateStrategy, OfflineStrategy, get_siglip_embedding

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


print("Initializing Fix-It Felix Backend...")
memory = MemorySystem(path="qdrant_db")
strategies = {
    "cloud": CloudMatryoshkaStrategy(),
    "local": PrivateStrategy(),
    "fast": OfflineStrategy()
}

@app.post("/analyze")
async def analyze_endpoint(request: Request):
    form = await request.form()
    image = form.get("image")
    mode = form.get("mode", "cloud")
    context = form.get("context", "")
    incident_id = str(uuid.uuid4())
    print(f"Received Request: {incident_id} | Mode: {mode}")


    temp_path = None
    if image:
        temp_path = f"temp_{incident_id}.jpg"
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    try:
        ref_case = None
        enhanced_context = context

        if temp_path:
            # 1. Generate Visual Embedding First (for RAG)
            visual_vector = get_siglip_embedding(temp_path)
            
            # 2. Retrieve Historical Context (Knowledge Base)
            ref_case = memory.get_reference_case(visual_vector, mode=3)
            
            if ref_case and ref_case['score'] > 0.75:
                print(f" RAG Injection: Found {ref_case['file_ref']} ({ref_case['score']:.2f})")
                enhanced_context += f"\n[SYSTEM NOTICE]: Auto-detected similar historical incident: '{ref_case['problem_type']}'. Proven solution: '{ref_case['solution']}'."
        else:
             print(" No image provided. Skipping Visual RAG.")

        # 3. Process Analysis (with injected context)
        engine = strategies.get(mode, strategies["cloud"])
        
        # Strategies need to handle None path
        result = engine.process(temp_path, incident_id, user_context=enhanced_context) if temp_path or mode == "cloud" or mode == "local" else {"analysis": json.dumps({"analysis": "Image required for this mode.", "severity": "low"})}

        try:
            analysis_data = json.loads(result.get("analysis", "{}"))
        except:
            analysis_data = {"analysis": result.get("analysis", "No data")}

        # ref_case is already computed above

        response = {
            "incident_id": incident_id,
            "status": "success",
            "analysis": {
                "detected_issues": analysis_data.get("detected_issues", "Unknown"),
                "severity": analysis_data.get("severity", "Pending"),
                "problem_description": analysis_data.get("analysis", "Processing completed."),
                "repair_solution": analysis_data.get("advice", "Review manual."),
            },
            "knowledge_base": {
                "found_match": ref_case["score"] > 0.7 if ref_case else False,
                "confidence_score": ref_case["score"] if ref_case else 0.0,
                "reference_solution": ref_case["solution"] if ref_case else "No matching historical case found.",
                "document_ref": ref_case["file_ref"] if ref_case else "N/A"
            }
        }

        return response

    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
