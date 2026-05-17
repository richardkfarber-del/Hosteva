export GOOGLE_MAPS_API_KEY="MOCKED_FOR_TESTING"
nohup python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 > server.log 2>&1 &
echo $! > server.pid
