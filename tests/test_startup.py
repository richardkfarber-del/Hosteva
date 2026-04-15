import sys
import time
import subprocess
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_agent_spawn():
    """Verify the daemon can successfully request an agent spawn via CLI."""
    try:
        cmd = ["openclaw", "agent", "--agent", "hawkeye", "-m", "QA connection test.", "--json"]
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode != 0:
            logger.error(f"❌ OpenClaw CLI failed with exit code {result.returncode}: {result.stderr}")
            return False
            
        try:
            data = json.loads(result.stdout)
            if data:
                logger.info(f"✅ Successfully spawned test agent via CLI. Output parsed.")
                return True
        except json.JSONDecodeError:
            logger.error(f"❌ Failed to parse JSON output: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"❌ OpenClaw CLI timed out after 15 seconds.")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to execute OpenClaw CLI: {e}")
        return False

if __name__ == "__main__":
    logger.info("Initiating QA Startup Protocol...")
    
    if not test_agent_spawn():
        sys.exit(1)
        
    logger.info("🎉 All QA startup tests passed. Safe to restart systemd service.")
    sys.exit(0)
