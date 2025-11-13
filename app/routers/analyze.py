from fastapi import APIRouter, Request, HTTPException
from app.schemas import TextAnalysisRequest, TextAnalysisResponse, AnalysisOptions


router = APIRouter()


@router.post("/analyze", response_model=TextAnalysisResponse)
async def analyze(req: Request, body: TextAnalysisRequest):
    service = req.app.state.service
    opts = body.options or AnalysisOptions()
    try:
        return await service.analyze(body.text, opts.sentiment, opts.keyphrases, opts.summary)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=503, detail="inference_error")


@router.get("/health")
async def health(req: Request):
    provider = req.app.state.provider
    return {"status": "ok", "provider": provider.name}