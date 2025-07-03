from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from src.data_frameworks.core.shared_models.base_data import BaseData


class Sentiment(BaseData):
    """Model for sentiment analysis data."""
    
    text: str = Field(..., description="Original text analyzed")
    score: float = Field(..., description="Sentiment score (-1 to 1)")
    confidence: float = Field(..., description="Confidence in sentiment analysis (0 to 1)")
    label: str = Field(..., description="Sentiment label (positive, negative, neutral)")
    emotions: Dict[str, float] = Field(default_factory=dict, description="Emotion scores")
    keywords: list = Field(default_factory=list, description="Key sentiment-driving words")
    
    def validate_data(self) -> bool:
        """Validate sentiment data integrity."""
        if not (-1 <= self.score <= 1):
            return False
        if not (0 <= self.confidence <= 1):
            return False
        if self.label not in ["positive", "negative", "neutral"]:
            return False
        return True
    
    @property
    def is_positive(self) -> bool:
        """Check if sentiment is positive."""
        return self.score > 0.1
    
    @property
    def is_negative(self) -> bool:
        """Check if sentiment is negative."""
        return self.score < -0.1
    
    @property
    def is_neutral(self) -> bool:
        """Check if sentiment is neutral."""
        return -0.1 <= self.score <= 0.1
    
    @property
    def strength(self) -> str:
        """Get sentiment strength description."""
        abs_score = abs(self.score)
        if abs_score >= 0.7:
            return "strong"
        elif abs_score >= 0.3:
            return "moderate"
        else:
            return "weak"
    
    def get_dominant_emotion(self) -> Optional[str]:
        """Get the dominant emotion from emotion scores."""
        if not self.emotions:
            return None
        return max(self.emotions.items(), key=lambda x: x[1])[0]