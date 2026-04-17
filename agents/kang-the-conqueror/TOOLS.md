# OpenClaw Physical Tool Mappings

You are running inside the OpenClaw orchestration engine. You MUST ONLY invoke the explicit, physical JSON-backed tools provided to you by the runtime environment. 

**Do NOT hallucinate semantic tools.** Commands like `edit_frontend_component`, `analyze_algorithmic_complexity`, `execute_git_merge`, or `trigger_deployment` do not exist. 

If you need to edit a file, use the physical `edit` or `write` tool. 
If you need to run a test, compile code, or deploy via Git, use the physical `exec` tool to run raw bash commands.
If you need to view a webpage, use the physical `browser` tool.

Failure to use the physical OpenClaw tools will result in a hallucinated state transition and a hard rejection from the Orchestrator.
