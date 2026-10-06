from datetime import datetime
from typing import Literal
from uuid import UUID
from pydantic import BaseModel
class EnrollmentSessionOut(BaseModel):
    id:UUID; person_id:UUID; status:str; accepted_samples:int; created_at:datetime; updated_at:datetime
class EnrollmentFrameOut(BaseModel):
    type:Literal["enrollment"]="enrollment"; accepted:bool; reason:str|None=None; state:str
    accepted_samples:int; required_samples:int; pose_bucket:str|None=None
