#!/bin/bash
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva
git add .dockerignore
git commit -m "fix: add .dockerignore to prevent massive context uploads"
git push origin master:main
