"""
Intent Parser - converts natural language to structured intent
"""
import re
from typing import Dict, List, Optional

class IntentParser:
    """
    Parse natural language prompts into structured intents
    
    Examples:
    - "Add Redis cache service" → {action: "add", type: "service", name: "redis"}
    - "Remove Grafana" → {action: "remove", type: "service", name: "grafana"}
    - "Change Ollama memory to 16GB" → {action: "modify", type: "resource", service: "ollama", resource: "memory", value: "16G"}
    """
    
    def __init__(self):
        self.patterns = {
            "add_service": [
                r"add\s+(?:a\s+)?(\w+)\s+(?:cache\s+)?(?:service|container)",
                r"add\s+(\w+)",
                r"create\s+(?:a\s+)?(\w+)\s+(?:service|container)",
                r"deploy\s+(?:a\s+)?(\w+)",
            ],
            "remove_service": [
                r"remove\s+(?:the\s+)?(\w+)\s+(?:service|container)?",
                r"delete\s+(?:the\s+)?(\w+)\s+(?:service|container)?",
                r"stop\s+(?:the\s+)?(\w+)\s+(?:service|container)?",
            ],
            "modify_resource": [
                r"change\s+(\w+)\s+(\w+)\s+to\s+(\S+)",
                r"set\s+(\w+)\s+(\w+)\s+to\s+(\S+)",
                r"update\s+(\w+)\s+(\w+)\s+to\s+(\S+)",
            ],
            "add_volume": [
                r"add\s+volume\s+(\S+)\s+to\s+(\w+)",
                r"mount\s+(\S+)\s+(?:to|in)\s+(\w+)",
            ],
            "change_port": [
                r"change\s+(\w+)\s+port\s+(?:to\s+)?(\d+)",
                r"expose\s+(\w+)\s+on\s+port\s+(\d+)",
            ]
        }
        
        # Known service templates
        self.service_templates = {
            "redis": {
                "image": "redis:7-alpine",
                "ports": ["6379:6379"],
                "type": "cache"
            },
            "reranker": {
                "image": "ghcr.io/bge-reranker-v2-mini:latest",
                "ports": ["9003:8003"],
                "type": "ml"
            },
            "postgres": {
                "image": "postgres:16-alpine",
                "ports": ["5432:5432"],
                "type": "database"
            },
            "nginx": {
                "image": "nginx:alpine",
                "ports": ["80:80"],
                "type": "proxy"
            }
        }
    
    def parse(self, prompt: str) -> Dict:
        """
        Parse natural language prompt into structured intent
        """
        prompt_lower = prompt.lower().strip()
        
        # Try to match patterns
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, prompt_lower, re.IGNORECASE)
                if match:
                    return self._build_intent(intent_type, match, prompt)
        
        # Fallback: generic intent
        return {
            "action": "unknown",
            "prompt": prompt,
            "message": "Could not parse intent. Please be more specific."
        }
    
    def _build_intent(self, intent_type: str, match: re.Match, original_prompt: str) -> Dict:
        """
        Build structured intent from regex match
        """
        if intent_type == "add_service":
            service_name = match.group(1).lower()
            template = self.service_templates.get(service_name, {})
            
            return {
                "action": "add",
                "type": "service",
                "service_name": service_name,
                "template": template,
                "prompt": original_prompt
            }
        
        elif intent_type == "remove_service":
            service_name = match.group(1).lower()
            
            return {
                "action": "remove",
                "type": "service",
                "service_name": service_name,
                "prompt": original_prompt
            }
        
        elif intent_type == "modify_resource":
            service_name = match.group(1).lower()
            resource_type = match.group(2).lower()
            new_value = match.group(3)
            
            return {
                "action": "modify",
                "type": "resource",
                "service_name": service_name,
                "resource_type": resource_type,
                "new_value": new_value,
                "prompt": original_prompt
            }
        
        elif intent_type == "add_volume":
            volume_path = match.group(1)
            service_name = match.group(2).lower()
            
            return {
                "action": "add",
                "type": "volume",
                "service_name": service_name,
                "volume_path": volume_path,
                "prompt": original_prompt
            }
        
        elif intent_type == "change_port":
            service_name = match.group(1).lower()
            new_port = match.group(2)
            
            return {
                "action": "modify",
                "type": "port",
                "service_name": service_name,
                "new_port": new_port,
                "prompt": original_prompt
            }
        
        return {
            "action": "unknown",
            "prompt": original_prompt
        }
