from ..llm_init import llm

def critique_refine(state):
    iteration = state.get("refine_count", 0) + 1
    state["refine_count"] = iteration
    original = state.get("refined_caption", state.get("caption_draft", ""))
    trends = state["trends"]

    prompt = f"""[Refinement Iteration {iteration}]
Refine the ad caption below to improve tone, clarity, and trend alignment.

Caption:
{original}

Trends and hashtags to consider:
{trends}

Goals:
- Match the tone: {state['user_input']['tone']}
- Boost engagement (add emojis/hashtags if helpful)
- Make platform-appropriate (e.g., punchy for Instagram)

Respond in:
Title: ...
Caption: ...
"""

    # ✅ Updated way using LangChain's .invoke
    response = llm.invoke(prompt)
    state["refined_caption"] = response.content.strip()
    return state