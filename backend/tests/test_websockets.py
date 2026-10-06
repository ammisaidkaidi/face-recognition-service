def test_enroll_then_identify(client,jpeg):
    pid=client.post("/api/v1/people",json={"name":"Grace"}).json()["id"]
    sid=client.post(f"/api/v1/people/{pid}/enrollment").json()["id"]
    with client.websocket_connect(f"/ws/v1/enrollment/{sid}") as ws:
        ws.send_bytes(jpeg); result=ws.receive_json(); assert result["accepted"]; assert result["state"]=="COMPLETE"
    with client.websocket_connect("/ws/v1/identify") as ws:
        ws.send_bytes(jpeg); result=ws.receive_json(); assert result["faces"][0]["status"]=="known"; assert result["faces"][0]["name"]=="Grace"

def test_malformed_frame_is_controlled(client):
    with client.websocket_connect("/ws/v1/identify") as ws:
        ws.send_bytes(b"not-an-image"); result=ws.receive_json(); assert result["code"]=="INVALID_FRAME"
