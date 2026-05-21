#!/bin/bash
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva
git push origin master:main > push_log.txt 2>&1
cat push_log.txt
