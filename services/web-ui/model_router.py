"""
Model Router - Intelligent routing between local and external models
"""
import httpx
from typing import Dict, Optional, List
from datetime import datetime
import os

class ModelRouter:
    def __init__(self):
        self.local_ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.external_qwen_url = os.getenv("QWEN_API_URL", "")
        self.external_qwen_key = os.getenv("QWEN_API_KEY", "")
        
        # Статистика использования
        self.usage_stats = {
            "local": {"calls": 0, "total_time": 0, "errors": 0},
            "external": {"calls": 0, "total_time": 0, "errors": 0}
        }
        
        # Кэш для частых запросов
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
    
    def should_use_external(self, prompt: str, context: Dict = None) -> bool:
        """Определить, использовать ли внешнюю модель"""
        if not self.external_qwen_url:
            return False
        
        # Критерии для использования внешней модели:
        
        # 1. Сложные задачи (длинный промпт)
        if len(prompt) > 500:
            return True
        
        # 2. Критичные операции
        if context and context.get("priority") == "high":
            return True
        
        # 3. Если локальная модель часто ошибается
        local_error_rate = self.usage_stats["local"]["errors"] / max(self.usage_stats["local"]["calls"], 1)
        if local_error_rate > 0.3:  # > 30% ошибок
            return True
        
        # 4. Ключевые слова сложности
        complex_keywords = ["refactor", "optimize", "architecture", "design pattern", "security"]
        if any(keyword in prompt.lower() for keyword in complex_keywords):
            return True
        
        return False
    
    async def generate(self, prompt: str, context: Dict = None, http_client: httpx.AsyncClient = None) -> Dict:
        """Генерация с автоматическим выбором модели"""
        import time
        
        # Проверка кэша
        cache_key = self._get_cache_key(prompt)
        if cache_key in self.cache:
            self.cache_hits += 1
            print(f"✓ Cache hit for prompt (total hits: {self.cache_hits})")
            return self.cache[cache_key]
        
        self.cache_misses += 1
        
        # Выбор модели
        use_external = self.should_use_external(prompt, context)
        model_type = "external" if use_external else "local"
        
        print(f"🤖 Using {model_type} model for generation")
        
        start_time = time.time()
        
        try:
            if use_external:
                result = await self._generate_external(prompt, http_client)
            else:
                result = await self._generate_local(prompt, http_client)
            
            duration = time.time() - start_time
            self.usage_stats[model_type]["calls"] += 1
            self.usage_stats[model_type]["total_time"] += duration
            
            # Кэшируем успешный результат
            if result.get("success"):
                self.cache[cache_key] = result
                # Ограничиваем размер кэша
                if len(self.cache) > 100:
                    # Удаляем самый старый
                    self.cache.pop(next(iter(self.cache)))
            
            return result
            
        except Exception as e:
            self.usage_stats[model_type]["errors"] += 1
            print(f"✗ {model_type} model error: {e}")
            
            # Fallback на другую модель
            if use_external and self.local_ollama_url:
                print("🔄 Falling back to local model")
                return await self._generate_local(prompt, http_client)
            
            return {
                "success": False,
                "error": str(e),
                "model": model_type
            }
    
    async def _generate_local(self, prompt: str, http_client: httpx.AsyncClient) -> Dict:
        """Генерация через локальную Ollama"""
        if not http_client:
            http_client = httpx.AsyncClient()
        
        response = await http_client.post(
            f"{self.local_ollama_url}/api/generate",
            json={
                "model": "qwen2.5-coder:7b",
                "prompt": prompt,
                "stream": False
            },
            timeout=60.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "content": data.get("response", ""),
                "model": "local_ollama",
                "model_name": "qwen2.5-coder:7b"
            }
        
        return {
            "success": False,
            "error": f"Status {response.status_code}",
            "model": "local_ollama"
        }
    
    async def _generate_external(self, prompt: str, http_client: httpx.AsyncClient) -> Dict:
        """Генерация через внешний Qwen API"""
        if not http_client:
            http_client = httpx.AsyncClient()
        
        headers = {}
        if self.external_qwen_key:
            headers["Authorization"] = f"Bearer {self.external_qwen_key}"
        
        response = await http_client.post(
            self.external_qwen_url,
            json={
                "model": "qwen-coder-plus",
                "prompt": prompt,
                "max_tokens": 2000
            },
            headers=headers,
            timeout=30.0
        )
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "content": data.get("response", data.get("content", "")),
                "model": "external_qwen",
                "model_name": "qwen-coder-plus"
            }
        
        return {
            "success": False,
            "error": f"Status {response.status_code}",
            "model": "external_qwen"
        }
    
    def _get_cache_key(self, prompt: str) -> str:
        """Генерация ключа кэша"""
        import hashlib
        return hashlib.md5(prompt.encode()).hexdigest()
    
    def get_stats(self) -> Dict:
        """Статистика использования моделей"""
        stats = {}
        
        for model_type, data in self.usage_stats.items():
            calls = data["calls"]
            if calls > 0:
                avg_time = data["total_time"] / calls
                error_rate = data["errors"] / calls * 100
            else:
                avg_time = 0
                error_rate = 0
            
            stats[model_type] = {
                "calls": calls,
                "avg_time": round(avg_time, 2),
                "error_rate": round(error_rate, 1),
                "total_errors": data["errors"]
            }
        
        stats["cache"] = {
            "hits": self.cache_hits,
            "misses": self.cache_misses,
            "hit_rate": round(self.cache_hits / max(self.cache_hits + self.cache_misses, 1) * 100, 1),
            "size": len(self.cache)
        }
        
        return stats
    
    def clear_cache(self):
        """Очистить кэш"""
        self.cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0

# Global model router
model_router = ModelRouter()
