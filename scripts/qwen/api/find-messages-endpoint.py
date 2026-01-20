#!/usr/bin/env python3
"""
Find endpoint for getting chat messages
"""
import sys
import json
import requests
from pathlib import Path

qwen_path = Path(r"C:\Users\Jack\source\kiro\qwen\src\mcp_server")
sys.path.insert(0, str(qwen_path))

from qwen_client import QwenChatClient

# Load chats
with open('data/qwen-chats-success.json', 'r', encoding='utf-8') as f:
    chats_data = json.load(f)

# Get first chat ID
chat_id = chats_data['data'][0]['id']
print(f"Testing with chat: {chats_data['data'][0]['title']}")
print(f"Chat ID: {chat_id}")
print()

# Initialize client
client = QwenChatClient(config_path=str(qwen_path / "qwen_config.json"))

# Try different endpoints
endpoints = [
    f"/api/v2/chats/{chat_id}/messages",
    f"/api/v2/chats/{chat_id}/history",
    f"/api/v2/messages?chat_id={chat_id}",
    f"/api/v2/chat/{chat_id}/messages",
]

for endpoint in endpoints:
    url = client.base_url + endpoint
    print(f"Trying: {endpoint}")
    
    try:
        response = requests.get(url, headers=client.headers, timeout=30)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  SUCCESS!")
                print(f"  Messages: {len(data.get('data', []))}")
                print(f"  Sample: {json.dumps(data, indent=2, ensure_ascii=False)[:300]}")
                
                with open('data/qwen-messages-sample.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"  Saved to: data/qwen-messages-sample.json")
                break
            else:
                print(f"  Response: {data}")
        else:
            print(f"  Failed")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    print()

print("Done!")
