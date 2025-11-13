import time
import asyncio
from typing import Optional, List, Dict
from app.schemas import TextAnalysisResponse, SentimentResult, MetaInfo
from app.providers.base import BaseProvider


class TextAnalysisService:
    def __init__(self, provider: BaseProvider, max_chars: int):
        self.provider = provider
        self.max_chars = max_chars

    async def analyze(self, text: str, do_sentiment: bool, do_keywords: bool, do_summary: bool) -> TextAnalysisResponse:
        if not text or len(text) > self.max_chars:
            raise ValueError("invalid_text")
        start = time.time()
        tasks = []
        if do_sentiment:
            tasks.append(self.provider.analyze_sentiment(text))
        else:
            tasks.append(asyncio.sleep(0, result=None))
        if do_keywords:
            tasks.append(self.provider.extract_keywords(text))
        else:
            tasks.append(asyncio.sleep(0, result=None))
        if do_summary:
            tasks.append(self.provider.summarize(text))
        else:
            tasks.append(asyncio.sleep(0, result=None))
        s_res, k_res, sum_res = await asyncio.gather(*tasks)
        sentiment = None
        if s_res is not None:
            sentiment = SentimentResult(label=s_res[0], score=float(s_res[1]))
        meta = MetaInfo(provider=self.provider.name, models={}, elapsed_ms=int((time.time() - start) * 1000))
        return TextAnalysisResponse(sentiment=sentiment, keyphrases=k_res, summary=sum_res, meta=meta)