import os
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent


class LogisticsAgent:
    def __init__(self, db_path="sales_data.db"):
        # Environment-aware database connection.
        # Fallback to local SQLite if DATABASE_URL is not provided.
        # To use BigQuery, set DATABASE_URL=bigquery://project-id/dataset-id
        self.db_path = os.getenv("DATABASE_URL", f"sqlite:///{db_path}")
        self.db = SQLDatabase.from_uri(self.db_path)
        
        # Init Gemini Model via Vertex AI (Secure Service Account Auth)
        from langchain_google_vertexai import ChatVertexAI
        self.llm = ChatVertexAI(
            model_name="gemini-2.0-flash-exp",
            temperature=0,
            location="us-central1"
        )

        # Create the SQL Agent using LangChain toolkit
        # This handles Schema fetching, SQL generation, and Execution automatically
        self.agent_executor = create_sql_agent(
            llm=self.llm,
            toolkit=None, # Standard SQL toolkit implied if None? No, need toolkit or db
            db=self.db,
            agent_type="zero-shot-react-description",
            verbose=True,
            handle_parsing_errors=True
        )

    def run(self, query):
        """
        Executes the query using the LangChain Agent.
        Returns a dictionary compatible with the frontend expectation.
        """
        try:
            # LangChain Agent returns the final string answer, 
            # but we can also capture intermediate steps if needed.
            response = self.agent_executor.invoke(query)
            
            # For the demo UI "Voice Output", we return the text.
            # Note: The SQLAgent executes the query internally and synthesizes the answer.
            # We don't distinctly get "SQL" and "Data" separately as raw objects easily 
            # without custom callback handlers, but for the User, the Answer is key.
            
            full_response = response.get("output", "I could not process that request.")
            
            return {
                "sql": "-- Executed internally by LangChain --", 
                "data": None, 
                "summary": full_response,
                "error": None
            }
        except Exception as e:
            return {"sql": "ERROR", "data": None, "summary": str(e), "error": str(e)}

# For backward compatibility with app.py until we refactor it
class RouterAgent:
    def route(self, user_input):
        # Everything goes to the Logistics Agent in this unified design
        return "LOGISTICS"

