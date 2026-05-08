import sys
import traceback

try:
    from app.main import app
    print("app.main booted successfully.")
except Exception as e:
    print("CRITICAL ERROR booting app.main:")
    traceback.print_exc()
