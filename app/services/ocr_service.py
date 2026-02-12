import io
import os
import docx
from typing import Dict, Any, Tuple
from PIL import Image
from pdf2image import convert_from_bytes
import pytesseract
from app.utils.image_preprocess import preprocess_image


# Supported MIME types and their internal category mapping
ALLOWED_TYPES = {
    "image/jpeg": "img",
    "image/jpg": "img",
    "image/png": "img",
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx"
}


def extract_text_from_image(img: Image.Image) -> str:
    """
    Performs OCR on a single PIL Image object using Tesseract.

    Args:
        img: Preprocessed PIL Image object

    Returns:
        Extracted text string from image
    """
    # --oem 3: Use LSTM OCR engine
    # --psm 3: Fully automatic page segmentation
    custom_config = r'--oem 3 --psm 3'
    return pytesseract.image_to_string(img, config=custom_config)


def process_document(
    file, 
    contents: bytes, 
    preprocess_config: Dict[str, Any] = None
) -> Tuple[str, int, str]:
    """
    Main document processing handler.

    This Function:
    1. Validates file type
    2. Applies optional preprocessing
    3. Extracts text depending on file category
    4. Returns extracted text, page count, and file type category
    
    Args:
        file: FastAPI UploadFile object
        contents: Raw file bytes
        preprocess_config: Configuration for image enhancement (brightness, contrast, etc.).

    Returns:
        full_text: Combined extracted text
        page_count: Number of processed pages/images
        file_category: Internal file category (img/pdf/docx)
    """

    # ===== Step 1: Validate file content type =====
    content_type = file.content_type
    if content_type not in ALLOWED_TYPES:
        raise ValueError(f"Unsupported file type: {content_type}")
    
    # Map MIME type to internal category
    file_category = ALLOWED_TYPES[content_type]
    
    # Ensure config exists for image processing logic
    config = preprocess_config or {}

    # Extract preprocessing parameters with default values
    grayscale = config.get("grayscale", False)
    denoise = config.get("denoise", False)
    brightness = float(config.get("brightness", 1.0))
    contrast = float(config.get("contrast", 1.0))

    # Store OCR results for each page/image
    results = []


    # ===== Step 2: Process Image Files =====
    if file_category == "img":
        # Load image from bytes
        img = Image.open(io.BytesIO(contents))
        
        # Apply image enhancement before OCR
        processed_img = preprocess_image(
            img, 
            grayscale=grayscale, 
            denoise=denoise, 
            brightness=brightness, 
            contrast=contrast
        )
        
        # Perform OCR extraction
        text = extract_text_from_image(processed_img)
        results.append(text)


    # ===== Step 3: Process PDF Files =====
    elif file_category == "pdf":
        # Convert PDF pages to list of PIL images
        images = convert_from_bytes(contents)
        for i, img in enumerate(images):
            # Apply preprocessing to each page
            processed_img = preprocess_image(
                img, 
                grayscale=grayscale, 
                denoise=denoise, 
                brightness=brightness, 
                contrast=contrast
            )

            # Perform OCR per page
            text = extract_text_from_image(processed_img)
            results.append(f"--- Page {i+1} ---\n{text}")


    # ===== Step 4: Process Word Documents =====
    elif file_category == "docx":
        # Handle Word documents via python-docx
        doc = docx.Document(io.BytesIO(contents))
        text = "\n".join([para.text for para in doc.paragraphs])
        results.append(text)


    # ===== Step 5: Combine and Return Results =====
    full_text = "\n\n".join(results).strip()
    
    # Return:
    # - Extracted text
    # - Number of processed units (pages/images)
    # - File category
    return full_text, len(results), file_category