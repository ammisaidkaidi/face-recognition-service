from fastapi import Header,HTTPException,Request,status

def container(request:Request): return request.app.state.container
async def management_auth(request:Request,x_api_key:str|None=Header(default=None)):
    key=request.app.state.settings.api_key
    if key and x_api_key != key: raise HTTPException(status.HTTP_401_UNAUTHORIZED,detail={"code":"UNAUTHORIZED","message":"Invalid API key"})
