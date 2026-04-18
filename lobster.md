# The Lobster Protocol: Swarm Governance

## 1. Permission Gates
- **Shell Access:** Only **Iron Man** and **Rocket Raccoon** have `bash` and `node` execution rights.
- **Financials/API Keys:** Only **Nick Fury** and **Black Panther** can read the `.env` file.
- **Logic Validation:** **Captain America** must sign off on any core logic changes before they are committed.

## 2. Communication Rules
- **No Raw Logs:** Agents shall not paste long stack traces into the main chat.
- **State Files:** Agents write technical outputs to `/workspace/Hosteva/state.json`.
- **Status Codes:** Responses must include a status (e.g., `[200 OK]` or `[403 VETO]`).

## 3. Hardware Awareness
- **VRAM Management:** Local agents (Stark/Vision) must monitor GPU usage. If VRAM > 11GB, they must signal a handoff to a cloud model.