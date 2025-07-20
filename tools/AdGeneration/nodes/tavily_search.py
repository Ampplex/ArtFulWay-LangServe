import os
import requests
from dotenv import load_dotenv

load_dotenv()

def tavily_search(state):
    query = f"{state['user_input']['platform']} {state['user_input']['product']} trends"
    api_key = os.getenv("TAVILY_API_KEY")

    response = requests.post("https://api.tavily.com/search", json={
        "api_key": api_key,
        "query": query,
        "num_results": 5
    }).json()

    # Log and check before using
    print("🔍 Tavily raw response:", response)

    if "results" not in response:
        raise ValueError(f"Tavily API failed: {response.get('error', 'No results key returned')}")

    state["search_snippets"] = [r["content"] for r in response["results"]]
    return state