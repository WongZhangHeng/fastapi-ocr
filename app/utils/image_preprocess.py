from PIL import ImageOps, ImageEnhance, ImageFilter

def preprocess_image(
    img,
    grayscale=False,
    denoise=False,
    brightness=1.0,
    contrast=1.0,
    sharpness=1.0
):

    """
    Applies configurable preprocessing steps to an image before OCR.

    This function enhances image quality to improve OCR accuracy.

    Args:
        img: PIL Image object.
        grayscale (bool): Convert image to grayscale.
        denoise (bool): Apply median filter to reduce noise.
        brightness (float): Adjust brightness level (1.0 = original).
        contrast (float): Adjust contrast level (1.0 = original).
        sharpness (float): Adjust sharpness level (1.0 = original).

    Returns:
        Processed PIL Image object.
    """

    # ===== Step 1: Convert to Grayscale =====
    # Reduces color complexity and improves OCR focus on text
    if grayscale:
        img = ImageOps.grayscale(img)


    # ===== Step 2: Apply Noise Reduction =====
    # Median filter helps remove small pixel noise
    if denoise:
        img = img.filter(ImageFilter.MedianFilter(size=3))


    # ===== Step 3: Adjust Brightness =====
    # Increase (>1.0) or decrease (<1.0) brightness intensity
    if brightness != 1.0:
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(brightness)


    # ===== Step 4: Adjust Contrast =====
    # Improves text visibility against background
    if contrast != 1.0:
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(contrast)

    return img
