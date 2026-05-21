import sys
import argparse
import re

def extract_code_block(text, lang=''):
    pattern = rf'```{lang}\n(.*?)\n```' if lang else r'```.*?\n(.*?)\n```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Fallback to entire text if no markdown block found
    return text.strip()

def main():
    parser = argparse.ArgumentParser(description="Extracts a code block from stdin and writes it to a file.")
    parser.add_argument('file', help="Target file to write to")
    parser.add_argument('--lang', default='', help="Language of the code block (e.g., 'python', 'yaml')")
    
    args = parser.parse_args()
    input_text = sys.stdin.read()
    
    code = extract_code_block(input_text, args.lang)
    
    with open(args.file, 'w') as f:
        f.write(code + '\n')
    print(f"Successfully extracted code and wrote to {args.file}")

if __name__ == '__main__':
    main()
