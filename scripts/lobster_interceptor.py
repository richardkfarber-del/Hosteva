import sys
import os
import re
import subprocess
from pathlib import Path

def parse_and_execute(markdown_content):
    print("[Lobster Protocol] Initiating markdown intercept...")
    
    # 1. Execute Bash Blocks
    bash_pattern = re.compile(r'```bash\n(.*?)\n```', re.DOTALL)
    bash_blocks = bash_pattern.findall(markdown_content)
    
    for i, block in enumerate(bash_blocks, 1):
        print(f"\n[Lobster Protocol] Executing Bash Block {i}...")
        try:
            result = subprocess.run(
                block, 
                shell=True, 
                check=True, 
                executable='/bin/bash', 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            print(f"[Stdout]: {result.stdout.strip()}")
            if result.stderr:
                print(f"[Stderr]: {result.stderr.strip()}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Bash block failed with code {e.returncode}")
            print(f"[Stderr]: {e.stderr.strip()}")
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
            print(f"\n[Lobster Protocol] Routing Python Block {i} to -> {file_path}")
            
            # Create parent directories if they don't exist
            target_path = Path(file_path)
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write the file (excluding the directive line)
            content = '\n'.join(lines[1:])
            target_path.write_text(content)
            print(f"[SUCCESS] Wrote {len(content.encode('utf-8'))} bytes to {file_path}")
        else:
            print(f"\n[WARNING] Python Block {i} ignored: Missing '# FILE: <path>' directive on line 1.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 lobster_interceptor.py <path_to_markdown_file>")
        sys.exit(1)
        
    md_file = Path(sys.argv[1])
    if not md_file.exists():
        print(f"[ERROR] File not found: {md_file}")
        sys.exit(1)
        
    parse_and_execute(md_file.read_text())
