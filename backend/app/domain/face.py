from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
import numpy as np

@dataclass(frozen=True, slots=True)
class BoundingBox:
    x: int; y: int; width: int; height: int

@dataclass(frozen=True, slots=True)
class HeadPose:
    yaw: float; pitch: float; roll: float

@dataclass(frozen=True, slots=True)
class DetectedFace:
    bbox: BoundingBox
    landmarks: list[tuple[float, float]]
    pose: HeadPose
    embedding: np.ndarray | None = None
    detection_score: float = 0.0

@dataclass(frozen=True, slots=True)
class FaceSample:
    id: UUID
    person_id: UUID
    embedding: np.ndarray
    embedding_model: str
    embedding_version: str
    quality_score: float
    pose: HeadPose
    created_at: datetime
