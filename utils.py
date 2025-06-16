import uuid
import os

def save_audio(content: bytes, filename: str) -> str:
    """
    Saves audio bytes to STORAGE_PATH and returns file URL or path.
    """
    from config import STORAGE_PATH
    filepath = os.path.join(STORAGE_PATH, filename)
    with open(filepath, 'wb') as f:
        f.write(content)
    # In production serve from public URL
    return filepath