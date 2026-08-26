#!/bin/bash
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva
git add app/main.py main.py
git commit -m "fix: syntax error in main.py causing crash"
git push origin main
