"""
Tree-of-Thought Engine
Генерирует несколько веток решений, отбирает успешные, скрывает неудачные
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


@dataclass
class ThoughtBranch:
    """Ветка размышлений"""
    branch_id: str
    parent_id: Optional[str]
    step: str
    reasoning: str
    confidence: float
    status: str = "pending"  # pending, success, failed
    result: Optional[Dict] = None
    children: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ThoughtTree:
    """Дерево размышлений"""
    tree_id: str
    root_task: str
    branches: Dict[str, ThoughtBranch] = field(default_factory=dict)
    successful_path: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())


class TreeOfThoughtEngine:
    """
    Движок Tree-of-Thought с отбором успешных веток
    
    Философия: Модель видит только успешные решения, неудачные ветки
    отбрасываются до того, как попадут в контекст следующего шага.
    """
    
    def __init__(self):
        self.trees: Dict[str, ThoughtTree] = {}
        self.branch_width = 3  # Сколько веток генерировать на каждом шаге
        self.max_depth = 5  # Максимальная глубина дерева
        
    async def generate_branches(
        self,
        task: str,
        parent_branch: Optional[ThoughtBranch] = None,
        context: Dict = None
    ) -> List[ThoughtBranch]:
        """
        Генерирует несколько веток решений для задачи
        
        Args:
            task: Задача для решения
            parent_branch: Родительская ветка (если есть)
            context: Контекст выполнения
            
        Returns:
            Список веток с разными подходами
        """
        branches = []
        
        # Генерируем несколько вариантов следующего шага
        strategies = [
            "direct",      # Прямое решение
            "analytical",  # Аналитический подход
            "creative"     # Креативный подход
        ]
        
        for i, strategy in enumerate(strategies[:self.branch_width]):
            branch_id = f"branch_{datetime.now().timestamp()}_{i}"
            
            # Генерируем шаг в зависимости от стратегии
            step, reasoning = self._generate_step(task, strategy, context)
            
            branch = ThoughtBranch(
                branch_id=branch_id,
                parent_id=parent_branch.branch_id if parent_branch else None,
                step=step,
                reasoning=reasoning,
                confidence=0.7 + (i * 0.1)  # Разная уверенность
            )
            
            branches.append(branch)
        
        return branches
    
    def _generate_step(self, task: str, strategy: str, context: Dict) -> tuple:
        """Генерирует шаг решения по стратегии"""
        if strategy == "direct":
            step = f"Выполнить задачу напрямую: {task}"
            reasoning = "Прямой подход - самый быстрый путь к решению"
        elif strategy == "analytical":
            step = f"Проанализировать задачу и разбить на подзадачи: {task}"
            reasoning = "Аналитический подход - снижает риск ошибок"
        else:  # creative
            step = f"Найти альтернативное решение для: {task}"
            reasoning = "Креативный подход - может найти неочевидные решения"
        
        return step, reasoning
    
    async def evaluate_branch(
        self,
        branch: ThoughtBranch,
        execution_engine,
        context: Dict
    ) -> bool:
        """
        Оценивает успешность ветки через выполнение
        
        Args:
            branch: Ветка для оценки
            execution_engine: Движок выполнения
            context: Контекст
            
        Returns:
            True если ветка успешна
        """
        try:
            # Выполняем шаг ветки
            result = await execution_engine.execute_task(
                [branch.step],
                context
            )
            
            # Проверяем успешность
            if result and len(result) > 0:
                step_result = result[0]
                success = step_result.get("status") in ["success", "completed"]
                
                branch.status = "success" if success else "failed"
                branch.result = step_result
                
                return success
            
            branch.status = "failed"
            return False
            
        except Exception as e:
            print(f"✗ Branch evaluation failed: {e}")
            branch.status = "failed"
            return False
    
    async def select_best_branch(
        self,
        branches: List[ThoughtBranch]
    ) -> Optional[ThoughtBranch]:
        """
        Выбирает лучшую ветку из успешных
        
        Args:
            branches: Список веток для выбора
            
        Returns:
            Лучшая успешная ветка или None
        """
        # Фильтруем только успешные
        successful = [b for b in branches if b.status == "success"]
        
        if not successful:
            return None
        
        # Выбираем с наибольшей уверенностью
        best = max(successful, key=lambda b: b.confidence)
        return best
    
    async def solve_with_tree(
        self,
        task: str,
        execution_engine,
        context: Dict = None
    ) -> Dict:
        """
        Решает задачу используя Tree-of-Thought
        
        Процесс:
        1. Генерирует несколько веток решений
        2. Оценивает каждую ветку
        3. Выбирает лучшую успешную
        4. Повторяет для следующего шага
        5. Возвращает только успешный путь (неудачи скрыты)
        
        Args:
            task: Задача для решения
            execution_engine: Движок выполнения
            context: Контекст выполнения
            
        Returns:
            Результат с успешным путем решения
        """
        import uuid
        tree_id = str(uuid.uuid4())
        tree = ThoughtTree(tree_id=tree_id, root_task=task)
        self.trees[tree_id] = tree
        
        context = context or {}
        current_branch = None
        depth = 0
        
        print(f"🌳 Starting Tree-of-Thought for: {task}")
        
        while depth < self.max_depth:
            # Генерируем ветки
            branches = await self.generate_branches(task, current_branch, context)
            print(f"  📊 Generated {len(branches)} branches at depth {depth}")
            
            # Сохраняем в дерево
            for branch in branches:
                tree.branches[branch.branch_id] = branch
                if current_branch:
                    current_branch.children.append(branch.branch_id)
            
            # Оцениваем ветки параллельно
            eval_tasks = [
                self.evaluate_branch(branch, execution_engine, context)
                for branch in branches
            ]
            await asyncio.gather(*eval_tasks)
            
            # Выбираем лучшую успешную ветку
            best_branch = await self.select_best_branch(branches)
            
            if not best_branch:
                print(f"  ✗ No successful branches at depth {depth}")
                break
            
            print(f"  ✓ Selected best branch: {best_branch.step[:50]}...")
            
            # Добавляем в успешный путь
            tree.successful_path.append(best_branch.branch_id)
            current_branch = best_branch
            
            # Проверяем завершение задачи
            if self._is_task_complete(best_branch, task):
                print(f"  🎯 Task completed at depth {depth}")
                break
            
            depth += 1
        
        # Формируем результат - ТОЛЬКО успешный путь
        successful_steps = [
            tree.branches[bid].step
            for bid in tree.successful_path
        ]
        
        successful_results = [
            tree.branches[bid].result
            for bid in tree.successful_path
            if tree.branches[bid].result
        ]
        
        # Статистика (для анализа, но не для модели)
        total_branches = len(tree.branches)
        successful_branches = len(tree.successful_path)
        failed_branches = total_branches - successful_branches
        
        return {
            "tree_id": tree_id,
            "task": task,
            "status": "completed" if tree.successful_path else "failed",
            "successful_path": successful_steps,
            "results": successful_results,
            "depth": len(tree.successful_path),
            "stats": {
                "total_branches_explored": total_branches,
                "successful_branches": successful_branches,
                "failed_branches": failed_branches,
                "efficiency": successful_branches / max(total_branches, 1)
            }
        }
    
    def _is_task_complete(self, branch: ThoughtBranch, original_task: str) -> bool:
        """Проверяет завершена ли задача"""
        # Простая эвристика - если результат есть и успешен
        if branch.result and branch.status == "success":
            # Можно добавить более сложную логику проверки
            return True
        return False
    
    def get_successful_context(self, tree_id: str) -> str:
        """
        Возвращает контекст ТОЛЬКО с успешными шагами
        
        Это то, что видит модель - чистая история успеха без ошибок
        """
        tree = self.trees.get(tree_id)
        if not tree:
            return ""
        
        context_parts = [f"Задача: {tree.root_task}\n"]
        context_parts.append("История успешных решений:")
        
        for i, branch_id in enumerate(tree.successful_path, 1):
            branch = tree.branches[branch_id]
            context_parts.append(f"{i}. {branch.step}")
            context_parts.append(f"   Результат: успех ✓")
        
        return "\n".join(context_parts)
    
    def get_tree_stats(self, tree_id: str) -> Dict:
        """Получить статистику дерева (для анализа системы)"""
        tree = self.trees.get(tree_id)
        if not tree:
            return {}
        
        total = len(tree.branches)
        successful = len([b for b in tree.branches.values() if b.status == "success"])
        failed = len([b for b in tree.branches.values() if b.status == "failed"])
        
        return {
            "tree_id": tree_id,
            "task": tree.root_task,
            "total_branches": total,
            "successful_branches": successful,
            "failed_branches": failed,
            "success_rate": successful / max(total, 1),
            "path_length": len(tree.successful_path),
            "created_at": tree.created_at
        }
    
    def get_stats(self) -> Dict:
        """Общая статистика всех деревьев"""
        total_trees = len(self.trees)
        total_branches = sum(len(t.branches) for t in self.trees.values())
        total_successful = sum(
            len([b for b in t.branches.values() if b.status == "success"])
            for t in self.trees.values()
        )
        
        return {
            "total_trees": total_trees,
            "total_branches_explored": total_branches,
            "total_successful_branches": total_successful,
            "average_success_rate": total_successful / max(total_branches, 1),
            "average_branches_per_tree": total_branches / max(total_trees, 1)
        }


# Global tree-of-thought engine
tree_of_thought = TreeOfThoughtEngine()
