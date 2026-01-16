"""
Natural Language Intent Parser
Parses user prompts into structured architecture modifications
"""
import re
from typing import Dict, Any, List
import structlog

logger = structlog.get_logger()


class ArchitectureParser:
    """Parse natural language into architecture intents"""
    
    def __init__(self):
        self.patterns = {
            "add_service": [
                r"add\s+(?:a\s+)?(.+?)\s+(?:service|container|component)",
                r"create\s+(?:a\s+)?(.+?)\s+(?:service|container)",
                r"deploy\s+(?:a\s+)?(.+)",
            ],
            "remove_service": [
                r"remove\s+(.+?)\s+(?:service|container)",
                r"delete\s+(.+?)\s+(?:service|container)",
                r"stop\s+(.+?)\s+(?:service|container)",
            ],
            "modify_service": [
                r"modify\s+(.+?)\s+to\s+(.+)",
                r"change\s+(.+?)\s+to\s+(.+)",
                r"update\s+(.+?)\s+(?:with|to)\s+(.+)",
            ],
            "scale_service": [
                r"scale\s+(.+?)\s+to\s+(\d+)",
                r"increase\s+(.+?)\s+(?:to|by)\s+(\d+)",
            ],
            "switch_component": [
                r"switch\s+(?:vector\s+)?(?:db|database)\s+to\s+(.+)",
                r"use\s+(.+?)\s+instead\s+of\s+(.+)",
                r"replace\s+(.+?)\s+with\s+(.+)",
            ]
        }
        
        # Component mappings
        self.component_map = {
            "reranker": {
                "image": "ghcr.io/huggingface/text-embeddings-inference:latest",
                "model": "BAAI/bge-reranker-v2-m3",
                "type": "reranker"
            },
            "qdrant": {
                "image": "qdrant/qdrant:latest",
                "port": 6333,
                "type": "vector_db"
            },
            "lancedb": {
                "image": "lancedb/lancedb:latest",
                "port": 8000,
                "type": "vector_db"
            },
            "redis": {
                "image": "redis:7-alpine",
                "port": 6379,
                "type": "cache"
            }
        }
    
    async def parse_intent(self, prompt: str) -> Dict[str, Any]:
        """Parse user prompt into structured intent"""
        prompt_lower = prompt.lower()
        
        # Try each pattern category
        for intent_type, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, prompt_lower, re.IGNORECASE)
                if match:
                    return await self._build_intent(intent_type, match, prompt)
        
        # Fallback: generic modification
        return {
            "type": "unknown",
            "description": prompt,
            "raw_prompt": prompt,
            "confidence": 0.3
        }
    
    async def _build_intent(self, intent_type: str, match: re.Match, prompt: str) -> Dict[str, Any]:
        """Build structured intent from regex match"""
        
        if intent_type == "add_service":
            component_name = match.group(1).strip()
            component_info = self._resolve_component(component_name)
            
            return {
                "type": "add_service",
                "description": f"Add {component_name} service",
                "component": component_name,
                "config": component_info,
                "raw_prompt": prompt,
                "confidence": 0.9
            }
        
        elif intent_type == "remove_service":
            service_name = match.group(1).strip()
            return {
                "type": "remove_service",
                "description": f"Remove {service_name} service",
                "service": service_name,
                "raw_prompt": prompt,
                "confidence": 0.9
            }
        
        elif intent_type == "switch_component":
            if len(match.groups()) == 1:
                new_component = match.group(1).strip()
                old_component = None
            else:
                old_component = match.group(1).strip()
                new_component = match.group(2).strip()
            
            component_info = self._resolve_component(new_component)
            
            return {
                "type": "switch_component",
                "description": f"Switch to {new_component}",
                "old_component": old_component,
                "new_component": new_component,
                "config": component_info,
                "raw_prompt": prompt,
                "confidence": 0.85
            }
        
        elif intent_type == "scale_service":
            service_name = match.group(1).strip()
            replicas = int(match.group(2))
            
            return {
                "type": "scale_service",
                "description": f"Scale {service_name} to {replicas} replicas",
                "service": service_name,
                "replicas": replicas,
                "raw_prompt": prompt,
                "confidence": 0.9
            }
        
        return {
            "type": intent_type,
            "description": prompt,
            "raw_prompt": prompt,
            "confidence": 0.7
        }
    
    def _resolve_component(self, component_name: str) -> Dict[str, Any]:
        """Resolve component name to configuration"""
        component_lower = component_name.lower()
        
        # Check known components
        for key, config in self.component_map.items():
            if key in component_lower:
                return config
        
        # Generic component
        return {
            "image": f"{component_name}:latest",
            "type": "generic"
        }
