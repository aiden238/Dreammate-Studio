# Phase 12 — Goals (검증 페이즈 / Validation — MVP 출력 품질·가치 실측)

> Phase: phase-12-validation
> 유형: **검증/계획 phase (런타임 0 — 측정·문서만)** — ★ behavior-preserving (운영 endpoint/agent/prompt 0 수정)
> 진입일: 2026-06-02 (entry 작성 — phase-start 정식 진입)
> 결정 근거: 사용자 지침 "12 = 검증 페이즈" + `PROJECT_STATE.md` §"다음: Phase 12 = 검증 페이즈" 확정 scope (2026-06-02)
> 근거 데모: 깊이 격차 라이브 데모 (gpt-4o-mini compact vs rich, 2026-06-02) — `notes.md` 참조

## 한 줄 정의

Phase 1~11 이 입증한 것은 **구조 정확성**(파이프라인 동작 / 3안 생성 / Critic revise / fallback / 라이브 3-provider) 뿐이다. Phase 12 는 그 위에서 **MVP 출력(영상기획안)의 품질·가치를 수치로 실측**한다 — golden_set 실 LLM eval baseline + **"깊이 격차(depth gap)" 정량화** + human review 로 LLM-as-judge 신뢰도 대조. 산출물은 **Phase 13+ 확장 우선순위의 데이터 근거**다. ★ 운영 코드는 0줄 수정 — Phase 12 는 측정·계획만, 실제 확장은 Phase 13.

## ★ 핵심 GAP = "깊이 격차 (depth gap)" — 이번 phase 의 중심 가설

```
관찰 (2026-06-02 라이브 데모로 입증):
  현재 운영 출력 = compact 7필드 (name / concept / hook / 2~4 beat / pros / risks)
  같은 모델(gpt-4o-mini)에 확장 프롬프트만 넣으면 = rich
    (hook 3변형 · 타임코드 · 대사 · 자막 · B-roll · 썸네일/제목 · CTA · 레퍼런스 · 길이 변형)
  → 단순함은 모델 한계가 아니라 prompt/schema 설계 선택이다.

결론:
  "구조 정확성 OK" ≠ "출력이 충분히 깊고 실행 가능하다"
  → Phase 12 는 이 격차를 수치(현재 깊이 X / 잠재 Y / gap Z)로 확정하고,
    확장(Phase 13+)의 ROI·우선순위 근거를 만든다.
```

## 측정 목표 (MO1~MO3 — 이번 phase 의 3개 측정 축)

| ID | 측정 목표 | 산출 | Slice |
|---|---|---|---|
| **MO1** | **golden_set 실 LLM eval 품질 baseline** — golden_set 확장본(~25)에 실 LLM eval 1회 실행 → 차원별 실 품질 점수 + 임계값 판정 | 차원별 점수 리포트 (baseline 수치) | S1·S2 |
| **MO2** | **깊이/실행가능성(depth/actionability) 정량화** — compact(현 운영) vs rich(확장 프롬프트) 비교 측정(필드수 / beat 깊이 / 대사·자막·샷·썸네일 유무 / 토큰 / 실행가능성) → "현재 깊이=X, 잠재=Y, gap=Z" 도출 | 깊이 격차 수치 (구체 metric) | S1·S3 |
| **MO3** | **LLM-as-judge 신뢰도 대조** — human review 표본 채점 ↔ LLM eval 점수 대조 설계로 자동 채점의 신뢰도 확인 | human review kit + 대조 설계 | S4 |

→ 세 축의 합 = **확장 우선순위 근거** (S5 종합 → Phase 13~20 로드맵 입력).

## 핵심 목표 (G1~G6)

| ID | 목표 | Slice |
|---|---|---|
| **G1** | **golden_set 15→~25 확장 + depth/actionability 평가 차원 추가** — 신규 케이스 + eval rubric 에 깊이/실행가능성 차원 정식 등록 (contract-change 경유) | S1 |
| **G2** | **실 LLM eval 실행** — 현 compact 운영 프롬프트 기준선으로 golden_set ~25 에 실 LLM eval 1회 → 차원별 점수 리포트 저장. ★ 실 LLM 호출 = 실비용(사용자 승인됨) | S2 |
| **G3** | **깊이 격차 정량 분석** — compact vs rich(확장 프롬프트) 비교 측정 → "현재 깊이 X / 잠재 Y / gap Z" 수치 도출. ★ 운영 코드 0 수정 (rich 는 측정용 프롬프트만, 운영 schema 미변경) | S3 |
| **G4** | **human review 표본 kit 준비** — 사용자가 직접 채점할 표본 + rubric 시트 + LLM 점수와의 대조 설계 (★ 사용자 시간 소요분은 deferred — kit 까지가 Phase 12 산출) | S4 |
| **G5** | **검증 종합 + Phase 13 확장 우선순위 제안** — MO1~MO3 종합 meta-retrospective + 확장 ROI/우선순위 데이터 근거 | S5 |
| **G6** | **behavior-preserving 회귀 0** — 운영 endpoint/agent/prompt/schema 0 수정. pytest 471 유지 | 전 Slice |

## 메타 목표 (MG1~MG3)

| ID | 목표 |
|---|---|
| **MG1** | multi-llm-validation self-form (11th) — Phase 12 진입 타당성 검증 (V1~V6) |
| **MG2** | contract-change — eval rubric 에 depth/actionability 차원 추가 + golden_set 확장 (S1 경유, ★ additive) |
| **MG3** | P-X1 §SELF-VERIFICATION 연속 유지 (Phase 11 → Phase 12, behavior-preserving + 운영 코드 0) |

## 사용자 가치 (Why)

- **품질의 실측화**: "동작한다"에서 "충분히 좋은가"로 — 구조 정확성(Phase 1~11)이 아닌 **출력의 깊이·실행가능성·도메인 적합성**을 수치로 본다. 추측이 아닌 데이터로 제품 완성도를 안다.
- **깊이 격차 = 확장 ROI 근거**: 같은 모델·같은 비용 근방에서 prompt/schema 만으로 출력 가치가 크게 변한다는 가설을 수치로 확정 → Phase 13 확장(어떤 필드를 먼저 추가할지)의 **우선순위를 데이터로 결정**.
- **자동 채점 신뢰도**: LLM-as-judge 를 human review 로 대조 → 향후 회귀 게이트에서 자동 점수를 얼마나 믿을지 보정.
- **안전한 검증**: 운영 코드 0 수정 + 측정 전용 — 검증이 운영 동작을 절대 바꾸지 않는다 (Phase 10 P-CAPABILITY-DEFAULT-OFF-001 정신 계승).

## ★ 절대 금지 (non_goals.md 상세)

운영 prompt/schema **실제 확장**(Phase 13) / 완성 대본·영상 제작(product_boundary 영구 non-goal — 확장본도 "기획 브리프"여야 함) / staging 배포(Phase 13+) / 새 모델 도입 / 기존 golden_set·contract·eval 파일 **사전 변경**(확장은 S1 에서 contract-change 경유) / 실 키 평문 커밋.
