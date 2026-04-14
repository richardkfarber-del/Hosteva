# TECH-001: Lobster OS-Level Bash Pipe

**Description:**
Modify the Lobster interceptor to natively accept standard input (stdin) and create an executable shell wrapper. This will allow the Swarm and local OS environment to pipe subagent standard output directly into Lobster for processing and formatting.

**Acceptance Criteria:**
* The `scripts/lobster_interceptor.py` script is modified to detect and read from standard input (stdin) when no file argument is provided (or when `-` is passed).
* A dedicated, executable shell wrapper (e.g., `lobster.sh` or alias) is created to route OS-level inputs into the core Lobster interceptor logic.
* The shell wrapper correctly processes standard pipeline chains (e.g., `<subagent_command> | lobster`).
* The modified interceptor retains full backward compatibility with existing direct-file argument invocations.
* Unit tests (or validation runs) verify that both stdin and standard file path arguments are parsed and executed correctly by the interceptor.
## Swarm Review
- **Vision (Data Engineer):** Approved
- **Iron Man (Lead Backend):** Approved
- **Black Widow (QA Shadow Operative):** Approved
- **Captain America (QA Gatekeeper):** Approved
