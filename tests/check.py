"""R6용 스모크: python3.12.exe tests/check.py (Windows는 python 대신 python3.12.exe 사용)"""
import sys
sys.path.insert(0, ".")
from backend.main import app
from fastapi.testclient import TestClient

c = TestClient(app)
assert c.get("/api/health").json() == {"ok": True}, "health 실패"
assert c.get("/").status_code == 200, "index 실패"
v = c.post("/api/vision/explain", json={"mock_keyword": "결제"}).json()
assert "say_text" in v, "vision 실패"
s = c.post("/api/speech/intent", json={"transcript": "처음으로"}).json()
assert s["intent"] == "go_back", "speech 실패"
print("ALL OK - localhost:3000 스켈레톤 정상")
