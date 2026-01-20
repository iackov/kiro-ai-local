#!/usr/bin/env python3
"""
Fetch Qwen chats using the same method as qwen_client.py
"""
import sys
import json
import requests
from pathlib import Path

# Add qwen path
qwen_path = Path(r"C:\Users\Jack\source\kiro\qwen\src\mcp_server")
sys.path.insert(0, str(qwen_path))

# Load config
config_path = qwen_path / "qwen_config.json"
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# Build headers (same as qwen_client.py)
cookie_string = config['cookies']['cookie_string']
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/event-stream, application/json, text/plain, */*",
    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Cache-Control": "no-cache",
    "Origin": "https://chat.qwen.ai",
    "Referer": "https://chat.qwen.ai/",
    "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Cookie": cookie_string
}

print("=== Fetching Qwen Chats ===")
print(f"Cookie length: {len(cookie_string)}")
print()

# Try to get chats
base_url = "https://chat.qwen.ai"
endpoints_to_try = [
    "/api/v2/chats",
    "/api/v2/chats/list",
    "/api/v2/user/chats",
]

for endpoint in endpoints_to_try:
    url = base_url + endpoint
    print(f"Trying: {endpoint}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  SUCCESS!")
            print(f"  Response: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
            
            # Save to file
            output_file = Path("data/qwen-chats-response.json")
            output_file.parent.mkdir(exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"  Saved to: {output_file}")
            break
        else:
            print(f"  Failed: {response.text[:200]}")
    except Exception as e:
        print(f"  Error: {e}")
    
    print()

print("\nDone!")
