from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Dict


class AnalysisOptions(BaseModel):
    sentiment: bool = True
    keyphrases: bool = True
    summary: bool = True


class TextAnalysisRequest(BaseModel):
    text: str = Field(..., min_length=1)
    language: Optional[str] = None
    options: Optional[AnalysisOptions] = None


class SentimentResult(BaseModel):
    label: Literal["positive", "negative", "neutral"]
    score: float


class MetaInfo(BaseModel):
    provider: str
    models: Dict[str, Optional[str]]
    elapsed_ms: int


class TextAnalysisResponse(BaseModel):
    sentiment: Optional[SentimentResult] = None
    keyphrases: Optional[List[str]] = None
    summary: Optional[str] = None
    meta: MetaInfo


class ErrorResponse(BaseModel):
    error: Dict[str, Optional[str]]