# R2 Backend-Python — `opencode/nemotron-3.5-lightning-free`
- 스택: FastAPI + uvicorn, port 3000, `backend/main.py` 단일 진입.
- 엔드포인트: `GET /`, `GET /api/health`, `POST /api/vision/explain`, `POST /api/speech/intent`.
- 원칙: HTML 서빙 포함 (StaticFiles), 이미지 미저장, MOCK 모드 지원.
