"""
Git Manager - version control for architecture changes
"""
import os
import git
from datetime import datetime
from typing import Dict, List
import shutil

class GitManager:
    """
    Manage Git-backed versioning of architecture changes
    """
    
    def __init__(self, repo_path="/host", history_path="/host/.arch-history"):
        self.repo_path = repo_path
        self.history_path = history_path
        self.states_path = os.path.join(history_path, "states")
        self.diffs_path = os.path.join(history_path, "diffs")
        
        # Initialize history directory
        os.makedirs(self.states_path, exist_ok=True)
        os.makedirs(self.diffs_path, exist_ok=True)
        
        # Initialize git repo if needed
        try:
            self.repo = git.Repo(repo_path)
        except git.InvalidGitRepositoryError:
            self.repo = git.Repo.init(repo_path)
    
    def commit_change(self, prompt: str, change_id: str) -> str:
        """
        Commit architecture change to git
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rollback_id = f"{timestamp}_{change_id[:8]}"
        
        # Save current state
        state_file = os.path.join(self.states_path, f"{rollback_id}.yml")
        compose_file = os.path.join(self.repo_path, "docker-compose.yml")
        shutil.copy(compose_file, state_file)
        
        # Git commit (with error handling)
        try:
            # Initialize repo if needed
            try:
                self.repo = git.Repo(self.repo_path)
            except git.InvalidGitRepositoryError:
                self.repo = git.Repo.init(self.repo_path)
            
            # Configure git if needed
            try:
                self.repo.config_writer().set_value("user", "name", "arch-engine").release()
                self.repo.config_writer().set_value("user", "email", "arch-engine@local").release()
            except:
                pass
            
            # Add and commit
            self.repo.index.add(["docker-compose.yml"])
            self.repo.index.add([".arch-history/"])
            commit_message = f"[arch-engine] {prompt}\n\nChange ID: {change_id}\nRollback ID: {rollback_id}"
            self.repo.index.commit(commit_message)
            
            # Create tag
            tag_name = f"arch-{rollback_id}"
            try:
                self.repo.create_tag(tag_name, message=prompt)
            except:
                pass  # Tag might already exist
            
            return rollback_id
        except Exception as e:
            # If git fails, still return rollback_id (state file is saved)
            print(f"Warning: Git commit failed: {str(e)}")
            return rollback_id
    
    def rollback(self, rollback_id: str) -> Dict:
        """
        Rollback to a previous architecture state
        """
        state_file = os.path.join(self.states_path, f"{rollback_id}.yml")
        
        if not os.path.exists(state_file):
            raise FileNotFoundError(f"Rollback state '{rollback_id}' not found")
        
        # Restore state
        compose_file = os.path.join(self.repo_path, "docker-compose.yml")
        shutil.copy(state_file, compose_file)
        
        # Git commit rollback
        try:
            self.repo.index.add(["docker-compose.yml"])
            commit_message = f"[arch-engine] Rollback to {rollback_id}"
            self.repo.index.commit(commit_message)
            
            return {
                "status": "success",
                "state": rollback_id,
                "file": state_file
            }
        except Exception as e:
            raise Exception(f"Git rollback failed: {str(e)}")
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """
        Get history of architecture changes
        """
        history = []
        
        try:
            commits = list(self.repo.iter_commits(max_count=limit))
            
            for commit in commits:
                # Only include arch-engine commits
                if "[arch-engine]" in commit.message:
                    history.append({
                        "sha": commit.hexsha[:8],
                        "message": commit.message.split("\n")[0].replace("[arch-engine] ", ""),
                        "timestamp": datetime.fromtimestamp(commit.committed_date).isoformat(),
                        "author": str(commit.author)
                    })
            
            return history
        except Exception as e:
            return []
    
    def get_current_state(self) -> str:
        """
        Get current git commit SHA
        """
        try:
            return self.repo.head.commit.hexsha[:8]
        except:
            return "unknown"
