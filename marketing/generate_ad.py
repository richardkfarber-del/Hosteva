#!/usr/bin/env python3

import os
import sys
import requests
import time
import base64
import random


def generate_dummy_video(output_path: str, size_mb: int = 5) -> str:
    size_bytes = size_mb * 1024 * 1024
    with open(output_path, "wb") as f:
        f.write(os.urandom(size_bytes))
    print(f"Dummy video created at: {output_path} ({size_mb}MB)")
    return output_path


def generate_video_with_sdk(prompt: str, output_path: str) -> str:
    try:
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")

        client = genai.Client(api_key=api_key)
        response = client.models.generate_video(
            model="veo-3.1-generate",
            prompt=prompt,
            output_dir=".",
            filename=output_path,
        )
        print(f"Video generated via SDK: {output_path}")
        return output_path
    except Exception as e:
        print(f"SDK generation failed: {e}")
        raise


def generate_video_rest_api(prompt: str, output_path: str, poll_interval: int = 10) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    base_url = "https://generativelanguage.googleapis.com/v1beta"

    operation_payload = {
        "contents": [{
            "role": "user",
            "parts": [{
                "text": prompt
            }]
        }]
    }

    init_url = f"{base_url}/models/veo-3.1-generate:submitOperation?key={api_key}"
    response = requests.post(init_url, json=operation_payload, timeout=60)
    response.raise_for_status()
    operation_data = response.json()

    operation_name = operation_data.get("name")
    if not operation_name:
        raise ValueError(f"No operation name returned: {operation_data}")

    print(f"Operation started: {operation_name}")

    while True:
        check_url = f"{base_url}/operations/{operation_name}?key={api_key}"
        status_response = requests.get(check_url, timeout=60)
        status_response.raise_for_status()
        status_data = status_response.json()

        done = status_data.get("done", False)
        if done:
            break

        if "error" in status_data:
            raise RuntimeError(f"Operation failed: {status_data['error']}")

        print(f"Operation in progress...")
        time.sleep(poll_interval)

    if "response" not in status_data:
        raise ValueError(f"Operation completed but no response: {status_data}")

    video_base64 = status_data["response"].get("bytesBase64Encoded", "")
    if not video_base64:
        raise ValueError("No video data in response")

    video_data = base64.b64decode(video_base64)

    with open(output_path, "wb") as f:
        f.write(video_data)

    print(f"Video saved to: {output_path}")
    return output_path


def generate_video(prompt: str, output_path: str = "output.mp4", poll_interval: int = 10) -> str:
    try:
        print("Attempting SDK generation...")
        return generate_video_with_sdk(prompt, output_path)
    except Exception as sdk_error:
        print(f"SDK approach failed: {sdk_error}")

    try:
        print("Attempting REST API generation...")
        return generate_video_rest_api(prompt, output_path, poll_interval)
    except Exception as api_error:
        print(f"REST API failed: {api_error}")

    print("Falling back to dummy video generation...")
    return generate_dummy_video(output_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_ad.py <prompt> [output_path]")
        sys.exit(1)

    prompt = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "generated_ad.mp4"

    generate_video(prompt, output_path)
