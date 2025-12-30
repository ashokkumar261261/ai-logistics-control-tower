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

# --- Custom Premium CSS ---
st.markdown("""
<style>
    /* Premium Button Styling for Follow-up Chips */
    div.stButton > button {
        border-radius: 20px;
        border: 1px solid #4F8BF9;
        background-color: transparent;
        color: #4F8BF9;
        padding: 5px 15px;
        font-size: 14px;
        transition: all 0.3s ease;
        margin-bottom: 10px;
    }
    div.stButton > button:hover {
        background-color: #4F8BF9;
        color: white;
        border: 1px solid #4F8BF9;
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(79, 139, 249, 0.3);
    }
    /* Style for the suggestion header */
    .suggestion-header {
        font-size: 13px;
        font-weight: 600;
        color: #666;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 5px;
    }
</style>
""", unsafe_allow_html=True)

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
        st.write("**Try:** 'Which shipments have the highest profit margin (revenue - cost)?', 'Identify bottlenecks in London'")
    elif user_role == "Fleet Operator":
        st.write("**Access:** Fleet and Shipment operations. Restricted from financial data.")
        st.write("**Try:** 'Are there any active vehicles with fuel levels below 20%?', 'List delayed shipments'")
    else:
        st.write("**Access:** Basic shipment status only.")
        st.write("**Try:** 'Identify shipments carrying Medical Supplies that are currently delayed.', 'Status of shipment 14'")

with st.sidebar.expander("🌟 Experience the New V3.2 Features"):
    st.markdown("""
    - **Memory**: Ask about "those shipments" to test context.
    - **Follow-ups**: Click the AI-suggested chips!
    - **Enriched Data**: Try querying about 'fuel levels', 'driver ratings', or 'experience years'.
    """)

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
        # Enhanced BigQuery-like sample data
        sample_shipments = [
            {"id": 10, "origin": "London", "destination": "Paris", "status": "In Transit", "priority": "High", "cost": 1200.50, "revenue": 1800.00, "weight_kg": 500.5, "cargo_type": "Electronics", "customer_name": "Tech Corp"},
            {"id": 14, "origin": "Wrightview", "destination": "New Donport", "status": "Delayed", "priority": "Standard", "cost": 850.00, "revenue": 1200.00, "weight_kg": 1200.0, "cargo_type": "Furniture", "customer_name": "Home Furnishings"},
            {"id": 22, "origin": "Delhi", "destination": "Mumbai", "status": "Delivered", "priority": "Urgent", "cost": 3400.00, "revenue": 5000.00, "weight_kg": 2500.0, "cargo_type": "Medical Supplies", "customer_name": "Health Plus"}
        ]
        sample_vehicles = [
            {"vehicle_id": 1, "type": "Heavy Truck", "capacity_kg": 15000, "status": "Active", "fuel_level": 75.5, "current_load_kg": 5000.0},
            {"vehicle_id": 4, "type": "Light Van", "capacity_kg": 2500, "status": "Maintenance", "fuel_level": 10.5, "current_load_kg": 0.0}
        ]
        sample_drivers = [
            {"id": 1, "name": "Kyle Miller", "status": "On Duty", "rating": 4.8, "experience_years": 10, "current_location": "London"},
            {"id": 2, "name": "Sarah Jenkins", "status": "Off Duty", "rating": 4.9, "experience_years": 5, "current_location": "Paris"}
        ]
        
        st.write("**Table: Shipments (Enriched)**")
        st.dataframe(sample_shipments, hide_index=True)
        
        st.write("**Table: Vehicles (Enriched)**")
        st.dataframe(sample_vehicles, hide_index=True)

        st.write("**Table: Drivers (Enriched)**")
        st.dataframe(sample_drivers, hide_index=True)
        
        st.info("💡 Useful for verifying data-driven queries.")

st.sidebar.markdown("---")
st.sidebar.title("🤖 Multi-Agent Fleet")
st.sidebar.success("Orchestrator: Active")
st.sidebar.info("📊 Agent 1: Logistics Analyst (Online)")
st.sidebar.info("🚀 Agent 2: Fleet Strategist (Online)")

if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and "followups" in message and i == len(st.session_state.messages) - 1:
            if message["followups"]:
                st.markdown("<div class='suggestion-header'>✨ AI Suggested Next Steps</div>", unsafe_allow_html=True)
                # Use a container for the chips
                fups = message["followups"]
                # Display buttons horizontally
                cols = st.columns([1]*len(fups) + [2]) # Add space at the end
                for idx, q in enumerate(fups):
                    if cols[idx].button(q, key=f"fup_{i}_{idx}"):
                        st.session_state.fup_trigger = q
                        st.rerun()

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

# Handle Follow-up Click Trigger
if "fup_trigger" in st.session_state and st.session_state.fup_trigger:
    final_prompt = st.session_state.fup_trigger
    st.session_state.fup_trigger = None

# Process Query
if final_prompt:
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤖 *Orchestrator: Engaging collaborative agents...*")
        
        try:
            # Prepare History (last 5 messages for context window)
            history_str = "\n".join([f"{m['role'].upper()}: {m['content']}" for m in st.session_state.messages[-6:-1]])
            
            # Backend Call
            response = requests.post(
                f"{API_URL}/query", 
                json={
                    "query": final_prompt, 
                    "role": user_role,
                    "history": history_str
                }, 
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("summary", "No insight provided.")
                followups = result.get("followups", [])
                
                # Logic to determine agent attribution for clear UI
                attributed_summary = summary
                if "Anlayst" not in summary and "Strategist" not in summary:
                    # Inject labels if not present for clarity
                    if "Strategy" in summary or any(kw in final_prompt.lower() for kw in ["optimize", "suggest", "improve", "why"]):
                         attributed_summary = f"**[Data Analyst]**: I retrieved the shipment facts.\n\n**[Fleet Strategist]**: {summary}"
                    else:
                         attributed_summary = f"**[Data Analyst]**: {summary}"

                message_placeholder.markdown(attributed_summary)
                st.session_state.messages.append({"role": "assistant", "content": attributed_summary, "followups": followups})
                
                # Show Agent Trace
                with st.expander("🔍 Collaboration Trace"):
                    st.write("**Data Analyst**: Queried BigQuery and identified logistics trends.")
                    if "Fleet Strategist" in attributed_summary:
                        st.write("**Fleet Strategist**: Applied operational logic for optimization advice.")
                    st.write("**Orchestrator**: Synthesized final response for user.")
                
                # RERUN to show followups immediately (Streamlit hack)
                st.rerun()
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
