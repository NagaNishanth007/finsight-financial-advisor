from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EmotionType(str, Enum):
    ANXIETY = "anxiety"
    EXCITEMENT = "excitement"
    FEAR = "fear"
    CONFIDENCE = "confidence"
    CONFUSION = "confusion"
    FRUSTRATION = "frustration"
    NEUTRAL = "neutral"


class IntentType(str, Enum):
    BUDGETING = "budgeting"
    INVESTING = "investing"
    SAVING = "saving"
    DEBT_MANAGEMENT = "debt_management"
    FINANCIAL_PLANNING = "financial_planning"
    EMOTIONAL_SUPPORT = "emotional_support"
    GENERAL = "general"


class EmotionDetection(BaseModel):
    emotion: EmotionType
    confidence: float
    intensity: float = Field(ge=0.0, le=1.0)


class IntentDetection(BaseModel):
    intent: IntentType
    confidence: float
    sub_intents: List[str] = []


class FinancialContext(BaseModel):
    mentioned_amounts: List[float] = []
    time_references: List[str] = []
    financial_products: List[str] = []
    goals_mentioned: List[str] = []


class ChatMessage(BaseModel):
    role: str  # user, assistant, system
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    emotion: Optional[EmotionDetection] = None
    intent: Optional[IntentDetection] = None


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    user_context: Optional[Dict[str, Any]] = {}


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    detected_emotion: Optional[EmotionDetection] = None
    detected_intent: Optional[IntentDetection] = None
    rag_sources: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationHistory(BaseModel):
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
