# Phase 18 — 진입 4점검 (phase-start §6)

## 1. Assumptions
### 1.1 확정
- 제안서 설계 확정(LLM 동적 / 카드+자유입력 / 후보3×방향+PKM 연결).
- Phase 17 brand_memory/PkmRepo 재사용 가능(시드 대상 존재).
- **audit_naming 통과 (2026-06-04, 0 drift)**.
- gated/additive: 신규 진입만, 기존 Quick/Discovery/planning byte-identical.
### 1.2 불확실
- U1 N고개 상한값 / U2 루프 비용·지연 / U3 세션 상태 보관 방식 — S2/S5에서 확정.

## 2. Simplest Slice (3회 압축)
```
1차: agent + endpoint + frontend + planning연결 + PKM시드.
2차: topic_discovery agent ask/finalize 2모드 + mock test.
3차: agent(Q&A 상태) → ask: 다음 질문 1개 + 카드 2~4개(or 종료) / finalize: 후보 3×방향.
     ← S1 = agent 단독(mock) — endpoint/frontend 전.
```
→ S1(agent) → S2(endpoint+상태) → S3(frontend) → S4(planning+PKM 시드) → S5(e2e+close).

## 3. Surgical Scope
- editable: `agents/topic_discovery.py`(신규) + tests + (S2)endpoint + (S3)frontend + (S4)planning/brand_memory wiring + phase/state/meta.
- read-only(→절차): `prompt_registry.md`(prompt-version-review로 P-신규 등록) · `docs/contracts/*`.
- forbidden: archive / commercial_viral / 2nd brain / 영상 제작.
- ★ Sub-agent P-X1 §SELF-VERIFICATION 의무.

## 4. Verification
- S1: 단위 test(mock LLM) — ask 질문+카드 스키마 / finalize 후보3 스키마 / 종료신호.
- 각 슬라이스: behavior-preserving(기존 pytest 608 green) + audit 0.
