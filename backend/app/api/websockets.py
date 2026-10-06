import asyncio,time
from dataclasses import asdict
from uuid import UUID
from fastapi import APIRouter,WebSocket,WebSocketDisconnect
from app.services.image import FrameError,decode_frame
from app.services.stability import IdentitySmoother
router=APIRouter()

async def receive_limited(ws,settings):
    payload=await ws.receive_bytes()
    return decode_frame(payload,settings.max_frame_bytes)

def recognition_json(results):
    return {"type":"recognition","timestamp":time.time(),"faces":[{"status":r.status,"person_id":str(r.person_id) if r.person_id else None,"name":r.name,"confidence":r.confidence,"distance":r.distance,"bbox":asdict(r.bbox),"head_pose":asdict(r.pose),"rotation":{"x":r.pose.pitch,"y":r.pose.yaw,"z":r.pose.roll},"landmarks":[list(x) for x in r.landmarks]} for r in results]}

@router.websocket("/ws/v1/identify")
async def identify(ws:WebSocket):
    await ws.accept(); c=ws.app.state.container; settings=ws.app.state.settings; last=0.0; smoothers=[]
    try:
        while True:
            now=time.monotonic(); frame=await receive_limited(ws,settings)
            wait=(1/settings.process_fps)-(now-last)
            if wait>0: await asyncio.sleep(wait)
            results=await asyncio.to_thread(c.pipeline.process,frame); last=time.monotonic()
            while len(smoothers) < len(results): smoothers.append(IdentitySmoother(settings.stability_frames,settings.unknown_hysteresis_frames))
            for i, result in enumerate(results):
                raw = str(result.person_id) if result.person_id else None
                stable = smoothers[i].update(raw)
                if stable != raw:
                    results[i] = type(result)("unknown",None,None,0.0,result.distance,result.bbox,result.landmarks,result.pose)
            await ws.send_json(recognition_json(results))
    except FrameError as e: await ws.send_json({"type":"error","code":e.code,"message":str(e)}); await ws.close(code=1003)
    except WebSocketDisconnect: pass
    except Exception: await ws.send_json({"type":"error","code":"MODEL_ERROR","message":"Frame processing failed"}); await ws.close(code=1011)

@router.websocket("/ws/v1/enrollment/{session_id}")
async def enroll(ws:WebSocket,session_id:UUID):
    c=ws.app.state.container; settings=ws.app.state.settings
    if not c.sessions.get(session_id): await ws.close(code=1008,reason="INVALID_ENROLLMENT_SESSION"); return
    await ws.accept()
    try:
        while True:
            frame=await receive_limited(ws,settings); result=await asyncio.to_thread(c.enrollment.process,session_id,frame)
            await ws.send_json({"type":"enrollment",**result})
    except FrameError as e: await ws.send_json({"type":"error","code":e.code,"message":str(e)}); await ws.close(code=1003)
    except WebSocketDisconnect: pass
    except Exception: await ws.send_json({"type":"error","code":"MODEL_ERROR","message":"Frame processing failed"}); await ws.close(code=1011)
