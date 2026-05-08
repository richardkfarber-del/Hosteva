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
            timeout=60,
            cwd="/home/rdogen/OpenClaw_Factory/projects/Hosteva"
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if result.returncode == 0:
            return f"SUCCESS (Code 0)\nSTDOUT:\n{out}"
        else:
            return f"FAILED (Code {result.returncode})\nSTDOUT:\n{out}\nSTDERR:\n{err}"
    except subprocess.TimeoutExpired:
        return "CRITICAL ERROR: Command timed out after 60 seconds. The process hung (e.g., infinite loop or hanging database connection)."
    except Exception as e:
        return f"CRITICAL ERROR: {str(e)}"

def read_file(filepath: str) -> str:
    """Reads the contents of a file from the disk."""
    try:
        with open(filepath, 'r') as f:
            return f.read()
    except Exception as e:
        return f"ERROR: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """Writes content to a file on the disk, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"SUCCESS: Wrote to {filepath}"
    except Exception as e:
        return f"ERROR: {str(e)}"
