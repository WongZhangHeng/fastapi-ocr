from fastapi import HTTPException


# Supported MIME types and their mapped internal categories
ALLOWED_TYPES = {
    "image/jpeg": "img",
    "image/jpg": "img",
    "image/png": "img",
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx"
}


def validate_file(file, contents, max_size):
    """
    Validates uploaded file before processing.

    This function ensures:
    1. The file MIME type is supported.
    2. The file size does not exceed the allowed limit.

    Args:
        file: FastAPI UploadFile object.
        contents: Raw file bytes.
        max_size: Maximum allowed file size in bytes.

    Raises:
        HTTPException 415: If file type is not supported.
        HTTPException 413: If file exceeds maximum size limit.
    """

    # ===== Step 1: Validate MIME Type =====
    # Prevent unsupported or potentially unsafe file formats
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,        # Unsupported Media Type
            detail=f"Unsupported file type: {file.content_type}"
        )


    # ===== Step 2: Validate File Size =====
    # Prevent excessively large uploads
    if len(contents) > max_size:
        raise HTTPException(
            status_code=413,        # Payload Too Large
            detail="File too large."
        )