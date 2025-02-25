from PIL import Image
import numpy as np

def resize_image(image, newsize):
    """
    Resize an image using PIL's LANCZOS resampling
    
    Args:
        image: numpy array of the image
        newsize: tuple of (width, height)
    
    Returns:
        numpy array of the resized image
    """
    # Convert numpy array to PIL Image
    pil_image = Image.fromarray(image)
    
    # Use the appropriate resampling method
    if hasattr(Image, 'Resampling'):
        resampling = Image.Resampling.LANCZOS
    else:
        resampling = Image.LANCZOS
    
    # Resize the image
    resized = pil_image.resize(newsize[::-1], resampling)
    
    # Convert back to numpy array
    return np.array(resized)
