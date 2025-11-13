import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette import status
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.routers.analyze import router as analyze_router
from app.services.text_analysis import TextAnalysisService
from app.providers.simple import SimpleProvider
from app.providers.hf_provider import HFTransformersProvider
from app.providers.spacy_provider import SpaCyProvider


def build_provider():
    p = settings.provider
    if p == "hf":
        return HFTransformersProvider(settings.sentiment_model, settings.summarizer_model)
    if p == "spacy":
        return SpaCyProvider(settings.spacy_model)
    return SimpleProvider()


app = FastAPI()


@app.on_event("startup")
async def on_startup():
    provider = build_provider()
    app.state.provider = provider
    app.state.service = TextAnalysisService(provider, settings.max_chars)


app.include_router(analyze_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": {"code": "validation_error", "message": "invalid_request"}})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, content={"error": {"code": "inference_error", "message": "service_unavailable"}})


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)

app.mount("/", StaticFiles(directory="public", html=True), name="static")