from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.ocr import process_ocr
from typing import Dict

router = APIRouter()

@router.post("/", response_model=Dict)
async def ocr_endpoint(file: UploadFile = File(...)):
    try:
        result = await process_ocr(file)
        return {"text": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))