from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from retrieval_pipeline import RetrievalPipeline
import os
from mangum import Mangum
import sys
from schema import AdGenerationRequest
# from tools.AdGeneration.graph_pipeline import build_graph, run_graph, refine_loop, postprocess_output
from tools.AdGeneration.graph_pipeline import build_graph, run_graph, refine_loop, postprocess_output


app = FastAPI(title="Artist Matching API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/match_artists")
async def match_artists_handler(project_id: Optional[str] = Query(None)):
    """
    Get matching artists for a project.
    
    Args:
        project_id: The ID of the project
    
    Returns:
        A list of artist IDs that match the project
    """
    try:
        matches = RetrievalPipeline(project_id).get_response()
        return {"artist_ids": matches}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/assist")
async def assist(project_id: Optional[str] = Query(None)):
    """
    Assist endpoint (implementation needed).
    
    Args:
        project_id: The ID of the project
    """
    # Placeholder for implementation
    
    return {"message": "Assist functionality not yet implemented"}

@app.get("/")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status of the API
    """
    return {"status": "healthy"}

@app.post("/ad_generation")
async def ad_generation_handler(raw_data: AdGenerationRequest):
    """
    Generate ad content based on user input.
    
    Args:
        raw_data: The data containing platform and product information
    
    Returns:
        A dictionary with generated ad content
    """

    user_input = {
            "platform": raw_data.platform,
            "product": raw_data.product,
            "tone": raw_data.tone if hasattr(raw_data, 'tone') else "informative",
            "goal": raw_data.goal if hasattr(raw_data, 'goal') else "engagement",
            "description": raw_data.description
    }

    # Initialize state
    state = {
        "user_input": user_input,
        "refine_count": 0,
    }

    # Build and run the graph
    graph = build_graph()
    state = run_graph(graph, state)
    state = refine_loop(state)
    postprocess_output(state)

    try:
        final_state = run_graph(graph, state)
        return JSONResponse(content=final_state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Lambda handler for AWS
handler = Mangum(app)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 1000))
    uvicorn.run(host="localhost", port=port, reload=True)