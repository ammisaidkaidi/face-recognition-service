from datetime import datetime, timezone
from uuid import UUID, uuid4
import numpy as np
from app.domain.face import FaceSample, HeadPose

class IncompatibleEmbeddingError(ValueError): pass
class SqliteEmbeddingRepository:
    def __init__(self,db): self.db=db
    def add(self,person_id:UUID,embedding:np.ndarray,model:str,version:str,quality:float,pose:HeadPose)->FaceSample:
        vector=np.asarray(embedding,dtype=np.float32).reshape(-1); now=datetime.now(timezone.utc); sid=uuid4()
        with self.db.connect() as c: c.execute("INSERT INTO face_samples VALUES(?,?,?,?,?,?,?,?,?,?,?)",(str(sid),str(person_id),vector.tobytes(),len(vector),model,version,quality,pose.yaw,pose.pitch,pose.roll,now.isoformat()))
        return FaceSample(sid,person_id,vector,model,version,quality,pose,now)
    def candidates(self,model:str,version:str,dimension:int)->list[tuple[UUID,str,np.ndarray]]:
        with self.db.connect() as c:
            rows=c.execute("SELECT f.*,p.name FROM face_samples f JOIN people p ON p.id=f.person_id WHERE p.active=1 AND f.embedding_model=? AND f.embedding_version=?",(model,version)).fetchall()
        out=[]
        for r in rows:
            if r["embedding_dim"] != dimension: raise IncompatibleEmbeddingError("Stored embedding dimension is incompatible")
            out.append((UUID(r["person_id"]),r["name"],np.frombuffer(r["embedding"],dtype=np.float32).copy()))
        return out
    def count(self,person_id:UUID)->int:
        with self.db.connect() as c: return int(c.execute("SELECT COUNT(*) FROM face_samples WHERE person_id=?",(str(person_id),)).fetchone()[0])
