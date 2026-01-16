"""
Knowledge Graph for reasoning and concept linking
"""
from typing import Dict, List, Set
from collections import defaultdict
import re

class KnowledgeGraph:
    """Simple knowledge graph for concept relationships"""
    
    def __init__(self):
        self.nodes: Dict[str, Dict] = {}  # concept -> metadata
        self.edges: Dict[str, Set[str]] = defaultdict(set)  # concept -> related concepts
        self.edge_types: Dict[tuple, str] = {}  # (from, to) -> relationship type
        
        # Initialize with domain knowledge
        self._initialize_domain_knowledge()
    
    def _initialize_domain_knowledge(self):
        """Initialize with Docker/DevOps domain knowledge"""
        # Core concepts
        concepts = {
            "docker": {"type": "technology", "category": "containerization"},
            "docker-compose": {"type": "tool", "category": "orchestration"},
            "service": {"type": "concept", "category": "architecture"},
            "container": {"type": "concept", "category": "infrastructure"},
            "volume": {"type": "concept", "category": "storage"},
            "network": {"type": "concept", "category": "networking"},
            "image": {"type": "concept", "category": "packaging"},
            "port": {"type": "concept", "category": "networking"},
            "environment": {"type": "concept", "category": "configuration"},
            "memory": {"type": "resource", "category": "hardware"},
            "cpu": {"type": "resource", "category": "hardware"},
            "health-check": {"type": "feature", "category": "monitoring"},
            "restart-policy": {"type": "feature", "category": "resilience"},
            "scaling": {"type": "operation", "category": "performance"},
            "logging": {"type": "feature", "category": "observability"},
        }
        
        for concept, metadata in concepts.items():
            self.add_node(concept, metadata)
        
        # Relationships
        relationships = [
            ("docker-compose", "service", "manages"),
            ("service", "container", "runs_in"),
            ("container", "image", "based_on"),
            ("service", "port", "exposes"),
            ("service", "volume", "mounts"),
            ("service", "network", "connects_to"),
            ("service", "environment", "configures"),
            ("service", "memory", "requires"),
            ("service", "cpu", "requires"),
            ("service", "health-check", "monitors_with"),
            ("service", "restart-policy", "uses"),
            ("service", "scaling", "supports"),
            ("service", "logging", "produces"),
        ]
        
        for from_node, to_node, rel_type in relationships:
            self.add_edge(from_node, to_node, rel_type)
    
    def add_node(self, concept: str, metadata: Dict = None):
        """Add a concept node"""
        self.nodes[concept] = metadata or {}
    
    def add_edge(self, from_concept: str, to_concept: str, relationship: str = "related_to"):
        """Add relationship between concepts"""
        self.edges[from_concept].add(to_concept)
        self.edge_types[(from_concept, to_concept)] = relationship
    
    def get_related_concepts(self, concept: str, depth: int = 1) -> List[Dict]:
        """Get related concepts up to specified depth"""
        if concept not in self.nodes:
            return []
        
        related = []
        visited = set()
        queue = [(concept, 0)]
        
        while queue:
            current, current_depth = queue.pop(0)
            
            if current in visited or current_depth > depth:
                continue
            
            visited.add(current)
            
            if current != concept:  # Don't include the query concept itself
                rel_type = self.edge_types.get((concept, current), "related_to")
                related.append({
                    "concept": current,
                    "relationship": rel_type,
                    "depth": current_depth,
                    "metadata": self.nodes.get(current, {})
                })
            
            # Add neighbors to queue
            for neighbor in self.edges.get(current, []):
                if neighbor not in visited:
                    queue.append((neighbor, current_depth + 1))
        
        return related
    
    def find_path(self, from_concept: str, to_concept: str) -> List[str]:
        """Find shortest path between two concepts"""
        if from_concept not in self.nodes or to_concept not in self.nodes:
            return []
        
        queue = [(from_concept, [from_concept])]
        visited = set()
        
        while queue:
            current, path = queue.pop(0)
            
            if current == to_concept:
                return path
            
            if current in visited:
                continue
            
            visited.add(current)
            
            for neighbor in self.edges.get(current, []):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        return []
    
    def reason_about_query(self, query: str) -> Dict:
        """Reason about a query using the knowledge graph"""
        # Extract concepts from query
        query_lower = query.lower()
        found_concepts = []
        
        for concept in self.nodes.keys():
            if concept in query_lower or concept.replace("-", " ") in query_lower:
                found_concepts.append(concept)
        
        if not found_concepts:
            return {"concepts": [], "reasoning": "No known concepts found in query"}
        
        # Get related concepts
        all_related = {}
        for concept in found_concepts:
            related = self.get_related_concepts(concept, depth=2)
            all_related[concept] = related
        
        # Generate reasoning
        reasoning_parts = []
        for concept in found_concepts:
            related = all_related[concept]
            if related:
                related_names = [r["concept"] for r in related[:3]]
                reasoning_parts.append(
                    f"{concept} is related to {', '.join(related_names)}"
                )
        
        # Find connections between concepts
        connections = []
        if len(found_concepts) > 1:
            for i, c1 in enumerate(found_concepts):
                for c2 in found_concepts[i+1:]:
                    path = self.find_path(c1, c2)
                    if path:
                        connections.append({
                            "from": c1,
                            "to": c2,
                            "path": path
                        })
        
        return {
            "concepts": found_concepts,
            "related_concepts": all_related,
            "connections": connections,
            "reasoning": ". ".join(reasoning_parts) if reasoning_parts else "Concepts identified",
            "suggestions": self._generate_suggestions(found_concepts, all_related)
        }
    
    def _generate_suggestions(self, concepts: List[str], related: Dict) -> List[str]:
        """Generate suggestions based on concepts"""
        suggestions = []
        
        # If asking about service, suggest related topics
        if "service" in concepts:
            suggestions.append("Consider checking service health-check configuration")
            suggestions.append("Review service restart-policy for resilience")
        
        if "docker-compose" in concepts:
            suggestions.append("Ensure all services are properly networked")
            suggestions.append("Check volume mounts for data persistence")
        
        if "memory" in concepts or "cpu" in concepts:
            suggestions.append("Monitor resource usage with metrics")
            suggestions.append("Consider scaling if resources are constrained")
        
        return suggestions

# Global knowledge graph instance
knowledge_graph = KnowledgeGraph()
