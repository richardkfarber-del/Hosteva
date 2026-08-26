#!/bin/bash
PROJECT_ROOT="/home/rdogen/OpenClaw_Factory/projects/Hosteva"
cd $PROJECT_ROOT
sudo pkill -9 -f openclaw
rm -rf ./.openclaw/agents/main/sessions/*
./launch.sh
