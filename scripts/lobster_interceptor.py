import sys
import os
import re
import subprocess
from pathlib import Path

def log(msg):
    print(msg, file=sys.stderr)

def parse_and_execute(markdown_content):
    log("[Lobster Protocol] Initiating markdown intercept...")
    
    # 1. Execute Bash Blocks
    bash_pattern = re.compile(r'```bash\n(.*?)\n```', re.DOTALL)
    bash_blocks = bash_pattern.findall(markdown_content)
    
    for i, block in enumerate(bash_blocks, 1):
        log(f"\n[Lobster Protocol] Executing Bash Block {i}...")
        try:
            # Added timeout constraint and isolated stdin to prevent EOF deadlocks
            result = subprocess.run(
                block, 
                shell=True, 
                check=True, 
                executable='/bin/bash', 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True,
                timeout=60,
                stdin=subprocess.DEVNULL
            )
            log(f"[Stdout]: {result.stdout.strip()}")
            if result.stderr:
                log(f"[Stderr]: {result.stderr.strip()}")
        except subprocess.TimeoutExpired as e:
            log(f"[ERROR] Bash block {i} timed out after {e.timeout}s.")
            if e.stdout: log(f"[Stdout]: {e.stdout.strip()}")
            if e.stderr: log(f"[Stderr]: {e.stderr.strip()}")
        except subprocess.CalledProcessError as e:
            log(f"[ERROR] Bash block failed with code {e.returncode}")
            log(f"[Stderr]: {e.stderr.strip()}")
            sys.exit(1)

    # 2. Extract and Write Python Blocks
    python_pattern = re.compile(r'```python\n(.*?)\n```', re.DOTALL)
    python_blocks = python_pattern.findall(markdown_content)
    
    for i, block in enumerate(python_blocks, 1):
        lines = block.split('\n')
        if not lines:
            continue
            
        first_line = lines[0].strip()
        if first_line.startswith('# FILE:'):
            file_path = first_line.replace('# FILE:', '').strip()
            log(f"\n[Lobster Protocol] Routing Python Block {i} to -> {file_path}")
            
            # Create parent directories if they don't exist
            target_path = Path(file_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file (excluding the directive line)
            content = '\n'.join(lines[1:])
            target_path.write_text(content)
            log(f"[SUCCESS] Wrote {len(content.encode('utf-8'))} bytes to {file_path}")
        else:
            log(f"\n[WARNING] Python Block {i} ignored: Missing '# FILE: <path>' directive on line 1.")

    # 3. CRITICAL: Passthrough Flaw Fix
    # Echo the original content cleanly to stdout for LangGraph state machine survival
    sys.stdout.write(markdown_content)
    sys.stdout.flush()

if __name__ == "__main__":
    content = ""
    if len(sys.argv) > 1 and sys.argv[1] != "-":
        md_file = Path(sys.argv[1])
        if not md_file.exists():
            log(f"[ERROR] File not found: {md_file}")
            sys.exit(1)
        content = md_file.read_text()
    else:
        # Handle Stdin safely
        if not sys.stdin.isatty():
            content = sys.stdin.read()
            # Explicitly close stdin after reading to prevent subprocess inheritance issues 
            # if they were ever somehow passed sys.stdin
            sys.stdin.close()
        else:
            log("Usage: python3 lobster_interceptor.py <path_to_markdown_file> (or pipe via stdin)")
            sys.exit(1)
            
    parse_and_execute(content)
