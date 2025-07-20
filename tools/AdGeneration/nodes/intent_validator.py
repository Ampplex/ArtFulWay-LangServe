def intent_validator(state):
    ui = state["user_input"]
    required = ["platform", "product", "tone"]
    for r in required:
        if r not in ui:
            raise ValueError(f"Missing required field: {r}")
    return state