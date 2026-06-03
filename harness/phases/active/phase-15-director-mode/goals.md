# Phase 15 — Goals (director 모드 — output_mode 3rd tier)

## 한 줄 정의
`output_mode` 를 **compact / rich / director** 3-tier 로 일반화하고, **director**(rich + 연출·리텐션 강화 슬롯)를 **gated/additive** 로 추가한다. director 는 **LLM-only(PKM/RAG 데이터레이어 비의존)** 라 지금 빌드 가능하며, 사용자가 원한 "더 깊은 대본기획"의 1단계다. ★ OFF/compact/rich 경로 byte-identical(behavior-preserving).

## 기반
- project-1 PARKED 제안서 `meta/proposals/2026-06-03_commercial-viral-mode-design.md` §2.1(4-tier) + §3(P-006 mode 분기) + §4(critic) + §6(cost). director = rich↔commercial_viral 중간 깊이(데이터레이어 비의존, 제안서 §7.2).
- ★ 제안서 open issue #1(director 슬롯 경계) = 본 phase 에서 확정. open issue #2(flag→enum) = 본 phase S1.

## 목표
1. **output_mode enum 일반화**: 현 `rich_output_enabled: bool` → `output_mode: compact|rich|director`(default compact). ★ backward-compat — 기존 flag 흡수/공존, OFF/rich 경로 회귀 0.
2. **director 슬롯 additive**: `Plan` 에 `hook_system`(재후크 설계) + `retention_architecture`(리텐션 구조) + `scene_breakdown[]`(씬 분해, director-subset 필드) — 전부 Optional, `DIRECTOR_FIELDS` frozenset + model_dump 모드별 제외.
3. **P-006 director 프롬프트**(gated 공존, prompt-version-review) — rich + director 슬롯 채움.
4. **Critic director 차원**(gated, retention_design) — P-007 bump, 얕은 director 감점.
5. **frontend** PlanCard director 조건부 섹션(rich 위에 hook_system/retention/scene).
6. **cost** director(rich↔commercial_viral 중간) 재조정 + director depth 측정 + close.

## 성공 기준 (acceptance 요약)
- compact/rich(기존) 경로 **byte-identical** (pytest 508 회귀 0) + director ON 경로 = rich + director 슬롯.
- output_mode enum 으로 일반화하되 기존 rich_output_enabled 동작 보존.
- director depth(연출/리텐션) 측정 + 키 0.

## 비목표 (요약 — non_goals.md)
- ❌ commercial_viral tier (market/audience/brand/conversion 등) — PKM/RAG 데이터레이어 선행(제안서 §7.2), 본 phase 제외.
- ❌ PKM/RAG 데이터레이어 — 로드맵 ③(별도).
- ❌ rich/director default ON 전환 — gated OFF 유지.
- ❌ 완성 대본/영상 제작 (product_boundary — scene_breakdown 은 "기획 의도/감정/근거"이지 촬영 지시 아님, 제안서 보정2).

## 로드맵 위치
**① Phase 15 director (본)** → ② 검증 보강(human review 실채점 + 전수 eval) → ③ PKM/RAG 데이터레이어 기획안 → (이후 commercial_viral).
