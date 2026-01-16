"""
Safety Validator - ensures architecture changes are safe
"""
from typing import Dict, List

class SafetyValidator:
    """
    Validate Docker Compose changes for safety
    """
    
    def __init__(self):
        self.max_cpu = 8
        self.max_memory_gb = 16
        self.forbidden_volumes = [
            "/",
            "/etc",
            "/sys",
            "/proc",
            "/boot",
            "C:\\Windows",
            "C:\\Program Files"
        ]
        self.allowed_networks = ["ai-local-net", "bridge"]
    
    def validate(self, patch: Dict) -> Dict:
        """
        Run all safety checks on a patch
        """
        checks = []
        safe = True
        reason = None
        
        compose = patch.get("compose", {})
        service_name = patch.get("service_name")
        
        if service_name and service_name in compose.get("services", {}):
            service = compose["services"][service_name]
            
            # Check 1: No privileged containers
            check = self._check_no_privileged(service)
            checks.append(check)
            if not check["passed"]:
                safe = False
                reason = check["message"]
            
            # Check 2: Resource limits
            check = self._check_resource_limits(service)
            checks.append(check)
            if not check["passed"]:
                safe = False
                reason = check["message"]
            
            # Check 3: Network isolation
            check = self._check_network_isolation(service)
            checks.append(check)
            if not check["passed"]:
                safe = False
                reason = check["message"]
            
            # Check 4: Volume safety
            check = self._check_volume_safety(service)
            checks.append(check)
            if not check["passed"]:
                safe = False
                reason = check["message"]
            
            # Check 5: No host network
            check = self._check_no_host_network(service)
            checks.append(check)
            if not check["passed"]:
                safe = False
                reason = check["message"]
        
        return {
            "safe": safe,
            "reason": reason,
            "checks": checks
        }
    
    def _check_no_privileged(self, service: Dict) -> Dict:
        """
        Ensure container is not privileged
        """
        privileged = service.get("privileged", False)
        
        return {
            "name": "no_privileged",
            "passed": not privileged,
            "message": "Container must not run in privileged mode" if privileged else "OK"
        }
    
    def _check_resource_limits(self, service: Dict) -> Dict:
        """
        Ensure resource limits are set and reasonable
        """
        deploy = service.get("deploy", {})
        resources = deploy.get("resources", {})
        limits = resources.get("limits", {})
        
        # Check CPU limit
        cpu_limit = limits.get("cpus", "0")
        if isinstance(cpu_limit, str):
            cpu_limit = float(cpu_limit)
        
        if cpu_limit > self.max_cpu:
            return {
                "name": "resource_limits",
                "passed": False,
                "message": f"CPU limit {cpu_limit} exceeds maximum {self.max_cpu}"
            }
        
        # Check memory limit
        memory_limit = limits.get("memory", "0")
        if isinstance(memory_limit, str):
            # Parse memory string (e.g., "8G", "1024M")
            if memory_limit.endswith("G"):
                memory_gb = float(memory_limit[:-1])
            elif memory_limit.endswith("M"):
                memory_gb = float(memory_limit[:-1]) / 1024
            else:
                memory_gb = 0
            
            if memory_gb > self.max_memory_gb:
                return {
                    "name": "resource_limits",
                    "passed": False,
                    "message": f"Memory limit {memory_limit} exceeds maximum {self.max_memory_gb}G"
                }
        
        return {
            "name": "resource_limits",
            "passed": True,
            "message": "OK"
        }
    
    def _check_network_isolation(self, service: Dict) -> Dict:
        """
        Ensure service uses allowed networks
        """
        networks = service.get("networks", [])
        
        for network in networks:
            if network not in self.allowed_networks:
                return {
                    "name": "network_isolation",
                    "passed": False,
                    "message": f"Network '{network}' not in allowed list: {self.allowed_networks}"
                }
        
        return {
            "name": "network_isolation",
            "passed": True,
            "message": "OK"
        }
    
    def _check_volume_safety(self, service: Dict) -> Dict:
        """
        Ensure no dangerous volume mounts
        """
        volumes = service.get("volumes", [])
        
        for volume in volumes:
            # Parse volume string (e.g., "/host/path:/container/path")
            if ":" in volume:
                host_path = volume.split(":")[0]
                
                # Check against forbidden paths
                for forbidden in self.forbidden_volumes:
                    if host_path.startswith(forbidden):
                        return {
                            "name": "volume_safety",
                            "passed": False,
                            "message": f"Volume mount '{host_path}' is forbidden (system directory)"
                        }
        
        return {
            "name": "volume_safety",
            "passed": True,
            "message": "OK"
        }
    
    def _check_no_host_network(self, service: Dict) -> Dict:
        """
        Ensure service doesn't use host network mode
        """
        network_mode = service.get("network_mode", "")
        
        if network_mode == "host":
            return {
                "name": "no_host_network",
                "passed": False,
                "message": "Host network mode is forbidden"
            }
        
        return {
            "name": "no_host_network",
            "passed": True,
            "message": "OK"
        }
