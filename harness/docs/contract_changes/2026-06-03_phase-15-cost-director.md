# Contract Change Log — Phase 15 S6 cost_control director cost (additive)

> ID: CC-020 | Status: **decided + applied** (2026-06-03, Phase 15 S6) | Date: 2026-06-03
> 대상: `ai_system/orchestration/cost_control_policy.md` (신규 §15 director cost)
> Related: CC-016(rich/B-RES-1 cost §13~§14 — 동형 패턴), CC-017(director 스키마)
> Skill: contract-change + cost-review

## 1. 변경 요약
- `cost_control_policy.md` 신규 **§15 director 출력 cost** (gated, additive). §1~§14 전부 보존.
- director(`output_mode=director`) = rich 12 + director 3슬롯(scene 리스트) → 출력 토큰 추가 증가(compact 대비 ~5~8배 추정). run_planning director max_tokens 1500→3500. paid/opt-in 권장(§13.4 계승).

## 2. 회귀 안전
- ★ additive — director(gated, default compact) 경로만. compact/rich cost 해석 불변(byte-identical). 정밀 단가는 실 LLM 측정 후 별도 CC.

## 3. Rollback
- §15 블록 git revert → CC-016 상태(§14까지) 복귀. director cost 미발생(default compact).

## 4. 변경 이력
- 2026-06-03: Phase 15 S6 — §15 director cost additive(CC-020). director N씬 상한 등 정밀 단가는 후속.
