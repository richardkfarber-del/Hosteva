#!/usr/bin/env python3
import sys
import argparse
import datetime

def main():
    parser = argparse.ArgumentParser(description='Append entry to daily ledger')
    parser.add_argument('--task', required=True, help='Task Name')
    parser.add_argument('--agent', required=True, help='Agent Name')
    parser.add_argument('--status', required=True, help='Status')
    parser.add_argument('--execution', required=True, help='Execution Details')
    parser.add_argument('--compute', required=True, help='Compute')
    parser.add_argument('--tags', required=True, help='Tags')

    args = parser.parse_args()

    ledger_path = "/home/rdogen/OpenClaw_Factory/projects/Hosteva/.openclaw/.openclaw/workspace/daily_ledger.md"
    
    entry = f"""
### {args.task}
- **Agent**: {args.agent}
- **Status**: [{args.status}]
- **Execution**: {args.execution}
- **Compute**: {args.compute}
- **Tag**: {args.tags}
"""

    try:
        with open(ledger_path, "a") as f:
            f.write(entry)
        print(f"Successfully appended entry to {ledger_path}")
    except Exception as e:
        print(f"Error writing to ledger: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
