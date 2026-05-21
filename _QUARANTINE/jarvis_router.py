import os
from graphbit import LlmConfig

# The Local Armory
LOCAL_MODELS = {
    'reasoning': 'llama3.1-orchestrator',
    'gemma_core': 'gemma4:e2b',
    'qwen_legacy': 'qwen2.5-coder:7b'
}

def get_optimal_compute(agent_name, task_category):
    """
    JARVIS TOLLGATE: Dynamic Model Router
    Analyzes the agent and task to assign the most efficient local model.
    """
    
    # GEMINI HARD LOCK: No API model is ever returned by this router.
    # API access requires manual override by the Director.

    # Gemma is our primary workhorse for speed, accuracy, and general development.
    gemma_tasks = ['coding', 'frontend', 'backend', 'qa', 'testing', 'documentation', 'ui_ux']
    gemma_agents = ['Wasp', 'Iron Man', 'Black Widow', 'Spider-Man', 'Ant-Man', 'Quicksilver', 'Shang-Chi']

    # Llama is reserved for deep, complex reasoning and architectural planning.
    llama_tasks = ['planning', 'architecture', 'audit', 'security', 'legal', 'tech_debt']
    llama_agents = ['Vision', 'Coulson', 'Black Panther', 'She-Hulk', 'Winter Soldier', 'Nick Fury']

    # Routing Logic
    if task_category in gemma_tasks or any(agent in agent_name for agent in gemma_agents):
        return LlmConfig.ollama(LOCAL_MODELS['gemma_core'])
        
    elif task_category in llama_tasks or any(agent in agent_name for agent in llama_agents):
        return LlmConfig.ollama(LOCAL_MODELS['reasoning'])
        
    # Default fallback to Gemma for maximum efficiency and lowest error rate
    return LlmConfig.ollama(LOCAL_MODELS['gemma_core'])
