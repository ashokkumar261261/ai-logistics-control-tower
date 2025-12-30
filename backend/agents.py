print("LOADING AGENTS.PY...")
import os
from langchain_google_vertexai import ChatVertexAI
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
import json

# Configuration
PROJECT_ID = "inspiring-keel-423204-c7"
DATASET_ID = "logistics_control_tower"

class MultiAgentLogisticsSystem:
    def __init__(self):
        """Initializes the specialized agents for data analysis and operational strategy."""
        # 1. Initialize LLM (Gemini 2.0 Flash Experimental)
        self.llm = ChatVertexAI(
            model_name="gemini-2.0-flash-exp",
            temperature=0
        )

        # 2. Database Connection
        self.db_uri = f"bigquery://{PROJECT_ID}/{DATASET_ID}"
        self.db = SQLDatabase.from_uri(self.db_uri)

        # 3. Dedicated Agent Components
        self.data_analyst = self._setup_data_analyst()
        self.fleet_strategist = self._setup_fleet_strategist()

    def _setup_data_analyst(self):
        """Logistics Data Analyst: Specializes in querying BigQuery and extracting raw facts."""
        return create_sql_agent(
            llm=self.llm,
            db=self.db,
            agent_type="zero-shot-react-description",
            verbose=True,
            handle_parsing_errors=True
        )

    def _setup_fleet_strategist(self):
        """Fleet Strategy Agent: Specializes in analyzing logistics data to provide optimization advice."""
        prompt = ChatPromptTemplate.from_template(
            "You are a Senior Fleet Operations Manager at a global logistics firm. "
            "Your persona is proactive, cost-conscious, and strategic.\n\n"
            "Conversation History: {history}\n\n"
            "Data Report from Analyst: {data_facts}\n\n"
            "Based on these facts, provide 2-3 specific, actionable recommendations to improve "
            "efficiency or resolve bottlenecks. Keep your response professional and executive-ready."
        )
        return prompt | self.llm

    def _generate_followups(self, response_text, history=""):
        """Generates 3 logical follow-up questions based on the current context."""
        prompt = ChatPromptTemplate.from_template(
            "Based on the following AI response and conversation history, suggest 3 concise follow-up questions "
            "the user might want to ask next. These questions should be helpful for a logistics manager.\n\n"
            "Conversation History: {history}\n"
            "AI Response: {response}\n\n"
            "Return ONLY a JSON list of strings. Example: [\"Question 1\", \"Question 2\", \"Question 3\"]"
        )
        chain = prompt | self.llm
        try:
            result = chain.invoke({"history": history, "response": response_text})
            # Handle potential markdown formatting in LLM output
            content = result.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception:
            return ["Show me delayed shipments", "What is the fleet capacity?", "Identify bottlenecks"]

    
    def _setup_communication_agent(self):
        """Communication Agent: Manages mockup email interactions."""
        from langchain.tools import tool

        @tool
        def fetch_inbox():
            """Returns a list of unread emails."""
            return """
            [UNREAD] Subject: Delay Report - Driver Kyle
            Body: Vehicle V-001 is stuck in traffic. ETA delayed by 45 mins.
            
            [READ] Subject: Monthly Capacity Report
            Body: Available for review.
            """

        @tool
        def send_email(to: str, subject: str, body: str):
            """Simulates sending an email."""
            return f"📧 SENT EMAIL\nTo: {to}\nSubject: {subject}\nBody: {body}"

        # Initialize an agent with these tools
        from langchain.agents import create_tool_calling_agent, AgentExecutor
        from langchain import hub
        
        # Use a simple prompt for tool calling
        prompt = ChatPromptTemplate.from_template(
            "You are a Logistics Communication Assistant. Help the user manage emails.\n"
            "Tools: {tools}\n"
            "User Query: {input}\n"
            "Variable 'agent_scratchpad' should come from intermediate steps."
        )
        # Note: Ideally use a predefined hub prompt, but for simplicity we rely on the LLM's tool ability directly or setup a simple chain if create_tool_calling_agent is complex without hub.
        # For simplicity in this script, we will just wrap the LLM with tools bound.
        llm_with_tools = self.llm.bind_tools([fetch_inbox, send_email])
        return llm_with_tools

    def run(self, query, role="Guest", history=""):
        """Orchestrates the multi-agent workflow with RBAC security and memory."""
        try:
            print(f"Orchestrator: User Role = {role}")
            
            # 0. RBAC Security Check
            query_lower = query.lower()
            if role == "Guest" and any(w in query_lower for w in ["cost", "price", "profit", "salary", "money"]):
                return {"summary": "🚫 Access Denied: Guests cannot access financial data.", "sql": None, "error": None, "followups": []}
            
            # 1. Intent Detection: Communication vs Analytics
            if any(w in query_lower for w in ["email", "mail", "inbox", "send", "read"]):
                print("Orchestrator: Routing to Communication Agent...")
                if "read" in query_lower or "inbox" in query_lower:
                    summary = "[UNREAD] Subject: Delay Report - Driver Kyle\nBody: Vehicle V-001 is stuck in traffic."
                    followups = ["Send an email to Kyle", "Find alternative vehicle", "Check shipment 14 status"]
                    return {"summary": summary, "sql": None, "error": None, "followups": followups}
                elif "send" in query_lower:
                    summary = f"📧 Draft Email Created for '{query}'. (Simulation: Email Sent)"
                    followups = ["Check inbox", "Show fleet status", "What is the next pickup?"]
                    return {"summary": summary, "sql": None, "error": None, "followups": followups}
            
            # 2. Analytics Workflow
            # Data Analyst fetching facts
            print(f"Orchestrator: Engaging Data Analyst for: {query} (Context included)")
            # Add history to query for data analyst to understand "it", "them", etc.
            contextual_query = f"Conversation Context: {history}\nUser Query: {query}" if history else query
            data_result = self.data_analyst.invoke(contextual_query)
            facts = data_result.get("output", "No data retrieved.")

            # 3. Strategy Layer
            strategy_keywords = ["optimize", "advice", "suggest", "improve", "why", "strategy", "fix"]
            needs_strategy = any(word in query.lower() for word in strategy_keywords)

            if needs_strategy:
                print("Orchestrator: Engaging Fleet Strategist for operational insight...")
                strategy_advice = self.fleet_strategist.invoke({"data_facts": facts, "history": history}).content
                
                final_response = (
                    f"### 📊 Analyst Data Report\n{facts}\n\n"
                    f"### 🚀 Fleet Strategy Recommendations\n{strategy_advice}"
                )
            else:
                final_response = facts

            # 4. Follow-up Generation
            followups = self._generate_followups(final_response, history)

            return {
                "summary": final_response,
                "sql": "-- Multi-Agent Coordination Hook --",
                "error": None,
                "followups": followups
            }
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Agent Execution Crash: {error_trace}")
            return {"summary": "System error in multi-agent workflow.", "sql": None, "error": str(e), "followups": []}

def get_multi_agent():
    return MultiAgentLogisticsSystem()
