#!/bin/bash
# Vibranium Gate Enforcement Script (The Shuri Protocol)
# This script ensures the Orchestrator cannot bypass the Hub-and-Spoke model.

echo "ERROR: LangGraph Hub-and-Spoke violation detected."
echo "The Orchestrator must not manually prompt subagents to 'do the next step'."
echo "All movement must occur via LangGraph automated hooks."
exit 1
