from datetime import datetime,timezone
from uuid import UUID,uuid4
class SqliteEnrollmentRepository:
    def __init__(self,db): self.db=db
    def create(self,person_id:UUID)->dict:
        now=datetime.now(timezone.utc).isoformat(); sid=uuid4()
        with self.db.connect() as c: c.execute("INSERT INTO enrollment_sessions VALUES(?,?,?,?,?,?)",(str(sid),str(person_id),"WAITING",0,now,now))
        return self.get(sid)
    def get(self,sid:UUID)->dict|None:
        with self.db.connect() as c: r=c.execute("SELECT * FROM enrollment_sessions WHERE id=?",(str(sid),)).fetchone()
        return dict(r) if r else None
    def update(self,sid:UUID,status:str,count:int):
        now=datetime.now(timezone.utc).isoformat()
        with self.db.connect() as c: c.execute("UPDATE enrollment_sessions SET status=?,accepted_samples=?,updated_at=? WHERE id=?",(status,count,now,str(sid)))
