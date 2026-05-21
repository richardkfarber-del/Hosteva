#!/bin/bash
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva
# Check branch
git branch -a
# Check recent commits
git log -n 3 --stat
