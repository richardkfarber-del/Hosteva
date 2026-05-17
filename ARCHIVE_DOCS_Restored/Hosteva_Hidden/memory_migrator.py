import sys
import os

def read_memory_file(file_path):
    """
    Safely reads a memory file using atomic file I/O.
    """
    if not os.path.exists(file_path):
        print(f"Error: The file '{file_path}' does not exist.")
        sys.exit(1)
        
    if not os.path.isfile(file_path):
        print(f"Error: The path '{file_path}' is not a file.")
        sys.exit(1)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            print(f"Successfully read {len(content)} characters from '{file_path}'.")
            return content
    except Exception as e:
        print(f"Error reading file '{file_path}': {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python memory_migrator.py <path_to_memory_file>")
        sys.exit(1)
        
    target_path = sys.argv[1]
    read_memory_file(target_path)
