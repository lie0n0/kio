# AGENTS.md — 어르신 키오스크 도우미 AI 오케스트레이션 중심

> 위치: `.agents/AGENTS.md` / 루트 `AGENTS.md`는 이 파일을 가리킴
> 스택: Python(FastAPI) + 순수 HTML/CSS/JS / 테스트: `http://localhost:3000`
> 원칙: **1 역할 = 1 무료모델**, 중복 배정 금지. Orchestrator가 분기, 각 역할은 subagent로 실행.

## 1. 프로젝트 목적
어르신의 키오스크 사용을 돕는 AI:
1. 카메라로 키오스크 화면 촬영 → 문자/버튼/단계 인식 (OCR + Vision)
2. 스피치(TTS) + 메신저형 채팅으로 쉬운 설명 (큰 글자, 느린 말, 단계별 확인)
3. 사람 말(STT) 인식 → 요청대로 작업 안내 수행 ("처음으로", "결제 방법 알려줘")

## 2. 고정 조건
- C1. 서버+API는 Python 기반 (FastAPI 권장, `backend/main.py`)
- C2. Web UI는 HTML 구성 (`frontend/index.html`, 프레임워크 없이 동작)
- C3. 완성 후 필수 1회 버그수정 패스 + 예비테스트(개발환경 vs 실제환경 차이) 수행
- C4. `localhost:3000`에서 테스트 가능해야 함 (Python이 3000으로 서빙, HTML 포함)

## 3. 폴더 트리
```
.
├─ AGENTS.md                 # 루트 포인터
├─ .agents/
│  ├─ AGENTS.md              # 본 파일 (중심)
│  ├─ PROJECT_BRIEF.md
│  ├─ roles/*.md             # 8개 역할 정의
│  └─ workflows/*.md         # build / bugfix-pass / field-parity-test
├─ backend/  (main.py, requirements.txt, api/)
├─ frontend/ (index.html, app.js, style.css)
├─ docs/     (시나리오, 예비테스트 체크리스트)
└─ tests/    (API + E2E 체크)
```

## 4. 역할 ↔ 무료모델 매핑 (OpenCode Zen Free 8종, 2026-10-08 기준)

| # | 역할 | 모델 ID | 선정 이유 (강점) | 담당 |
|---|------|---------|-----------------|------|
| R0 | Orchestrator/PM | `opencode/muse-spark-1.3-contributor-free` | 균형 잡힌 지시이행, 현 세션 기본모델로 안정적 분기 | 작업 분해, 순서 제어, 1모델1역할 강제 |
| R1 | Architect | `opencode/longcat-2.5-preview-free` | Long context, Preview 세대의 설계 강점 | API 명세, 폴더 구조, 인터페이스 고정 |
| R2 | Backend-Python | `opencode/nemotron-3.5-lightning-free` | NVIDIA 계열 코딩/추론 + Lightning 속도 | FastAPI, `/api/*`, STT/OCR 연동 |
| R3 | Frontend-HTML | `opencode/mimo-v2.6-flash-free` | Flash급 UI 반복, 접근성 UI 강점 | 큰글자 메신저 UI, 카메라/마이크 연동 |
| R4 | Vision-Kiosk OCR | `opencode/space-bunny-free` | variants low~max 단계 조절 = 해상도/정밀도 조절에 적합, 멀티모달 추정 | 카메라 프레임 → 텍스트/버튼/단계 JSON |
| R5 | Speech-Dialog | `opencode/ling-3.1-flash-free` | Flash 저지연 대화, 짧은 발화 처리 강점 | STT→의도→TTS 스크립트, 어르신 말투 |
| R6 | QA-Bugfix | `opencode/fledge-alpha-free` | Alpha 에이전틱, high/max 변형으로 심층 추적 | 재현→수정→`localhost:3000` 검증 |
| R7 | Field-Test/Docs | `opencode/big-pickle` | 이색 네이밍 = 시나리오 기억성, 매뉴얼 작성용 | 예비테스트 시나리오, dev/prod 차이 리포트 |

> variants 사용: `space-bunny`는 저사양 low, 실측 max / `fledge-alpha`는 평소 low, 버그사냥 high,max / `muse-spark`는 orchestrator medium 권장.

## 5. 오케스트레이션 규칙
1. Orchestrator(R0)만 전체를 조망. 다른 역할은 자신의 `roles/*.md` 범위만 수행.
2. 실행은 병렬 subagent: `subagent(agent=general, model=<역할모델>)` 형태로 1역할 1호출.
3. 순서: R1 설계 확정 → R2+R3+R4+R5 병렬 구현 → R0 통합 → R6 버그수정 → R7 예비테스트.
4. 모든 API 변경은 R1 승인 필요. 프론트는 백엔드 스펙 없이 임의 fetch 금지.
5. `localhost:3000` 기동 실패 시 R6이 최우선 개입, R7이 환경차이 기록.
6. 어르신 UX 원칙: 글자 18pt+, 버튼 56px+, 한 화면 1질문, 모든 설명에 음성+텍스트 병행.

## 6. API 계약 (초안, R1이 확정)
- `GET /` → `frontend/index.html` 서빙 (3000포트 단일 기동)
- `POST /api/vision/explain` {image_b64} → {steps[], current_step, say_text}
- `POST /api/speech/intent` {transcript} → {intent, reply_text, action}
- `GET /api/health` → {ok:true}
- Web UI: 카메라 미리보기, 촬영 버튼, 메신저 로그, 음성듣기/말하기 버튼

## 7. 워크플로우
- `workflows/build.md`: 설계→구현→통합→기동
- `workflows/bugfix-pass.md`: 완성 후 1회 전수 버그수정
- `workflows/field-parity-test.md`: 개발 vs 실제(키오스크 실물, 조명, 네트워크) 차이 테스트

## 8. 다음 챕터 실행 명령
```
1. R1 Architect: API 명세 확정
2. R2+R3 병렬: backend/main.py + frontend/index.html 스켈레톤 → localhost:3000 기동 확인
3. R4+R5: vision/speech 목업 → 실연동
4. R6: 버그수정 패스
5. R7: 예비테스트 리포트 (docs/field-test.md)
```
