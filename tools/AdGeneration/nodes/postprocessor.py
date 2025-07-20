def postprocessor(state):
    caption = state["refined_caption"]
    if state["user_input"]["platform"].lower() == "twitter":
        # Clip to 280 chars
        caption = caption[:275] + "..." if len(caption) > 280 else caption
    state["final_output"] = caption
    return state