import streamlit as st
import time
import json
import os
from agents import EfficiencyAgent
from safety import SafetyAgent

# CONFIGURATION
st.set_page_config(page_title="Neuro-Rail Control", layout="wide", page_icon="🚄")

# --- SIDEBAR (CONTROLS) ---
st.sidebar.header("🎛️ Neuro-Rail Control")
uploaded_file = st.sidebar.file_uploader("Upload Track Image", type=["jpg", "png"])
speed_input = st.sidebar.slider("Telematics: Train Speed (km/h)", 0, 200, 130)
track_status = st.sidebar.checkbox("Track Occupied?", value=False)

# --- MAIN HEADER ---
st.title("🚄 Fix-It Felix: Neuro-Symbolic Rail Brain")
st.markdown("---")

# --- INITIALIZE AGENTS ---
if 'efficiency_agent' not in st.session_state:
    st.session_state['efficiency_agent'] = EfficiencyAgent()
    st.session_state['safety_agent'] = SafetyAgent()

# --- THE MAIN LOOP ---
if uploaded_file is not None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("1. Perception (Visual Input)")
        st.image(uploaded_file, caption="Live CCTV Feed", use_container_width=True)
        
        # MOCK SEARCH (Since we are in demo mode)
        # In real life, this would call qdrant_client.search()
        with st.spinner("🔍 Searching Golden Runs..."):
            time.sleep(1.2) # UX Pause
            st.info("✅ Match Found: 'Broken Rail' (Confidence: 94%)")
            st.json({
                "incident": "Broken Rail",
                "severity": "CRITICAL", 
                "history": "2022-04-12: Derailment Prevented"
            })

    with col2:
        st.subheader("2. Reasoning (The Debate)")
        
        # A. EFFICIENCY AGENT (NEURAL)
        st.markdown("**🤖 Efficiency Agent (Neural)**")
        proposal = st.session_state['efficiency_agent'].propose_fix("Broken Rail", "CRITICAL")
        
        # Display the Neural thought process
        with st.expander("See Neural Reasoning", expanded=True):
            st.write(f"**Proposal:** `{proposal['action']}`")
            st.write(f"**Reason:** {proposal['reason']}")

        st.markdown("⬇️ _Passes to Safety Layer_")
        time.sleep(0.5)

        # B. SAFETY AGENT (SYMBOLIC)
        st.markdown("**🛡️ Safety Agent (Symbolic)**")
        
        # Prepare sensor data from the sidebar sliders
        sensor_data = {
            "current_speed_kmh": speed_input,
            "track_occupied": track_status
        }
        
        audit = st.session_state['safety_agent'].audit_decision(proposal, sensor_data)

        # C. FINAL VERDICT
        if audit["status"] == "APPROVED":
            st.success(f"🟢 ACTION APPROVED: {audit['final_action']}")
        elif audit["status"] == "VETOED":
            st.error(f"🔴 VETOED BY PHYSICS ENGINE")
            st.warning(f"⚠️ OVERRIDE ACTION: {audit['override_action']}")
            st.caption(f"Reason: {audit['reason']}")
        else:
            st.warning(f"🟡 WARNING: {audit['reason']}")

else:
    st.info("👋 Waiting for visual input... Upload an image to start.")

# --- DEBUG FOOTER ---
st.markdown("---")
st.caption("System Status: ONLINE | Connected to Qdrant (Local) | Safety Protocols Active")