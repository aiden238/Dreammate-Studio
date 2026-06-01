# Phase 12 S2+S3 — 깊이 격차(depth gap) 실측 리포트

> 작성: 2026-06-02 | Phase 12 검증 페이즈 (Slice S2 실 LLM eval + S3 깊이 격차 정량 분석)
> 평가 차원 근거: CC-011 `depth_actionability` (eval/video_planning_eval.md §2.A.1)

## 1. 목적

지금까지 검증된 것은 **구조 정확성**(파이프라인 동작·3안 생성·fallback·flag OFF 보존)뿐이다.
미검증 핵심 질문 = **"출력(영상기획안)이 실제로 충분히 깊은가 / 쓸만한가"**.
본 측정은 그 중 **깊이(depth/actionability)** 격차를 수치로 확정한다.

가설(2026-06-02 라이브 데모 기반): 현재 출력의 단순함은 **모델 한계가 아니라 프롬프트/스키마 설계 선택**이다.

## 2. 방법 (재현 가능)

- **모델**: `gpt-4o-mini` (현재 운영 slot0 과 **동일 모델** — 모델 변수 통제).
- **A. compact**: 실 운영 함수 `backend/fastapi/agents/planning.run_planning()` (운영 `SYSTEM_PROMPT` 그대로, json_mode, max_tokens 1500). ★ 운영 코드 0 수정.
- **B. rich**: 동일 모델 + **확장 프롬프트**(후크 3변형 / 타임코드·화면·대사·자막·목적 / B-roll·샷 / 썸네일·제목 / CTA / 레퍼런스 / 길이변형 / 타깃·톤 요구), max_tokens 3000.
- **표본**: golden_set 도메인 대표 6 (요리·뷰티·IT리뷰·운동·여행·교육).
- **채점**: `depth_actionability` 13 feature 의 구조적 존재 여부(0/1) → depth = 존재 비율(0~1).
  - features: target_audience, tone, hook_variants, beats_3plus, beat_visual, beat_dialogue, beat_caption, shots_broll, thumbnail, title_candidates, cta, references, length_variants
- 측정 스크립트(임시, 레포 외 보관)는 위 방법을 그대로 구현 — 운영 코드 import 만(수정 0).

## 3. 결과

| 케이스(도메인) | compact | rich | gap |
|---|---|---|---|
| 자취요리 30s | 0.23 | 1.00 | +0.77 |
| 메이크업 60s | 0.23 | 1.00 | +0.77 |
| 이어폰 리뷰 45s | 0.23 | 1.00 | +0.77 |
| 홈트 30s | 0.23 | 1.00 | +0.77 |
| 여행 브이로그 60s | 0.23 | 1.00 | +0.77 |
| 광합성 교육 60s | 0.23 | 1.00 | +0.77 |
| **평균** | **0.231** | **1.000** | **+0.769 (4.3x)** |

격차가 6/6 케이스에서 **완전히 일관**(편차 0) — 도메인 무관, 구조적 격차.

### feature별 (compact 평균 / rich 평균)

| feature | compact | rich | 비고 |
|---|---|---|---|
| beats_3plus | 1.00 | 1.00 | compact 보유 |
| beat_visual | 1.00 | 1.00 | compact 보유 (beat 설명) |
| cta | 1.00 | 1.00 | compact 보유 (purpose) |
| target_audience | **0.00** | 1.00 | compact 결핍 |
| tone | **0.00** | 1.00 | compact 결핍 |
| hook_variants | **0.00** | 1.00 | compact = 후크 1개뿐 |
| beat_dialogue (대사) | **0.00** | 1.00 | 스키마에 슬롯 없음 |
| beat_caption (자막) | **0.00** | 1.00 | 스키마에 슬롯 없음 |
| shots_broll | **0.00** | 1.00 | 스키마에 슬롯 없음 |
| thumbnail | **0.00** | 1.00 | 스키마에 슬롯 없음 |
| title_candidates | **0.00** | 1.00 | 스키마에 슬롯 없음 |
| references | **0.00** | 1.00 | 스키마에 슬롯 없음 |
| length_variants | **0.00** | 1.00 | 스키마에 슬롯 없음 |

→ compact 는 13 feature 중 **3개만**(23%) 보유, **10개 결핍**.

## 4. 결론

- **깊이 격차 = 실재하고 크다 (4.3배).** 같은 모델인데 프롬프트만 바꿔도 0.23 → 1.00.
- 따라서 단순함은 **모델 한계가 아니라 프롬프트 + 스키마 설계의 결과**. (가설 확정)
- 결핍 10개 중 다수(대사·자막·샷·썸네일·제목·레퍼런스·길이변형)는 **출력 스키마(`Plan`)에 슬롯 자체가 없어** 모델이 생성해도 담기지 않는다 → **스키마 확장**이 프롬프트 확장과 함께 필요.

## 5. 한계 / 주의 (정직한 캘리브레이션)

- rich=1.00 은 **확장 프롬프트가 13 feature 를 명시적으로 요구**해서 나온 상한선이다 — "이만큼 가능"의 증거이지 "이것이 최적"은 아님. 최적 깊이는 human review(S4)로 보정.
- 구조적 feature 채점(0/1 존재)은 **존재 여부**만 보고 **품질**은 안 본다 — 대사가 있어도 진부할 수 있음. 품질 채점은 human review / LLM-as-judge 보강 대상.
- 표본 6 (golden_set 25 중 대표). 일관성(편차 0)이 높아 6으로도 방향성은 robust.

## 6. 비용 트레이드오프 (cost_control 연계)

- rich 출력은 compact 대비 **출력 토큰이 크게 증가**(데모 기준 ~1000+ vs 수백). 3안 생성이면 **× 3**.
- → 확장(Phase 13) 시 cost_control_policy 재조정 필수(B안 잔여 B-RES-1 과 연동).

## 7. Phase 13 함의 (S5 입력)

- **확장 1순위 = 프롬프트 + 스키마 확장** (모델 교체 아님). 결핍 10 feature 를 스키마 슬롯 + 프롬프트로 추가.
- 단, 제품 경계 유지: 확장본도 **"기획 브리프"**(촬영·편집 가이드)지 완성 대본/제작이 아니어야 함 (product_boundary).
- human review(S4)로 "어느 깊이가 실제로 가치 있는가"(전부 vs 선별) 보정 후 확정.
