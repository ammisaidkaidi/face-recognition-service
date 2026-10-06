import cv2,numpy as np,pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app,build_container
@pytest.fixture
def settings(tmp_path):
    return Settings(database_url=f"sqlite:///{tmp_path}/test.db",vision_backend="fake",min_face_size=16,min_sharpness=0,min_brightness=0,max_brightness=255,enrollment_min_samples=1,pose_diversity_degrees=0,stability_frames=1)
@pytest.fixture
def app(settings): return create_app(settings,build_container(settings))
@pytest.fixture
def client(app):
    with TestClient(app) as c: yield c
@pytest.fixture
def jpeg():
    image=np.zeros((100,100,3),dtype=np.uint8); image[:,:50]=(40,80,120); image[:,50:]=(160,200,240)
    ok,data=cv2.imencode(".jpg",image); assert ok; return data.tobytes()
