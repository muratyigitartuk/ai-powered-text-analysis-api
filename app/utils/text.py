import re
from typing import List


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[\.!?])\s+", text.strip())
    return [p for p in parts if p]


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()