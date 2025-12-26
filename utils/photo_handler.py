import base64
from io import BytesIO
from PIL import Image
from typing import Optional
import tempfile
from pathlib import Path


def decode_photo(base64_string: str) -> Optional[Image.Image]:
    try:
        if ',' in base64_string:
            base64_string = base64_string.split(',')[-1]
        
        photo_b64 = base64_string.replace('-', '+').replace('_', '/')
        padding = len(photo_b64) % 4
        if padding:
            photo_b64 += '=' * (4 - padding)
        
        photo_bytes = base64.b64decode(photo_b64)
        
        jp2_bytes = _extract_jp2_from_iso(photo_bytes)
        
        return _convert_jp2_to_pil(jp2_bytes)
        
    except Exception as e:
        print(f"Error decoding photo: {e}")
        return None


def _extract_jp2_from_iso(photo_bytes: bytes) -> bytes:
    jp2_header = bytes([0x00, 0x00, 0x00, 0x0C, 0x6A, 0x50, 0x32, 0x20])
    jp2_codestream = bytes([0xFF, 0x4F, 0xFF, 0x51])
    
    if photo_bytes[:8] == jp2_header:
        return photo_bytes
    
    jp2_pos = photo_bytes.find(jp2_header)
    if jp2_pos >= 0:
        return photo_bytes[jp2_pos:]
    
    codestream_pos = photo_bytes.find(jp2_codestream)
    if codestream_pos >= 0:
        return photo_bytes[codestream_pos:]
    
    return photo_bytes


def _convert_jp2_to_pil(jp2_bytes: bytes) -> Optional[Image.Image]:
    try:
        return _try_glymur(jp2_bytes)
    except:
        pass
    
    try:
        return _try_opencv(jp2_bytes)
    except:
        pass
    
    try:
        return _try_pillow(jp2_bytes)
    except Exception as e:
        print(f"All JP2 conversion methods failed: {e}")
        return None


def _try_glymur(jp2_bytes: bytes) -> Optional[Image.Image]:
    try:
        import glymur
        
        with tempfile.NamedTemporaryFile(suffix='.jp2', delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(jp2_bytes)
        
        try:
            jp2 = glymur.Jp2k(temp_path)
            img_array = jp2[:]
            
            if len(img_array.shape) == 2:
                img = Image.fromarray(img_array, mode='L')
            elif len(img_array.shape) == 3:
                if img_array.shape[2] == 3:
                    img = Image.fromarray(img_array, mode='RGB')
                elif img_array.shape[2] == 4:
                    img = Image.fromarray(img_array, mode='RGBA')
                else:
                    raise ValueError(f"Unexpected color channels: {img_array.shape[2]}")
            else:
                raise ValueError(f"Unexpected image shape: {img_array.shape}")
            
            return img
        finally:
            Path(temp_path).unlink()
            
    except ImportError:
        raise Exception("glymur not available")
    except Exception as e:
        raise Exception(f"glymur conversion failed: {e}")


def _try_opencv(jp2_bytes: bytes) -> Optional[Image.Image]:
    try:
        import cv2
        import numpy as np
        
        nparr = np.frombuffer(jp2_bytes, dtype=np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise ValueError("Failed to decode JP2 image with OpenCV")
        
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return Image.fromarray(img_rgb)
        
    except ImportError:
        raise Exception("opencv-python not available")
    except Exception as e:
        raise Exception(f"OpenCV conversion failed: {e}")


def _try_pillow(jp2_bytes: bytes) -> Optional[Image.Image]:
    try:
        img = Image.open(BytesIO(jp2_bytes))
        if img.format == 'JPEG2000':
            return img.convert('RGB')
        return img
    except Exception as e:
        raise Exception(f"Pillow conversion failed: {e}")
