# R6 Bugfix Report (2026-10-08)

역할: R6 QA-Bugfix / 모델: opencode/fledge-alpha-free 관점
대상: `backend/main.py`, `frontend/index.html`, `tests/check.py`

## 1. 테스트 결과 (수정 전)

| 항목 | 방법 | 결과 |
|---|---|---|
| `python3.12.exe tests/check.py` | TestClient | ALL OK (exit 0). 단, 한글 로그가 Windows 콘솔(cp949)에서 깨져 보임 — 앱 버그 아님 |
| 실서버 `GET /api/health` | 서버 기동 후 urllib | 200 `{"ok":true}` |
| 실서버 `GET /` | 서버 기동 후 urllib | 200 `text/html; charset=utf-8` (한글 UTF-8 정상) |
| `POST /api/vision/explain {"image_b64":...}` | urllib | 200, `say_text` 정상 |
| `POST /api/vision/explain {"image_base64":...}` (프론트가 보내던 키) | urllib | **200이지만 이미지 데이터가 무시됨 (pydantic extra 무시) — 치명적 불일치** |
| 5MB 초과 이미지 | urllib | 413 정상 (백엔드) — 단 프론트에 413 전용 안내 없음 |
| CORS preflight (OPTIONS + Origin) | urllib | 200, `Access-Control-Allow-Origin: *` — 정상 |
| `PORT=3001` 환경변수 | env override 기동 | 수정 전: 무시되고 3000 고정 (포트 충돌 시 대응 불가) |

## 2. 발견 버그 및 수정 내역

### B1 (치명) — fetch 필드명 불일치: 프론트 `image_base64` vs 백엔드 `image_b64`
- 증상: `captureAndExplain()`이 촬영 이미지를 `image_base64` 키로 전송 → 백엔드 `VisionReq`는
  `image_b64`만 읽으므로 이미지 페이로드가 조용히 버려짐. 겉으로는 200 OK라서 발견이 어려움.
- 수정:
  - `frontend/index.html`: 전송 키를 `image_b64`로 변경 (정규 키 일치) — `file_path:line_number` 기준 `frontend/index.html:70`
  - `backend/main.py`: 구 키 호환용 `image_base64` 필드 추가 + `image_data()` 병합 메서드로 양쪽 키 모두 수신
    (`backend/main.py:39-46`, `vision_explain`에서 `req.image_data()` 사용)

### B2 — 413 (image_b64 5MB 초과) 프론트 미처리
- 증상: 백엔드는 413을 올바로 반환하나 프론트는 일반 연결 오류 문구만 표시.
- 수정: `frontend/index.html:70` `captureAndExplain()`에 `r.status===413` 분기 추가 —
  "사진이 너무 커서 보낼 수 없어요. 다시 한 번 촬영 버튼을 눌러주세요." + 음성 안내.

### B3 — 포트 충돌 대응 불가 (PORT 하드코딩)
- 증상: `PORT = 3000` 고정. 3000번 사용 중이면 기동 실패 외에 대안 없음.
- 수정: `backend/main.py` → `PORT = int(os.getenv("PORT", "3000"))`. 검증: `PORT=3001` 기동 후 `/api/health` 200 확인.

### B4 (경미) — 카메라 권한 메시지 단일화
- 증상: 권한 거부/카메라 없음/기타 오류가 모두 동일 문구.
- 수정: `startCam()`에서 `NotAllowedError`/`SecurityError`(권한), `NotFoundError`/`OverconstrainedError`(장치 없음) 구분 안내.
  기존 권한 안내 문구는 그대로 유지 (fallback 포함).

### 점검 후 이상 없음 (수정 불필요)
- CORS: `allow_origins=["*"] + allow_credentials=False` 조합 유효. preflight 200 + `ACAO: *` 실측.
- 한글 UTF-8: `/` 응답 `text/html; charset=utf-8`, JSON 한글 정상. `<meta charset="utf-8">` 존재.
  콘솔 로그 깨짐은 Windows cp949 출력 인코딩 문제이며 앱 응답과 무관.

## 3. 재검증 (수정 후)

| 항목 | 결과 |
|---|---|
| `python3.12.exe tests/check.py` | ALL OK (exit 0) |
| 실서버 `GET /api/health` / `GET /` | 200 / 200 (`charset=utf-8`) |
| `POST {"image_b64":...}` (정규 키) | 200, `say_text` 정상 |
| `POST {"image_base64":...}` (구 키 호환) | 200, `say_text` 정상 (하위호환 확보) |
| 5MB 초과 | 413 확인 |
| `PORT=3001` 기동 | `/api/health` 200 확인 |
| 프론트 전송 키 grep | `image_b64` 전송 + `413` 분기 존재 확인 |

## 4. 잔여 리스크 / 후속 제안
- `canvas.toDataURL('image/jpeg', 0.8)` 전체 dataURL(접두사 포함)을 길이 제한에 포함 — 현행 5MB 기준과 일관되나,
  추후 dataURL 접두사 제외 길이로 바꾸려면 백/프론트 합의 필요.
- Windows 콘솔 한글 로그 가독성: `logging` 포맷 변경 불필요하나, 필요 시 `PYTHONUTF8=1` 또는
  `chcp 65001` 사용을 개발 가이드에 명시 권장.
