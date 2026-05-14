import os
import json
import requests
import re

local_config = {
    "model": "qwen-agent-32k:latest"
}

def run_single_agent(agent_id, agent_name, skill_file, config, state, allowed_tools=None):
    # 1. Load the Skill File
    skill_path = os.path.join(os.path.dirname(__file__), "skills", skill_file)
    try:
        with open(skill_path, "r") as f:
            system_prompt = f.read()
    except Exception:
        system_prompt = f"You are {agent_name}."

    # 2. Load Agent Identity, Soul, and Memory
    agent_dir = agent_name.lower().replace(" ", "-")
    agent_base_path = os.path.join(os.path.dirname(__file__), "agents", agent_dir)
    
    profile_components = []
    for file_name in ["IDENTITY.md", "SOUL.md", "MEMORY.md"]:
        file_path = os.path.join(agent_base_path, file_name)
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                profile_components.append(f"\n--- {file_name} ---\n" + f.read())
    
    if profile_components:
        system_prompt += "\n\n" + "".join(profile_components)

    # 3. Inject Global Project Context
    system_prompt += "\n\n--- GLOBAL PROJECT CONTEXT ---\n"
    system_prompt += "Hosteva is a Python backend application with a Vanilla JS and HTML/Jinja frontend. Do NOT assume Ruby, PHP, or Handlebars syntax.\n"
    
    import inspect
    tool_descriptions = "\n".join([f"- {t.__name__}{inspect.signature(t)}: {t.__doc__}" for t in allowed_tools]) if allowed_tools else "None"
    
    system_prompt += f"\n\nAVAILABLE TOOLS:\n{tool_descriptions}\n"
    system_prompt += "CRITICAL INSTRUCTION: Before taking any action or calling a tool, you MUST write down your reasoning inside <thinking> tags.\n"
    system_prompt += "After your <thinking> block, if you need to use a tool, output a markdown JSON block. Example:\n"
    system_prompt += "<thinking>\nI need to search for 'template literal' in the dashboard file.\n</thinking>\n"
    system_prompt += "```json\n{\"name\": \"tool_name\", \"arguments\": {\"param1\": \"value\"}}\n```\n"
    system_prompt += "Wait for the tool result before continuing.\n\nCRITICAL EXIT CONDITION: When you have found the bug and are ready to output your final plan, DO NOT output any JSON tool calls. Just output your final markdown response directly.\n\nCRITICAL RULE: DO NOT use read_file on dashboard_new.html (it is massive and will crash your context window). Use content_search instead!"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Current State: {json.dumps(state)}\n\nPlease analyze the ticket and provide your phase output."}
    ]

    tool_map = {t.__name__: t for t in allowed_tools} if allowed_tools else {}
    model = config.get("model", "qwen-agent-32k:latest")
    url = "http://localhost:11434/api/chat"
    
    for iteration in range(15):
        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=payload, timeout=300).json()
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"
        
        message = response.get("message", {})
        content = message.get("content", "")
        
        print(f"\n[RAW MODEL OUTPUT]:\n{content}\n")
        
        messages.append(message)
        
        # Robust JSON parser
        tool_req = None
        parse_error = None
        
        # Try parsing exact markdown block first
        matches = re.findall(r'```(?:json)?\s*(\{.*?\})\s*```', content, re.DOTALL)
        if matches:
            match_text = matches[-1]
            try:
                parsed = json.loads(match_text)
                if isinstance(parsed, dict) and (parsed.get("name") or parsed.get("tool")):
                    tool_req = parsed
            except Exception as e:
                parse_error = str(e)
                
        # Fallback: find first { to last }
        if not tool_req and not parse_error:
            start = content.find('{')
            end = content.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = content[start:end+1]
                try:
                    parsed = json.loads(json_str)
                    if isinstance(parsed, dict) and (parsed.get("name") or parsed.get("tool")):
                        tool_req = parsed
                except Exception as e:
                    parse_error = str(e)

        if tool_req and isinstance(tool_req, dict) and tool_map and (tool_req.get("name") or tool_req.get("tool")):
            func_name = tool_req.get("name") or tool_req.get("tool")
            kwargs = tool_req.get("arguments") or tool_req.get("kwargs") or {}
            
            if func_name in tool_map:
                try:
                    result = tool_map[func_name](**kwargs)
                    if func_name == 'submit_phase_plan':
                        return kwargs.get('plan_markdown', 'Plan submitted but empty.')
                except Exception as e:
                    result = f"Error executing {func_name}: {str(e)}"
            else:
                result = f"Unknown tool: {func_name}"
                
            print(f"[TOOL EXECUTION] {func_name} -> Result length: {len(str(result))}")
            messages.append({
                "role": "user",
                "content": f"Tool Result for {func_name}:\n{result}\n\nWhat is your next step?"
            })
            continue
        elif parse_error:
            error_msg = f"SYSTEM ERROR: Invalid JSON format. {parse_error}. Remember: DO NOT escape single quotes (\\') inside JSON strings. Output exactly ONE valid JSON block."
            print(f"-> [JSON PARSE ERROR]: Feeding error back to agent...")
            messages.append({"role": "user", "content": error_msg})
            continue
        else:
            return content
            
    return "Agent halted after reaching maximum tool iterations."