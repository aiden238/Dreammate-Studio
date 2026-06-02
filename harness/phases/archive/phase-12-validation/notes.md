# Phase 12 — Notes

## 진입 맥락
- Phase 1~11 완료: MVP 파이프라인 동작 + 라이브 3-provider 3안 입증(Phase 11 B안). 그러나 입증된 것은 **구조 정확성**(동작/생성/fallback)뿐 — **출력 품질·가치는 미실측**.
- 사용자 지침 "12 = 검증 페이즈" + `PROJECT_STATE.md` §"다음: Phase 12 = 검증 페이즈" 확정 scope(2026-06-02) → Phase 12 = MVP 출력(영상기획안) **품질·가치 실측** + 확장(Phase 13~20) 우선순위 근거.

## ★ 깊이 격차 라이브 증거 (gpt-4o-mini compact vs rich, 2026-06-02) — 중심 가설
```
현재 운영 출력 (compact) = 7필드:
  name / concept / hook / 2~4 beat / pros / risks

같은 모델(gpt-4o-mini) + 확장 프롬프트만 (rich) =
  hook 3변형 · 타임코드 · 대사 · 자막 · B-roll · 썸네일/제목 · CTA · 레퍼런스 · 길이 변형

→ 핵심 결론: 출력의 단순함은 **모델 한계가 아니라 prompt/schema 설계 선택**이다.
  "구조 정확성 OK" ≠ "출력이 충분히 깊고 실행 가능하다".
```
- Phase 12 는 이 격차를 **수치(현재 깊이 X / 잠재 Y / gap Z)로 확정**하고, 확장 ROI·우선순위 데이터 근거를 만든다. 데모는 단일 표본 — S3 가 golden_set 다수 표본으로 일반화.

## 측정 3축 (MO1~MO3)
| 축 | 측정 | Slice |
|---|---|---|
| MO1 golden_set 실 LLM eval baseline | 현 compact 기준선 차원별 실 품질 점수 | S1·S2 |
| MO2 깊이/실행가능성 정량화 | compact vs rich 비교 → 깊이 격차 수치 | S1·S3 |
| MO3 LLM-as-judge 신뢰도 대조 | human review 표본 ↔ LLM 점수 대조 설계 | S4 |

## 비용 트레이드오프
- ★ S2·S3 = **실 LLM 호출 = 실비용**(사용자 승인). golden_set ~25 × 1회 + compact/rich 비교로 한정. CI 미실행(mock 게이트 유지, NG9).
- rich = **출력 토큰 ↑** (필드·서술·변형 증가) × 3안 = **비용 배수**. 토큰/비용도 metric 으로 기록 → Phase 13 확장 ROI 판단 입력.
- 깊이 ↑ 가 항상 가치 ↑ 아님(과잉 상세 risk) → actionability rubric 으로 "실행 가능한 깊이"를 측정(맹목 토큰 증가 ≠ 가치).
- 비용 기준 = `ai_system/orchestration/cost_control_policy.md` (B-RES-1 다중-provider 재조정 잔여 참조).

## ★ 제품 경계 유지 (기획 브리프)
```
확장본(rich)도 "실행 가능한 기획 브리프"여야 한다 — 완성 대본·영상 제작물 아님.
depth = 기획의 깊이(타임코드·대사 가이드·샷 제안·썸네일 방향 등 "기획 브리프" 수준).
촬영·편집·TTS·BGM = product_boundary 영구 non-goal (NG2).
→ 깊이를 더하되 경계를 넘지 않는다.
```

## ★ 안전 게이트
```
behavior-preserving : 운영 endpoint/agent/prompt/output_schema 0 수정 (pytest 471 유지)
운영 코드 0         : backend/fastapi/**, apps/web/** 0줄 (측정·문서만)
측정 전용 rich      : 운영 prompt_registry/output_schema 0 반영 (확장은 Phase 13)
mock 게이트 보존    : CI 회귀 = mock-deterministic 유지 / real = 측정 전용 1회
기획 브리프 경계    : 확장본도 product_boundary 준수 (완성 대본·영상 0)
키 0                : .env user-provided + 평문 commit 금지
P-X1                : sub-agent forbidden 검사 연속 (운영 .py 0)
```

## B안(Phase 11) 비차단 잔여 — GPT 검토 ④ (추적)
- B-RES-1: `cost_control_policy` 다중-provider cost 재조정(§18.D) → S2 비용 추정 기준.
- B-RES-2: B안 ADR(3-provider 결정) → 범위·가정 근거.
- B-RES-3: agent_io/registry contract-change(B안 반영) → depth 측정 시 provider/alias slot 정합.
- ★ 모두 **정식화(문서) 잔여** — 운영 코드 변경 아님. Phase 12 비용·범위 기준에 영향 → dependency/추적. Phase 12 내 또는 직후 처리(dependencies §B안). acceptance blocking 아님.

## 결정 대기 / 옵션
- human review 실 채점 — Phase 12 = kit 준비까지(NG7). 실 채점·대조 분석은 후속(사용자 시간).
- 깊이 격차 측정 표본 수 / rich 프롬프트 구성 상세 — S1·S3 에서 확정.
- 실 LLM eval provider 선택(단일 vs 3-provider) — Phase 11 B안 활용 가능(신규 도입 아님, NG4).

## 다음 (Phase 12 이후 — Phase 13~20)
- **Phase 13 = 확장 구현** — Phase 12 우선순위 근거로 운영 prompt/schema 확장(어떤 필드를 먼저: hook 변형 / 타임코드·대사 / 샷·썸네일 / CTA·레퍼런스 / 길이 변형). prompt-version-review + output_schema contract-change 경유.
- human review 실 채점 + LLM-as-judge 신뢰도 대조 분석(Phase 12 kit 활용).
- staging 배포 골격(Phase 13+, 사용자 확정 staging 이관).
- B안 정식화 잔여(B-RES-1~3) 마무리 + 확장 시 cost-review.
