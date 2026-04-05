import redis
import json
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.core.config import get_settings
from app.models.schemas import ChatMessage, EmotionDetection, IntentDetection, ConversationHistory
import logging

logger = logging.getLogger(__name__)


class MemoryService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        settings = get_settings()
        
        try:
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)
            self.redis.ping()
            logger.info("Memory service connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available, using in-memory fallback: {e}")
            self.redis = None
            self._memory_fallback = {}
        
        self._initialized = True
    
    def _get_key(self, conversation_id: str) -> str:
        return f"conversation:{conversation_id}"
    
    def create_conversation(self) -> str:
        """Create a new conversation and return its ID"""
        conversation_id = str(uuid.uuid4())
        data = {
            "conversation_id": conversation_id,
            "messages": [],
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "user_context": {}
        }
        
        if self.redis:
            self.redis.setex(
                self._get_key(conversation_id),
                86400 * 7,  # 7 days TTL
                json.dumps(data)
            )
        else:
            self._memory_fallback[conversation_id] = data
        
        return conversation_id
    
    def get_history(self, conversation_id: str) -> Optional[ConversationHistory]:
        """Get conversation history"""
        try:
            if self.redis:
                data = self.redis.get(self._get_key(conversation_id))
                if not data:
                    return None
                data = json.loads(data)
            else:
                data = self._memory_fallback.get(conversation_id)
                if not data:
                    return None
            
            messages = []
            for msg in data.get("messages", []):
                message = ChatMessage(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=datetime.fromisoformat(msg["timestamp"])
                )
                if msg.get("emotion"):
                    message.emotion = EmotionDetection(**msg["emotion"])
                if msg.get("intent"):
                    message.intent = IntentDetection(**msg["intent"])
                messages.append(message)
            
            return ConversationHistory(
                conversation_id=conversation_id,
                messages=messages,
                created_at=datetime.fromisoformat(data["created_at"]),
                updated_at=datetime.fromisoformat(data["updated_at"])
            )
            
        except Exception as e:
            logger.error(f"Error retrieving history: {e}")
            return None
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        emotion: Optional[EmotionDetection] = None,
        intent: Optional[IntentDetection] = None
    ):
        """Add a message to conversation history"""
        try:
            # Get existing data
            if self.redis:
                data_str = self.redis.get(self._get_key(conversation_id))
                data = json.loads(data_str) if data_str else {
                    "conversation_id": conversation_id,
                    "messages": [],
                    "created_at": datetime.utcnow().isoformat(),
                    "user_context": {}
                }
            else:
                data = self._memory_fallback.get(conversation_id, {
                    "conversation_id": conversation_id,
                    "messages": [],
                    "created_at": datetime.utcnow().isoformat(),
                    "user_context": {}
                })
            
            # Add message
            message_data = {
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat()
            }
            if emotion:
                message_data["emotion"] = emotion.model_dump()
            if intent:
                message_data["intent"] = intent.model_dump()
            
            data["messages"].append(message_data)
            data["updated_at"] = datetime.utcnow().isoformat()
            
            # Keep last 20 messages to manage context window
            if len(data["messages"]) > 20:
                data["messages"] = data["messages"][-20:]
            
            # Save
            if self.redis:
                self.redis.setex(
                    self._get_key(conversation_id),
                    86400 * 7,
                    json.dumps(data)
                )
            else:
                self._memory_fallback[conversation_id] = data
                
        except Exception as e:
            logger.error(f"Error saving message: {e}")
    
    def get_formatted_history(self, conversation_id: str, last_n: int = 10) -> str:
        """Get formatted conversation history for LLM context"""
        history = self.get_history(conversation_id)
        if not history or not history.messages:
            return ""
        
        messages = history.messages[-last_n:]
        formatted = []
        for msg in messages:
            prefix = "User" if msg.role == "user" else "Assistant"
            formatted.append(f"{prefix}: {msg.content}")
        
        return "\n".join(formatted)


memory_service = MemoryService()
