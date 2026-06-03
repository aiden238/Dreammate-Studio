# Phase 17 — Non-Goals

```
✗ PKM/RAG Orchestrator 전체(6 scope/BM25/trend 수집/instruction search) — 본 phase 는 개인+브랜드
  구속 주입 1차만. series/global/trend/instruction 고도화는 후속(제안서 §9 고도화).
✗ 자동 promotion — feedback→PKM 자동 승격 금지(ADR-031 NG12 계승). 적재는 수동/pending 까지.
✗ commercial_viral 모드 — Phase 18+.
✗ 영상 제작 기능 — product_boundary 영구 non-goal.
✗ output_schema 출력 구조 변경 — 주입은 입력(프롬프트)측. 출력 tier(compact/rich/director)는 불변.
✗ 운영 default 경로 강제 변경 — 익명/무메모리 경로 byte-identical (gated).
✗ user_locked 자동 갱신 — is_user_locked 항목 자동 덮어쓰기 금지(제안서 §6.2).
```

## 회피할 함정

- **scope creep**: orchestrator 전체로 번지지 않기 — 개인+브랜드 구속 주입에 한정.
- **회귀**: 신원/메모리 없는 기존 흐름이 1바이트라도 바뀌면 안 됨 (gated 필수).
- **PII/격리**: brand_memory 는 RLS 격리분만 로드. 교차 계정 노출 0.
