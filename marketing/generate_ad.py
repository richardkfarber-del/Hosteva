#!/usr/bin/env python3

import os
import sys
import requests
import time

def generate_video_rest(prompt: str, output_path: str = "output.mp4", poll_interval: int = 10):
    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    base_url = "https://generativelanguage.googleapis.com/v1beta"
    model_name = "veo-3.1-fast-generate-preview"
    init_url = f"{base_url}/models/{model_name}:predictLongRunning?key={api_key}"

    operation_payload = {
        "instances": [
            {
                "prompt": prompt
            }
        ],
        "parameters": {
            "aspectRatio": "16:9",
            "resolution": "720p",
            "durationSeconds": 8
        }
    }

    print(f"Submitting Veo 3.1 Fast video generation job...")
    response = requests.post(init_url, json=operation_payload, timeout=60)
    
    if response.status_code != 200:
        print(f"API Error: {response.status_code} - {response.text}")
        response.raise_for_status()
        
    operation_data = response.json()
    operation_name = operation_data.get("name")
    
    if not operation_name:
        raise ValueError(f"No operation name returned: {operation_data}")

    print(f"Operation started successfully: {operation_name}")
    print(f"Polling for completion (this may take 1-3 minutes)...")

    while True:
        check_url = f"{base_url}/{operation_name}?key={api_key}"
        status_response = requests.get(check_url, timeout=60)
        status_response.raise_for_status()
        status_data = status_response.json()

        done = status_data.get("done", False)
        if done:
            if "error" in status_data:
                raise RuntimeError(f"Operation failed: {status_data['error']}")
            print("Operation complete!")
            break

        print(f"Still processing...")
        time.sleep(poll_interval)

    # Extract the generated video URI from the nested response
    response_data = status_data.get("response", {})
    generate_video_response = response_data.get("generateVideoResponse", {})
    generated_samples = generate_video_response.get("generatedSamples", [])
    
    if not generated_samples:
        raise ValueError(f"No generated samples found in the response: {status_data}")
        
    video_uri = generated_samples[0].get("video", {}).get("uri")
    
    if not video_uri:
         raise ValueError(f"No video URI found in the sample: {generated_samples[0]}")

    print(f"Video ready at URI: {video_uri}")
    print("Downloading video asset...")
    
    # We must append the API key to the download URL to authenticate the media fetch
    download_url = f"{video_uri}&key={api_key}" if "?" in video_uri else f"{video_uri}?key={api_key}"
    
    vid_resp = requests.get(download_url)
    if vid_resp.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(vid_resp.content)
        print(f"Video successfully downloaded to: {output_path}")
        return output_path
    else:
        raise RuntimeError(f"Failed to download from URI: {vid_resp.status_code} - {vid_resp.text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_ad.py <prompt> [output_path]")
        sys.exit(1)

    prompt = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "generated_ad.mp4"

    generate_video_rest(prompt, output_path)
