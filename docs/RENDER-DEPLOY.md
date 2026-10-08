# Render 배포 가이드

## 파일 시스템 (Render 전용)
- `requirements.txt` (루트, Render 기본 인식) ← canonical
- `backend/requirements.txt` (로컬용, 내용 동일 유지)
- `render.yaml` Blueprint: build `pip install -r requirements.txt`, start `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- `Procfile`: 동일 start 명령
- `.python-version`: `3.12.10`
- `backend/__init__.py`: `backend.main:app` import 고정
- `backend/main.py`: `host="0.0.0.0"`, `PORT=int(os.getenv("PORT","3000"))` → Render `$PORT` 자동 바인딩

## Render 설정
1. New → Web Service → 이 repo 연결
2. Build: `pip install -r requirements.txt`
3. Start: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
4. Env: `MOCK_VISION=1`, `PYTHON_VERSION=3.12.10`
5. Free 플랜: 첫 요청 wake-up 지연 정상, `/api/health`로 헬스체크

## 로컬 검증 (Render 명령 동일)
`$env:PORT=3001; python3.12.exe -m uvicorn backend.main:app --host 0.0.0.0 --port 3001`
→ `http://127.0.0.1:3001/api/health` true 확인
