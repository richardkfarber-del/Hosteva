# Core Project Context
# Project Overview: Hosteva

## What is it?
Hosteva is the "Iron Man Suit" for short-term rental hosts. It is a mobile and web application designed to help hosts navigate the increasingly complex world of STR compliance, taxes, and listing requirements.

## Problem We Are Solving
In Florida (specifically Pasco and Hillsborough counties), the laws change weekly. Hosts are getting fined or delisted because they can't keep up.

## The Solution
A smart assistant that:
1. Scrapes local ordinances to find compliance gaps.
2. Automatically generates the necessary paperwork for permits.
3. Optimizes listing descriptions to ensure they are "Search-Safe" and "Platform-Compliant."



## Infrastructure Constraints
# Hosteva Infrastructure Profile

This document outlines the highly customized environmental constraints for the Hosteva project. ALL agents (especially Rocket Raccoon and Nick Fury) MUST adhere to these rules for all diagnostic and deployment commands.

## 1. The Operating Environment (WSL2 & Pathing)
* **Host:** Running Ubuntu on WSL2 inside a Windows machine.

## 2. The Gateway & Daemon Rules

## 3. The Local Compute Bridge (Ollama)

## 4. Package Management (PEP 668)
* **Strict Python Rules:** The Ubuntu environment strictly enforces PEP 668. NEVER suggest installing global CLI tools using `python -m pip` or `pip install`.
* **The Pipx Mandate:** Any global Python tool (like Aider) MUST be installed using `pipx` (e.g., `pipx install aider-chat`).

## 5. Configuration Integrity

## 6. The "Infinite Reload" Failsafe (Daemon Ban)
* **Single-Execution Only:** The "Sprint Flush" (or any automation) MUST NEVER be implemented as a continuous background daemon. It must be a standard, single-execution script that runs ONLY when explicitly triggered, performs its job, and immediately exits.

### Systemic Failsafe: Web Tool Timeouts & Transparency
- **Hard Timeouts:** All `web_search`, `web_fetch`, and `browser` tool executions MUST enforce a strict wall-clock timeout. If a process does not resolve within 30 seconds, the tool wrapper must sever the connection and return a hard error to prevent main-thread starvation.
- **Asynchronous Heartbeats:** To prevent silent failures, heartbeat intervals must run in an isolated execution context. If an agent's main loop hangs and misses a check-in, the isolated heartbeat must automatically terminate the stalled process.
- **Mandatory Notification (The Transparency Rule):** If an agent is unsuccessful in utilizing an expected external tool (e.g., Bruce Banner experiencing a CAPTCHA trap during an R&D web scrape), the agent is explicitly FORBIDDEN from silently falling back to internal knowledge without notifying the Director. Any tool failure or forced degradation (e.g., `browser` -> `web_fetch`) MUST trigger an immediate, high-priority alert to the Orchestrator, who will then present the failure to the Director. Silent fallbacks are a violation of swarm transparency.

