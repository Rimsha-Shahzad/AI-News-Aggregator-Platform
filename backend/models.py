from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class Article(BaseModel):
    title: str
    url: str
    source: str
    content: Optional[str] = None
    published_at: Optional[datetime] = None
    bias_label: Optional[str] = None
    bias_score: Optional[float] = None
    embedding: Optional[List[float]] = None

class UserPreferences(BaseModel):
    user_id: str
    topics: List[str] = []
    sources: List[str] = []
    reading_history: List[str] = []

class DigestItem(BaseModel):
    user_id: str
    date: datetime = Field(default_factory=datetime.utcnow)
    articles: List[Article] = []
    summary: Optional[str] = None