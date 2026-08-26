import sys

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/gb_config.py', 'r') as f:
    content = f.read()

old_block = """    import inspect
    tool_descriptions = "\n".join([f"- {t.__name__}{inspect.signature(t)}: {t.__doc__}" for t in allowed_tools]) if allowed_tools else "None"
    
    system_prompt += f"\n\nAVAILABLE TOOLS:\n{tool_descriptions}\n"
    system_prompt += "CRITICAL INSTRUCTION: Before taking any action or calling a tool, you MUST write down your reasoning inside <thinking> tags.\n"
    system_prompt += "After your <thinking> block, if you need to use a tool, output a markdown JSON block. Example:\n"
    system_prompt += "<thinking>\nI need to search for 'template literal' in the dashboard file.\n</thinking>\n"
    system_prompt += "```json\n{\"name\": \"tool_name\", \"arguments\": {\"param1\": \"value\"}}\n```\n"
    system_prompt += "Wait for the tool result before continuing.\n\nCRITICAL EXIT CONDITION: When you have found the bug and are ready to output your final plan, DO NOT output any JSON tool calls. Just output your final markdown response directly.\n\nCRITICAL RULE: DO NOT use read_file on dashboard_new.html (it is massive and will crash your context window). Use content_search instead!"""

new_block = """    if allowed_tools:
        import inspect
        tool_descriptions = "\n".join([f"- {t.__name__}{inspect.signature(t)}: {t.__doc__}" for t in allowed_tools])
        system_prompt += f"\n\nAVAILABLE TOOLS:\n{tool_descriptions}\n"
        system_prompt += "CRITICAL INSTRUCTION: Before taking any action or calling a tool, you MUST write down your reasoning inside <thinking> tags.\n"
        system_prompt += "After your <thinking> block, if you need to use a tool, output a markdown JSON block. Example:\n"
        system_prompt += "<thinking>\nI need to search for 'template literal' in the dashboard file.\n</thinking>\n"
        system_prompt += "```json\n{\"name\": \"tool_name\", \"arguments\": {\"param1\": \"value\"}}\n```\n"
        system_prompt += "Wait for the tool result before continuing.\n\nCRITICAL EXIT CONDITION: When you have found the bug and are ready to output your final plan, DO NOT output any JSON tool calls. Just output your final markdown response directly."
    else:
        system_prompt += "\n\nCRITICAL INSTRUCTION: YOU DO NOT HAVE ACCESS TO ANY TOOLS. DO NOT OUTPUT JSON TOOL CALLS. YOU MUST DIRECTLY OUTPUT YOUR FINAL MARKDOWN RESPONSE."""

content = content.replace(old_block, new_block)

with open('/home/rdogen/OpenClaw_Factory/projects/Hosteva/gb_config.py', 'w') as f:
    f.write(content)

print("Patch applied successfully.")
