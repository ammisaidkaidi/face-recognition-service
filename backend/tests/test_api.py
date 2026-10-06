def test_health(client):
    body=client.get("/api/v1/health").json(); assert body["status"]=="ok"; assert body["vision_backend"]=="fake"
def test_person_lifecycle(client):
    made=client.post("/api/v1/people",json={"name":"Ada Lovelace"}); assert made.status_code==201
    pid=made.json()["id"]; assert client.get(f"/api/v1/people/{pid}").json()["name"]=="Ada Lovelace"
    assert len(client.get("/api/v1/people").json())==1
    assert client.delete(f"/api/v1/people/{pid}").status_code==204
    assert client.get(f"/api/v1/people/{pid}").status_code==404

def test_management_auth(tmp_path):
    from fastapi.testclient import TestClient
    from app.config import Settings
    from app.main import create_app,build_container
    s=Settings(database_url=f"sqlite:///{tmp_path}/auth.db",vision_backend="fake",api_key="secret")
    with TestClient(create_app(s,build_container(s))) as c:
        assert c.get("/api/v1/people").status_code==401
        assert c.get("/api/v1/people",headers={"x-api-key":"secret"}).status_code==200
