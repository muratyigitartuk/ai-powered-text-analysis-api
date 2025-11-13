from typing import List, Optional, Any
from .base import BaseProvider


class SpaCyProvider(BaseProvider):
    name = "spacy"

    def __init__(self, model: Optional[str] = None):
        self._model_name = model or "en_core_web_sm"
        self._nlp: Any = None

    def _ensure(self):
        if self._nlp is None:
            try:
                import importlib
                spacy = importlib.import_module("spacy")
                self._nlp = spacy.load(self._model_name)
            except Exception as e:
                raise RuntimeError("spacy_model_not_available") from e

    async def analyze_sentiment(self, text: str) -> Optional[tuple]:
        from app.providers.simple import SimpleProvider
        return await SimpleProvider().analyze_sentiment(text)

    async def extract_keywords(self, text: str) -> Optional[List[str]]:
        self._ensure()
        import asyncio
        nlp = self._nlp
        if nlp is None:
            raise RuntimeError("spacy_model_not_available")
        doc = await asyncio.get_running_loop().run_in_executor(None, lambda: nlp(text))
        chunks = list(dict.fromkeys([c.text.strip() for c in doc.noun_chunks]))
        ents = list(dict.fromkeys([e.text.strip() for e in doc.ents]))
        result = list(dict.fromkeys(chunks + ents))
        return result[:10]

    async def summarize(self, text: str) -> Optional[str]:
        self._ensure()
        import asyncio
        nlp = self._nlp
        if nlp is None:
            raise RuntimeError("spacy_model_not_available")
        doc = await asyncio.get_running_loop().run_in_executor(None, lambda: nlp(text))
        sents = [s.text.strip() for s in doc.sents]
        if not sents:
            return None
        return sents[0][:280]