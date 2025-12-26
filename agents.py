import sqlite3
import pandas as pd
import re

class MockLLM:
    """
    Simulates an LLM for demonstration purposes.
    In a real app, this would call OpenAI/Gemini APIs.
    """
    @staticmethod
    def generate_sql(query):
        query = query.lower()
        if "employee" in query or "staff" in query:
            return "SELECT * FROM employees LIMIT 5;"
        elif "sales" in query and "count" in query:
             return "SELECT COUNT(*) FROM sales;"
        elif "sales" in query or "revenue" in query:
            return "SELECT * FROM sales ORDER BY amount DESC LIMIT 5;"
        elif "count" in query:
             return "SELECT COUNT(*) FROM employees;"
        else:
            return "SELECT * FROM employees LIMIT 5;"

    @staticmethod
    def summarize(data, query):
        if isinstance(data, pd.DataFrame):
            count = len(data)
            if count == 0:
                return "I found no records matching your request."
            
            # Simple template-based summary
            columns = ", ".join(data.columns)
            return f"I found {count} records. Here is the data covering {columns}. The top result is {data.iloc[0].values}."
        return str(data)

class SQLAgent:
    def __init__(self, db_path="sales_data.db"):
        self.db_path = db_path

    def get_schema(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schema = {}
        for table in tables:
            t_name = table[0]
            cursor.execute(f"PRAGMA table_info({t_name})")
            columns = cursor.fetchall()
            schema[t_name] = [col[1] for col in columns]
        conn.close()
        return schema

    def run_query(self, query):
        """
        Translates natural language to SQL (mock) and executes it.
        """
        sql = MockLLM.generate_sql(query)
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(sql, conn)
            conn.close()
            return {"sql": sql, "data": df, "error": None}
        except Exception as e:
            return {"sql": sql, "data": None, "error": str(e)}

class AnalystAgent:
    def analyze(self, data, query):
        """
        Synthesizes the data into a natural language response.
        """
        summary = MockLLM.summarize(data, query)
        return summary

class RouterAgent:
    def route(self, user_input):
        """
        Decides whether to route to SQL Agent or just General Chat.
        For this demo, we default everything to SQL Agent logic 
        since it's a 'Data Concierge'.
        """
        # In a real app, you'd classification here.
        # If input is "Hello", return "General"
        # If input is "Show me sales", return "SQL"
        if "hello" in user_input.lower() or "hi" in user_input.lower():
            return "GENERAL"
        return "SQL"
