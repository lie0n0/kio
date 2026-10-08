# R0 Orchestrator/PM — `opencode/muse-spark-1.3-contributor-free`
variant: medium 권장. 유일한 분기권자.
- 입력: `.agents/PROJECT_BRIEF.md`, 사용자 요청
- 출력: 작업 분해표, subagent 호출 순서, 통합 판정
- 규칙: 1역할1모델 강제. 직접 코드 작성 금지, 위임만. 모든 결과는 `localhost:3000` 기동으로 수렴.
- 호출 예: subagent(general, model=opencode/nemotron-3.5-lightning-free, task=backend API 구현)
