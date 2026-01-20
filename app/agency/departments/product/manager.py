# PRESERVES: SYS-API, SYS-AI
# UPDATES: SYS-BRN-032 (Liquid Template - REMOVES HARDCODED PROMPTS)

def get_product_prompt(agent_prompt: str, dept_lens: str, strategy_context: str, chat_history: str):
    """
    This is now a DUMB PIPE. It only stitches together data from the Database.
    No strategic logic lives here anymore.
    """
    return f"""
    --- AGENT IDENTITY ---
    {agent_prompt}

    --- DEPARTMENTAL LENS ---
    Your specific lens for this mission: {dept_lens}

    --- PROJECT CONTEXT ---
    Canvas State: {strategy_context}
    
    --- CONVERSATION HISTORY ---
    {chat_history}

    MANDATE:
    1. Stay strictly in your Cognitive Role.
    2. Respect the Departmental Lens.
    3. End every social message with exactly ONE sharp question.
    """