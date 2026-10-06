import cv2
import numpy as np
from app.domain.face import DetectedFace

class QualityGate:
    def __init__(self, min_face_size:int, min_sharpness:float, min_brightness:float,
                 max_brightness:float, max_abs_yaw:float, max_abs_pitch:float):
        self.min_face_size=min_face_size; self.min_sharpness=min_sharpness
        self.min_brightness=min_brightness; self.max_brightness=max_brightness
        self.max_abs_yaw=max_abs_yaw; self.max_abs_pitch=max_abs_pitch

    def evaluate(self, face: DetectedFace, face_image: np.ndarray) -> tuple[bool,str|None,float]:
        if min(face.bbox.width, face.bbox.height) < self.min_face_size: return False,"FACE_TOO_SMALL",0.0
        if face_image.size == 0: return False,"INVALID_FRAME",0.0
        gray=cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)
        sharp=float(cv2.Laplacian(gray,cv2.CV_64F).var()); bright=float(gray.mean())
        if sharp < self.min_sharpness: return False,"LOW_QUALITY",min(1.0,sharp/max(self.min_sharpness,1))
        if bright < self.min_brightness or bright > self.max_brightness: return False,"BAD_BRIGHTNESS",0.0
        if abs(face.pose.yaw)>self.max_abs_yaw or abs(face.pose.pitch)>self.max_abs_pitch: return False,"EXTREME_POSE",0.0
        if face.embedding is None or not np.isfinite(face.embedding).all(): return False,"INVALID_EMBEDDING",0.0
        quality=min(1.0, .5*(sharp/max(self.min_sharpness,1)) + .5*face.detection_score)
        return True,None,float(quality)
