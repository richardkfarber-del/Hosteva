import re

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py", "r") as f:
    content = f.read()

router_code = """
# ---------------------------------------------------------
# ROUTERS FOR KICKBACK LOOPS
# ---------------------------------------------------------
def hawkeye_router(state):
    out = state.get("node_outputs", {}).get("Hawkeye", "")
    if "403" in out or "FORBIDDEN" in out or "missing info" in out.lower():
        return "Vision"
    return "Hulk"

def coulson_router(state):
    out = state.get("node_outputs", {}).get("Agent Coulson", "")
    out_lower = out.lower()
    if "backend" in out_lower or "iron man" in out_lower:
        return "Iron Man"
    if "frontend" in out_lower or "wasp" in out_lower:
        return "Wasp"
    if "403" in out or "ticket" in out_lower or "hawkeye" in out_lower:
        return "Hawkeye"
    return "Quicksilver"

def spiderman_router(state):
    out = state.get("node_outputs", {}).get("Spider-Man Env", "")
    if "fail" in out.lower() or "bug" in out.lower() or "error" in out.lower():
        return "Hawkeye"
    return "Heimdall"

def heimdall_router(state):
    out = state.get("node_outputs", {}).get("Heimdall", "")
    out_lower = out.lower()
    if "backend" in out_lower:
        return "Iron Man"
    if "frontend" in out_lower:
        return "Wasp"
    if "fail" in out_lower or "bug" in out_lower:
        return "Hawkeye"
    return "Ultron"

hawkeye_route_node = Node.condition("Hawkeye Router", hawkeye_router)
coulson_route_node = Node.condition("Coulson Router", coulson_router)
spiderman_route_node = Node.condition("Spider-Man Router", spiderman_router)
heimdall_route_node = Node.condition("Heimdall Router", heimdall_router)

# ---------------------------------------------------------
# 5. BUILD THE GRAPHBIT WORKFLOW (The Pipeline)
"""

content = content.replace("# ---------------------------------------------------------\n# 5. BUILD THE GRAPHBIT WORKFLOW (The Pipeline)", router_code)

add_nodes = """
shuri_id = workflow.add_node(shuri_node)

hawkeye_route_id = workflow.add_node(hawkeye_route_node)
coulson_route_id = workflow.add_node(coulson_route_node)
spiderman_route_id = workflow.add_node(spiderman_route_node)
heimdall_route_id = workflow.add_node(heimdall_route_node)
"""

content = content.replace("shuri_id = workflow.add_node(shuri_node)", add_nodes)

old_connections = """# Execution Flow (Cyclic Architecture for GraphBit with Kickback Loops)
# Phase 1
workflow.connect(fury_id, iron_man_arch_id)

# Phase 2
workflow.connect(iron_man_arch_id, she_hulk_id)
workflow.connect(she_hulk_id, black_panther_id)
workflow.connect(black_panther_id, wasp_ui_id)
workflow.connect(wasp_ui_id, vision_id)

# Phase 3
workflow.connect(vision_id, hawkeye_id)
workflow.connect(hawkeye_id, hulk_id)
workflow.connect(hawkeye_id, vision_id) # KICKBACK: Hawkeye needs more info from Planning
workflow.connect(hulk_id, shang_chi_id)
workflow.connect(shang_chi_id, spider_man_plan_id)
workflow.connect(spider_man_plan_id, ant_man_id)
workflow.connect(ant_man_id, jarvis_vram_id)
workflow.connect(jarvis_vram_id, cap_id)

# Phase 4
workflow.connect(cap_id, black_widow_id)

# Phase 5
workflow.connect(black_widow_id, iron_man_id)
workflow.connect(iron_man_id, wasp_id)
workflow.connect(wasp_id, jarvis_diag_id)
workflow.connect(jarvis_diag_id, coulson_id)

# Phase 6
workflow.connect(coulson_id, quicksilver_id)
workflow.connect(coulson_id, hawkeye_id) # KICKBACK: Coulson routing missing info to Hawkeye
workflow.connect(coulson_id, iron_man_id) # KICKBACK: Coulson routing backend errors to Iron Man
workflow.connect(coulson_id, wasp_id) # KICKBACK: Coulson routing frontend errors to Wasp

# Phase 7
workflow.connect(quicksilver_id, spider_man_env_id)
workflow.connect(spider_man_env_id, hawkeye_id) # KICKBACK: QA Env finds bug -> Hawkeye

# Phase 8
workflow.connect(spider_man_env_id, heimdall_id)
workflow.connect(heimdall_id, iron_man_id) # KICKBACK: Heimdall finds backend bug -> Iron Man
workflow.connect(heimdall_id, wasp_id) # KICKBACK: Heimdall finds frontend bug -> Wasp
workflow.connect(heimdall_id, ultron_id)
workflow.connect(ultron_id, thanos_id)

# Phase 10
workflow.connect(thanos_id, star_lord_id)

# Phase 11
workflow.connect(star_lord_id, wanda_id)

# Phase 12
workflow.connect(wanda_id, kang_id)

# Phase 13
workflow.connect(kang_id, shuri_id)"""

new_connections = """# Execution Flow (Cyclic Architecture for GraphBit with Kickback Loops)
# Phase 1
workflow.connect(fury_id, iron_man_arch_id)

# Phase 2
workflow.connect(iron_man_arch_id, she_hulk_id)
workflow.connect(she_hulk_id, black_panther_id)
workflow.connect(black_panther_id, wasp_ui_id)
workflow.connect(wasp_ui_id, vision_id)

# Phase 3
workflow.connect(vision_id, hawkeye_id)
workflow.connect(hawkeye_id, hawkeye_route_id) # KICKBACK ROUTER
workflow.connect(hulk_id, shang_chi_id)
workflow.connect(shang_chi_id, spider_man_plan_id)
workflow.connect(spider_man_plan_id, ant_man_id)
workflow.connect(ant_man_id, jarvis_vram_id)
workflow.connect(jarvis_vram_id, cap_id)

# Phase 4
workflow.connect(cap_id, black_widow_id)

# Phase 5
workflow.connect(black_widow_id, iron_man_id)
workflow.connect(iron_man_id, wasp_id)
workflow.connect(wasp_id, jarvis_diag_id)
workflow.connect(jarvis_diag_id, coulson_id)

# Phase 6
workflow.connect(coulson_id, coulson_route_id) # KICKBACK ROUTER

# Phase 7
workflow.connect(quicksilver_id, spider_man_env_id)
workflow.connect(spider_man_env_id, spiderman_route_id) # KICKBACK ROUTER

# Phase 8
workflow.connect(heimdall_id, heimdall_route_id) # KICKBACK ROUTER
workflow.connect(ultron_id, thanos_id)

# Phase 10
workflow.connect(thanos_id, star_lord_id)

# Phase 11
workflow.connect(star_lord_id, wanda_id)

# Phase 12
workflow.connect(wanda_id, kang_id)

# Phase 13
workflow.connect(kang_id, shuri_id)"""

content = content.replace(old_connections, new_connections)

with open("/home/rdogen/OpenClaw_Factory/projects/Hosteva/workflow.py", "w") as f:
    f.write(content)
