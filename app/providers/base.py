from typing import List, Optional
from abc import ABC, abstractmethod


class BaseProvider(ABC):
    name: str

    @abstractmethod
    async def analyze_sentiment(self, text: str) -> Optional[tuple]:
        ...

    @abstractmethod
    async def extract_keywords(self, text: str) -> Optional[List[str]]:
        ...

    @abstractmethod
    async def summarize(self, text: str) -> Optional[str]:
        ...