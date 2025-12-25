"""Photo handling utilities for decoding base64 photo strings."""
import base64
from io import BytesIO
from PIL import Image
from typing import Optional


def decode_photo(base64_string: str) -> Optional[Image.Image]:
    """
    Decode a base64 encoded photo string to a PIL Image.
    
    Args:
        base64_string: Base64 encoded image string
        
    Returns:
        PIL Image object or None if decoding fails
    """
    try:
        # Remove data URL prefix if present (e.g., "data:image/jpeg;base64,")
        if ',' in base64_string:
            base64_string = base64_string.split(',')[-1]
        
        # Decode base64 string
        image_data = base64.b64decode(base64_string)
        
        # Create PIL Image from bytes
        image = Image.open(BytesIO(image_data))
        
        return image
    except Exception as e:
        print(f"Error decoding photo: {e}")
        return None

