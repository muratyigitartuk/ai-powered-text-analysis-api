from typing import List, Optional
from .base import BaseProvider


class HFTransformersProvider(BaseProvider):
    name = "hf"

    def __init__(self, sentiment_model: Optional[str] = None, summarizer_model: Optional[str] = None):
        self._sentiment_model = sentiment_model or "distilbert-base-uncased-finetuned-sst-2-english"
        self._summarizer_model = summarizer_model or "facebook/bart-large-cnn"
        self._sentiment = None
        self._summarizer = None

    def _ensure_sentiment(self):
        if self._sentiment is None:
            try:
                import importlib
                transformers = importlib.import_module("transformers")
                pipeline = getattr(transformers, "pipeline")
            except Exception as e:
                raise RuntimeError("transformers_not_available") from e
            self._sentiment = pipeline("sentiment-analysis", model=self._sentiment_model)

    def _ensure_summarizer(self):
        if self._summarizer is None:
            try:
                import importlib
                transformers = importlib.import_module("transformers")
                pipeline = getattr(transformers, "pipeline")
            except Exception as e:
                raise RuntimeError("transformers_not_available") from e
            self._summarizer = pipeline("summarization", model=self._summarizer_model)

    async def analyze_sentiment(self, text: str) -> Optional[tuple]:
        self._ensure_sentiment()
        out = await self._run_in_thread(self._sentiment, text)
        item = out[0]
        label = item["label"].lower()
        score = float(item["score"])
        if label.startswith("pos"):
            label = "positive"
        elif label.startswith("neg"):
            label = "negative"
        else:
            label = "neutral"
        return (label, round(score, 4))

    async def extract_keywords(self, text: str) -> Optional[List[str]]:
        from app.providers.simple import SimpleProvider
        return await SimpleProvider().extract_keywords(text)

    async def summarize(self, text: str) -> Optional[str]:
        self._ensure_summarizer()
        out = await self._run_in_thread(self._summarizer, text, max_length=200, min_length=30, do_sample=False)
        item = out[0]
        return item.get("summary_text")

    async def _run_in_thread(self, func, *args, **kwargs):
        import asyncio
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, lambda: func(*args, **kwargs))