import streamlit as st
import os
import uuid
from PIL import Image
import tempfile
from src.memory import MemorySystem
from src.strategies.cloud import CloudMatryoshkaStrategy
from src.strategies.local import PrivateStrategy, OfflineStrategy
st.set_page_config(page_title="Fix-It Felix: Multi-Modal Engine", layout="wide")
@st.cache_resource
def load_memory():
    return MemorySystem(path="qdrant_db")
@st.cache_resource
def load_strategies():
    return {
        1: CloudMatryoshkaStrategy(), 
        3: PrivateStrategy(),         
        4: OfflineStrategy()          
    }
memory = load_memory()
strategies = load_strategies()
st.sidebar.title(" Engine Mode")
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
st.title(" Fix-It Felix: Diagnostics Dashboard")
st.markdown("---")
uploaded_file = st.file_uploader("Upload Image for Analysis", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])
    with col1:
        image = Image.open(uploaded_file)
        st.image(image, caption="Données d'entrée", use_container_width=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        image.save(tmp_file.name)
        tmp_path = tmp_file.name
    with col2:
        st.subheader("Analysis Results")
        if st.button(" Run Analysis Engine", type="primary"):
            with st.spinner("Processing through Tier 1-4..."):
                try:
                    incident_id = str(uuid.uuid4())
                    engine = strategies[mode_selection]
                    result = engine.process(tmp_path, incident_id)
                    st.success("Analyse de l'image terminée !")
                    log_text = result.get("analysis") or str(result.get("detections"))
                    vector_data = result.get("vector_full", result.get("vector_preview", [0.0]*768))
                    
                    # --- NOUVEAU : RECHERCHE MULTIMODALE (Image + Docs) ---
                    st.markdown("### 🔍 Expertise Multimodale (Image + Documents)")
                    ref_case = memory.get_reference_case(vector_data, mode_selection)
                    
                    if ref_case and ref_case["score"] > 0.7:
                        col_a, col_b = st.columns(2)
                        with col_a:
                            st.metric("Similarité Image", f"{ref_case['score']:.2%}")
                            st.write(f"**Archive détectée :** {ref_case['file_ref']}")
                        with col_b:
                            st.warning(f"**Solution Issue des Rapports :**\n{ref_case['solution']}")
                        
                        with st.expander("📜 Règlements & Documents associés"):
                            st.info(ref_case["rules"])
                            if ref_case.get("all_rules"):
                                for i, r in enumerate(ref_case["all_rules"][1:]):
                                    st.write(f"--- Document lié {i+2} ---")
                                    st.write(r)
                        st.divider()
                    else:
                        st.info("Aucun cas de référence exact trouvé. Analyse autonome uniquement.")

                    # Affichage du JSON d'analyse actuelle
                    with st.expander("Détails techniques de l'analyse"):
                        st.json(result)
                    
                    # Sauvegarde (Optionnelle ou automatique)
                    st.info(f"Enregistrement de cet incident dans la mémoire (Mode {mode_selection})...")
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
                    st.toast("ID d'incident archivé !", icon="💾")
                except Exception as e:
                    st.error(f"Pipeline Error: {e}")
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
st.markdown("---")
with st.expander(" Inspect Database Memory"):
    st.write("Recent Logs (Raw Check):")
    try:
        info = memory.client.get_collection(memory.collection)
        st.write(f"Collection '{memory.collection}' Status: {info.status}")
        st.write(f"Vectors Count: {info.points_count}")
    except Exception as e:
        st.warning(f"Could not fetch memory stats: {e}")