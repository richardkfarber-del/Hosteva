#!/bin/bash
# Temporary Xvfb wrapper to force headless chromium under WSL2
if ! command -v xvfb-run &> /dev/null; then
    sudo apt-get update && sudo apt-get install -y xvfb
fi
export DISPLAY=:99
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
export XAUTHORITY=$HOME/.Xauthority
openclaw gateway restart
