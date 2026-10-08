# R4 Vision-Kiosk OCR — `opencode/space-bunny-free`
- variants: 개발 low/medium, 실측 high/max.
- 입력: base64 JPEG 프레임 → 출력: {texts[], buttons[], current_step, say_text}.
- 초기 목업 허용 (키워드 매칭), 이후 Tesseract/EasyOCR 또는 외부 Vision API로 교체. 조명/반사 대응 전처리 포함.
