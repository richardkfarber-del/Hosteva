#!/bin/bash
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva
git add app/main.py
git commit -m "fix: update Jinja2Templates directory path to app/templates"
git push origin master:main
