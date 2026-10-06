import json,logging,time,uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from fastapi import FastAPI,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import Settings,get_settings
from app.storage.database import Database
from app.repositories.people_repository import SqlitePeopleRepository
from app.repositories.embedding_repository import SqliteEmbeddingRepository
from app.repositories.enrollment_repository import SqliteEnrollmentRepository
from app.services.adapters.insightface_adapter import InsightFaceEngine
from app.services.adapters.fake_adapter import FakeVisionEngine
from app.services.quality import QualityGate
from app.services.matcher import CosineFaceMatcher
from app.services.recognition_pipeline import RecognitionPipeline
from app.services.enrollment import EnrollmentService
from app.api.routes_health import router as health_router
from app.api.routes_people import router as people_router
from app.api.websockets import router as ws_router

log=logging.getLogger("app")
@dataclass
class Container: db:object; people:object; embeddings:object; sessions:object; engine:object; quality:object; matcher:object; pipeline:object; enrollment:object

def build_container(s:Settings):
    db=Database(s.database_url); db.initialize(); people=SqlitePeopleRepository(db); embeddings=SqliteEmbeddingRepository(db); sessions=SqliteEnrollmentRepository(db)
    engine=FakeVisionEngine() if s.vision_backend=="fake" else InsightFaceEngine(s.model_name,s.model_root,s.model_version,s.providers,s.detection_size)
    quality=QualityGate(s.min_face_size,s.min_sharpness,s.min_brightness,s.max_brightness,s.max_abs_yaw,s.max_abs_pitch)
    matcher=CosineFaceMatcher(s.recognition_threshold); pipeline=RecognitionPipeline(engine,embeddings,matcher,quality)
    enrollment=EnrollmentService(engine,people,embeddings,sessions,quality,s.enrollment_min_samples,s.enrollment_max_samples,s.pose_diversity_degrees)
    return Container(db,people,embeddings,sessions,engine,quality,matcher,pipeline,enrollment)

def create_app(settings:Settings|None=None,container=None):
    s=settings or get_settings()
    @asynccontextmanager
    async def lifespan(app):
        if not hasattr(app.state,"container"): app.state.container=container or build_container(s)
        yield
    app=FastAPI(title="Face Recognition Service",version="1.0.0",docs_url="/docs" if s.app_env!="production" else None,redoc_url=None,lifespan=lifespan)
    app.state.settings=s
    if container: app.state.container=container
    app.add_middleware(CORSMiddleware,allow_origins=s.cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
    @app.middleware("http")
    async def operational_logging(request:Request,call_next):
        request_id=request.headers.get("x-request-id",str(uuid.uuid4())); start=time.perf_counter()
        response=await call_next(request); response.headers["x-request-id"]=request_id
        log.info(json.dumps({"request_id":request_id,"operation":f"{request.method} {request.url.path}","status":response.status_code,"processing_time_ms":round((time.perf_counter()-start)*1000,2)}))
        return response
    @app.exception_handler(Exception)
    async def unhandled(request,exc):
        log.exception("Unhandled error",extra={"path":request.url.path}); return JSONResponse(500,{"detail":{"code":"INTERNAL_ERROR","message":"Internal service error"}})
    app.include_router(health_router,prefix="/api/v1"); app.include_router(people_router,prefix="/api/v1"); app.include_router(ws_router)
    return app
app=create_app()
