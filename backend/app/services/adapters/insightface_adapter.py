"""Lazy InsightFace adapter. Import/model loading happen once at application startup."""
from pathlib import Path
import cv2
import numpy as np
from app.domain.face import BoundingBox, DetectedFace, HeadPose

class InsightFaceEngine:
    def __init__(self, model_name: str, model_root: Path, model_version: str,
                 providers: list[str], detection_size: int):
        try:
            from insightface.app import FaceAnalysis
        except ImportError as exc:
            raise RuntimeError("Install the model backend: pip install -e '.[insightface]'") from exc
        self.model_name = model_name
        self.model_version = model_version
        self.embedding_dimension = 512
        self._app = FaceAnalysis(name=model_name, root=str(model_root), providers=providers)
        self._app.prepare(ctx_id=-1, det_size=(detection_size, detection_size))

    def analyze(self, frame: np.ndarray) -> list[DetectedFace]:
        results = []
        for face in self._app.get(frame):
            x1, y1, x2, y2 = [int(v) for v in face.bbox]
            landmarks = [(float(x), float(y)) for x, y in np.asarray(face.kps)]
            embedding = np.asarray(face.normed_embedding, dtype=np.float32)
            # InsightFace pose convention is pitch, yaw, roll. Canonical API is yaw, pitch, roll.
            raw_pose = np.asarray(getattr(face, "pose", [0, 0, 0]), dtype=float)
            pitch, yaw, roll = (raw_pose.tolist() + [0, 0, 0])[:3]
            results.append(DetectedFace(
                bbox=BoundingBox(x1, y1, max(0, x2-x1), max(0, y2-y1)),
                landmarks=landmarks, pose=HeadPose(float(yaw), float(pitch), float(roll)),
                embedding=embedding, detection_score=float(face.det_score)))
        return results
