from dataclasses import dataclass
from uuid import UUID
from .face import BoundingBox, HeadPose

@dataclass(frozen=True, slots=True)
class RecognitionResult:
    status: str
    person_id: UUID | None
    name: str | None
    confidence: float
    distance: float | None
    bbox: BoundingBox
    landmarks: list[tuple[float, float]]
    pose: HeadPose
