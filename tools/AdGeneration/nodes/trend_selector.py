from llm_init import llm

def trend_selector(state):
    raw = "\n".join(state["search_snippets"])
    prompt = f"""Extract up to 5 relevant hashtags or trend topics from this text:

{raw}

Respond as:
#Hashtag1, #Hashtag2, Trend1, Trend2
"""
    trends = llm.invoke(prompt).content
    state["trends"] = trends
    return state