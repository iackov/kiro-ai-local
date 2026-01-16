"""
Docker Compose Generator - creates and modifies docker-compose.yml
"""
import yaml
import os
from typing import Dict
from datetime import datetime

class ComposeGenerator:
    """
    Generate Docker Compose service definitions and patches
    """
    
    def __init__(self, compose_path="/host/docker-compose.yml"):
        self.compose_path = compose_path
    
    def generate(self, intent: Dict) -> Dict:
        """
        Generate Docker Compose patch based on intent
        """
        action = intent.get("action")
        
        if action == "add" and intent.get("type") == "service":
            return self._generate_add_service(intent)
        elif action == "remove" and intent.get("type") == "service":
            return self._generate_remove_service(intent)
        elif action == "modify" and intent.get("type") == "resource":
            return self._generate_modify_resource(intent)
        elif action == "modify" and intent.get("type") == "port":
            return self._generate_modify_port(intent)
        elif action == "add" and intent.get("type") == "volume":
            return self._generate_add_volume(intent)
        else:
            raise ValueError(f"Unsupported intent: {intent}")
    
    def _generate_add_service(self, intent: Dict) -> Dict:
        """
        Generate patch to add a new service
        """
        service_name = intent["service_name"]
        template = intent.get("template", {})
        
        # Build service definition
        service_def = {
            "image": template.get("image", f"{service_name}:latest"),
            "container_name": f"ai-{service_name}",
            "networks": ["ai-local-net"],
            "restart": "unless-stopped"
        }
        
        # Add ports if specified
        if "ports" in template:
            service_def["ports"] = template["ports"]
        
        # Add resource limits
        service_def["deploy"] = {
            "resources": {
                "limits": {
                    "cpus": "1",
                    "memory": "1G"
                }
            }
        }
        
        # Load current compose
        with open(self.compose_path, 'r') as f:
            compose = yaml.safe_load(f)
        
        # Check if service already exists
        if service_name in compose.get("services", {}):
            raise ValueError(f"Service '{service_name}' already exists")
        
        # Add service
        if "services" not in compose:
            compose["services"] = {}
        compose["services"][service_name] = service_def
        
        # Generate diff
        diff = self._generate_diff(service_name, None, service_def)
        
        return {
            "type": "add_service",
            "service_name": service_name,
            "definition": service_def,
            "compose": compose,
            "diff": diff,
            "preview": yaml.dump({service_name: service_def}, default_flow_style=False)
        }
    
    def _generate_remove_service(self, intent: Dict) -> Dict:
        """
        Generate patch to remove a service
        """
        service_name = intent["service_name"]
        
        # Load current compose
        with open(self.compose_path, 'r') as f:
            compose = yaml.safe_load(f)
        
        # Check if service exists
        if service_name not in compose.get("services", {}):
            raise ValueError(f"Service '{service_name}' not found")
        
        # Get old definition for diff
        old_def = compose["services"][service_name]
        
        # Remove service
        del compose["services"][service_name]
        
        # Generate diff
        diff = self._generate_diff(service_name, old_def, None)
        
        return {
            "type": "remove_service",
            "service_name": service_name,
            "compose": compose,
            "diff": diff,
            "preview": f"Service '{service_name}' will be removed"
        }
    
    def _generate_modify_resource(self, intent: Dict) -> Dict:
        """
        Generate patch to modify resource limits
        """
        service_name = intent["service_name"]
        resource_type = intent["resource_type"]
        new_value = intent["new_value"]
        
        # Load current compose
        with open(self.compose_path, 'r') as f:
            compose = yaml.safe_load(f)
        
        # Check if service exists
        if service_name not in compose.get("services", {}):
            raise ValueError(f"Service '{service_name}' not found")
        
        service = compose["services"][service_name]
        
        # Modify resource
        if "deploy" not in service:
            service["deploy"] = {"resources": {"limits": {}}}
        if "resources" not in service["deploy"]:
            service["deploy"]["resources"] = {"limits": {}}
        if "limits" not in service["deploy"]["resources"]:
            service["deploy"]["resources"]["limits"] = {}
        
        old_value = service["deploy"]["resources"]["limits"].get(resource_type, "not set")
        service["deploy"]["resources"]["limits"][resource_type] = new_value
        
        # Generate diff
        diff = f"- {service_name}.deploy.resources.limits.{resource_type}: {old_value}\n"
        diff += f"+ {service_name}.deploy.resources.limits.{resource_type}: {new_value}"
        
        return {
            "type": "modify_resource",
            "service_name": service_name,
            "resource_type": resource_type,
            "old_value": old_value,
            "new_value": new_value,
            "compose": compose,
            "diff": diff,
            "preview": f"{service_name}: {resource_type} {old_value} → {new_value}"
        }
    
    def _generate_modify_port(self, intent: Dict) -> Dict:
        """
        Generate patch to modify port mapping
        """
        service_name = intent["service_name"]
        new_port = intent["new_port"]
        
        # Load current compose
        with open(self.compose_path, 'r') as f:
            compose = yaml.safe_load(f)
        
        # Check if service exists
        if service_name not in compose.get("services", {}):
            raise ValueError(f"Service '{service_name}' not found")
        
        service = compose["services"][service_name]
        old_ports = service.get("ports", [])
        
        # Modify first port mapping
        if old_ports:
            old_port = old_ports[0].split(":")[0]
            container_port = old_ports[0].split(":")[1]
            service["ports"][0] = f"{new_port}:{container_port}"
        else:
            service["ports"] = [f"{new_port}:{new_port}"]
            old_port = "not set"
        
        diff = f"- {service_name}.ports: {old_port}\n"
        diff += f"+ {service_name}.ports: {new_port}"
        
        return {
            "type": "modify_port",
            "service_name": service_name,
            "old_port": old_port,
            "new_port": new_port,
            "compose": compose,
            "diff": diff,
            "preview": f"{service_name}: port {old_port} → {new_port}"
        }
    
    def _generate_add_volume(self, intent: Dict) -> Dict:
        """
        Generate patch to add volume mount
        """
        service_name = intent["service_name"]
        volume_path = intent["volume_path"]
        
        # Load current compose
        with open(self.compose_path, 'r') as f:
            compose = yaml.safe_load(f)
        
        # Check if service exists
        if service_name not in compose.get("services", {}):
            raise ValueError(f"Service '{service_name}' not found")
        
        service = compose["services"][service_name]
        
        # Add volume
        if "volumes" not in service:
            service["volumes"] = []
        service["volumes"].append(volume_path)
        
        diff = f"+ {service_name}.volumes: {volume_path}"
        
        return {
            "type": "add_volume",
            "service_name": service_name,
            "volume_path": volume_path,
            "compose": compose,
            "diff": diff,
            "preview": f"{service_name}: added volume {volume_path}"
        }
    
    def _generate_diff(self, service_name: str, old_def, new_def) -> str:
        """
        Generate human-readable diff
        """
        if old_def is None:
            return f"+ Added service: {service_name}\n" + yaml.dump({service_name: new_def}, default_flow_style=False)
        elif new_def is None:
            return f"- Removed service: {service_name}\n" + yaml.dump({service_name: old_def}, default_flow_style=False)
        else:
            return f"~ Modified service: {service_name}"
    
    def apply_patch(self, patch: Dict):
        """
        Apply generated patch to docker-compose.yml
        """
        compose = patch["compose"]
        
        # Backup current file
        backup_path = f"{self.compose_path}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.rename(self.compose_path, backup_path)
        
        try:
            # Write new compose file
            with open(self.compose_path, 'w') as f:
                yaml.dump(compose, f, default_flow_style=False, sort_keys=False)
            
            return {"status": "applied", "backup": backup_path}
        except Exception as e:
            # Restore backup on error
            os.rename(backup_path, self.compose_path)
            raise e
