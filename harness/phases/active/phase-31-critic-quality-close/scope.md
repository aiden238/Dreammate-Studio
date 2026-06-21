# Phase 31 — scope

## Slices

### S1 — consensus-min 배선 (judge, additive gated)
- `critic_judge_provider` 에 `consensus_min` 모드 추가(또는 별 flag): OpenAI + Claude 둘 다
  채점 → **더 엄격한 verdict 채택**(reject > revise > approve 순, 단조 — 절대 더 약해지지 않음).
- gated default-off(기존 `openai` default 유지) + ANTHROPIC_API_KEY 없으면 안전 차단(graceful/ValueError).
- 테스트: consensus 선택 로직 + OFF byte-identical 회귀. pytest green 유지.
- 근거: eval/regression_results/2026-06-21-cross-provider-judge.md §consensus-min(안전 default 후보).

### S2 — P-006 prompt-version-review (생성 프롬프트 개선)
- `prompt-version-review` 절차로 P-006(director 생성 프롬프트) 개선:
  검증된 표면 레버만 — 후크 각색 + 고유명/숫자 구체화 + 타깃 "예:" 명시.
  ★ 가드: 미검증 사실은 `추정/예시:` 라벨 강제 + 과확장(단일→다중 남발) 금지.
- semver bump + golden_set 회귀(cross-provider judge로 Δ측정) + verdict 비퇴행 + 할루시네이션 단정 0 게이트.
- 근거: 2026-06-21-improved-output-ab.md §7 stub + codex 리포트 §7 P-006 stub.

### S3 — golden_set RAG ON/OFF 품질측정 (2c 후속, judge 사용)
- golden_set 케이스를 use_rag=True/False 두 조건으로 생성 → cross-provider Claude judge 채점 → 비교.
- RAG_EMBEDDING_PROVIDER=gemini(8건 코퍼스, 라이브 검증됨 6ba1aaf) 기준.
- 판정: 개선/중립/하락. 5% 이상 하락 시 use_rag 보류 신호(candidate-ready.md A9 결단 기준).

### S4 — 릴리스: research + project-2 → main 머지/push
- phase-29-agent-ux 의 누적 커밋(research 5 + project-2 결착 + 본 phase)을 main에 통합.
- 두-워크트리(OneDrive ↔ dreammate-p27) 재분기 주의 — 머지 순서 조율 + OneDrive 트리 main 정렬.
- ★ outward-facing(push) — 사용자 승인 하에 진행.

## 영향 영역
- `backend/fastapi/agents/critic.py`(consensus 로직) · `config.py`(flag) · `tests/`
- `ai_system/prompts/prompt_registry.md`(P-006) · `backend/fastapi/agents/planning.py`(프롬프트)
- `eval/golden_set.md` · `eval/regression_results/` · `scripts/`(측정 재현)
- git: phase-29-agent-ux → main

## 의존성
- cross-provider judge 계측기(72b57a9, 배선됨) · RAG Gemini(6ba1aaf, 라이브) · 실 LLM/Supabase(비용 opt-in).
