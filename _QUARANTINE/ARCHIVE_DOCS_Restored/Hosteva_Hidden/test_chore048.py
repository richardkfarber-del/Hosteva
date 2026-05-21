from app.core.agent_memory import get_agent_memory

if __name__ == "__main__":
    result = get_agent_memory("iron-man")
    print(result)
    assert "CORE RULES" in result
    print("CHORE-048 VERIFIED")
