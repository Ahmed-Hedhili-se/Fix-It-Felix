import streamlit as st
import torch
from transformers import AutoProcessor, AutoModel
from qdrant_client import QdrantClient
from PIL import Image
import os

st.set_page_config(page_title="Neuro-Rail Control", page_icon="🚄", layout="wide")

st.title("FIX IT FELIX : Neuro-Rail: Autonomous Network Brain")
st.markdown("###  Perception & Decision Engine")

@st.cache_resource
def load_brain():
    print(">> Loading Models...")
    model_id = "google/siglip-base-patch16-224"
    processor = AutoProcessor.from_pretrained(model_id)
    model = AutoModel.from_pretrained(model_id)
    client = QdrantClient(path="rail_db")
    return processor, model, client

try:
    processor, model, client = load_brain()
    st.success("✅ System Online: Brain Connected.")
except Exception as e:
    st.error(f"❌ System Offline: {e}")
    st.stop()

st.sidebar.header("📡 Live Feed Input")
mode = st.sidebar.radio("Input Source", ["Text Query (Manual)", "Drone Image (Upload)"])

COLLECTION_NAME = "railway_knowledge"

if mode == "Text Query (Manual)":
    query = st.text_input("Enter patrol observation:", "a broken railway track")
    if st.button("Analyze Report"):
        with st.spinner("Processing language vector..."):
            inputs = processor(text=[query], images=None, return_tensors="pt", padding="max_length")
            with torch.no_grad():
                outputs = model.get_text_features(**inputs)
            
            text_vector = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
            results = client.query_points(
                collection_name=COLLECTION_NAME,
                query=text_vector[0].tolist(),
                limit=1
            ).points
            
            best_match = results[0] if results else None

elif mode == "Drone Image (Upload)":
    uploaded_file = st.file_uploader("Upload Drone Surveillance Photo", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, caption="Live Feed", width=400)
        
        if st.button("Scan for Anomalies"):
            with st.spinner("Vision Model Scanning..."):
                inputs = processor(images=image, return_tensors="pt")
                with torch.no_grad():
                    outputs = model.get_image_features(**inputs)
                
                img_vector = outputs / outputs.norm(p=2, dim=-1, keepdim=True)
                results = client.query_points(
                    collection_name=COLLECTION_NAME,
                    query=img_vector[0].tolist(),
                    limit=1
                ).points
                
                best_match = results[0] if results else None

if 'best_match' in locals() and best_match:
    st.divider()
    st.subheader(" Memory Retrieval & Decision")
    
    col1, col2 = st.columns(2)
    
    payload = best_match.payload
    status = payload['status']
    score = best_match.score
    
    with col1:
        st.write(f"**Matched Historical Event:** `{payload['filename']}`")
        st.write(f"**Similarity Score:** `{score:.4f}`")
        
        memory_path = os.path.join("data", payload['filename'])
        if os.path.exists(memory_path):
            st.image(memory_path, caption="Visual Match from Memory Bank", width=300)
    
    with col2:
        if status == "CRITICAL":
            st.error(f"##  STATUS: {status}")
            st.markdown("### ACTION: STOP TRAIN IMMEDIATELY")
            st.write("Reason: High structural damage detected matching critical failure patterns.")
        elif status == "WARNING":
            st.warning(f"##  STATUS: {status}")
            st.markdown("### ACTION: SLOW DOWN")
            st.write("Reason: Obstruction or weather conditions detected.")
        else:
            st.success(f"##  STATUS: {status}")
            st.markdown("### ACTION: PROCEED")
            st.write("Reason: Track appears clear matches safe patterns.")