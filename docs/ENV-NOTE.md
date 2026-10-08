# Windows Python 주의
- 이 PC는 `python`이 MS Store 스텁이라 `python3.12.exe`를 사용할 것.
- 기동: `python3.12.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 3000`
- 테스트: `python3.12.exe tests/check.py`
- `http://localhost:3000` 확인됨 (2026-10-08, /api/health + / 200).
