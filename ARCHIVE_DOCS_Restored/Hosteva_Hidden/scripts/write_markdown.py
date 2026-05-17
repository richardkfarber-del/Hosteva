#!/usr/bin/env python3
import sys
import argparse
import re

def main():
    parser = argparse.ArgumentParser(description="Robustly write or update markdown files from stdin.")
    parser.add_argument('file', help="Target markdown file")
    parser.add_argument('--mode', choices=['overwrite', 'append', 'replace-section'], default='overwrite', help="Mode of operation")
    parser.add_argument('--section', help="Section header to replace (e.g., '## Ledger')")
    
    args = parser.parse_args()
    
    input_text = sys.stdin.read()
    
    if args.mode == 'overwrite':
        with open(args.file, 'w') as f:
            f.write(input_text)
        print(f"Overwrote {args.file}")
        
    elif args.mode == 'append':
        with open(args.file, 'a') as f:
            f.write(input_text)
        print(f"Appended to {args.file}")
        
    elif args.mode == 'replace-section':
        if not args.section:
            print("Error: --section is required for replace-section mode")
            sys.exit(1)
            
        try:
            with open(args.file, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            content = ""
            
        header_level = len(args.section) - len(args.section.lstrip('#'))
        if header_level == 0:
            print("Error: section must start with #")
            sys.exit(1)
            
        pattern = re.compile(
            rf'(^{re.escape(args.section)}[ \t]*\n.*?)'
            rf'(?=^#{{1,{header_level}}}[ \t]|\Z)',
            re.MULTILINE | re.DOTALL
        )
        
        replacement = f"{args.section}\n{input_text.strip()}\n\n"
        
        if pattern.search(content):
            new_content = pattern.sub(replacement.replace('\\', '\\\\'), content, count=1)
            with open(args.file, 'w') as f:
                f.write(new_content)
            print(f"Replaced section '{args.section}' in {args.file}")
        else:
            with open(args.file, 'a') as f:
                if content and not content.endswith('\n'):
                    f.write('\n')
                f.write(replacement)
            print(f"Section '{args.section}' not found. Appended to {args.file}")

if __name__ == '__main__':
    main()
