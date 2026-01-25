import streamlit as st
import os
import uuid
from PIL import Image
import tempfile

# --- IMPORT YOUR ARCHITECTURE ---
from src.memory import MemorySystem
from src.strategies.cloud import CloudMatryoshkaStrategy
from src.strategies.local import PrivateStrategy, OfflineStrategy

# --- PAGE CONFIG ---
st.set_page_config(page_title="Fix-It Felix: Multi-Modal Engine", layout="wide")

# --- INITIALIZE BACKEND (TIERS 3 & 4) ---
@st.cache_resource
def load_memory():
    return MemorySystem(path="qdrant_db")

@st.cache_resource
def load_strategies():
    return {
        1: CloudMatryoshkaStrategy(), # Tier 1: Cloud Matryoshka
        3: PrivateStrategy(),         # Tier 3: Local YOLO + Slicing
        4: OfflineStrategy()          # Tier 4: Local YOLO + Binary
    }

memory = load_memory()
strategies = load_strategies()

# --- SIDEBAR: MODE SELECTION (TIER 1) ---
st.sidebar.title("⚙️ Engine Mode")
mode_selection = st.sidebar.radio(
    "Select Processing Pipeline:",
    options=[1, 3, 4],
    format_func=lambda x: {
        1: "1. Cloud Matryoshka (GPT-4o + 256-dim)",
        3: "3. Private/Secure (Local | Privacy)",
        4: "4. Offline/Edge (Local | No Internet)"
    }[x]
)

st.sidebar.info(f"**Current Strategy:**\n{strategies[mode_selection].__class__.__name__}")

# --- MAIN INTERFACE ---
st.title("🔧 Fix-It Felix: Diagnostics Dashboard")
st.markdown("---")

uploaded_file = st.file_uploader("Upload Image for Analysis", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    # 1. Show Image
    col1, col2 = st.columns([1, 1])
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption="Input Data", use_column_width=True)
    
    # 2. Save Temp File (Strategies need a path)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        image.save(tmp_file.name)
        tmp_path = tmp_file.name

    # 3. Process Button
    with col2:
        st.subheader("Analysis Results")
        if st.button("🚀 Run Analysis Engine", type="primary"):
            
            with st.spinner("Processing through Tier 1-4..."):
                try:
                    # Generate ID
                    incident_id = str(uuid.uuid4())
                    
                    # --- EXECUTE STRATEGY (Tier 3) ---
                    engine = strategies[mode_selection]
                    result = engine.process(tmp_path, incident_id)
                    
                    # Display Raw Result
                    st.success("Processing Complete!")
                    st.json(result)

                    # --- EXTRACT DATA FOR DB ---
                    # Note: Cloud strategy saves to DB internally. Local strategies return data.
                    # We only need to manually save for Local modes if they don't do it themselves.
                    # Looking at code: CloudMatryoshkaStrategy saves to DB. 
                    # PrivateStrategy/OfflineStrategy do NOT save to DB in process().
                    
                    # --- EXTRACT DATA FOR DB ---
                    log_text = result.get("analysis") or str(result.get("detections"))
                    
                    # Get the vector (Full or Sliced)
                    vector_data = result.get("vector_full", result.get("vector_preview", [0.0]*768))
                    
                    # --- SAVE TO MEMORY (All modes now handled centrally) ---
                    st.info(f"Saving to Neuro-Rail Memory (Mode {mode_selection})...")
                    
                    memory.save_incident(
                        vector=vector_data,
                        mode=mode_selection,
                        payload={
                            "id": incident_id,
                            "mode": result.get("mode"),
                            "source": "dashboard_upload",
                            "analysis": log_text
                        }
                    )
                    st.toast("✅ Saved to Qdrant Database!", icon="💾")

                except Exception as e:
                    st.error(f"Pipeline Error: {e}")
                finally:
                    # Cleanup temp file
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

# --- MEMORY INSPECTOR (OPTIONAL) ---
st.markdown("---")
with st.expander("🔍 Inspect Database Memory"):
    st.write("Recent Logs (Raw Check):")
    # Since we can't search by text easily without embedding model, 
    # we'll just check if we can retrieve points or verify connection.
    try:
        # Just show info about collection
        info = memory.client.get_collection(memory.collection)
        st.write(f"Collection '{memory.collection}' Status: {info.status}")
        st.write(f"Vectors Count: {info.points_count}")
    except Exception as e:
        st.warning(f"Could not fetch memory stats: {e}")