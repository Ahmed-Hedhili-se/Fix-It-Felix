from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid
import json
from src.memory import MemorySystem
from src.strategies.cloud import CloudMatryoshkaStrategy
from src.strategies.local import PrivateStrategy, OfflineStrategy

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
async def analyze_endpoint(
    image: UploadFile = File(...),
    mode: str = Form("cloud"),
    context: str = Form("")
):
    incident_id = str(uuid.uuid4())
    print(f"Received Request: {incident_id} | Mode: {mode}")


    temp_path = f"temp_{incident_id}.jpg"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    try:

        engine = strategies.get(mode, strategies["cloud"])

        if mode == "cloud":
            result = engine.process(temp_path, incident_id, user_context=context)
        else:
            result = engine.process(temp_path, incident_id, user_context=context)

        try:
            analysis_data = json.loads(result.get("analysis", "{}"))
        except:
            analysis_data = {"analysis": result.get("analysis", "No data")}

        vector_data = result.get("vector_full", result.get("vector_preview", [0.0]*768))


        mode_map = {"cloud": 1, "local": 3, "fast": 4}
        mode_int = mode_map.get(mode, 1)

        ref_case = memory.get_reference_case(vector_data, mode_int)

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
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
