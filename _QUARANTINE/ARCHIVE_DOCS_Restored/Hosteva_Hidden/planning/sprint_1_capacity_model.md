# Phase 2: Sprint 1 Capacity & Compute Model

## Overview
This document outlines the compute routing strategy and token cost optimization model for the Sprint 1 regression remediation of Hosteva. 

## Task Profile Analysis
Based on the sealed backlog (`sprint_1_backlog.md`), the workload is highly concentrated on **frontend execution**:
- **CSS / Visuals:** Tailwind class repairs, animation throttling (BUG-01, BUG-06).
- **Client-side JS:** API routing updates, modal focus trapping, keyboard navigation (BUG-02, BUG-03, BUG-04).
- **HTML / Layout:** Dead link removal, unified navigation shell (BUG-05, STORY-01).
- **Backend (Minimal):** Removing a single obsolete endpoint (TECH-01).

No heavy database schema migrations or complex system-level reasoning tasks are required. This presents an excellent opportunity to offload the majority of the Maker work to local inference to optimize for latency, privacy, and zero API token cost.

## Hardware & Environment
- **Host GPU:** NVIDIA RTX 4070 SUPER (12GB VRAM).
- **Inference Engine:** Local Ollama + OpenClaw Swarm architecture.

## Routing Recommendations (The Gauntlet)

### Makers (Execution Team)
Given the RTX 4070 SUPER, local models like `qwen2.5-coder:7b` will easily fit into VRAM with high context sizes, outputting extremely fast tokens (70+ t/s) for standard HTML/JS/CSS logic.

- **Wasp (Frontend & CSS fixes):** 
  - **Model:** `qwen2.5-coder:7b` (Local)
  - **Reasoning:** Perfect for surgical DOM edits, Tailwind class manipulation, and CSS animations. Highly cost-effective (free) and extremely low latency.
- **Shang-Chi (JS Logic & API Wiring):**
  - **Model:** `qwen2.5-coder:7b` (Local)
  - **Reasoning:** Strong enough to handle the JS fetch updates for `wizard.html` and modal focus trapping without needing cloud API calls.
- **Hulk (Layout Consolidation / Heavy HTML Refactors):**
  - **Model:** `qwen2.5-coder:7b` or `qwen2.5-coder:14b` (Local)
  - **Reasoning:** Can handle the broader scope of STORY-01 (Unified Navigation Shell). If context limits hit local boundaries, this agent can fallback to `google/gemini-3-pro-preview`, but local is strongly recommended first to save costs.

### Quality Assurance & Validation (Review Team)
QA roles require broader context awareness across multiple files, strict adherence to Gherkin criteria, and a lower tolerance for hallucination during security and integration reviews.

- **Black Widow (Code Review / Regression Checking):**
  - **Model:** `google/gemini-3-pro` (Cloud)
  - **Reasoning:** Deep context window required to review the diffs against the entire application state. Justifies the token cost to ensure zero regressions.
- **Captain America (Integration & Verification / DoD Check):**
  - **Model:** `google/gemini-3-pro` (Cloud)
  - **Reasoning:** Requires high-level reasoning to ensure cross-module integration and chain-of-custody rules are met before marking tickets as done.

## Cost & Speed Summary
- **Cloud Tokens Saved:** ~70% reduction in cloud API usage by routing Wasp, Shang-Chi, and Hulk to local Ollama (`qwen2.5-coder`).
- **Speed Optimization:** The execution phase will benefit from zero network latency and fast generation times from the 4070 SUPER. Cloud wait times are reserved only for critical review paths.