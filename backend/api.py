from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from agents import LogisticsAgent
import uvicorn
import os

app = FastAPI(title="Logistics Control Tower API", version="1.0.0")

# Initialize Agent
# Note: In a real cloud run, this logic might be per-request or cached
agent = LogisticsAgent(db_path="sales_data.db")

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    summary: str
    sql: str
    error: str = None

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    try:
        print(f"Received query: {request.query}")
        result = agent.run(request.query)
        
        # Determine if result was successful based on 'error' key
        if result.get("error"):
            return QueryResponse(
                summary=result.get("summary", "An error occurred."),
                sql=result.get("sql", "ERROR"),
                error=result.get("error")
            )
            
        return QueryResponse(
            summary=result.get("summary", ""),
            sql=result.get("sql", "-- Agent Executed --")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/schema")
def get_schema():
    """Returns the database schema for the frontend to visualize."""
    return {"schema": agent.db.get_table_info()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
