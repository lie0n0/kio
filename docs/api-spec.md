# API 명세 (R1 확정, 2026-10-08)

Base: `http://localhost:3000` / 서버: `backend/main.py` (FastAPI) / UI: `frontend/index.html`
인코딩: 요청/응답 모두 UTF-8, `Content-Type: application/json; charset=utf-8`. 한글 이스케이프 금지, 원문 그대로. TTS 발화문(`say_text`, `reply_text`)은 구어체 존댓말, 2문장 이내.
CORS: 동일 오리진 단일 기동이므로 기본 차단. 외부 테스트 필요 시 `CORSMiddleware allow_origins=["*"]` (개발 한정).
개인정보: `image_b64` 메모리 처리만, 디스크 저장 금지.

## GET / → 200 text/html
`frontend/index.html` 서빙. 파일 없으면 `200 {"msg","health"}` (R3 미완성 상태).

## GET /api/health → 200
Res: `{"ok": true}`

## POST /api/vision/explain
Req (`application/json`):
```json
{"image_b64": "string (data:image/... 또는 순수 base64, 빈 문자열 허용-목업)", "mock_keyword": "string (선택, 예: 시작|주문|결제)"}
```
Res 200:
```json
{"steps": ["string x N (N>=3)"], "current_step": "string (=steps[0])", "say_text": "string (어르신용 발화문)"}
```
목업 분기(`backend/main.py:28-39`): `결제` 포함→결제 3단계 / `주문` 포함→주문 3단계 / 그 외→첫 화면 3단계.

## POST /api/speech/intent
Req:
```json
{"transcript": "string (STT 결과, 예: 처음으로 돌아가줘)"}
```
Res 200:
```json
{"intent": "go_back|how_to_pay|repeat|order_start", "reply_text": "string", "action": "speak+show (고정)"}
```
분류(`backend/main.py:44-52`): `처음`→go_back / `결제`→how_to_pay / `다시|천천히`→repeat / 그 외→order_start (빈 문자열도 order_start).

## 에러코드
| 코드 | 조건 | body 예시 |
|------|------|-----------|
| 404 | 경로 오타 | `{"detail":"Not Found"}` |
| 405 | GET으로 POST 경로 호출 | `{"detail":"Method Not Allowed"}` |
| 422 | JSON 파싱 실패/타입 오류 | `{"detail":[...]}` |
| 500 | 서버 예외 | `{"detail":"Internal Server Error"}` |

프론트 규칙(R3): 모든 fetch는 `Content-Type: application/json`, `r.json()` 전 `r.ok` 확인, 실패 시 채팅 버블에 한글 에러 표시. 변경 시 R1 승인 필수 (AGENTS.md §5-4).
