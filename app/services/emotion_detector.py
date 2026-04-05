import torch
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from app.core.config import get_settings
from app.models.schemas import EmotionDetection, EmotionType
import logging

logger = logging.getLogger(__name__)


class EmotionDetector:
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
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        try:
            self.classifier = pipeline(
                "text-classification",
                model=settings.emotion_model,
                device=0 if self.device == "cuda" else -1,
                top_k=None
            )
            logger.info(f"Emotion detector loaded on {self.device}")
        except Exception as e:
            logger.error(f"Failed to load emotion model: {e}")
            self.classifier = None
        
        self._initialized = True
    
    def detect(self, text: str) -> EmotionDetection:
        if self.classifier is None:
            return EmotionDetection(emotion=EmotionType.NEUTRAL, confidence=0.0, intensity=0.5)
        
        try:
            results = self.classifier(text[:512])  # Truncate for safety
            emotions = results[0] if isinstance(results, list) else results
            
            # Map to our emotion types and find best match
            emotion_map = {
                "fear": EmotionType.FEAR,
                "anger": EmotionType.FRUSTRATION,
                "sadness": EmotionType.ANXIETY,
                "joy": EmotionType.EXCITEMENT,
                "surprise": EmotionType.CONFIDENCE,
                "disgust": EmotionType.CONFUSION,
                "neutral": EmotionType.NEUTRAL,
            }
            
            best_emotion = max(emotions, key=lambda x: x["score"])
            mapped_emotion = emotion_map.get(best_emotion["label"].lower(), EmotionType.NEUTRAL)
            
            # Calculate intensity based on confidence
            intensity = min(best_emotion["score"] * 1.2, 1.0)
            
            return EmotionDetection(
                emotion=mapped_emotion,
                confidence=best_emotion["score"],
                intensity=intensity
            )
            
        except Exception as e:
            logger.error(f"Emotion detection error: {e}")
            return EmotionDetection(emotion=EmotionType.NEUTRAL, confidence=0.0, intensity=0.5)


emotion_detector = EmotionDetector()
