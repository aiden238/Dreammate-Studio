# Phase 12 S5 — 검증 종합 + Phase 13 확장 제안

> 작성: 2026-06-02 | Phase 12 검증 페이즈 Slice S5 (종합·우선순위)

## 1. Phase 12 검증 종합

| Slice | 산출 | 결과 |
|---|---|---|
| Entry | 8파일 + self-validation (11th) | Phase 12 active, 깊이 격차 핵심 GAP 정의 |
| S1 | golden_set 15→25 + depth_actionability 차원 (CC-011) | 측정 기반 확장, additive |
| S2+S3 | 깊이 격차 실측 (6 도메인, 13 feature) | **compact 0.231 vs rich 1.000 = 4.3x, 편차 0** |
| S4 | human review kit (3케이스 compact vs rich + 채점 시트) | ⏳ **사용자 채점 대기** (LLM-as-judge 신뢰도 대조) |
| S5 | 본 종합 | Phase 13 우선순위 도출 |

### 핵심 발견 (확정)
1. **MVP 출력의 단순함 = 모델 한계 아님.** 같은 모델(gpt-4o-mini)에 프롬프트만 바꿔 0.231→1.000.
2. **결핍 10/13 feature** (타깃·톤·후크변형·대사·자막·샷·썸네일·제목·레퍼런스·길이변형) — 다수가 **출력 스키마에 슬롯 부재**라 모델이 생성해도 담기지 않음.
3. → 확장 레버는 **프롬프트 + 스키마**(모델 교체 아님). cost 동반.

### 미해소 (Phase 12 잔여)
- **S4 human review**: 사용자가 kit 채점 → 구조적 측정(0.231/1.000)과 대조. **"전부 채우는 게 가치 있나, 일부만이 나은가"**를 사람 기준으로 보정. ★ 이게 Phase 13 범위(어느 feature까지)를 좁힌다.

## 2. Phase 13 확장 제안 (검증 근거 기반)

### 우선순위 1 — 출력 스키마 + 프롬프트 확장 (depth)
- `Plan` 스키마에 결핍 feature 슬롯 추가(예: `hook_variants[]`, beat 에 `visual`/`dialogue`/`caption`, `shots[]`, `thumbnail`, `title_candidates[]`, `cta`, `references[]`, `length_variants`). + 타깃/톤.
- planning `SYSTEM_PROMPT` 를 이 슬롯을 채우도록 확장 → **prompt-version-review 경유**(P-006 semver bump + golden_set 회귀).
- ★ 제품 경계 유지: 확장본도 **"기획 브리프"**(촬영·편집 가이드)지 완성 대본/제작 아님 (product_boundary).
- ★ behavior-preserving: 신규 필드 **optional/additive** + 기존 소비자(프론트 PlanCard 등) 회귀 0. gated/단계 활성 권장.

### 우선순위 2 — cost_control 재조정 (B안 잔여 B-RES-1 연동)
- rich 출력 = 토큰 ↑ (× 3안). 확장 전 **요청당 cost 추정 + tier 정책** 갱신 필수.
- B안 다중-provider cost 재조정(§18.D)과 묶어 처리.

### 우선순위 3 — (S4 결과 의존) 깊이 범위 확정
- human review 가 "일부 feature 는 과함/불필요"로 나오면 그 feature 는 제외 → 스키마 비대화 방지.

### 비포함 (Phase 13 non-goal)
- 모델 tier 상향(opus/gpt-5.5)은 **2차 레버** — 프롬프트/스키마 확장 후 효과 재측정 뒤 검토.
- 완성 대본/영상 제작 (product boundary).

## 3. 권고 진입 순서

```
[지금] S4 사용자 채점 (kit: eval/human_review/2026-06-02_phase-12-s4-review-kit.md)
   ↓  (사람 점수 ≈ 0.23/1.00 이면 자동 eval 신뢰 → 깊이 범위 확정)
Phase 12 phase-complete (retrospective + archive)
   ↓
Phase 13 진입 — 스키마+프롬프트 확장 (prompt-version-review + cost 재조정, additive/gated)
```

## 4. 근거 문서
- `eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md` (실측)
- `eval/human_review/2026-06-02_phase-12-s4-review-kit.md` (사용자 채점 대기)
- `docs/contract_changes/2026-06-02_phase-12-s1-golden-set-depth.md` (CC-011)
- `eval/video_planning_eval.md` §2.A.1 (depth_actionability)
