"""
Health Monitor with Auto-Recovery
Monitors system health and triggers auto-recovery on failures
"""
import asyncio
import time
from typing import Dict, List
from datetime import datetime
import subprocess
import os

class HealthMonitor:
    """Monitors system health and triggers recovery"""
    
    def __init__(self):
        self.health_history = []
        self.failure_count = 0
        self.last_recovery = None
        self.recovery_actions = []
        
    def record_health(self, health_score: int, status: str):
        """Record health check result"""
        self.health_history.append({
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "status": status
        })
        
        # Keep only last 100
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
        
        # Track failures
        if health_score < 50 or status != "healthy":
            self.failure_count += 1
        else:
            self.failure_count = 0
    
    def should_trigger_recovery(self) -> bool:
        """Check if auto-recovery should be triggered"""
        # Trigger if 3 consecutive failures
        if self.failure_count >= 3:
            return True
        
        # Trigger if health dropped significantly
        if len(self.health_history) >= 5:
            recent = [h["health_score"] for h in self.health_history[-5:]]
            if all(score < 60 for score in recent):
                return True
        
        return False
    
    def trigger_recovery(self, reason: str) -> Dict:
        """Trigger automatic recovery"""
        recovery_action = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "actions_taken": []
        }
        
        # Action 1: Try to restore from latest backup
        try:
            # Find latest backup
            backup_dir = "services/web-ui"
            backups = [f for f in os.listdir(backup_dir) if f.startswith("main.py.backup.")]
            
            if backups:
                latest_backup = sorted(backups)[-1]
                backup_path = os.path.join(backup_dir, latest_backup)
                
                # Restore
                import shutil
                shutil.copy(backup_path, os.path.join(backup_dir, "main.py"))
                
                recovery_action["actions_taken"].append({
                    "action": "restore_code",
                    "backup": latest_backup,
                    "status": "success"
                })
        except Exception as e:
            recovery_action["actions_taken"].append({
                "action": "restore_code",
                "status": "failed",
                "error": str(e)
            })
        
        # Action 2: Restart service
        try:
            subprocess.run(["docker", "compose", "restart", "web-ui"], 
                         capture_output=True, timeout=30)
            recovery_action["actions_taken"].append({
                "action": "restart_service",
                "status": "success"
            })
        except Exception as e:
            recovery_action["actions_taken"].append({
                "action": "restart_service",
                "status": "failed",
                "error": str(e)
            })
        
        self.recovery_actions.append(recovery_action)
        self.last_recovery = datetime.now().isoformat()
        self.failure_count = 0
        
        return recovery_action
    
    def get_status(self) -> Dict:
        """Get monitor status"""
        return {
            "health_history_count": len(self.health_history),
            "failure_count": self.failure_count,
            "last_recovery": self.last_recovery,
            "recovery_actions_count": len(self.recovery_actions),
            "should_recover": self.should_trigger_recovery()
        }

# Global health monitor
health_monitor = HealthMonitor()
