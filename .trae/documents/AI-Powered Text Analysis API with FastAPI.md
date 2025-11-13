## Goal
Build an async FastAPI REST API that accepts text and returns sentiment, key phrases, and a brief summary using spaCy or Hugging Face Transformers, with optional OpenAI integration.

## Core Deliverables
1. POST `/analyze` — async endpoint returning `{ sentiment, keyphrases, summary, meta }`
2. GET `/health` — liveness/readiness
3. Clean architecture with pluggable NLP providers
4. Robust error handling, validation, logging
5. Tests (unit + integration) and containerized deployment

## Architecture
- API Layer
  - FastAPI app with routers: `analyze`, `health`
  - Pydantic request/response schemas
  - Dependency-injected `TextAnalysisService`
- Service Layer
  - `TextAnalysisService` orchestrates sentiment, keywords, summary concurrently
  - Aggregates results and builds response
- NLP Providers (strategy pattern)
  - `SpaCyProvider` — keyword extraction (noun chunks + entities), lightweight summary (extractive), optional sentiment via third-party model or rule-based
  - `HFTransformersProvider` — `sentiment-analysis` pipeline, summarization via `bart-large-cnn` or `t5-small`; keywords via spaCy fallback or a transformer-based keyphrase model if added later
  - `OpenAIProvider` (optional) — sentiment/summary via GPT models; keywords via prompt
  - Common interface: `analyze_sentiment(text)`, `extract_keywords(text)`, `summarize(text)`
- Configuration
  - `BaseSettings` (Pydantic) for `PROVIDER=spacy|hf|openai`, model names, timeouts, max text length, CORS origins, etc.
- Error Handling
  - Central exception handlers mapping to consistent JSON errors
  - Domain errors: `ModelLoadError`, `InferenceError`, `ValidationError`, `TimeoutError`
- Logging & Observability
  - Structured logging (JSON) with request IDs
  - Metrics hooks (optional): request count/latency, model inference timings

## Data Contracts
- Request
  - `{ text: string, language?: string, options?: { sentiment?: bool, keyphrases?: bool, summary?: bool } }`
- Response
  - `{ sentiment: { label: 'positive'|'negative'|'neutral', score: number } | null,
       keyphrases: string[] | null,
       summary: string | null,
       meta: { provider: string, models: { sentiment?: string, summary?: string }, elapsed_ms: number } }`
- Error Response
  - `{ error: { code: string, message: string, details?: object } }`

## Async Pipeline
- Validate input size and content
- Run tasks concurrently
  - Use `asyncio.gather` with `to_thread` for CPU-bound (spaCy) or I/O-bound (OpenAI)
  - Per-task timeouts; cancel remaining on timeout if necessary
- Aggregate results and build response
- Record timings per step in `meta`

## NLP Choices
- Sentiment
  - HF: `distilbert-base-uncased-finetuned-sst-2-english` via `pipeline('sentiment-analysis')`
  - OpenAI: classify sentiment via prompt (optional)
  - SpaCy: rule-based fallback (lexicon + negation handling) if transformers unavailable
- Keywords
  - SpaCy: noun chunks + named entities; deduplicate and rank by frequency/TF
  - Optional future: YAKE/KeyBERT as add-on (not required initially)
- Summary
  - HF: `facebook/bart-large-cnn` or `t5-small` summarization pipeline
  - OpenAI: short abstract via prompt with word/character cap
  - SpaCy: simple extractive summary (top sentences by keyword overlap) for baseline

## Endpoints
- POST `/analyze`
  - Async; respects `options` to skip tasks
  - Returns JSON per contract; enforces `max_chars` via config
- GET `/health`
  - Checks model load status and returns `{ status: 'ok', provider, models }`

## Error Handling & Validation
- Input validation via Pydantic
  - Non-empty `text`; `max_chars` limit; supported languages
- Exception handlers
  - Map provider/model failures to `HTTP 503` with `InferenceError`
  - Bad request → `HTTP 400` with `ValidationError`
  - Timeout → `HTTP 504`
- Safe logging
  - Do not log full text; log sizes and hashes

## Performance & Scalability
- Model Loading
  - Lazy-init providers on startup; cache pipelines/models with `lru_cache`
- Concurrency
  - Use thread pool for spaCy CPU-bound operations
  - Control max concurrency via config
- Limits
  - `max_chars` (e.g., 10k), per-request timeout (e.g., 5s sentiment, 8s summary)
- Caching (optional)
  - Memoize frequent texts keyed by hash (size-bounded)

## Security
- CORS configuration per environments
- Rate limiting (optional) via `slowapi`
- PII considerations
  - Avoid storing raw texts; mask logs; configurable redaction
- Secrets management
  - Read `OPENAI_API_KEY` from environment; never log

## Testing
- Unit tests
  - Provider methods with sample texts and edge cases
  - Service orchestration with `asyncio` and timeouts
- Integration tests
  - `httpx.AsyncClient` against FastAPI app
  - Validate contracts, status codes, error shapes
- Performance tests (optional)
  - Small benchmarks for typical text sizes

## Deployment
- Packaging
  - `pyproject.toml` or `requirements.txt`
- Runtime
  - `uvicorn` with reasonable workers/timeout
- Containerization
  - Minimal `Dockerfile` with model cache directory; healthcheck
- Config
  - Environment-driven provider selection and model names

## Milestones
1. Project Skeleton
   - FastAPI app, routers, schemas, config, logging, health endpoint
2. SpaCy Baseline
   - Keyword extraction + extractive summary; basic sentiment fallback
3. HF Integration
   - Sentiment + abstractive summarization; spaCy keywords as default
4. OpenAI Optional
   - Pluggable provider; prompt templates; configurable usage
5. Error Handling & Limits
   - Central handlers, timeouts, max text length, safe logging
6. Tests & Docs
   - Unit/integration tests; example cURL; usage README snippet
7. Container & Release
   - Docker image; environment configuration; deployment guide

## Example Usage (for validation)
- Request
  ```json
  { "text": "I love the new design, but the navigation feels slow.", "options": { "sentiment": true, "keyphrases": true, "summary": true } }
  ```
- Response (illustrative)
  ```json
  {
    "sentiment": { "label": "positive", "score": 0.92 },
    "keyphrases": ["new design", "navigation"],
    "summary": "Positive feedback with concern about slow navigation.",
    "meta": { "provider": "hf", "models": { "sentiment": "distilbert-sst2", "summary": "bart-large-cnn" }, "elapsed_ms": 120 }
  }
  ```

## Next Steps
- Confirm provider preference (spaCy-only, HF, or OpenAI optional)
- Confirm model selections and `max_chars`/timeouts
- Proceed with Milestone 1 implementation