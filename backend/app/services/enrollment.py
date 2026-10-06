from uuid import UUID
from app.services.image import crop

class EnrollmentService:
    def __init__(self,engine,people,embeddings,sessions,quality,min_samples,max_samples,diversity):
        self.engine=engine; self.people=people; self.embeddings=embeddings; self.sessions=sessions; self.quality=quality
        self.min_samples=min_samples; self.max_samples=max_samples; self.diversity=diversity; self._poses={}
    @staticmethod
    def bucket(yaw,pitch):
        if yaw < -10:return "left"
        if yaw > 10:return "right"
        if pitch < -8:return "up"
        if pitch > 8:return "down"
        return "front"
    def process(self,sid:UUID,frame)->dict:
        session=self.sessions.get(sid)
        if not session:return {"accepted":False,"reason":"INVALID_ENROLLMENT_SESSION","state":"FAILED","accepted_samples":0,"required_samples":self.min_samples}
        if session["status"]=="COMPLETE":return {"accepted":False,"reason":"ENROLLMENT_COMPLETE","state":"COMPLETE","accepted_samples":session["accepted_samples"],"required_samples":self.min_samples}
        faces=self.engine.analyze(frame)
        if len(faces)==0:return self._reject(session,"FACE_NOT_FOUND")
        if len(faces)>1:return self._reject(session,"MULTIPLE_FACES")
        face=faces[0]; ok,reason,score=self.quality.evaluate(face,crop(frame,face.bbox))
        if not ok:return self._reject(session,reason or "LOW_QUALITY")
        bucket=self.bucket(face.pose.yaw,face.pose.pitch); seen=self._poses.setdefault(str(sid),[])
        if any(abs(face.pose.yaw-y)<self.diversity and abs(face.pose.pitch-p)<self.diversity for y,p in seen):
            return self._reject(session,"DUPLICATE_POSE",bucket)
        self.embeddings.add(UUID(session["person_id"]),face.embedding,self.engine.model_name,self.engine.model_version,score,face.pose)
        seen.append((face.pose.yaw,face.pose.pitch)); count=session["accepted_samples"]+1
        state="COMPLETE" if count>=self.min_samples else "SAMPLE_ACCEPTED"
        self.sessions.update(sid,state,count)
        return {"accepted":True,"reason":None,"state":state,"accepted_samples":count,"required_samples":self.min_samples,"pose_bucket":bucket}
    def _reject(self,s,reason,bucket=None):
        self.sessions.update(UUID(s["id"]),"QUALITY_REJECTED",s["accepted_samples"])
        return {"accepted":False,"reason":reason,"state":"QUALITY_REJECTED","accepted_samples":s["accepted_samples"],"required_samples":self.min_samples,"pose_bucket":bucket}
