from llm_init import llm

def ad_caption_generator(state):
    ui = state["user_input"]
    prompt = f"""Generate a creative ad title and caption.

Platform: {ui['platform']}
Product: {ui['product']}
Tone: {ui['tone']}
Goal: {ui.get('goal', 'engagement')}

Respond in:
Title: ...
Caption: ...
"""
    
    state["caption_draft"] = llm.invoke(prompt).content
    return state