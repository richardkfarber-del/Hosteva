import subprocess
import os

def run_shell_command(command: str) -> str:
    """
    Executes a shell command. Use this to run pytest, git, or system commands.
    Has a strict 60-second timeout to prevent hanging processes.
    """
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=600,
            cwd="/home/rdogen/OpenClaw_Factory/projects/Hosteva"
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if result.returncode == 0:
            return f"SUCCESS (Code 0)\nSTDOUT:\n{out}"
        else:
            return f"FAILED (Code {result.returncode})\nSTDOUT:\n{out}\nSTDERR:\n{err}"
    except subprocess.TimeoutExpired:
        return "CRITICAL ERROR: Command timed out after 600 seconds. The process hung (e.g., infinite loop or hanging database connection)."
    except Exception as e:
        return f"CRITICAL ERROR: {str(e)}"

def read_file(path: str) -> str:
    """Reads the contents of a file from the disk."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"ERROR: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Writes content to a file on the disk, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"SUCCESS: Wrote to {path}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def content_search(pattern: str, path: str) -> str:
    """Searches for a regex pattern inside a specific file and returns the matching lines with line numbers."""
    try:
        result = subprocess.run(
            f"grep -n '{pattern}' {path}",
            shell=True,
            capture_output=True,
            text=True,
            cwd="/home/rdogen/OpenClaw_Factory/projects/Hosteva"
        )
        if result.returncode == 0:
            return result.stdout.strip()
        elif result.returncode == 1:
            return "No matches found."
        else:
            return f"ERROR: {result.stderr.strip()}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def submit_phase_plan(plan_markdown: str) -> str:
    """Call this tool ONLY when you have completed your analysis and are ready to submit your final markdown plan. Pass your entire final response into the plan_markdown parameter."""
    return "PLAN_ACCEPTED"
