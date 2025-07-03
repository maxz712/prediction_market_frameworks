from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from src.data_frameworks.core.shared_models.base_data import BaseData


class Article(BaseData):
    """Model for news article data."""
    
    title: str = Field(..., description="Article title")
    description: Optional[str] = Field(default=None, description="Article description/summary")
    content: Optional[str] = Field(default=None, description="Full article content")
    url: str = Field(..., description="Article URL")
    author: Optional[str] = Field(default=None, description="Article author")
    published_at: Optional[datetime] = Field(default=None, description="Publication date")
    category: Optional[str] = Field(default=None, description="Article category")
    tags: List[str] = Field(default_factory=list, description="Article tags")
    sentiment_score: Optional[float] = Field(default=None, description="Sentiment analysis score")
    
    def validate_data(self) -> bool:
        """Validate article data integrity."""
        if not self.title or not self.url:
            return False
        if self.sentiment_score is not None and not (-1 <= self.sentiment_score <= 1):
            return False
        return True
    
    @property
    def word_count(self) -> int:
        """Get word count of the article content."""
        if not self.content:
            return 0
        return len(self.content.split())
    
    @property
    def is_recent(self) -> bool:
        """Check if article is recent (within last 24 hours)."""
        if not self.published_at:
            return False
        time_diff = datetime.now() - self.published_at
        return time_diff.days < 1
    
    @property
    def sentiment_label(self) -> str:
        """Get sentiment label based on score."""
        if self.sentiment_score is None:
            return "unknown"
        if self.sentiment_score > 0.1:
            return "positive"
        elif self.sentiment_score < -0.1:
            return "negative"
        else:
            return "neutral"