from uuid import uuid4
import numpy as np
from app.services.matcher import CosineFaceMatcher
from app.services.stability import IdentitySmoother

def test_match_threshold_does_not_force_match():
    pid=uuid4(); m=CosineFaceMatcher(.1)
    assert m.match(np.array([1.,0.]),[(pid,"A",np.array([0.,1.]))]).person_id is None
    assert m.match(np.array([1.,0.]),[(pid,"A",np.array([1.,0.]))]).person_id==pid

def test_identity_smoothing():
    s=IdentitySmoother(3,2); assert s.update("a") is None; assert s.update("a") is None; assert s.update("a")=="a"
    assert s.update(None)=="a"; assert s.update(None) is None
