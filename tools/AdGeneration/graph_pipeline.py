import json
import logging
from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph
from pydantic import BaseModel, Field, ValidationError

from nodes.intent_validator import intent_validator
from nodes.ad_caption_generator import ad_caption_generator
from nodes.tavily_search import tavily_search
from nodes.trend_selector import trend_selector
from nodes.critique_refine import critique_refine
from nodes.postprocessor import postprocessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_REFINEMENT_ITERATIONS = 3

class GetContent(BaseModel):
    title: str = Field(..., description="The title of the content")
    caption: str = Field(..., description="The caption of the content")

class AdGenState(TypedDict):
    user_input: Dict[str, Any]
    refine_count: int
    caption_draft: str
    trends: str
    search_snippets: list
    refined_caption: str
    final_output: str

def build_graph() -> StateGraph:
    """Build and return the state graph for content generation."""
    builder = StateGraph(AdGenState)
    builder.add_node("validate", intent_validator)
    builder.add_node("generate", ad_caption_generator)
    builder.add_node("search", tavily_search)
    builder.add_node("select_trends", trend_selector)
    builder.add_node("refine", critique_refine)
    builder.add_node("post", postprocessor)

    builder.set_entry_point("validate")
    builder.add_edge("validate", "generate")
    builder.add_edge("generate", "search")
    builder.add_edge("search", "select_trends")
    builder.add_edge("select_trends", "refine")

    def refinement_condition(state: AdGenState) -> str:
        """Determine the next step based on the refinement count."""
        return "refine" if state.get("refine_count", 0) < MAX_REFINEMENT_ITERATIONS else "post"

    builder.add_conditional_edges("refine", refinement_condition, {"refine": "refine", "post": "post"})
    builder.set_finish_point("post")

    return builder.compile()

def run_graph(graph: StateGraph, state: AdGenState) -> AdGenState:
    """Run the graph with the given state."""
    try:
        state = graph.invoke(state)
        logger.info("Graph invocation successful.")
    except Exception as e:
        logger.error(f"Graph invocation failed: {e}")
        raise
    return state

def refine_loop(state: AdGenState) -> AdGenState:
    """Perform the refinement loop."""
    for iteration in range(MAX_REFINEMENT_ITERATIONS):
        try:
            state = critique_refine(state)
            logger.info(f"Refinement iteration {iteration + 1} successful.")
        except Exception as e:
            logger.error(f"Refinement iteration {iteration + 1} failed: {e}")
            raise
    return state

def parse_title_caption(raw_text: str) -> GetContent:
    lines = raw_text.strip().splitlines()

    title, caption_lines = None, []
    capture_caption = False

    for line in lines:
        if "**Title:**" in line:
            continue  # skip marker
        elif "**Caption:**" in line:
            capture_caption = True
            continue
        elif not line.strip():
            continue

        if not capture_caption:
            title = line.strip()
        else:
            caption_lines.append(line.strip())

    if not title or not caption_lines:
        raise ValueError("Failed to extract title or caption")

    caption = "\n".join(caption_lines)
    return GetContent(title=title, caption=caption)

def postprocess_output(state: AdGenState) -> None:
    """Postprocess the final output and validate it."""
    try:
        state = postprocessor(state)

        parsed = parse_title_caption(state["final_output"])

        logger.info("Final Output (JSON):\n" + json.dumps(parsed.model_dump(), indent=2))
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        logger.info("Raw Output:\n" + state["final_output"])
    except Exception as e:
        logger.error(f"Postprocessing failed: {e}")
        raise

def main() -> None:
    """Main function to build the graph and run the content generation pipeline."""
    graph = build_graph()
    user_input = {
        "platform": "LinkedIn",
        "product": "Real-Time Architectural Visualization",
        "tone": "Professional",
        "goal": "Awareness",
        "description": "Photorealistic 3D environment built using Unreal Engine for architects"
    }
    state = {
        "user_input": user_input,
        "refine_count": 0
    }

    state = run_graph(graph, state)
    state = refine_loop(state)
    postprocess_output(state)

if __name__ == "__main__":
    main()
