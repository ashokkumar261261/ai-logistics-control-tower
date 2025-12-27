import functions_framework
from agents import LogisticsAgent
import json

# Global variable to hold the agent instance
agent = None

def get_agent():
    """Lazy initialization of the LogisticsAgent."""
    global agent
    if agent is None:
        print("Initializing LogisticsAgent for the first time...")
        agent = LogisticsAgent()
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
    print(f"Request Path: {path}, Method: {request.method}")

    # Health Check Route
    if path == '/health' or path == '':
        if request.method == 'GET':
            return (json.dumps({"status": "healthy"}), 200, headers)

    # Query Route
    if path == '/query' or path == '':
        if request.method == 'POST':
            request_json = request.get_json(silent=True)
            if not request_json or 'query' not in request_json:
                return (json.dumps({"error": "Missing 'query' parameter"}), 400, headers)

            query = request_json['query']
            print(f"Cloud Function processing query: {query}")

            try:
                current_agent = get_agent()
                result = current_agent.run(query)
                return (json.dumps({
                    "summary": result.get("summary", ""),
                    "sql": result.get("sql", "-- Agent Executed --"),
                    "error": result.get("error")
                }), 200, headers)
            except Exception as e:
                print(f"Error running agent: {str(e)}")
                return (json.dumps({"error": str(e)}), 500, headers)

    return (json.dumps({"error": f"Not Found: {path}"}), 404, headers)
