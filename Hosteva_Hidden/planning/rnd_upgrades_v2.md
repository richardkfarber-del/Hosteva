# Swarm Capability & R&D Proposal v2
**Author:** Shuri (Head of Platform Engineering)
**Target:** Director Richard Farber

## Context & Bottlenecks
Director, you asked what tools or plugins we need to better enable the team. Just because our current setup works doesn't mean it can't be vastly improved. We are currently bleeding tokens and time on inefficient workarounds. Here is my analysis of our current bottlenecks:

1. **Visual QA Deficit:** The internal OpenClaw `browser` plugin hangs on WSL2, leaving us blind.
2. **API Discovery Friction:** We rely heavily on `web_fetch` to scrape API docs, which is inefficient for dynamic schema exploration.
3. **Manual CI/CD Overhead:** Heimdall pushes to `main` manually, lacking a direct GitHub PR automation and CI/CD integration.
4. **Database State Blindness:** Vision has to guess database state from code rather than querying it directly.

## Proposed Capability Upgrades (The "Digital Vibranium" Drops)

### 1. Headless Playwright/Puppeteer CLI Wrappers (Visual QA Unlock)
**The Problem:** The internal browser tool hangs in WSL2. 
**The Solution:** Build a standalone Python CLI wrapping Playwright that connects to a host browser or runs headlessly with Xvfb/Wayland workarounds, completely bypassing the native plugin. This CLI will take a URL and return a screenshot (or base64 image) and serialized DOM structure directly back to Vision.
**Impact:** Immediate automated visual QA. We stop flying blind and start validating UI renders instantly.

### 2. GitHub & CI/CD MCP Server (Workflow Automation)
**The Problem:** Heimdall is functioning as a manual commit bot. Render auto-builds, but we lack PR checks, automated testing, and direct CI feedback.
**The Solution:** Deploy the official **GitHub Model Context Protocol (MCP) server**. This allows Heimdall to automatically open PRs, read Actions logs, review CI/CD check failures, and merge code. 
**Impact:** True CI/CD integration. We move from manual git pushes to a professional Pull Request workflow managed entirely by the Swarm.

### 3. Native Database / SQLite3 MCP Server (State Verification)
**The Problem:** Vision is guessing DB state based on schema files rather than querying live data.
**The Solution:** Integrate a **SQLite (or Postgres) MCP server** or configure explicit `sqlite3` CLI tool wrappers. This gives the Swarm direct, read-only (or read-write in dev) SQL execution capabilities.
**Impact:** End of guesswork. Vision can execute `SELECT * FROM ...` to verify migrations applied correctly or validate state changes.

## Next Steps
Approve this R&D vector, and I will begin forging these tools for the Swarm immediately. Let's optimize.
