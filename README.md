# 🛠️ Fix-It Felix: AI-Powered Rail Safety System v2.0

Fix-It Felix is an advanced research project designed to automate railway infrastructure inspection designed for technical staff . It combines Computer Vision and Multimodal **RAG (Retrieval-Augmented Generation)** to detect track defects and provide instant regulatory advice.

## 🚀 Key Features

-   **High-Precision RAG Flow**: Grounds local AI analysis in historical data, ensuring accurate results even when visual detection is ambiguous (e.g., heavy snow or fire).
-   **Flexible Input Analysis**: Supports **Image-only**, **Text-only** (Context Protocol), or **Hybrid** diagnostic requests.
-   **Multimodal Memory**: Deep integration with **Qdrant Vector Database** for cross-referencing visual logs with technical manuals.
-   **Matryoshka Embeddings**: Sliced vector search optimized for speed and low-latency on edge-tier devices.
-   **Hybrid AI Core**: Intelligent routing between Cloud (matryoshka(dim=256)-> GPT-4o Vision), Local Privacy (matryoshka (dim=256) ->SiGLIP -> YOLO11n-> Ollama Llama 3.2 1B), and Fast/Offline (Binary Quantization-> SigLIP -> YOLO -> ollama 3.2 1B) modes.

## 🏛️ Project Architecture

The system is built on a modern 4-tier stack:
1.  **Interface Layer (Next.js)**: A premium, industrial React dashboard with real-time analysis streaming and responsive design.
2.  **API Layer (FastAPI)**: A high-performance Python backend orchestrating model inference and memory retrieval.
3.  **Perception (YOLOv11 & SigLIP)**: State-of-the-art vision engines for real-time defect identification and visual embedding.
4.  **Memory (Qdrant)**: Multi-vector database storing 768d (offline) and 1536d (fast) lanes for visual and technical knowledge.

## 🛠️ Getting Started

### 1. Requirements
Ensure you have Python 3.10+ and Node.js 18+ installed.

### 2. Backend Setup
```bash
pip install -r requirements.txt
python bulk_ingest.py  
python backend_api.py  
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 📂 Project Structure
-   `src/`: Core logic, AI strategy patterns, and memory management.
-   `frontend/`: Next.js source code and industrial UI components.
-   `bulk_ingest.py`: ETL pipeline for multimodal data ingestion.
-   `datasets/`: Training images and technical knowledge repository.

---
*Created by the Fix-It-Felix Development Team. Powered by Advanced Agentic AI.*             (marbou7a nchlh)
