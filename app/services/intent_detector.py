from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from app.core.config import get_settings
from app.models.schemas import IntentDetection, IntentType
import logging

logger = logging.getLogger(__name__)


class IntentDetector:
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
            self.model = SentenceTransformer(settings.intent_model)
            
            # Define intent categories with example phrases
            self.intent_examples = {
                IntentType.BUDGETING: [
                    "how do I budget my money",
                    "track my spending",
                    "manage monthly expenses",
                    "rent and bills are due",
                    "can I afford this",
                    "spending too much",
                ],
                IntentType.INVESTING: [
                    "should I invest in stocks",
                    "want to start investing",
                    "is crypto a good idea",
                    "where to put my money",
                    "investment options",
                    "grow my savings",
                ],
                IntentType.SAVING: [
                    "how to save more",
                    "emergency fund",
                    "save for vacation",
                    "put money aside",
                    "build savings",
                    "saving goals",
                ],
                IntentType.DEBT_MANAGEMENT: [
                    "pay off debt",
                    "student loans",
                    "credit card debt",
                    "loan repayment",
                    "managing debt",
                    "get out of debt",
                ],
                IntentType.FINANCIAL_PLANNING: [
                    "financial plan",
                    "long term goals",
                    "retirement planning",
                    "future finances",
                    "plan ahead",
                ],
                IntentType.EMOTIONAL_SUPPORT: [
                    "stressed about money",
                    "scared to invest",
                    "worried about finances",
                    "overwhelmed",
                    "financial anxiety",
                    "need help",
                ],
            }
            
            # Pre-compute embeddings for examples
            self.intent_embeddings = {}
            for intent, examples in self.intent_examples.items():
                embeddings = self.model.encode(examples)
                self.intent_embeddings[intent] = embeddings
            
            logger.info("Intent detector loaded")
        except Exception as e:
            logger.error(f"Failed to load intent model: {e}")
            self.model = None
        
        self._initialized = True
    
    def detect(self, text: str) -> IntentDetection:
        if self.model is None:
            return IntentDetection(intent=IntentType.GENERAL, confidence=0.0)
        
        try:
            # Encode input text
            input_embedding = self.model.encode([text])
            
            # Compare with all intent categories
            intent_scores = {}
            for intent, embeddings in self.intent_embeddings.items():
                similarities = cosine_similarity(input_embedding, embeddings)[0]
                intent_scores[intent] = np.max(similarities)
            
            # Get best matching intent
            best_intent = max(intent_scores, key=intent_scores.get)
            confidence = intent_scores[best_intent]
            
            # Get sub-intents (intents with >0.3 similarity)
            sub_intents = [
                intent.value for intent, score in intent_scores.items()
                if score > 0.3 and intent != best_intent
            ]
            
            return IntentDetection(
                intent=best_intent,
                confidence=confidence,
                sub_intents=sub_intents
            )
            
        except Exception as e:
            logger.error(f"Intent detection error: {e}")
            return IntentDetection(intent=IntentType.GENERAL, confidence=0.0)


intent_detector = IntentDetector()
