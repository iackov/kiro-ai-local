"""
Self-Modification Engine - System can modify its own code
FINAL LEVEL OF AUTONOMY: System improves itself
"""
import os
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

class SelfModification:
    def __init__(self):
        self.modification_history = []
        self.backup_dir = Path("/app/backups")
        self.backup_dir.mkdir(exist_ok=True)
        
        # Безопасные зоны для модификации
        self.safe_modification_zones = [
            "services/web-ui/adaptive_planner.py",
            "services/web-ui/decision_engine.py",
            "services/web-ui/autonomous_optimizer.py",
            "services/web-ui/proactive_engine.py",
            "services/web-ui/knowledge_store.py",
            "services/web-ui/model_router.py"
        ]
        
        # Критичные файлы, которые нельзя трогать
        self.protected_files = [
            "services/web-ui/main.py",
            "docker-compose.yml",
            "Dockerfile"
        ]
    
    def can_modify(self, file_path: str) -> Dict:
        """Проверить, можно ли модифицировать файл"""
        path = Path(file_path)
        
        # Проверка 1: Файл существует
        if not path.exists():
            return {
                "allowed": False,
                "reason": "File does not exist"
            }
        
        # Проверка 2: Не защищенный файл
        if any(protected in str(path) for protected in self.protected_files):
            return {
                "allowed": False,
                "reason": "File is protected from modification"
            }
        
        # Проверка 3: В безопасной зоне
        if not any(safe in str(path) for safe in self.safe_modification_zones):
            return {
                "allowed": False,
                "reason": "File is not in safe modification zone"
            }
        
        return {
            "allowed": True,
            "reason": "File can be safely modified"
        }
    
    def create_backup(self, file_path: str) -> Dict:
        """Создать резервную копию файла"""
        try:
            path = Path(file_path)
            if not path.exists():
                return {"success": False, "error": "File not found"}
            
            # Генерируем имя бэкапа
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{path.name}.backup.{timestamp}"
            backup_path = self.backup_dir / backup_name
            
            # Копируем файл
            shutil.copy2(path, backup_path)
            
            # Сохраняем хэш для проверки целостности
            with open(path, 'rb') as f:
                file_hash = hashlib.sha256(f.read()).hexdigest()
            
            return {
                "success": True,
                "backup_path": str(backup_path),
                "original_hash": file_hash,
                "timestamp": timestamp
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def propose_modification(self, file_path: str, modification_type: str, description: str) -> Dict:
        """Предложить модификацию"""
        # Проверка возможности модификации
        can_modify = self.can_modify(file_path)
        if not can_modify["allowed"]:
            return {
                "approved": False,
                "reason": can_modify["reason"]
            }
        
        # Создаем бэкап
        backup = self.create_backup(file_path)
        if not backup["success"]:
            return {
                "approved": False,
                "reason": f"Backup failed: {backup['error']}"
            }
        
        # Анализ риска
        risk_level = self._assess_risk(file_path, modification_type)
        
        proposal = {
            "file_path": file_path,
            "modification_type": modification_type,
            "description": description,
            "risk_level": risk_level,
            "backup_path": backup["backup_path"],
            "timestamp": datetime.now().isoformat(),
            "approved": risk_level in ["low", "medium"],
            "requires_confirmation": risk_level == "high"
        }
        
        return proposal
    
    def _assess_risk(self, file_path: str, modification_type: str) -> str:
        """Оценить риск модификации"""
        # Низкий риск: добавление новых функций
        if modification_type in ["add_function", "add_method", "add_parameter"]:
            return "low"
        
        # Средний риск: изменение логики
        if modification_type in ["modify_logic", "optimize_code", "refactor"]:
            return "medium"
        
        # Высокий риск: удаление или критичные изменения
        if modification_type in ["delete_function", "change_api", "modify_core"]:
            return "high"
        
        return "medium"
    
    async def apply_modification(self, file_path: str, new_content: str, proposal: Dict) -> Dict:
        """Применить модификацию"""
        try:
            # Проверка proposal
            if not proposal.get("approved"):
                return {
                    "success": False,
                    "error": "Modification not approved"
                }
            
            # Записываем новый контент
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            # Проверяем синтаксис (для Python файлов)
            if file_path.endswith('.py'):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), file_path, 'exec')
                except SyntaxError as e:
                    # Откатываем изменения
                    self.rollback(proposal["backup_path"], file_path)
                    return {
                        "success": False,
                        "error": f"Syntax error: {e}",
                        "rolled_back": True
                    }
            
            # Сохраняем в историю
            modification_record = {
                **proposal,
                "applied_at": datetime.now().isoformat(),
                "new_hash": self._get_file_hash(file_path),
                "status": "applied"
            }
            self.modification_history.append(modification_record)
            
            return {
                "success": True,
                "modification_id": len(self.modification_history) - 1,
                "backup_path": proposal["backup_path"],
                "message": "Modification applied successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def rollback(self, backup_path: str, original_path: str) -> Dict:
        """Откатить модификацию"""
        try:
            if not Path(backup_path).exists():
                return {"success": False, "error": "Backup not found"}
            
            shutil.copy2(backup_path, original_path)
            
            return {
                "success": True,
                "message": f"Rolled back to {backup_path}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _get_file_hash(self, file_path: str) -> str:
        """Получить хэш файла"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return ""
    
    def get_modification_history(self, limit: int = 10) -> List[Dict]:
        """Получить историю модификаций"""
        return self.modification_history[-limit:]
    
    def get_stats(self) -> Dict:
        """Статистика самомодификации"""
        total = len(self.modification_history)
        successful = len([m for m in self.modification_history if m.get("status") == "applied"])
        
        risk_distribution = {}
        for mod in self.modification_history:
            risk = mod.get("risk_level", "unknown")
            risk_distribution[risk] = risk_distribution.get(risk, 0) + 1
        
        return {
            "total_modifications": total,
            "successful": successful,
            "success_rate": (successful / total * 100) if total > 0 else 0,
            "risk_distribution": risk_distribution,
            "safe_zones": len(self.safe_modification_zones),
            "protected_files": len(self.protected_files)
        }
    
    async def autonomous_self_improvement(self, analysis: Dict, http_client) -> Dict:
        """Автономное самоулучшение на основе анализа"""
        improvements = []
        
        # Анализ 1: Если много ошибок в decision_engine
        if analysis.get("decision_errors", 0) > 10:
            proposal = self.propose_modification(
                "services/web-ui/decision_engine.py",
                "optimize_code",
                "Optimize decision making to reduce errors"
            )
            if proposal.get("approved"):
                improvements.append({
                    "type": "decision_optimization",
                    "proposal": proposal,
                    "reason": "High error rate in decision engine"
                })
        
        # Анализ 2: Если низкая производительность
        if analysis.get("avg_latency", 0) > 2000:
            proposal = self.propose_modification(
                "services/web-ui/model_router.py",
                "optimize_code",
                "Optimize model routing for better performance"
            )
            if proposal.get("approved"):
                improvements.append({
                    "type": "performance_optimization",
                    "proposal": proposal,
                    "reason": "High latency detected"
                })
        
        return {
            "improvements_proposed": len(improvements),
            "improvements": improvements,
            "auto_applied": 0,  # Требуют подтверждения
            "message": "Self-improvement proposals created"
        }

# Global self-modification engine
self_modification = SelfModification()
