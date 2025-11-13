import os


class Settings:
    def __init__(self):
        self.provider = os.getenv("PROVIDER", "simple").lower()
        self.max_chars = int(os.getenv("MAX_CHARS", "10000"))
        self.sentiment_model = os.getenv("SENTIMENT_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
        self.summarizer_model = os.getenv("SUMMARIZER_MODEL", "facebook/bart-large-cnn")
        self.spacy_model = os.getenv("SPACY_MODEL", "en_core_web_sm")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.request_timeout_ms = int(os.getenv("REQUEST_TIMEOUT_MS", "8000"))


settings = Settings()