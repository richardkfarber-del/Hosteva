#!/usr/bin/env python3
import subprocess

def get_git_diff():
    result = subprocess.run(["git", "diff", "main"], capture_output=True, text=True)
    return result.stdout

def chunk_and_summarize(diff_text):
    chunks = diff_text.split("diff --git")
    summary = "## PR Diff Summary Map\n"
    for chunk in chunks[1:]:
        if not chunk.strip(): continue
        lines = chunk.strip().split('\n')
        file_name = lines[0].split(' ')[-1]
        additions = sum(1 for line in lines if line.startswith('+') and not line.startswith('+++'))
        deletions = sum(1 for line in lines if line.startswith('-') and not line.startswith('---'))
        summary += f"- **{file_name}**: +{additions} / -{deletions} lines changed.\n"
    return summary

if __name__ == "__main__":
    diff = get_git_diff()
    print(chunk_and_summarize(diff))
