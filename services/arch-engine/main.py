"""
Self-Architecture Modification Engine
Accepts natural language prompts and modifies Docker Compose architecture
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import yaml
import os
from datetime import datetime
import hashlib

from parsers.intent import IntentParser
from generators.compose import ComposeGenerator
from validators.safety import SafetyValidator
from versioning.git_manager import GitManager

app = FastAPI(
    title="Architecture Engine",
    description="Self-modifying AI infrastructure orchestrator",
    version="1.0.0"
)

# Initialize components
intent_parser = IntentParser()
compose_generator = ComposeGenerator()
safety_validator = SafetyValidator()
git_manager = GitManager()

# Models
class ArchitectureProposal(BaseModel):
    prompt: str
    auto_apply: bool = False

class ArchitectureChange(BaseModel):
    change_id: str
    confirm: bool

class RollbackRequest(BaseModel):
    rollback_id: str

# In-memory store for pending changes (in production, use Redis)
pending_changes = {}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "arch-engine"}

@app.post("/arch/propose")
async def propose_architecture_change(proposal: ArchitectureProposal):
    """
    Parse natural language prompt and generate Docker Compose patch
    """
    try:
        # Parse intent
        intent = intent_parser.parse(proposal.prompt)
        
        # Generate Docker Compose changes
        compose_patch = compose_generator.generate(intent)
        
        # Validate safety
        safety_check = safety_validator.validate(compose_patch)
        
        if not safety_check["safe"]:
            raise HTTPException(
                status_code=400,
                detail=f"Safety check failed: {safety_check['reason']}"
            )
        
        # Generate change ID
        change_id = hashlib.sha256(
            f"{proposal.prompt}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]
        
        # Store pending change
        pending_changes[change_id] = {
            "prompt": proposal.prompt,
            "intent": intent,
            "patch": compose_patch,
            "timestamp": datetime.now().isoformat()
        }
        
        # Auto-apply if requested
        if proposal.auto_apply:
            result = await apply_architecture_change(
                ArchitectureChange(change_id=change_id, confirm=True)
            )
            return result
        
        return {
            "change_id": change_id,
            "intent": intent,
            "diff": compose_patch["diff"],
            "preview": compose_patch["preview"],
            "safe": True,
            "safety_checks": safety_check["checks"],
            "message": "Review the changes and call /arch/apply to confirm"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/arch/apply")
async def apply_architecture_change(change: ArchitectureChange):
    """
    Apply confirmed architecture change
    """
    if change.change_id not in pending_changes:
        raise HTTPException(status_code=404, detail="Change ID not found")
    
    if not change.confirm:
        raise HTTPException(status_code=400, detail="Confirmation required")
    
    try:
        pending = pending_changes[change.change_id]
        
        # Apply Docker Compose patch
        compose_generator.apply_patch(pending["patch"])
        
        # Commit to git
        rollback_id = git_manager.commit_change(
            prompt=pending["prompt"],
            change_id=change.change_id
        )
        
        # Remove from pending
        del pending_changes[change.change_id]
        
        return {
            "status": "applied",
            "change_id": change.change_id,
            "rollback_id": rollback_id,
            "message": "Architecture updated successfully",
            "next_steps": [
                "Run: docker compose down",
                "Run: docker compose up -d",
                "Verify: docker compose ps"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Apply failed: {str(e)}")

@app.post("/arch/rollback")
async def rollback_architecture(rollback: RollbackRequest):
    """
    Rollback to previous architecture state
    """
    try:
        result = git_manager.rollback(rollback.rollback_id)
        
        return {
            "status": "rolled_back",
            "rollback_id": rollback.rollback_id,
            "restored_state": result["state"],
            "message": "Architecture rolled back successfully",
            "next_steps": [
                "Run: docker compose down",
                "Run: docker compose up -d"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")

@app.get("/arch/history")
async def get_architecture_history():
    """
    Get history of architecture changes
    """
    try:
        history = git_manager.get_history()
        return {
            "total": len(history),
            "changes": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/arch/pending")
async def get_pending_changes():
    """
    Get list of pending (not yet applied) changes
    """
    return {
        "total": len(pending_changes),
        "pending": [
            {
                "change_id": cid,
                "prompt": data["prompt"],
                "timestamp": data["timestamp"]
            }
            for cid, data in pending_changes.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
