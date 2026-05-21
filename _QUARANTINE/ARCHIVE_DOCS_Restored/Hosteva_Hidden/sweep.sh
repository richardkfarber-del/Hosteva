#!/bin/bash
echo "🧹 Sweeping the deck for ghost processes..."
pkill -9 -f chromium 2>/dev/null && echo "✅ Chromium ghosts eliminated."
pkill -9 -f chrome 2>/dev/null && echo "✅ Chrome ghosts eliminated."
pkill -9 -f openclaw-gateway 2>/dev/null && echo "✅ Zombie gateways terminated."
echo "Airspace is completely clear."
