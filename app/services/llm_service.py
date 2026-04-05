import openai
from app.core.config import get_settings
from app.models.schemas import EmotionDetection, IntentDetection
from app.services.rag_service import rag_service
import logging

logger = logging.getLogger(__name__)


class LLMService:
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
        self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        
        self._initialized = True
    
    def _build_system_prompt(
        self,
        emotion: EmotionDetection,
        intent: IntentDetection,
        rag_context: str
    ) -> str:
        """Build system prompt based on detected emotion and intent"""
        
        base_prompt = """You are FinSight, a financial advisor AI that talks like a smart, empathetic friend. You understand messy, emotional financial situations and give practical advice without being robotic.

Rules:
- Talk conversationally, like texting a knowledgeable friend
- Acknowledge emotions first - validate anxiety, excitement, fear before giving advice
- Give specific, actionable advice, not generic bullet points
- When there's a conflict (rent vs invest), help them think through it, don't just say "do both"
- Use the provided financial knowledge but phrase it naturally
- Keep responses concise (2-4 paragraphs max) but meaningful
- If they're scared about investing, address the fear directly
- Never use corporate speak like "leverage your assets" or "optimize your portfolio"
"""
        
        # Emotion-specific guidance
        emotion_guidance = {
            "anxiety": "The user seems anxious. Be reassuring but honest. Help them focus on what they can control. Small steps are okay.",
            "fear": "The user is scared (possibly about investing or money decisions). Acknowledge the fear as valid. Explain risks clearly but don't be alarmist.",
            "excitement": "The user is excited. Match their energy but add caution where appropriate. Help them channel excitement into good decisions.",
            "frustration": "The user is frustrated. Acknowledge the frustration. Be direct about solutions without being preachy.",
            "confidence": "The user seems confident. Support their momentum but check for blind spots gently.",
            "confusion": "The user is confused. Break things down simply. One concept at a time.",
            "neutral": "Keep it balanced and helpful."
        }
        
        emotion_text = emotion_guidance.get(emotion.emotion.value, emotion_guidance["neutral"])
        
        # Intent context
        intent_text = f"Primary topic: {intent.intent.value.replace('_', ' ')}."
        if intent.sub_intents:
            intent_text += f" Also relevant: {', '.join(intent.sub_intents)}."
        
        full_prompt = f"""{base_prompt}

Current context:
- {emotion_text}
- {intent_text}

Relevant financial knowledge:
{rag_context}

Remember: You are texting with a friend who needs help. Be real, be helpful, be concise."""
        
        return full_prompt
    
    async def generate_response(
        self,
        user_message: str,
        conversation_history: str,
        emotion: EmotionDetection,
        intent: IntentDetection
    ) -> str:
        """Generate AI response with full context"""
        
        # Get RAG context
        rag_results = rag_service.query(user_message, n_results=3)
        rag_context = "\n\n".join([r["text"] for r in rag_results]) if rag_results else "No specific knowledge retrieved."
        
        # Build system prompt
        system_prompt = self._build_system_prompt(emotion, intent, rag_context)
        
        # Build messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if conversation_history:
            # Parse history and add as context
            messages.append({
                "role": "system",
                "content": f"Previous conversation:\n{conversation_history}"
            })
        
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return "I'm having trouble processing that right now. Can you try again?"


llm_service = LLMService()
