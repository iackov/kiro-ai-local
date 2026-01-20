#!/usr/bin/env python3
"""
Try to get chats list using QwenChatClient directly
"""
import sys
import json
import requests
from pathlib import Path

# Add qwen path
qwen_path = Path(r"C:\Users\Jack\source\kiro\qwen\src\mcp_server")
sys.path.insert(0, str(qwen_path))

from qwen_client import QwenChatClient

print("=== Getting Qwen Chats via Client ===")
print()

try:
    # Initialize client
    client = QwenChatClient(config_path=str(qwen_path / "qwen_config.json"))
    print(f"Client initialized")
    print(f"Base URL: {client.base_url}")
    print()
    
    # Try different endpoints with client's headers
    endpoints = [
        "/api/v2/chats",
        "/api/v2/chats/list", 
        "/api/v2/user/chats",
        "/api/v2/conversations",
        "/api/chats"
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
                    print(f"  Data: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")
                    
                    # Save
                    with open('data/qwen-chats-success.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print(f"  Saved to: data/qwen-chats-success.json")
                    break
                else:
                    print(f"  Response: {data}")
            else:
                print(f"  Failed: {response.text[:200]}")
                
        except Exception as e:
            print(f"  Error: {e}")
        
        print()
    
    print("Done!")
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
