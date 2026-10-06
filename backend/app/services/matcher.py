from dataclasses import dataclass
from uuid import UUID
import numpy as np

@dataclass(frozen=True)
class Match:
    person_id: UUID | None
    name: str | None
    distance: float | None
    confidence: float

class CosineFaceMatcher:
    def __init__(self, threshold: float): self.threshold=threshold
    def match(self, query: np.ndarray, candidates: list[tuple[UUID,str,np.ndarray]]) -> Match:
        if not candidates: return Match(None,None,None,0.0)
        q=query/(np.linalg.norm(query)+1e-12)
        scored=[(float(1-np.dot(q,e/(np.linalg.norm(e)+1e-12))),pid,name) for pid,name,e in candidates]
        distance,pid,name=min(scored,key=lambda x:x[0])
        confidence=max(0.0,min(1.0,1.0-distance/max(self.threshold,1e-9)))
        return Match(pid,name,distance,confidence) if distance<=self.threshold else Match(None,None,distance,confidence)
