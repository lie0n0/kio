"""R2 Backend: python3.12.exe backend/main.py -> http://localhost:3000"""
import logging
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

PORT = int(os.getenv("PORT", "3000"))
ROOT = Path(__file__).resolve().parent.parent
FRONT = ROOT / "frontend"

# 5MB 제한 (base64 문자열 길이 기준)
MAX_IMAGE_B64_LEN = 5 * 1024 * 1024

# MOCK_VISION=1 이면 키워드 기반 목업 응답 (기본 1)
MOCK_VISION = os.getenv("MOCK_VISION", "1")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("kiosk-r2")

app = FastAPI(title="어르신 키오스크 도우미")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VisionReq(BaseModel):
    image_b64: str = Field(default="")
    # 구 프론트 호환: image_base64 키로 와도 받는다 (정규 키는 image_b64)
    image_base64: str = Field(default="")
    mock_keyword: str = Field(default="")

    def image_data(self) -> str:
        return self.image_b64 or self.image_base64 or ""


class SpeechReq(BaseModel):
    transcript: str = Field(default="")


def _vision_scenario(kw: str):
    """mock_keyword -> 5개 시나리오 중 하나. (steps, say_text) 반환."""
    k = (kw or "").strip()
    if not k:
        k = "시작"
    if any(s in k for s in ("관리자", "직원", "호출", "도움", "staff", "help")):
        return (
            ["관리자 호출 확인", "직원에게 알림", "자리에서 대기"],
            "직원을 불러드릴게요. 자리에 그대로 계시면 직원이 곧 와서 도와드릴 거예요.",
        )
    if any(s in k for s in ("영수증", "receipt")):
        return (
            ["영수증 출력 선택", "영수증 수령", "주문 완료"],
            "영수증 화면입니다. 영수증이 필요하시면 출력 버튼을 눌러주세요. 필요 없으시면 완료 버튼을 눌러주세요.",
        )
    if any(s in k for s in ("결제", "카드", "현금", "pay", "결재")):
        return (
            ["결제 방법 선택", "카드 투입", "완료 확인"],
            "결제 화면입니다. 카드로 결제하려면, 가운데 카드 결제 버튼을 눌러주세요.",
        )
    if any(s in k for s in ("주문", "메뉴", "장바구니", "옵션")):
        return (
            ["메뉴 선택", "옵션 선택", "장바구니 확인"],
            "주문 화면입니다. 드시고 싶은 메뉴 사진을 눌러주세요.",
        )
    # 시작 (기본): "시작/처음/매장/포장" 포함 또는 fallback
    return (
        ["매장/포장 선택", "메뉴 선택", "결제"],
        "첫 화면입니다. 매장에서 드시면 왼쪽 매장 버튼을, 가져가시면 오른쪽 포장 버튼을 눌러주세요.",
    )


def _speech_classify(t: str):
    """transcript -> 6종 intent 중 하나. (intent, reply) 반환."""
    s = (t or "").strip()
    if any(w in s for w in ("직원", "관리자", "사람", "호출", "도와")):
        return ("call_staff", "네, 직원을 불러드릴게요. 잠시만 자리에 계셔 주세요.")
    if "영수증" in s or "receipt" in s.lower():
        return ("receipt", "영수증이 필요하시군요. 결제 마지막에 영수증 출력 버튼을 눌러주세요.")
    if any(w in s for w in ("결제", "카드", "현금", "돈", "계산")):
        return ("how_to_pay", "결제는 카드나 현금으로 하실 수 있어요. 카드면 카드 넣는 곳을 알려드릴게요.")
    if any(w in s for w in ("처음", "뒤로", "이전", "돌아가")):
        return ("go_back", "네, 처음으로 돌아갈게요. 매장, 포장 버튼부터 다시 알려드릴게요.")
    if any(w in s for w in ("다시", "천천히", "반복", "못 들")):
        return ("repeat", "네, 천천히 다시 말씀드릴게요. 화면을 카메라에 보여주세요.")
    return ("order_start", "네, 알겠습니다. 화면을 카메라에 보여주시면, 한 단계씩 알려드릴게요.")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.post("/api/vision/explain")
def vision_explain(req: VisionReq):
    img = req.image_data()
    if len(img) > MAX_IMAGE_B64_LEN:
        log.warning("vision image_b64 too large: %d chars", len(img))
        raise HTTPException(status_code=413, detail="image_b64 exceeds 5MB limit")
    kw = req.mock_keyword or "시작"
    if MOCK_VISION != "1":
        # 실제 OCR/VLM 연동 전까지는 목업으로 폴백 (환경변수만으로 차단하지 않음)
        log.info("MOCK_VISION=%s, fallback to mock (kw=%s)", MOCK_VISION, kw)
    steps, say = _vision_scenario(kw)
    log.info("vision kw=%r -> steps=%s", kw, steps)
    return {"steps": steps, "current_step": steps[0], "say_text": say}


@app.post("/api/speech/intent")
def speech_intent(req: SpeechReq):
    intent, reply = _speech_classify(req.transcript)
    log.info("speech %r -> %s", req.transcript, intent)
    return {"intent": intent, "reply_text": reply, "action": "speak+show"}


if FRONT.exists():
    app.mount("/static", StaticFiles(directory=str(FRONT)), name="static")


@app.get("/")
def index():
    idx = FRONT / "index.html"
    if idx.exists():
        return FileResponse(str(idx))
    return JSONResponse({"msg": "frontend/index.html 없음. R3 작업 필요", "health": "/api/health"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app" if (ROOT / "backend/__init__.py").exists() else app,
        host="127.0.0.1",
        port=PORT,
        reload=False,
    )
