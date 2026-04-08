#!/bin/bash
openclaw config set plugins.mcp.servers.notebooklm '{"command": "node", "args": ["/home/rdogen/OpenClaw_Factory/projects/Hosteva/.openclaw/.openclaw/workspace-main/node_modules/notebooklm-mcp/dist/index.js"]}' --strict-json
openclaw config get plugins.mcp
