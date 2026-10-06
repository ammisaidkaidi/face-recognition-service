import cv2
import numpy as np

class FrameError(ValueError):
    def __init__(self, code: str, message: str):
        self.code = code
        super().__init__(message)

def decode_frame(payload: bytes, max_bytes: int) -> np.ndarray:
    if not payload:
        raise FrameError("INVALID_FRAME", "Frame payload is empty")
    if len(payload) > max_bytes:
        raise FrameError("FRAME_TOO_LARGE", "Frame exceeds configured byte limit")
    arr = np.frombuffer(payload, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None or frame.ndim != 3:
        raise FrameError("INVALID_FRAME", "Payload is not a supported JPEG/WebP image")
    return frame

def crop(frame: np.ndarray, bbox, margin: float = .1) -> np.ndarray:
    h, w = frame.shape[:2]; mx=int(bbox.width*margin); my=int(bbox.height*margin)
    x1=max(0,bbox.x-mx); y1=max(0,bbox.y-my); x2=min(w,bbox.x+bbox.width+mx); y2=min(h,bbox.y+bbox.height+my)
    return frame[y1:y2, x1:x2]
