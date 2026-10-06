from typing import Protocol
import numpy as np
from app.domain.face import BoundingBox, DetectedFace, HeadPose

class FaceDetector(Protocol):
    def detect(self, frame: np.ndarray) -> list[DetectedFace]: ...
class FaceLandmarkDetector(Protocol):
    def landmarks(self, frame: np.ndarray, bbox: BoundingBox) -> list[tuple[float, float]]: ...
class FacePoseEstimator(Protocol):
    def estimate(self, frame: np.ndarray, landmarks: list[tuple[float, float]]) -> HeadPose: ...
class FaceEmbedder(Protocol):
    model_name: str
    model_version: str
    embedding_dimension: int
    def embed(self, face_image: np.ndarray) -> np.ndarray: ...
class VisionEngine(Protocol):
    model_name: str
    model_version: str
    embedding_dimension: int
    def analyze(self, frame: np.ndarray) -> list[DetectedFace]: ...
