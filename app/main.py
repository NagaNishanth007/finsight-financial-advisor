import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.models.schemas import ChatRequest, ChatResponse, ConversationHistory
from app.services.emotion_detector import emotion_detector
from app.services.intent_detector import intent_detector
from app.services.memory_service import memory_service
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("FinSight backend starting up...")
    
    # Warm up models
    try:
        _ = emotion_detector.detect("test")
        _ = intent_detector.detect("test")
        _ = rag_service.query("test")
        logger.info("Models warmed up successfully")
    except Exception as e:
        logger.warning(f"Model warmup issue (may be slow on first request): {e}")
    
    yield
    
    logger.info("FinSight backend shutting down...")


app = FastAPI(
    title="FinSight API",
    description="Conversational AI financial advisor with emotion awareness",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "emotion_detector": emotion_detector.classifier is not None,
            "intent_detector": intent_detector.model is not None,
            "memory": memory_service.redis is not None or True,  # Fallback always works
            "rag": rag_service.collection is not None,
            "llm": llm_service.client is not None
        }
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint"""
    try:
        # Create new conversation if needed
        conversation_id = request.conversation_id or memory_service.create_conversation()
        
        # Get conversation history
        history = memory_service.get_formatted_history(conversation_id, last_n=8)
        
        # Detect emotion and intent (parallel - done via separate service calls)
        emotion = emotion_detector.detect(request.message)
        intent = intent_detector.detect(request.message)
        
        logger.info(f"Detected emotion: {emotion.emotion.value} ({emotion.confidence:.2f})")
        logger.info(f"Detected intent: {intent.intent.value} ({intent.confidence:.2f})")
        
        # Store user message with metadata
        memory_service.add_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            emotion=emotion,
            intent=intent
        )
        
        # Generate AI response
        ai_response = await llm_service.generate_response(
            user_message=request.message,
            conversation_history=history,
            emotion=emotion,
            intent=intent
        )
        
        # Store AI response
        memory_service.add_message(
            conversation_id=conversation_id,
            role="assistant",
            content=ai_response
        )
        
        # Get RAG sources for transparency
        rag_results = rag_service.query(request.message, n_results=3)
        rag_sources = [r["topic"] for r in rag_results] if rag_results else []
        
        return ChatResponse(
            conversation_id=conversation_id,
            message=ai_response,
            detected_emotion=emotion,
            detected_intent=intent,
            rag_sources=rag_sources
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/conversation/new")
async def new_conversation():
    """Start a new conversation"""
    conversation_id = memory_service.create_conversation()
    return {"conversation_id": conversation_id}


@app.get("/conversation/{conversation_id}/history", response_model=ConversationHistory)
async def get_history(conversation_id: str):
    """Get conversation history"""
    history = memory_service.get_history(conversation_id)
    if not history:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return history


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "FinSight API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "POST /chat",
            "health": "GET /health",
            "new_conversation": "POST /conversation/new",
            "history": "GET /conversation/{id}/history"
        }
    }
