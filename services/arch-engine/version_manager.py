"""
Version Manager
Maintains versioned history of architecture states
"""
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import structlog

logger = structlog.get_logger()


class VersionManager:
    """Manage architecture versions"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.versions_dir = self.workspace_path / ".arch-versions"
        self.versions_dir.mkdir(exist_ok=True)
        
        self.manifest_file = self.versions_dir / "manifest.json"
        self._load_manifest()
    
    def _load_manifest(self):
        """Load version manifest"""
        if self.manifest_file.exists():
            with open(self.manifest_file, 'r') as f:
                self.manifest = json.load(f)
        else:
            self.manifest = {"versions": []}
    
    def _save_manifest(self):
        """Save version manifest"""
        with open(self.manifest_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    async def save_version(self, description: str) -> str:
        """Save current architecture as a version"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        version_id = f"v-{timestamp}"
        
        version_dir = self.versions_dir / version_id
        version_dir.mkdir(exist_ok=True)
        
        # Copy docker-compose.yml
        compose_file = self.workspace_path / "docker-compose.yml"
        if compose_file.exists():
            shutil.copy(compose_file, version_dir / "docker-compose.yml")
        
        # Copy config directory
        config_dir = self.workspace_path / "config"
        if config_dir.exists():
            shutil.copytree(config_dir, version_dir / "config", dirs_exist_ok=True)
        
        # Add to manifest
        version_entry = {
            "id": version_id,
            "timestamp": timestamp,
            "description": description,
            "created_at": datetime.now().isoformat()
        }
        
        self.manifest["versions"].append(version_entry)
        self._save_manifest()
        
        logger.info("version_saved", version_id=version_id, description=description)
        
        return version_id
    
    async def list_versions(self) -> List[Dict[str, Any]]:
        """List all versions"""
        return self.manifest["versions"]
    
    async def rollback(self, version_id: str):
        """Rollback to a specific version"""
        version_dir = self.versions_dir / version_id
        
        if not version_dir.exists():
            raise ValueError(f"Version {version_id} not found")
        
        # Restore docker-compose.yml
        compose_backup = version_dir / "docker-compose.yml"
        if compose_backup.exists():
            shutil.copy(compose_backup, self.workspace_path / "docker-compose.yml")
        
        # Restore config
        config_backup = version_dir / "config"
        if config_backup.exists():
            config_target = self.workspace_path / "config"
            if config_target.exists():
                shutil.rmtree(config_target)
            shutil.copytree(config_backup, config_target)
        
        logger.info("version_restored", version_id=version_id)
