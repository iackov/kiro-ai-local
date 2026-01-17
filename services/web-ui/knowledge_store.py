"""
Knowledge Store - Automatic storage of execution results in RAG
"""
import httpx
from typing import Dict, List, Optional
from datetime import datetime
import json

class KnowledgeStore:
    def __init__(self, rag_url: str):
        self.rag_url = rag_url
        self.stored_count = 0
    
    async def store_execution_result(self, task_result: Dict, message: str, http_client: httpx.AsyncClient) -> bool:
        """Store execution result in RAG for future reference"""
        try:
            # Формируем документ для сохранения
            summary = task_result.get('summary', {})
            
            # Создаем читаемое описание выполнения
            content = f"""Задача: {message}
Дата выполнения: {datetime.now().isoformat()}
Task ID: {task_result.get('task_id')}

Результат:
- Статус: {summary.get('status', 'unknown')}
- Успешно выполнено: {summary.get('successful', 0)}/{summary.get('total_steps', 0)} шагов
- Success Rate: {summary.get('success_rate', 0)}%

Выполненные шаги:
"""
            
            for i, step in enumerate(task_result.get('result', []), 1):
                status = '✅' if step['status'] in ['success', 'completed'] else '❌'
                content += f"{i}. {status} {step['step']}\n"
                if step.get('result'):
                    content += f"   Результат: {step['result']}\n"
            
            # Добавляем метаданные
            metadata = {
                "type": "execution_result",
                "task_id": task_result.get('task_id'),
                "success_rate": summary.get('success_rate', 0),
                "timestamp": datetime.now().isoformat(),
                "intent": "create" if "создать" in message.lower() or "create" in message.lower() else "execute"
            }
            
            # Отправляем в RAG
            response = await http_client.post(
                f"{self.rag_url}/add",
                json={
                    "content": content,
                    "metadata": metadata
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                self.stored_count += 1
                print(f"✓ Execution result stored in RAG (total: {self.stored_count})")
                return True
            else:
                print(f"✗ Failed to store in RAG: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error storing execution result: {e}")
            return False
    
    async def store_learning_insight(self, insight: Dict, http_client: httpx.AsyncClient) -> bool:
        """Store learning insight in RAG"""
        try:
            content = f"""Обучающий инсайт
Дата: {datetime.now().isoformat()}
Тип: {insight.get('type', 'general')}

Описание: {insight.get('description', '')}

Рекомендации:
{insight.get('recommendations', '')}
"""
            
            metadata = {
                "type": "learning_insight",
                "insight_type": insight.get('type'),
                "timestamp": datetime.now().isoformat()
            }
            
            response = await http_client.post(
                f"{self.rag_url}/add",
                json={"content": content, "metadata": metadata},
                timeout=10.0
            )
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"✗ Error storing learning insight: {e}")
            return False
    
    async def query_similar_executions(self, query: str, http_client: httpx.AsyncClient, top_k: int = 3) -> List[Dict]:
        """Query similar past executions from RAG"""
        try:
            response = await http_client.post(
                f"{self.rag_url}/query",
                json={"query": query, "top_k": top_k},
                timeout=5.0
            )
            
            if response.status_code == 200:
                data = response.json()
                # Фильтруем только результаты выполнения
                executions = [
                    doc for doc in data.get('documents', [])
                    if doc.get('metadata', {}).get('type') == 'execution_result'
                ]
                return executions
            
            return []
            
        except Exception as e:
            print(f"✗ Error querying similar executions: {e}")
            return []
    
    def get_stats(self) -> Dict:
        """Get knowledge store statistics"""
        return {
            "stored_executions": self.stored_count,
            "status": "active"
        }

# Global knowledge store
knowledge_store = None

def init_knowledge_store(rag_url: str):
    """Initialize global knowledge store"""
    global knowledge_store
    knowledge_store = KnowledgeStore(rag_url)
    return knowledge_store
