import streamlit as st
import os
import uuid
from PIL import Image
import tempfile
import json
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

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_files" not in st.session_state:
    st.session_state.processed_files = set()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

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
        user_context = st.text_area("Context / Question (Optional):", placeholder="Describe the issue or ask a specific question about this image...")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        image.save(tmp_file.name)
        tmp_path = tmp_file.name

    with col2:
        st.subheader("Analysis Engine")

        current_file_id = f"{uploaded_file.name}-{uploaded_file.size}"
        if "last_upload_id" not in st.session_state or st.session_state.last_upload_id != current_file_id:
            st.session_state.messages = []
            st.session_state.processed_files = set()
            st.session_state.last_upload_id = current_file_id
            st.rerun()

        should_analyze = st.button(" Run Analysis Engine", type="primary") or (uploaded_file.name not in st.session_state.processed_files)

        if should_analyze and uploaded_file.name not in st.session_state.processed_files:
            with st.spinner("Processing through Tier 1-4..."):
                try:
                    incident_id = str(uuid.uuid4())

                    user_msg_content = f"**Uploaded:** {uploaded_file.name}"
                    if user_context:
                        user_msg_content += f"\n\n**Context:** {user_context}"
                    st.session_state.messages.append({"role": "user", "content": user_msg_content})

                    engine = strategies[mode_selection]
                    result = engine.process(tmp_path, incident_id, user_context)
                    st.session_state.processed_files.add(uploaded_file.name)

                    try:
                        analysis_data = json.loads(result.get("analysis", "{}"))
                    except:
                        analysis_data = {"analysis": result.get("analysis", "No data")}

                    advice = analysis_data.get("advice", "Consultez les manuels de maintenance standards.")
                    severity = analysis_data.get("severity", "Inconnu")
                    technical_summary = analysis_data.get("analysis", "Pas de résumé disponible.")

                    vector_data = result.get("vector_full", result.get("vector_preview", [0.0]*768))
                    ref_case = memory.get_reference_case(vector_data, mode_selection)

                    chat_content = f"
                    chat_content += f"**Sévérité :** `{severity}`\n\n"
                    chat_content += f"**Avis de réparation :**\n{advice}\n\n"
                    chat_content += f"**Analyse technique :**\n{technical_summary}\n\n"

                    if ref_case and ref_case["score"] > 0.7:
                        chat_content += f"--- \n **Solution issue de la base de connaissances :**\n{ref_case['solution']}\n\n"
                        chat_content += f"**Référence :** {ref_case['file_ref']}"

                    st.session_state.messages.append({"role": "assistant", "content": chat_content})
                    st.success("Analyse terminée ! Consultez le chat pour les conseils.")
                    st.rerun()

                except Exception as e:
                    st.error(f"Pipeline Error: {e}")
                finally:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)

st.markdown("---")
if prompt := st.chat_input("Ask Felix for more advice..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        st.write("I'm analyzing your request...")
        st.write("Felix is ready to help you with the repair!")

with st.expander(" Inspect Database Memory"):
    st.write("Recent Logs (Raw Check):")
    try:
        info = memory.client.get_collection(memory.collection)
        st.write(f"Collection '{memory.collection}' Status: {info.status}")
        st.write(f"Vectors Count: {info.points_count}")
    except Exception as e:
        st.warning(f"Could not fetch memory stats: {e}")
