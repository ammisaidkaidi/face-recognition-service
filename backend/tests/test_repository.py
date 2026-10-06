import numpy as np,pytest
from app.domain.face import HeadPose
from app.repositories.embedding_repository import IncompatibleEmbeddingError

def test_embedding_roundtrip(app):
    c=app.state.container; person=c.people.create("Test"); v=np.arange(c.engine.embedding_dimension,dtype=np.float32)
    c.embeddings.add(person.id,v,c.engine.model_name,c.engine.model_version,1.0,HeadPose(1,2,3))
    stored=c.embeddings.candidates(c.engine.model_name,c.engine.model_version,len(v)); np.testing.assert_array_equal(stored[0][2],v)
    with pytest.raises(IncompatibleEmbeddingError): c.embeddings.candidates(c.engine.model_name,c.engine.model_version,len(v)+1)
