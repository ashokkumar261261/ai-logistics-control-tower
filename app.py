import streamlit as st
import time
from agents import SQLAgent, AnalystAgent, RouterAgent

# Page Config
st.set_page_config(page_title="Voice Data Concierge", page_icon="🎙️", layout="wide")

st.title("🎙️ AI Voice Data Concierge")
st.markdown("""
This demo showcases a **Multi-Agent Workflow** where you can ask questions about your business data.
It simulates a voice-activated interface.
""")

# Initialize Agents
if 'sql_agent' not in st.session_state:
    st.session_state.sql_agent = SQLAgent()
if 'analyst_agent' not in st.session_state:
    st.session_state.analyst_agent = AnalystAgent()
if 'router_agent' not in st.session_state:
    st.session_state.router_agent = RouterAgent()

# Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Input (Simulating Voice)
prompt = st.chat_input("Ask a question (e.g., 'Show me the top sales')...")

if prompt:
    # 1. User Input
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Router Step
    with st.status("🤖 Processing...", expanded=True) as status:
        st.write("Authored by **Router Agent**")
        route = st.session_state.router_agent.route(prompt)
        st.write(f"Routing to: **{route}**")
        
        response_text = ""
        
        if route == "GENERAL":
            time.sleep(1)
            response_text = "Hello! I am your Data Concierge. You can ask me about Employees or Sales."
            status.update(label="Complete", state="complete")
            
        elif route == "SQL":
            # 3. SQL Agent Step
            st.write("Handoff to **SQL Agent**...")
            time.sleep(1)
            result = st.session_state.sql_agent.run_query(prompt)
            
            if result['error']:
                response_text = f"I encountered an error querying the database: {result['error']}"
                status.update(label="Error", state="error")
            else:
                st.code(result['sql'], language="sql")
                st.dataframe(result['data'])
                
                # 4. Analyst Agent Step
                st.write("Handoff to **Analyst Agent** for synthesis...")
                time.sleep(1)
                analysis = st.session_state.analyst_agent.analyze(result['data'], prompt)
                response_text = analysis
                status.update(label="Complete", state="complete")

    # 5. Final Response (Voice Output)
    with st.chat_message("assistant"):
        st.write("🔊 **Voice Output:**")
        st.markdown(f"*{response_text}*")
        
    st.session_state.messages.append({"role": "assistant", "content": response_text})

# Sidebar - Database Preview
st.sidebar.header("Database Preview")
if st.sidebar.button("Refresh Schema"):
    schema = st.session_state.sql_agent.get_schema()
    st.sidebar.json(schema)
