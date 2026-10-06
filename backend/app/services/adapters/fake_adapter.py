"""Deterministic adapter for tests; never use it for biometric decisions."""
import numpy as np
from app.domain.face import BoundingBox, DetectedFace, HeadPose

class FakeVisionEngine:
    model_name = "fake"
    model_version = "fake-v1"
    embedding_dimension = 8
    def analyze(self, frame: np.ndarray) -> list[DetectedFace]:
        if frame.size == 0 or float(frame.mean()) < 1:
            return []
        h, w = frame.shape[:2]
        vec = np.array([float(frame.mean()), float(frame.std()), h, w, *frame.mean(axis=(0,1)).tolist(), 1.0], dtype=np.float32)[:8]
        vec /= max(float(np.linalg.norm(vec)), 1e-12)
        return [DetectedFace(BoundingBox(w//4,h//4,w//2,h//2), [(w*.4,h*.4),(w*.6,h*.4),(w*.5,h*.5),(w*.43,h*.62),(w*.57,h*.62)], HeadPose(0,0,0), vec, .99)]
