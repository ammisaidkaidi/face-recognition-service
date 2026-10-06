import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA="""
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS people(id TEXT PRIMARY KEY,name TEXT NOT NULL,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS face_samples(id TEXT PRIMARY KEY,person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,embedding BLOB NOT NULL,embedding_dim INTEGER NOT NULL,embedding_model TEXT NOT NULL,embedding_version TEXT NOT NULL,quality_score REAL NOT NULL,yaw REAL NOT NULL,pitch REAL NOT NULL,roll REAL NOT NULL,created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS enrollment_sessions(id TEXT PRIMARY KEY,person_id TEXT NOT NULL REFERENCES people(id) ON DELETE CASCADE,status TEXT NOT NULL,accepted_samples INTEGER NOT NULL DEFAULT 0,created_at TEXT NOT NULL,updated_at TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_samples_person ON face_samples(person_id);
"""
class Database:
    def __init__(self,url:str):
        if not url.startswith("sqlite:///"): raise ValueError("Only sqlite:/// URLs are supported in this deployment")
        self.path=url.removeprefix("sqlite:///")
        if self.path != ":memory:": Path(self.path).parent.mkdir(parents=True,exist_ok=True)
    @contextmanager
    def connect(self):
        con=sqlite3.connect(self.path,check_same_thread=False); con.row_factory=sqlite3.Row; con.execute("PRAGMA foreign_keys=ON")
        try: yield con; con.commit()
        except Exception: con.rollback(); raise
        finally: con.close()
    def initialize(self):
        with self.connect() as con: con.executescript(SCHEMA)
