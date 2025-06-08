import json
import requests
import subprocess
from scanner.detector import analyze_response
from security.filter import is_prompt_safe
import os


def load_payloads(path):
    all_payloads = []

    if os.path.isdir(path):
        # It's a folder, load all JSON files inside
        for file in os.listdir(path):
            if file.endswith('.json'):
                full_path = os.path.join(path, file)
                try:
                    with open(full_path, 'r') as f:
                        content = json.load(f)
                        if isinstance(content, list):
                            all_payloads.extend(content)
                        else:
                            print(f"[!] Skipping {file}: not a list of payloads")
                except json.JSONDecodeError:
                    print(f"[!] Skipping {file}: invalid JSON")
    else:
        # It's a single file
        with open(path, 'r') as f:
            all_payloads = json.load(f)

    return all_payloads


def send_to_http_target(prompt, url):
    try:
        headers = {
            "Authorization": f"Bearer YOUR_HF_API_KEY",
            "Content-Type": "application/json"
        }
        payload = {
            "inputs": prompt
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()
        return result[0]['generated_text'] if isinstance(result, list) else result.get("generated_text", str(result))
    
    except Exception as e:
        
        return f"[ERROR] HTTP Target Failed: {str(e)}"



def send_to_ollama(prompt, model="mistral"):
    try:
        result = subprocess.run(
            ["ollama", "run", model],
            input=prompt.encode(),
            capture_output=True,
            timeout=30
        )
        return result.stdout.decode().strip()
    except Exception as e:
        return f"[ERROR] Ollama Failed: {str(e)}"


def scan(payloads, target_type, target_value):
    results = []

    for payload in payloads:
        print(f"[*] Testing: {payload['id']} ({payload['category']})")

        # First, block if the input is unsafe
        is_safe, matched_pattern = is_prompt_safe(payload['prompt'])
        if not is_safe:
            results.append({
                "id": payload['id'],
                "category": payload['category'],
                "prompt": payload['prompt'],
                "response": f"[BLOCKED] Prompt matched dangerous pattern: {matched_pattern}",
                "verdict": {
                    "severity": "BLOCKED",
                    "reason": f"Input filter triggered on: '{matched_pattern}'"
                }
            })
            continue  # Skip execution

        # If safe, run the prompt
        if target_type == "http":
            response = send_to_http_target(prompt=payload['prompt'], url=target_value)
        elif target_type == "local":
            response = send_to_ollama(prompt=payload['prompt'], model=target_value)
        else:
            response = "[!] Unknown target type"

        verdict = analyze_response(response)

        results.append({
            "id": payload['id'],
            "category": payload['category'],
            "prompt": payload['prompt'],
            "response": response,
            "verdict": verdict
        })

    return results
