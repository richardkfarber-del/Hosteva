import sys
import asyncio
from temporalio.client import Client

async def test_connection():
    try:
        # Connect to the local Temporal server
        client = await Client.connect("localhost:7233")
        print("✅ Successfully connected to Temporal Server at localhost:7233.")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to Temporal Server: {e}")
        return False

if __name__ == "__main__":
    if not asyncio.run(test_connection()):
        sys.exit(1)
    sys.exit(0)
