# Phase 13 — Notes

## 진입 맥락
- Phase 1~11 완료(MVP 파이프라인 + LLM Gateway). Phase 12 = 검증 페이즈 — MVP 출력의 **깊이 격차**를 수치로 확정(compact 0.231 vs rich 1.000 = 4.3x).
- Phase 12 결론: 단순함은 **모델 한계가 아니라 prompt/schema 설계 선택**. 결핍 10/13 feature, 다수가 출력 스키마(`Plan`) 슬롯 부재. → Phase 13 = 그 격차를 **운영 출력에 실제로 반영**(compact→rich).
- 사용자 확정: **롤아웃 = gated**(flag default OFF → 검증 후 ON) / **범위 = 풀**(backend + frontend, /generate 화면까지 rich).

## ★ Phase 12 격차 근거 (Phase 13 의 입력)
```
측정(Phase 12): gpt-4o-mini · golden_set 6 도메인 · depth_actionability 13 feature(0/1)
  compact 0.231 (결핍 10/13) vs rich 1.000 — 4.3x, 6/6 편차 0 (도메인 무관, 구조적)
  결핍 = target_audience·tone·hook_variants·beat_dialogue·beat_caption·shots·thumbnail·
         title_candidates·references·length_variants (다수가 Plan 스키마 슬롯 부재)
근거 문서: eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md
          phases/archive/phase-12-validation/s5_synthesis_and_phase13_proposal.md
```
- Phase 13 S1(스키마 슬롯) + S2(프롬프트)가 이 결핍 10 feature 를 운영 출력에 추가. 목표 depth 0.231 → ≥0.8.

## ★ 88점 함정 (Critic depth 미반영) — S4 의 근거
```
관찰(Phase 12 + 사용자 실 UI 2026-06-02): compact 출력이 Critic 88점을 받아도
  depth(0.231)는 점수에 반영 안 됨 — Critic 평가 체계가 "얕음"을 감점하지 않는다.
→ 깊이를 운영 출력에 넣어도(S1·S2), Critic 이 depth 를 안 보면 품질 게이트가 못 잡는다.
S4: Critic 평가에 depth_actionability 차원 additive → 얕으면 감점 → 88점 함정 해소.
```

## ★ gated 이유 (첫 출력 변경)
```
이 프로젝트가 처음으로 운영 출력을 의도적으로 바꾼다(compact→rich).
  → 위험: 기존 사용자/소비자(PlanCard·orchestrator·Critic)에 영향.
안전 장치 2개:
  1. gated     — rich_output_enabled default False. OFF 면 compact byte-identical.
                 (Phase 11 multi_provider_plans_enabled·cross_validation_enabled 패턴 동형)
  2. additive  — rich 슬롯 전부 Optional default None/[]. 기존 7필드·소비자 회귀 0.
→ flag OFF 가 default → 검증(S6 depth ≥0.8 + 라이브 데모) 통과 후 단계적 ON.
  default ON 즉시 전환은 별도 결정(NG3) — 첫 출력 변경은 신중하게.
```

## ★ 제품 경계 유지 (기획 브리프)
```
확장본(rich)도 "실행 가능한 기획 브리프"여야 한다 — 완성 대본·영상 제작물 아님.
rich = 후크 변형 · 타임코드 · 화면 · 대사 가이드 · 자막 · 샷 제안 · 썸네일/제목 방향 ·
       CTA · 레퍼런스 · 길이 변형 · 타깃 · 톤 ("기획 브리프" 수준).
촬영·편집·TTS·BGM = product_boundary 영구 non-goal (NG1).
→ 깊이를 더하되 경계를 넘지 않는다 (Phase 12 와 동일 원칙).
```

## cost 트레이드오프
- rich = 출력 토큰 ↑(필드·서술·변형 증가) × 3안 = **비용 배수**(Phase 12 측정: compact 수백 vs rich 1000+ 토큰).
- 깊이 ↑ 가 항상 가치 ↑ 아님(과잉 상세 risk) → depth_actionability rubric 으로 "실행 가능한 깊이" 측정(맹목 토큰 증가 ≠ 가치).
- ★ flag gated 라 OFF 시 비용 증가 0(default). S6 cost_control 재조정 = rich tier 정책 + B안 잔여 **B-RES-1**(다중-provider §18.D) 통합.
- 비용 기준 = `ai_system/orchestration/cost_control_policy.md`.

## ★ 안전 게이트
```
gated 롤아웃     : rich_output_enabled default False → 검증 후 ON (NG3)
flag OFF 동작    : 기존 compact 출력 byte-identical (Envelope 불변, behavior-preserving)
additive 스키마  : rich 슬롯 전부 Optional → 기존 7필드·소비자 회귀 0 (기존 compact 프롬프트 보존)
prompt bump      : P-006(planning)·P-007(critic) prompt-version-review 경유(semver + golden_set 회귀)
제품 경계        : 확장본도 "기획 브리프" (완성 대본·영상 0, product_boundary)
모델 불변        : 같은 모델(gpt-4o-mini) — tier 상향은 2차 레버(재측정 후, NG2)
키 0             : .env user-provided + 평문 commit 금지
P-X1             : sub-agent forbidden 검사 + flag OFF byte-identical 회귀
```

## B안(Phase 11) 비차단 잔여 — Phase 12 승계 (추적·통합)
- **B-RES-1**: `cost_control_policy` 다중-provider cost 재조정(§18.D) → ★ **Phase 13 S6 통합**(rich cost 재조정과 함께).
- **B-RES-2**: B안 ADR(3-provider 결정) → 추적(비차단, S6 ADR 묶음 가능).
- **B-RES-3**: agent_io/registry contract-change(B안 반영) → 추적(비차단, depth 슬롯 contract-change S1 과 별개).

## 결정 대기 / 옵션
- rich 슬롯 **전부 추가 vs 선별** — Phase 12 human review(deferred) + cost 트레이드오프로 보정. 1차는 결핍 10 feature 전부 슬롯화(additive 라 비용 OFF 시 0).
- depth 목표 **≥0.8** — 운영 균형(전부 채우기는 비용↑) 고려 상한 1.0(Phase 12 측정) 미만 설정.
- flag default ON 전환 시점 — S6 검증 후 **별도 결정**(Phase 13 외).

## 다음 (Phase 13 이후 — Phase 14~20)
- **flag default ON 전환 결정** — S6 검증(depth ≥0.8 + 라이브) 통과 후 별도 판단.
- **모델 tier 상향(2차 레버)** — prompt/schema 확장 후 효과 재측정 뒤 검토(NG2).
- **staging 배포 골격**(Phase 14+, Phase 12·13 staging 이관 계승).
- **B안 UX 노출**(consensus/divergence, cross_validation 응답) + B-RES-2/3 마무리.
- Phase 12 human review 실 채점 + LLM-as-judge 신뢰도 대조(Phase 13 depth 재측정과 묶음 가능).
