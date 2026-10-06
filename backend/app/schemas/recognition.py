from typing import Literal
from uuid import UUID
from pydantic import BaseModel
class BBoxOut(BaseModel): x:int; y:int; width:int; height:int
class PoseOut(BaseModel): yaw:float; pitch:float; roll:float
class RotationOut(BaseModel): x:float; y:float; z:float
class FaceOut(BaseModel):
    status:Literal["known","unknown"]; person_id:UUID|None=None; name:str|None=None
    confidence:float; distance:float|None=None; bbox:BBoxOut; head_pose:PoseOut; rotation:RotationOut
    landmarks:list[list[float]]
class RecognitionMessage(BaseModel):
    type:Literal["recognition"]="recognition"; timestamp:float; faces:list[FaceOut]
class ErrorMessage(BaseModel):
    type:Literal["error"]="error"; code:str; message:str
