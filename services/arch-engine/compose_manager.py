"""
Docker Compose Manager
Generates and applies changes to docker-compose.yml
"""
import yaml
import os
from typing import Dict, Any, List
from pathlib import Path
import structlog
from datetime import datetime

logger = structlog.get_logger()


class ComposeManager:
    """Manage docker-compose.yml modifications"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.compose_file = self.workspace_path / "docker-compose.yml"
    
    async def generate_changes(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate changes based on intent"""
        changes = []
        
        intent_type = intent.get("type")
        
        if intent_type == "add_service":
            changes.append(await self._generate_add_service(intent))
        
        elif intent_type == "remove_service":
            changes.append(await self._generate_remove_service(intent))
        
        elif intent_type == "switch_component":
            changes.extend(await self._generate_switch_component(intent))
        
        elif intent_type == "scale_service":
            changes.append(await self._generate_scale_service(intent))
        
        return changes
    
    async def _generate_add_service(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service addition"""
        component = intent["component"]
        config = intent["config"]
        
        service_name = component.replace(" ", "-").lower()
        
        service_def = {
            "image": config.get("image", f"{component}:latest"),
            "container_name": f"ai-{service_name}",
            "networks": ["ai-local-net"],
            "restart": "unless-stopped",
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "1",
                        "memory": "1G"
                    }
                }
            }
        }
        
        # Add port if specified
        if "port" in config:
            service_def["ports"] = [f"{config['port']}:{config['port']}"]
        
        # Add model for reranker
        if config.get("type") == "reranker":
            service_def["environment"] = [
                f"MODEL_ID={config.get('model', 'BAAI/bge-reranker-v2-m3')}"
            ]
        
        return {
            "action": "add_service",
            "service_name": service_name,
            "definition": service_def
        }
    
    async def _generate_remove_service(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service removal"""
        service_name = intent["service"].replace(" ", "-").lower()
        
        return {
            "action": "remove_service",
            "service_name": service_name
        }
    
    async def _generate_switch_component(self, intent: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate component switch (remove old, add new)"""
        changes = []
        
        if intent.get("old_component"):
            changes.append({
                "action": "remove_service",
                "service_name": intent["old_component"].replace(" ", "-").lower()
            })
        
        # Add new component
        add_intent = {
            "component": intent["new_component"],
            "config": intent["config"]
        }
        changes.append(await self._generate_add_service(add_intent))
        
        return changes
    
    async def _generate_scale_service(self, intent: Dict[str, Any]) -> Dict[str, Any]:
        """Generate service scaling"""
        return {
            "action": "scale_service",
            "service_name": intent["service"].replace(" ", "-").lower(),
            "replicas": intent["replicas"]
        }
    
    async def create_diff(self, changes: List[Dict[str, Any]]) -> str:
        """Create human-readable diff"""
        diff_lines = ["# Architecture Changes\n"]
        
        for change in changes:
            action = change["action"]
            
            if action == "add_service":
                diff_lines.append(f"+ Add service: {change['service_name']}")
                diff_lines.append(f"  Image: {change['definition']['image']}")
                
            elif action == "remove_service":
                diff_lines.append(f"- Remove service: {change['service_name']}")
                
            elif action == "scale_service":
                diff_lines.append(f"~ Scale service: {change['service_name']} to {change['replicas']} replicas")
        
        return "\n".join(diff_lines)
    
    async def apply_changes(self, changes: List[Dict[str, Any]]):
        """Apply changes to docker-compose.yml"""
        # Load current compose file
        with open(self.compose_file, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        # Apply each change
        for change in changes:
            action = change["action"]
            
            if action == "add_service":
                compose_data["services"][change["service_name"]] = change["definition"]
                logger.info("service_added", service=change["service_name"])
            
            elif action == "remove_service":
                if change["service_name"] in compose_data["services"]:
                    del compose_data["services"][change["service_name"]]
                    logger.info("service_removed", service=change["service_name"])
            
            elif action == "scale_service":
                service_name = change["service_name"]
                if service_name in compose_data["services"]:
                    if "deploy" not in compose_data["services"][service_name]:
                        compose_data["services"][service_name]["deploy"] = {}
                    compose_data["services"][service_name]["deploy"]["replicas"] = change["replicas"]
                    logger.info("service_scaled", service=service_name, replicas=change["replicas"])
        
        # Write back
        with open(self.compose_file, 'w') as f:
            yaml.dump(compose_data, f, default_flow_style=False, sort_keys=False)
        
        logger.info("compose_file_updated", file=str(self.compose_file))
    
    async def get_current_architecture(self) -> Dict[str, Any]:
        """Get current architecture state"""
        with open(self.compose_file, 'r') as f:
            compose_data = yaml.safe_load(f)
        
        services = []
        for name, config in compose_data.get("services", {}).items():
            services.append({
                "name": name,
                "image": config.get("image", "N/A"),
                "ports": config.get("ports", []),
                "status": "defined"
            })
        
        return {
            "services": services,
            "networks": list(compose_data.get("networks", {}).keys()),
            "volumes": list(compose_data.get("volumes", {}).keys())
        }
