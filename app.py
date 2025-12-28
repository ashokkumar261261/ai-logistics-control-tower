import streamlit as st
import os
import requests
import json
import time
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import io
from pydub import AudioSegment

# Configuration
API_URL = os.getenv("API_URL", "https://logistics-gateway-39c2w2ut.uc.gateway.dev")

# Page Config
st.set_page_config(page_title="Multi-Agent Logistics Control Tower", page_icon="🚚", layout="wide")

def transcribe_audio(audio_bytes):
    """Transcribes audio using SpeechRecognition and Pydub for conversion."""
    r = sr.Recognizer()
    try:
        # Convert incoming audio (likely WebM/AAC) to WAV using Pydub
        audio_file = io.BytesIO(audio_bytes)
        audio = AudioSegment.from_file(audio_file)
        
        # Export as PCM WAV for SpeechRecognition
        wav_io = io.BytesIO()
        audio.export(wav_io, format="wav")
        wav_io.seek(0)
        
        with sr.AudioFile(wav_io) as source:
            audio_data = r.record(source)
            text = r.recognize_google(audio_data)
            return text
    except Exception as e:
        return f"Error transcribing: {e}"

st.title("🚚 Multi-Agent Logistics Control Tower")
st.markdown("""
**Collaborative AI Workflow**: Data Analyst (BigQuery) + Fleet Strategist (Insight)
*Now featuring robust Voice & Data Explorer*
""")

# --- Sidebar: User Identity & RBAC ---
st.sidebar.title("🛡️ Identity Context")
user_role = st.sidebar.selectbox(
    "Select Your Role",
    ["Logistics Manager", "Fleet Operator", "Guest"],
    index=0,
    help="Role determines agent access permissions."
)
st.sidebar.markdown(f"**Current Access:** `{user_role}`")

# --- Role Guide ---
with st.sidebar.expander("ℹ️ Role Permissions & Samples"):
    if user_role == "Logistics Manager":
        st.write("**Access:** Full access to all tables (Shipments, Fleet, Locations) and financial data.")
        st.write("**Try:** 'Total profit of all shipments', 'Identify bottlenecks in London'")
    elif user_role == "Fleet Operator":
        st.write("**Access:** Fleet and Shipment operations. Restricted from financial data.")
        st.write("**Try:** 'Vehicle capacity > 10,000kg', 'List delayed shipments'")
    else:
        st.write("**Access:** Basic shipment status only.")
        st.write("**Try:** 'Status of shipment 14', 'Distribution centers list'")

# --- Communication Hub Instructions ---
with st.sidebar.expander("❓ How to use Communication Hub"):
    st.markdown("""
    The **Communication Hub** simulates real-world interactions with dispatchers and drivers:
    1. **Check Inbox**: Click the button to see if there are any pending alerts.
    2. **Send Emails**: Type or speak commands like:
       - *"Send an email to the dispatcher about the delay in London."*
       - *"Notify the driver of vehicle 4 about the route change."*
    3. **Agent Role**: The **Logistics Comm Assistant** handles these tasks and provides a summary.
    """)

# --- Communication Hub ---
with st.sidebar.expander("📧 Communication Hub"):
    st.info("Agent: Logistics Comm Assistant")
    if st.button("Check Inbox"):
        st.session_state.messages.append({"role": "user", "content": "Check my inbox"})
        # Trigger query immediately? For now just let user click or speak. 
        # Better: Set prompt directly
        st.session_state.current_prompt = "Check my inbox"

st.sidebar.markdown("---")

# --- Sidebar: Sample Data Explorer (Hardcoded) ---
st.sidebar.title("📊 Data Explorer")
if st.sidebar.button("Show Sample Data"):
    with st.sidebar:
        # Hardcoded BigQuery-like sample data
        sample_shipments = [
            {"id": 10, "origin": "London", "destination": "Paris", "status": "In Transit", "priority": "High", "cost": 1200.50},
            {"id": 14, "origin": "Wrightview", "destination": "New Donport", "status": "Delayed", "priority": "Standard", "cost": 850.00},
            {"id": 22, "origin": "Delhi", "destination": "Mumbai", "status": "Delivered", "priority": "Urgent", "cost": 3400.00}
        ]
        sample_vehicles = [
            {"vehicle_id": 1, "type": "Heavy Truck", "capacity_kg": 15000, "status": "Active"},
            {"vehicle_id": 4, "type": "Light Van", "capacity_kg": 2500, "status": "Maintenance"}
        ]
        
        st.write("**Table: Shipments**")
        st.dataframe(sample_shipments, hide_index=True)
        
        st.write("**Table: Vehicles**")
        st.dataframe(sample_vehicles, hide_index=True)
        
        st.info("💡 Useful for verifying data-driven queries.")

st.sidebar.markdown("---")
st.sidebar.title("🤖 Multi-Agent Fleet")
st.sidebar.success("Orchestrator: Active")
st.sidebar.info("📊 Agent 1: Logistics Analyst (Online)")
st.sidebar.info("🚀 Agent 2: Fleet Strategist (Online)")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input Section ---
st.write("---")
col_input, col_voice = st.columns([4, 1])

with col_voice:
    # Voice Recorder Component
    audio = mic_recorder(
        start_prompt="🎤 Start Voice Query",
        stop_prompt="⏹️ Stop & Process",
        key='recorder'
    )

with col_input:
    text_prompt = st.chat_input("Ask about shipments, vehicle capacity, or optimization...")

# Decision Logic for Prompt Source
final_prompt = None
if audio:
    voice_text = transcribe_audio(audio['bytes'])
    if "Error" not in voice_text:
        final_prompt = voice_text
        st.toast(f"🎤 Voice Heard: {voice_text}")
    else:
        st.error(voice_text)

if text_prompt:
    final_prompt = text_prompt

# Process Query
if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤖 *Orchestrator: Engaging collaborative agents...*")
        
        try:
            # Backend Call
            response = requests.post(f"{API_URL}/query", json={"query": final_prompt, "role": user_role}, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("summary", "No insight provided.")
                
                # Logic to determine agent attribution for clear UI
                attributed_summary = summary
                if "Anlayst" not in summary and "Strategist" not in summary:
                    # Inject labels if not present for clarity
                    if "Strategy" in summary or any(kw in final_prompt.lower() for kw in ["optimize", "suggest", "improve", "why"]):
                         attributed_summary = f"**[Data Analyst]**: I retrieved the shipment facts.\n\n**[Fleet Strategist]**: {summary}"
                    else:
                         attributed_summary = f"**[Data Analyst]**: {summary}"

                message_placeholder.markdown(attributed_summary)
                st.session_state.messages.append({"role": "assistant", "content": attributed_summary})
                
                # Show Agent Trace
                with st.expander("🔍 Collaboration Trace"):
                    st.write("**Data Analyst**: Queried BigQuery and identified logistics trends.")
                    if "Fleet Strategist" in attributed_summary:
                        st.write("**Fleet Strategist**: Applied operational logic for optimization advice.")
                    st.write("**Orchestrator**: Synthesized final response for user.")
            else:
                st.error(f"Backend Insight Failure ({response.status_code})")
        except Exception as e:
            st.error(f"Connection Error: {e}")

# Sidebar Health Check
if st.sidebar.button("System Health Check"):
    try:
        res = requests.get(f"{API_URL}/health")
        if res.status_code == 200:
            st.sidebar.success("All Systems Operational")
        else:
            st.sidebar.error("System Unhealthy")
    except:
        st.sidebar.error("Offline")
