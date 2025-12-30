print("LOADING MAIN.PY...")
import functions_framework
from agents import get_multi_agent
import json

# Configuration
PROJECT_ID = "inspiring-keel-423204-c7"
DATASET_ID = "logistics_control_tower"

# Global variable to hold the agent instance
agent = None

def get_agent():
    """Lazy initialization of the Multi-Agent Logistics System."""
    global agent
    if agent is None:
        print("Initializing Multi-Agent Logistics Workflow...")
        agent = get_multi_agent()
    return agent

@functions_framework.http
def process_query(request):
    """HTTP Cloud Function to handle /query and /health."""
    # CORS headers
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Max-Age': '3600'
    }

    if request.method == 'OPTIONS':
        return ('', 204, headers)

    path = request.path.rstrip('/')
    print(f"Request Path: {path}, Method: {request.method} | Version: V3.1-FIXED")

    # Health Check Route
    if path == '/health' or path == '':
        if request.method == 'GET':
            return (json.dumps({"status": "healthy"}), 200, headers)

    # Query Route
    if path == '/query' or path == '':
        if request.method == 'POST':
            request_json = request.get_json(silent=True)
            if not request_json:
                return (json.dumps({"error": "Invalid or missing JSON body"}), 400, headers)
            query = request_json.get('query')
            role = request_json.get('role', 'Guest')
            history = request_json.get('history', '')
            
            if not query:
                return (json.dumps({"error": "No query provided"}), 400, headers)

            print(f"Processing Query: {query} | Role: {role} | History Length: {len(history)}")
            try:
                current_agent = get_agent()
                result = current_agent.run(query, role=role, history=history)
                return (json.dumps({
                    "summary": result.get("summary", ""),
                    "sql": result.get("sql", "-- Agent Executed --"),
                    "error": result.get("error"),
                    "followups": result.get("followups", [])
                }), 200, headers)
            except Exception as e:
                print(f"Error running agent: {str(e)}")
                return (json.dumps({"error": str(e)}), 500, headers)

    # Sample Data Route
    if path == '/sample':
        if request.method == 'GET':
            try:
                from google.cloud import bigquery
                client = bigquery.Client(project=PROJECT_ID)
                tables = ["shipments", "drivers", "vehicles"]
                samples = {}
                for t in tables:
                    query = f"SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{t}` LIMIT 5"
                    results = client.query(query).result()
                    samples[t] = [dict(row.items()) for row in results]
                
                # Custom serializer for Date/Time objects
                def json_serial(obj):
                    from datetime import date, datetime
                    from decimal import Decimal
                    if isinstance(obj, (date, datetime)):
                        return obj.isoformat()
                    if isinstance(obj, Decimal):
                        return float(obj)
                    raise TypeError(f"Type {type(obj)} not serializable")

                return (json.dumps(samples, default=json_serial), 200, headers)
            except Exception as e:
                return (json.dumps({"error": str(e)}), 500, headers)

    return (json.dumps({"error": f"Not Found: {path}"}), 404, headers)
