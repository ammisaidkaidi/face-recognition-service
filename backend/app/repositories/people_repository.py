from datetime import datetime, timezone
from uuid import UUID, uuid4
from app.domain.person import Person

class SqlitePeopleRepository:
    def __init__(self,db): self.db=db
    def create(self,name:str)->Person:
        now=datetime.now(timezone.utc); person=Person(uuid4(),name.strip(),now,now,True)
        with self.db.connect() as c: c.execute("INSERT INTO people VALUES(?,?,?,?,?)",(str(person.id),person.name,now.isoformat(),now.isoformat(),1))
        return person
    def list(self,include_inactive=False)->list[Person]:
        sql="SELECT * FROM people"+("" if include_inactive else " WHERE active=1")+" ORDER BY created_at"
        with self.db.connect() as c: rows=c.execute(sql).fetchall()
        return [self._map(r) for r in rows]
    def get(self,person_id:UUID,include_inactive=False)->Person|None:
        with self.db.connect() as c: r=c.execute("SELECT * FROM people WHERE id=?"+("" if include_inactive else " AND active=1"),(str(person_id),)).fetchone()
        return self._map(r) if r else None
    def deactivate(self,person_id:UUID)->bool:
        now=datetime.now(timezone.utc).isoformat()
        with self.db.connect() as c:
            cur=c.execute("UPDATE people SET active=0,updated_at=? WHERE id=? AND active=1",(now,str(person_id)))
            if cur.rowcount: c.execute("DELETE FROM face_samples WHERE person_id=?",(str(person_id),))
            return bool(cur.rowcount)
    @staticmethod
    def _map(r): return Person(UUID(r["id"]),r["name"],datetime.fromisoformat(r["created_at"]),datetime.fromisoformat(r["updated_at"]),bool(r["active"]))
