# Phase 13 — Assumptions

## A. 제품 phase 성격 (첫 의도적 출력 변경)
- ★ Phase 13 = 런타임 有 — **이 프로젝트 첫 의도적 출력 변경**(compact→rich). 그래서 **gated 단계 롤아웃**(flag default OFF → 검증 후 ON) + **additive 스키마**(전부 Optional)로 안전하게. flag OFF 면 compact byte-identical(behavior-preserving).
- 산출물 = 운영 코드(output.py/planning/config/critic/frontend) + contract(output_schema/prompt_registry/cost_control) + depth 재측정. ★ 본 entry(문서)는 운영 코드 0.

## B. gated 롤아웃 가정 (★ 핵심)
- ★ `rich_output_enabled` default **False** — Phase 11 `multi_provider_plans_enabled`·`cross_validation_enabled`(default False) 패턴 동형. OFF 가 default → 기존 사용자 영향 0(byte-identical).
- rich 는 **opt-in 경로**(flag ON) — S6 검증(depth ≥0.8 + 라이브 데모) 통과 후 default ON 전환은 **별도 결정**(Phase 13 acceptance 아님, NG3).
- gated 가 "출력 확장"(rich 추가) ↔ "기존 동작 불변"(behavior-preserving) 표면 모순을 화해: capability(rich 구축) vs 발화(flag, opt-in). Phase 10 P-CAPABILITY-DEFAULT-OFF-001 + Phase 11 gated default-off 계승.

## C. additive 스키마로 회귀 0 가정
- ★ rich 슬롯 **전부 Optional default None/[]** — 기존 7필드(name/concept/hook/flow/pros/risks/approach_label) 직렬화 불변 + 기존 소비자(PlanCard·orchestrator·Critic) rich 슬롯 미참조 → 회귀 0.
- `PlanFlowBeat` 확장(visual/dialogue/caption)도 Optional → 기존 beat(beat_index/beat/duration_sec/purpose) 불변.
- output_schema contract-change = additive(기존 §8.1 보존) + agent-io-check 회귀. 기존 compact 프롬프트 보존(미삭제).

## D. rich 프롬프트가 depth ≥0.8 달성 가정 (Phase 12 데모 근거)
- ★ Phase 12 가 입증 — 같은 모델(gpt-4o-mini) + 확장 프롬프트만으로 depth 0.231→1.000(rich 측정 프롬프트). Phase 13 운영 rich 프롬프트(P-006 v1.1.0)가 **목표 ≥0.8** 달성한다고 가정(S6 재측정으로 확정).
- rich=1.0(Phase 12)은 상한선 — 운영 rich 는 스키마 슬롯 충족 + 품질 균형으로 ≥0.8 목표(전부 채우기 vs 선별은 human review/cost 로 보정).
- 미달 시 그 자체가 결과 → 프롬프트/슬롯 재조정 또는 범위 축소.

## E. 실 LLM 데모 비용 가정 (사용자 승인)
- ★ S6 flag ON 라이브 데모 + depth 재측정 = 실 LLM 호출 = 실비용(사용자 승인). golden_set 표본 + 라이브 1회로 한정. CI 회귀 = mock-deterministic 유지(Phase 12 NG9 계승).
- rich 출력 = 출력 토큰 ↑ × 3안 = 비용 배수 → S6 cost_control 재조정(B-RES-1 통합). 키 = .env user-provided, 평문 0.

## F. frontend Next.js PlanCard 확장 가정
- ★ S5 = `apps/web/components/PlanCard.tsx`(+ lib/types·api) **conditional 확장** — rich 필드(후크 변형/타임코드·화면·대사·자막/샷/썸네일/제목/길이변형) 있을 때만 렌더. 기존 compact 렌더 회귀 0(PlanCard 35연속·component_map 45연속 baseline 보호).
- design-review 7원칙(모바일 우선, 카드 단위, 영상 제작 UI 미포함) 정합 — rich 카드도 "기획 브리프" 표시지 영상 편집 UI 아님.

## G. Critic depth 반영 가정
- ★ S4 = Critic 평가에 depth_actionability 차원 additive — 기존 8차원 canonical 0–1 체계(ADR-018) 보존 + depth 추가(얕으면 감점, 88점 함정 해소). gated 정합(rich 출력 평가 시 depth 활성).
- P-007 prompt bump(prompt-version-review) — 기존 점수 체계 회귀 0(additive).

## H. cost 트레이드오프 가정
- rich = 출력 토큰 ↑(필드·서술·변형) × 3안 = 비용 배수. 깊이 ↑ 가 항상 가치 ↑ 는 아님(과잉 상세 risk) → depth_actionability rubric 으로 "실행 가능한 깊이" 측정(맹목 토큰 증가 ≠ 가치).
- S6 cost_control 재조정 = rich tier 정책 + B-RES-1(다중-provider) 통합. flag gated 라 OFF 시 비용 증가 0(default).

## I. B안 비차단 잔여 가정 (Phase 12 승계)
- B-RES-1(cost_control 다중-provider 재조정) = ★ **S6 통합**(rich cost 재조정과 함께). B-RES-2(B안 ADR)/B-RES-3(agent_io/registry contract-change) = 추적(비차단, Phase 13 직후). acceptance blocking 아님.

## J. Slice 분리 가정
- Entry → S1(스키마) → S2(프롬프트 P-006) → S3(gated wiring) → S4(Critic depth) → S5(frontend) → S6(cost+검증+close). S2·S3 는 S1 슬롯 의존, S4 는 S1·S3 의존, S5 는 S1 의존, S6 는 전체 의존(sequential). sub-agent dispatch, P-X1 게이트.

## K. 리스크 & 완화
| 리스크 | 완화 |
|---|---|
| 첫 출력 변경이 기존 동작 깸 | ★ gated(flag OFF default) + additive(Optional) → OFF byte-identical. A5-PP 게이트 + pytest green |
| 스키마 확장이 기존 소비자 회귀 | ★ 전부 Optional default None/[] + agent-io-check + 기존 7필드 보존. 기존 test 수정 0 |
| rich 프롬프트가 depth ≥0.8 미달 | Phase 12 데모(1.0 상한) 근거 + S6 재측정. 미달 시 슬롯/프롬프트 재조정(가설 반증도 결과) |
| rich 가 완성 대본화 | actionability = "기획 브리프" 깊이로 한정(product_boundary). 촬영·편집·TTS·BGM 0(NG1) |
| frontend rich 렌더가 compact 깸 | ★ conditional(rich 있을 때만) + design-review + tsc/build 게이트. 기존 렌더 회귀 0 |
| 비용 폭증 | flag gated(OFF default 비용 0) + S6 cost 재조정 + depth ↔ 토큰 트레이드오프 측정 |
| flag 즉시 ON 압박 | ★ default OFF 유지(NG3) — 검증 후 별도 결정. 라이브 데모는 ON opt-in |
| 키 노출 | .env user-provided + .gitignore + push 전 `git diff \| grep sk-/AIza` |
| P-006/P-007 bump 회귀 | prompt-version-review 경유 + golden_set 회귀 + semver + 이전 버전 deactivation 일정 |
