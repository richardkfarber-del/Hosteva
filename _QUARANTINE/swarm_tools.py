import subprocess
import os
import json
import urllib.request

def run_shell_command(command: str) -> str:
    """
    Executes a shell command. Use this to run pytest, git, or system commands.
    Has a strict 60-second timeout to prevent hanging processes.
    """
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=600,
            cwd="/home/rdogen/OpenClaw_Factory/projects/Hosteva"
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if result.returncode == 0:
            return f"SUCCESS (Code 0)\nSTDOUT:\n{out}"
        else:
            return f"FAILED (Code {result.returncode})\nSTDOUT:\n{out}\nSTDERR:\n{err}"
    except subprocess.TimeoutExpired:
        return "CRITICAL ERROR: Command timed out after 600 seconds. The process hung (e.g., infinite loop or hanging database connection)."
    except Exception as e:
        return f"CRITICAL ERROR: {str(e)}"

def read_file(path: str) -> str:
    """Reads the contents of a file from the disk."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"ERROR: {str(e)}"

def write_file(path: str, content: str) -> str:
    """Writes content to a file on the disk, creating directories if needed."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return f"SUCCESS: Wrote to {path}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def content_search(pattern: str, path: str) -> str:
    """Searches for a regex pattern inside a specific file and returns the matching lines with line numbers."""
    try:
        result = subprocess.run(
            f"grep -n '{pattern}' {path}",
            shell=True,
            capture_output=True,
            text=True,
            cwd="/home/rdogen/OpenClaw_Factory/projects/Hosteva"
        )
        if result.returncode == 0:
            return result.stdout.strip()
        elif result.returncode == 1:
            return "No matches found."
        else:
            return f"ERROR: {result.stderr.strip()}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def submit_phase_plan(plan_markdown: str) -> str:
    """Call this tool ONLY when you have completed your analysis and are ready to submit your final markdown plan. Pass your entire final response into the plan_markdown parameter."""
    return "PLAN_ACCEPTED"

def render_deploy(service_id: str) -> str:
    """
    Triggers a deployment to Render via their REST API.
    Requires RENDER_API_KEY environment variable.
    """
    api_key=os.environ.get("RENDER_API_KEY")
    if not api_key:
        return "ERROR: RENDER_API_KEY environment variable not set. Cannot authenticate with Render."
    
    url = f"https://api.render.com/v1/services/{service_id}/deploys"
    req = urllib.request.Request(url, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Accept", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 201:
                data = json.loads(response.read().decode())
                deploy_id = data.get("id", "UNKNOWN")
                return f"SUCCESS: Render deployment triggered. Deploy ID: {deploy_id}"
            else:
                return f"ERROR: Render API returned status {response.status}"
    except urllib.error.HTTPError as e:
        return f"ERROR: Render API HTTP Error: {e.code} - {e.read().decode()}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def docker_build(image_name: str, tag: str = "latest", dockerfile_path: str = ".") -> str:
    """
    Builds a Docker image using the local Docker daemon.
    """
    command = f"docker build -t {image_name}:{tag} {dockerfile_path}"
    return run_shell_command(command)

def git_push() -> str:
    """Pushes committed changes to the remote origin/main branch."""
    return run_shell_command("git push origin main")

def verify_render_deployment(service_id="srv-d798m4chg0os73e3it70", *args, **kwargs):
    """Polls the Render API until the deployment is live or fails."""
    import requests, os, time
    from dotenv import load_dotenv
    load_dotenv("/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env")
    api_key=os.environ.get("RENDER_API_KEY")
    if not api_key: return "ERROR: RENDER_API_KEY not found in environment."
    
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}
    url = f"https://api.render.com/v1/services/{service_id}/deploys"
    
    print("\n-> Polling Render API for deployment status (this may take up to 10 minutes)...")
    for _ in range(90): # Poll 90 times at 10-second intervals
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            deploys = response.json()
            if not deploys: return "ERROR: No deployments found for this service."
            
            status = deploys[0]["deploy"]["status"]
            print(f"   ...Status: {status}")
            
            if status == "live":
                return "STATUS: LIVE (GREEN). Health checks passed. Deployment successful."
            elif status in ["build_failed", "update_failed", "canceled"]:
                return f"STATUS: FAILED ({status}). The deployment crashed."
            
            time.sleep(10)
        except Exception as e:
            return f"ERROR polling Render API: {str(e)}"
    
    return "ERROR: Deployment timed out after 15 minutes."

def get_render_logs(service_id='srv-d798m4chg0os73e3it70', *args, **kwargs):
    '''Fetches raw server logs natively using the local Render CLI and dynamic Workspace ID.'''
    import os, subprocess, requests
    from dotenv import load_dotenv
    load_dotenv('/home/rdogen/OpenClaw_Factory/projects/Hosteva/.env')
    api_key=os.environ.get('RENDER_API_KEY')
    if not api_key: return 'ERROR: RENDER_API_KEY not found in environment.'

    env = os.environ.copy()
    env['RENDER_API_KEY'] = api_key

    try:
        print('-> Fetching Render Workspace ID via REST API...')
        headers = {'Authorization': f'Bearer {api_key}', 'Accept': 'application/json'}
        ws_res = requests.get('https://api.render.com/v1/owners', headers=headers)
        ws_res.raise_for_status()
        workspace_id = ws_res.json()[0]['owner']['id']

        bin_path = '/home/rdogen/.local/bin/render'
        print(f'-> Setting active workspace {workspace_id}...')
        subprocess.check_output([bin_path, 'workspace', 'set', workspace_id], env=env, text=True, stderr=subprocess.STDOUT)

        print(f'-> Fetching live logs...')
        log_output = subprocess.check_output(
            [bin_path, 'logs', '--resources', service_id, '--output', 'text'], 
            env=env, text=True, stderr=subprocess.STDOUT
        )

        snippet = f'--- RENDER LOGS ---\n{log_output[-3000:]}'
        print(f'\n[RAW CLI OUTPUT TO AGENT]:\n{snippet}\n')
        return snippet

    except requests.exceptions.RequestException as e:
        return f'ERROR fetching workspace: {str(e)}'
    except subprocess.CalledProcessError as e:
        return f'ERROR executing Render CLI: {e.output}'
    except Exception as e:
        return f'ERROR: {str(e)}'
