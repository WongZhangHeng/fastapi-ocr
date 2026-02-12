import time
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Header, Form

from app.services.ocr_service import process_document
from app.utils.file_validation import validate_file

# Create router instance for grouping related endpoints
router = APIRouter()

# Maximum allowed upload file size (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

@router.post("/analyze")
async def analyze_file(
    file: UploadFile = File(...),           # Upload file from client
    x_token: str = Header(...),             # API authentication token(from request header)
    request: Request = None,                # Request object to access app state
    
    # ===== OCR Preprocessing Parameters =====
    grayscale: bool = Form(False),          # Convert image to grayscale before OCR
    denoise: bool = Form(False),            # Apply noise reduction filter
    brightness: float = Form(1.0),          # Adjust brightness level (default = 1.0)
    contrast: float = Form(1.0)             # Adjust contrast level (default = 1.0)
):
    
    # Record processing time
    start_time = time.time()

    # ===== Step 1: Validate API Token =====
    # Ensure request is authorized before processing
    if x_token != request.app.state.API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing API Token")
    
    # Read uploaded file content into memory
    contents = await file.read()

    # ===== Step 2: Validate Uploaded File =====
    # Check file type, extension, and size limit
    validate_file(file, contents, MAX_FILE_SIZE)

    try:
        # ===== Step 3: Process Document via OCR Service =====
        # Pass preprocessing configuration into OCR logic
        full_text, page_count, file_category = process_document(
            file=file,
            contents=contents,
            preprocess_config={
                "grayscale": grayscale,
                "denoise": denoise,
                "brightness": brightness,
                "contrast": contrast
            }
        )

        # Calculate total processing time
        processing_time = round(time.time() - start_time, 3)

        # ===== Step 4: Return Structured JSON Response =====
        return {
            "status": "success",
            "data": {
                "content": full_text or "No text could be identified.",
                "insights": {
                    "filename": file.filename,
                    "extension": os.path.splitext(file.filename)[1],
                    "type": file_category.upper(),
                    "word_count": len(full_text.split()) if full_text else 0,
                    "execution_time": f"{processing_time}s",
                    "page_count": page_count,
                    "config_applied": {
                        "grayscale": grayscale,
                        "denoise": denoise,
                        "brightness": brightness,
                        "contrast": contrast
                    }
                }
            }
        }

    except Exception as e:
        # Handle unexpected server-side errors
        raise HTTPException(status_code=500, detail=str(e))