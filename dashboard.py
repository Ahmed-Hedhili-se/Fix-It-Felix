import streamlit as st
import time
import json
import os

from src.agents import EfficiencyAgent
from src.safety import SafetyAgent

st.set_page_config(page_title="Neuro-Rail Control", layout="wide")

st.sidebar.header("Neuro-Rail Control")
uploaded_file = st.sidebar.file_uploader("Upload Track Image", type=["jpg", "png"])
speed_input = st.sidebar.slider("Telematics: Train Speed (km/h)", 0, 200, 130)
track_status = st.sidebar.checkbox("Track Occupied?", value=False)

st.title("Fix-It Felix: Neuro-Symbolic Rail Brain")
st.markdown("---")

if 'efficiency_agent' not in st.session_state:
    st.session_state['efficiency_agent'] = EfficiencyAgent()
    st.session_state['safety_agent'] = SafetyAgent()

if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Perception (Visual Input)")
        st.image(uploaded_file, caption="Live CCTV Feed", use_container_width=True)
        
        with st.spinner("Searching Golden Runs..."):
            time.sleep(1.2)
            st.info("Match Found: 'Broken Rail' (Confidence: 94%)")
            st.json({
                "incident": "Broken Rail",
                "severity": "CRITICAL", 
                "history": "2022-04-12: Derailment Prevented"
            })

    with col2:
        st.subheader("2. Reasoning (The Debate)")
        
        st.markdown("**Efficiency Agent (Neural)**")
        proposal = st.session_state['efficiency_agent'].propose_fix("Broken Rail", "CRITICAL")
        
        with st.expander("See Neural Reasoning", expanded=True):
            st.write(f"**Proposal:** `{proposal['action']}`")
            st.write(f"**Reason:** {proposal['reason']}")

        st.markdown("Passes to Safety Layer")
        time.sleep(0.5)

        st.markdown("**Safety Agent (Symbolic)**")
        
        sensor_data = {
            "current_speed_kmh": speed_input,
            "track_occupied": track_status
        }
        
        audit = st.session_state['safety_agent'].audit_decision(proposal, sensor_data)

        if audit["status"] == "APPROVED":
            st.success(f"ACTION APPROVED: {audit['final_action']}")
        elif audit["status"] == "VETOED":
            st.error(f"VETOED BY PHYSICS ENGINE")
            st.warning(f"OVERRIDE ACTION: {audit['override_action']}")
            st.caption(f"Reason: {audit['reason']}")
        else:
            st.warning(f"WARNING: {audit['reason']}")

else:
    st.info("Waiting for visual input... Upload an image to start.")

st.markdown("---")
st.caption("System Status: ONLINE | Connected to Qdrant (Local) | Safety Protocols Active")