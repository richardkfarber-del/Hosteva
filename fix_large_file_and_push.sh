#!/bin/bash
cd /home/rdogen/OpenClaw_Factory/projects/Hosteva
# Remove the large file from git tracking
git rm --cached openclaw-state.tgz
# Add it to gitignore so it never gets tracked again
echo "openclaw-state.tgz" >> .gitignore
git add .gitignore
# Amend the previous commit to remove the large file
git commit --amend --no-edit
# Push to GitHub
git push origin master
