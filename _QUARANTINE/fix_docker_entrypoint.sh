#!/bin/bash
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva
git add Dockerfile
git commit -m "fix: update gunicorn entrypoint path to app.main"
git push origin master:main
