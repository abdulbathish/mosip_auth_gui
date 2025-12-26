import base64
from io import BytesIO
from PIL import Image
from typing import Optional


def decode_photo(base64_string: str) -> Optional[Image.Image]:
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',')[-1]
        
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        
        return image
    except Exception as e:
        print(f"Error decoding photo: {e}")
        return None
