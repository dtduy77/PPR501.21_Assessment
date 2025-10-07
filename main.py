import os
import tempfile
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import Dict, Any
import uvicorn

from app.models import ExtractionResult
from app.services import extract_from_image_with_langchain
from app.configs import get_model_config

app = FastAPI(
    title="Bill Extraction API",
    description="Extract bill information using LangChain and Vision Models",
    version="1.0.0",
)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/extract")
async def extract_bill(file: UploadFile = File(...)):
    """
    Extract bill information from uploaded image

    - **file**: Image file (PNG, JPG, JPEG, WEBP)
    """
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    suffix = os.path.splitext(file.filename or "image.jpg")[1]
    tmp_path = None

    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # Get provider from environment (configs.py will handle detection)
        config = get_model_config()
        result = extract_from_image_with_langchain(tmp_path, config.provider)

        return {
            "success": True,
            "data": result,
            "message": "Extraction completed successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
    finally:
        # Clean up temporary file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception:
                pass


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Bill Extraction API",
        "version": "1.0.0",
        "endpoints": {"health": "/health", "extract": "/extract", "docs": "/docs"},
    }


if __name__ == "__main__":
    print("Starting Bill Extraction API server...")
    print("API Documentation: http://localhost:8000/docs")
    print("Health check: http://localhost:8000/health")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
