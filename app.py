import streamlit as st
import os
import requests
import json
import time

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8003")

# Page Config
st.set_page_config(page_title="AI Logistics Control Tower", page_icon="🚚", layout="wide")

st.title("🚚 AI Logistics Control Tower")
st.markdown("""
**Powered by LangChain & Google Gemini** | *Cloud Native Architecture*
Ask about: **Shipments**, **Vehicles**, **Drivers**.
""")

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask a question (e.g., 'Where are the delayed shipments?')..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("🤖 *Routing query to Cloud Logistics Agent...*")
        
        try:
            # Call Backend API
            response = requests.post(f"{API_URL}/query", json={"query": prompt})
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("summary")
                error = result.get("error")
                
                if error:
                    st.error(f"Agent Error: {error}")
                    message_placeholder.markdown("⚠️ I encountered an error processing your request.")
                    st.session_state.messages.append({"role": "assistant", "content": f"Error: {error}"})
                else:
                    message_placeholder.markdown(summary)
                    st.session_state.messages.append({"role": "assistant", "content": summary})
                    
                    # Optional: Log the fact that SQL was executed (opaque in LangChain agent)
                    with st.expander("Agent Trace (Cloud Native)"):
                        st.write("Processed by: LangChain SQL Agent")
                        st.code("Processing logic handled by Backend API")
            else:
                st.error(f"API Error: {response.status_code}")
                message_placeholder.markdown("❌ Failed to contact Logistics Cloud API.")
        except Exception as e:
             st.error(f"Connection Error: {e}")
             message_placeholder.markdown("❌ Could not connect to the Backend API. Is it running?")

# Sidebar
st.sidebar.title("System Status")
st.sidebar.success("Cloud Agent: Online")
st.sidebar.info("Architecture: Streamlit -> FastAPI -> LangChain -> Gemini")
st.sidebar.markdown("---")
if st.sidebar.button("Ping Health Check"):
    try:
        res = requests.get(f"{API_URL}/health")
        if res.status_code == 200:
            st.sidebar.success(f"Health: {res.json()['status']}")
        else:
            st.sidebar.error("Unhealthy")
    except:
        st.sidebar.error("Offline")

