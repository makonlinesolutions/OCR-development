from fastapi import FastAPI, UploadFile, File
import shutil
import os
from app.services.ocr import process_pan_card
from uuid import uuid4

app = FastAPI()

@app.post("/upload-pan/")
async def upload_pan_card(file: UploadFile = File(...)):
    # Get file extension
    ext = file.filename.split('.')[-1].lower()
    allowed = ['jpg', 'jpeg', 'png', 'pdf']
    
    if ext not in allowed:
        return {"error": f"Unsupported file type: {ext}"}

    # Save uploaded file with a unique name
    filename = f"temp_{uuid4()}.{ext}"
    with open(filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Validate file size
    if os.path.getsize(filename) < 1024:
        return {"error": "Uploaded file is empty or corrupted."}

    # Pass to OCR
    try:
        result = process_pan_card(filename)
        os.remove(filename)  # Clean up
        return result
    except Exception as e:
        os.remove(filename)
        return {"error": str(e)}
