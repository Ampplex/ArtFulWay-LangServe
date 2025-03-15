#!/usr/bin/env python
from fastapi import FastAPI, Query
from langserve import add_routes
import uvicorn
from typing import Dict, List
from allocator import Allocator

app = FastAPI(
    title="Artist Matching Service",
    version="1.0",
    description="API server for artist matching using RAG pipeline",
)

# Create a direct endpoint for your pipeline with parameter
@app.get("/match-artists")
async def match_artists(client_id: str = Query(..., description="Client ID to match artists for")):
    print(client_id)
    allocator = Allocator(client_id)
    matches = allocator.get_best_matches()
    return {"artist_ids": matches}

# For LangServe compatibility
from langchain.schema.runnable import RunnableConfig, Runnable

class AllocatorRunnable(Runnable):
    def invoke(self, input: Dict, config: RunnableConfig = None) -> List[str]:
        client_id = input.get("client_id")
        print(client_id)
        if not client_id:
            raise ValueError("client_id is required")
        
        allocator = Allocator(client_id)
        return allocator.get_best_matches()

# Add LangServe routes
add_routes(
    app,
    AllocatorRunnable(),
    path="/langserve/match-artists/",
)

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)