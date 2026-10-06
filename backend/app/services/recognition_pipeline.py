import time
from app.domain.recognition import RecognitionResult
from app.services.image import crop

class RecognitionPipeline:
    def __init__(self,engine,embeddings,matcher,quality):
        self.engine=engine; self.embeddings=embeddings; self.matcher=matcher; self.quality=quality
    def process(self,frame):
        faces=self.engine.analyze(frame)
        candidates=self.embeddings.candidates(self.engine.model_name,self.engine.model_version,self.engine.embedding_dimension)
        results=[]
        for face in faces:
            ok,_,_=self.quality.evaluate(face,crop(frame,face.bbox))
            if not ok: continue
            match=self.matcher.match(face.embedding,candidates)
            results.append(RecognitionResult("known" if match.person_id else "unknown",match.person_id,match.name,match.confidence,match.distance,face.bbox,face.landmarks,face.pose))
        return results
