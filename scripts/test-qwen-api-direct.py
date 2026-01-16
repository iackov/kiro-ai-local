#!/usr/bin/env python3
"""
Test Qwen API directly - send a message and get response
"""
import sys
from pathlib import Path

# Add qwen path
qwen_path = Path(r"C:\Users\Jack\source\kiro\qwen\src\mcp_server")
sys.path.insert(0, str(qwen_path))

print("=== Testing Qwen API Direct ===")
print()

try:
    # Import QwenChatClient from qwen_client
    print("[1/3] Importing Qwen client...")
    from qwen_client import QwenChatClient
    print("  OK Imported")
    print()
    
    # Initialize client
    print("[2/3] Initializing Qwen client...")
    client = QwenChatClient(
        config_path=str(qwen_path / "qwen_config.json")
    )
    print(f"  OK Client initialized")
    print(f"  Base URL: {client.base_url}")
    print(f"  Default model: {client.default_model}")
    print()
    
    # Send test message
    print("[3/3] Sending test message to Qwen...")
    print("  Message: 'Hello! Please respond with just OK if you can read this.'")
    print()
    
    # Create new chat
    chat_id = client.create_chat(title="API Test", model="qwen3-coder-plus")
    print(f"  Chat created: {chat_id}")
    
    # Send message
    response_text = ""
    for chunk in client.send_message("Hello! Please respond with just OK if you can read this."):
        response_text += chunk
        print(chunk, end='', flush=True)
    
    print()
    print()
    print("=== SUCCESS! ===")
    print(f"Qwen API is working!")
    print(f"Response length: {len(response_text)} chars")
    print()
    print("This means:")
    print("  ✓ Cookies are valid")
    print("  ✓ API connection works")
    print("  ✓ Qwen MCP can communicate with Qwen")
    print()
    
    # Clean up - delete test chat
    try:
        client.delete_chat()
        print("Test chat deleted")
    except:
        pass
    
except Exception as e:
    print()
    print("=== FAILED ===")
    print(f"Error: {e}")
    print()
    print("This means:")
    print("  ✗ Cookies may be expired")
    print("  ✗ Or API connection issue")
    print()
    print("To fix:")
    print("  .\\scripts\\refresh-qwen-cookies.ps1")
    sys.exit(1)
