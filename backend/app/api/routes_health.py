from fastapi import APIRouter,Request
router=APIRouter(tags=["health"])
@router.get("/health")
def health(request:Request):
    c=request.app.state.container
    return {"status":"ok","environment":request.app.state.settings.app_env,"vision_backend":c.engine.model_name,"model_version":c.engine.model_version}
