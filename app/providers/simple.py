import asyncio
import math
import re
from typing import List, Optional
from .base import BaseProvider
from app.utils.text import split_sentences, normalize


_POSITIVE = {
    "good",
    "great",
    "excellent",
    "love",
    "like",
    "awesome",
    "amazing",
    "happy",
    "satisfied",
    "fantastic",
}

_NEGATIVE = {
    "bad",
    "terrible",
    "awful",
    "hate",
    "dislike",
    "sad",
    "angry",
    "slow",
    "bug",
    "issue",
}

_STOPWORDS = {
    "the",
    "is",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "on",
    "for",
    "with",
    "that",
    "this",
    "it",
    "as",
    "at",
    "by",
    "from",
}


class SimpleProvider(BaseProvider):
    name = "simple"

    async def analyze_sentiment(self, text: str) -> Optional[tuple]:
        t = normalize(text).lower()
        words = re.findall(r"[a-zA-Z']+", t)
        pos = sum(1 for w in words if w in _POSITIVE)
        neg = sum(1 for w in words if w in _NEGATIVE)
        if pos == 0 and neg == 0:
            return ("neutral", 0.5)
        total = pos + neg
        score = pos / total if total > 0 else 0.5
        label = "positive" if score > 0.6 else "negative" if score < 0.4 else "neutral"
        return (label, round(score, 4))

    async def extract_keywords(self, text: str) -> Optional[List[str]]:
        t = normalize(text).lower()
        tokens = re.findall(r"[a-zA-Z][a-zA-Z\-']+", t)
        tokens = [w for w in tokens if w not in _STOPWORDS and len(w) > 2]
        freq = {}
        for w in tokens:
            freq[w] = freq.get(w, 0) + 1
        ranked = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
        single = [w for w, c in ranked[:10]]
        phrases = []
        sentences = split_sentences(text)
        for s in sentences:
            s2 = normalize(s).lower()
            words = [w for w in re.findall(r"[a-zA-Z][a-zA-Z\-']+", s2) if w not in _STOPWORDS]
            buf = []
            for w in words:
                buf.append(w)
            if len(buf) >= 2:
                phrases.append(" ".join(buf[:2]))
        result = list(dict.fromkeys(phrases + single))
        return result[:10]

    async def summarize(self, text: str) -> Optional[str]:
        sentences = split_sentences(text)
        if not sentences:
            return None
        best = sentences[0]
        return normalize(best)[:280]