"""
Conversation Manager - Natural Language Interface
"""
from typing import Dict, List, Optional
from datetime import datetime
import uuid

class ConversationSession:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now().isoformat()
        self.messages = []
        self.context = {}
        self.last_activity = datetime.now().isoformat()
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.last_activity = datetime.now().isoformat()
    
    def get_context_window(self, max_messages: int = 10) -> List[Dict]:
        return self.messages[-max_messages:]
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "created_at": self.created_at,
            "last_activity": self.last_activity,
            "message_count": len(self.messages),
            "context": self.context
        }

class ConversationManager:
    def __init__(self):
        self.sessions: Dict[str, ConversationSession] = {}
        self.intent_patterns = {
            "query": ["what", "how", "why", "explain", "tell me"],
            "execute": ["do", "run", "execute", "perform", "create"],
            "analyze": ["analyze", "check", "inspect", "review"],
            "modify": ["change", "update", "modify", "add", "remove"]
        }
    
    def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ConversationSession(session_id)
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        return self.sessions.get(session_id)
    
    def detect_intent(self, message: str) -> str:
        """Advanced intent detection with context awareness"""
        message_lower = message.lower()
        
        # Priority 1: Action verbs (execute)
        action_verbs = ["check", "test", "run", "execute", "perform", "start", "stop", 
                       "restart", "deploy", "rollback", "apply", "fix", "debug"]
        if any(verb in message_lower for verb in action_verbs):
            return "execute"
        
        # Priority 2: Creation/Modification
        creation_verbs = ["add", "create", "build", "setup", "configure", "install",
                         "update", "modify", "change", "remove", "delete"]
        if any(verb in message_lower for verb in creation_verbs):
            return "modify"
        
        # Priority 3: Analysis
        analysis_verbs = ["analyze", "inspect", "review", "investigate", "examine",
                         "diagnose", "profile", "measure"]
        if any(verb in message_lower for verb in analysis_verbs):
            return "analyze"
        
        # Priority 4: Information queries
        query_words = ["what", "how", "why", "when", "where", "who", "explain",
                      "tell me", "show me", "list", "get", "find"]
        if any(word in message_lower for word in query_words):
            return "query"
        
        # Default: treat as query
        return "query"
    
    def extract_entities(self, message: str) -> Dict:
        """Extract key entities from message"""
        message_lower = message.lower()
        entities = {
            "services": [],
            "actions": [],
            "metrics": [],
            "technologies": []
        }
        
        # Services
        services = ["rag", "ollama", "arch", "redis", "postgres", "mongodb", "nginx"]
        entities["services"] = [s for s in services if s in message_lower]
        
        # Actions
        actions = ["optimize", "scale", "monitor", "backup", "restore", "migrate"]
        entities["actions"] = [a for a in actions if a in message_lower]
        
        # Metrics
        metrics = ["latency", "throughput", "memory", "cpu", "disk", "network"]
        entities["metrics"] = [m for m in metrics if m in message_lower]
        
        # Technologies
        tech = ["docker", "kubernetes", "python", "fastapi", "flask"]
        entities["technologies"] = [t for t in tech if t in message_lower]
        
        return entities
    
    def build_prompt(self, session: ConversationSession, user_message: str, 
                     rag_context: List[Dict] = None) -> str:
        system_prompt = """You are an autonomous AI system with 9 capabilities. Be concise and technical."""
        
        context_section = ""
        if rag_context:
            context_section = "\n\nContext:\n"
            for doc in rag_context[:2]:
                context_section += f"{doc.get('content', '')[:200]}...\n"
        
        history_section = ""
        recent = session.get_context_window(max_messages=3)
        if recent:
            history_section = "\n\nHistory:\n"
            for msg in recent[-2:]:
                history_section += f"{msg['role']}: {msg['content'][:100]}\n"
        
        return f"{system_prompt}{context_section}{history_section}\n\nUser: {user_message}\n\nAssistant:"

# Global conversation manager
conversation_manager = ConversationManager()
