"""
Code Generation Engine - Generate and execute code safely
Gives system ability to create new files and programs
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Any
import httpx

class CodeGenerator:
    # Safe zones where code can be created
    SAFE_ZONES = [
        'playground/',
        'generated/',
        'experiments/',
        'tic-tac-toe/',
        'demos/',
        'examples/'
    ]
    
    # Dangerous patterns that should never be in generated code
    DANGEROUS_PATTERNS = [
        'rm -rf',
        'del /f',
        'format c:',
        'DROP DATABASE',
        'DELETE FROM',
        '__import__("os").system',
        'eval(',
        'exec(',
        'subprocess.call',
    ]
    
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
    
    def is_safe_zone(self, path: str) -> bool:
        """Check if path is in a safe zone"""
        path_obj = Path(path)
        for safe_zone in self.SAFE_ZONES:
            if str(path_obj).startswith(safe_zone) or safe_zone in str(path_obj):
                return True
        return False
    
    def contains_dangerous_code(self, code: str) -> bool:
        """Check if code contains dangerous patterns"""
        code_lower = code.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern.lower() in code_lower:
                return True
        return False
    
    async def generate_code(self, prompt: str, language: str = "python") -> Dict[str, Any]:
        """Generate code using Ollama"""
        try:
            print(f"DEBUG generate_code: Starting generation for prompt: {prompt[:100]}...")
            # Увеличенный таймаут для генерации кода
            async with httpx.AsyncClient(timeout=180.0) as client:
                print(f"DEBUG generate_code: Calling Ollama at {self.ollama_url}")
                
                # Упрощённый промпт для быстрой генерации
                simple_prompt = f"Write a simple {language} {prompt.split('.')[0]}. Keep it minimal and functional."
                
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": "qwen2.5-coder:7b",
                        "prompt": simple_prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.7,
                            "num_predict": 500  # Ограничиваем длину для скорости
                        }
                    }
                )
                
                print(f"DEBUG generate_code: Ollama response status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    code = result.get("response", "")
                    print(f"DEBUG generate_code: Got code, length: {len(code)}")
                    
                    # Clean up code (remove markdown if present)
                    if "```" in code:
                        parts = code.split("```")
                        if len(parts) >= 2:
                            code = parts[1]
                            if code.startswith("python") or code.startswith("py"):
                                code = "\n".join(code.split("\n")[1:])
                    
                    return {
                        "success": True,
                        "code": code.strip(),
                        "language": language
                    }
                else:
                    error_msg = f"Ollama returned {response.status_code}"
                    print(f"DEBUG generate_code: ERROR - {error_msg}")
                    return {
                        "success": False,
                        "error": error_msg
                    }
        except Exception as e:
            error_msg = str(e)
            print(f"DEBUG generate_code: EXCEPTION - {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate generated code for safety"""
        issues = []
        
        # Check for dangerous patterns
        if self.contains_dangerous_code(code):
            issues.append("Contains dangerous patterns")
        
        # Check for basic syntax (Python only for now)
        if language == "python":
            try:
                compile(code, '<string>', 'exec')
            except SyntaxError as e:
                issues.append(f"Syntax error: {e}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def create_file(self, path: str, content: str) -> Dict[str, Any]:
        """Create a file in a safe zone"""
        # Check if path is safe
        if not self.is_safe_zone(path):
            return {
                "success": False,
                "error": f"Path '{path}' is not in a safe zone. Allowed: {self.SAFE_ZONES}"
            }
        
        try:
            # Create directory if needed
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "path": path,
                "size": len(content),
                "lines": len(content.split('\n'))
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_folder(self, path: str) -> Dict[str, Any]:
        """Create a folder in a safe zone"""
        # Check if path is safe
        if not self.is_safe_zone(path):
            return {
                "success": False,
                "error": f"Path '{path}' is not in a safe zone. Allowed: {self.SAFE_ZONES}"
            }
        
        try:
            # Create directory
            Path(path).mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "path": path,
                "message": f"Folder created: {path}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Execute code in a safe sandbox"""
        if language != "python":
            return {
                "success": False,
                "error": f"Execution not supported for {language}"
            }
        
        # Validate first
        validation = self.validate_code(code, language)
        if not validation["valid"]:
            return {
                "success": False,
                "error": f"Validation failed: {validation['issues']}"
            }
        
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute with timeout
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=10  # 10 second timeout
            )
            
            # Clean up
            os.unlink(temp_file)
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Execution timeout (10s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_and_run(self, prompt: str, save_path: str = None) -> Dict[str, Any]:
        """Generate code, optionally save it, and run it"""
        # Generate code
        gen_result = await self.generate_code(prompt)
        if not gen_result["success"]:
            return gen_result
        
        code = gen_result["code"]
        
        # Validate
        validation = self.validate_code(code, "python")
        if not validation["valid"]:
            return {
                "success": False,
                "error": f"Generated code failed validation: {validation['issues']}",
                "code": code
            }
        
        # Save if path provided
        if save_path:
            save_result = self.create_file(save_path, code)
            if not save_result["success"]:
                return save_result
        
        # Execute
        exec_result = self.execute_code(code)
        
        return {
            "success": exec_result["success"],
            "code": code,
            "saved_to": save_path if save_path else None,
            "output": exec_result.get("stdout", ""),
            "errors": exec_result.get("stderr", ""),
            "validation": validation
        }

# Global instance
code_generator = None
