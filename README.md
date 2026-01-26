# 🛠️ Fix-It Felix: AI-Powered Rail Safety System

Fix-It Felix is an advanced research project focused on automating railway infrastructure inspection. It combines Computer Vision and Multimodal RAG (Retrieval-Augmented Generation) to detect track defects and provide instant regulatory advice.

## 🚀 Key Features

- **Hybrid AI Core**: Supports both Cloud (GPT-4o Vision) and local edge processing (YOLOv11).
- **Multimodal Memory**: Uses **Qdrant Vector Database** to store visual logs and technical documentation (PDFs, Excel, JSON).
- **Advanced Retrieval**: When a defect is detected, the system automatically finds the corresponding safety rules and historical solutions.
- **Matryoshka Embeddings**: Optimized for speed and low-latency search on edge devices.

## 🏛️ Project Architecture

The project is structured into 4 main layers:
1. **Frontend**: Streamlit-based (just before submission 3) dashboard for real-time analysis.
2. **Perception**: Vision engines (YOLO/SigLIP) for defect identification.
3. **Brain (Qdrant)**: Multi-vector memory system for cross-referencing visual data with technical manuals.
4. **ETL Pipeline**: Automated ingestion script for processing large datasets of images and documents.

## 🛠️ Installation & Usage

### 1. Requirements
Ensure you have Python 3.10+ installed. Install dependencies:
```bash
pip install -r requirements.txt
```

### 2. Database Setup
To build the knowledge base from your datasets:
```bash
python bulk_ingest.py
```

### 3. Launch Dashboard
```bash
streamlit run dashboard.py
```

## 📂 Project Structure
- `src/`: Core logic and strategy patterns for AI processing.
- `tools/`: Diagnostic and test scripts.
- `datasets/`: Storage for training images and technical documents.
- `qdrant_db/`: Local vector database (Git-ignored).

---
*Created by the Fix-It Felix Development Team.*
