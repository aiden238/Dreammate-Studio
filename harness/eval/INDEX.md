# eval/INDEX.md — 평가 체계 카테고리 색인

> 위치: `eval/INDEX.md`
> 작성: 2026-05-26 (Phase 1 진입 시)
> 목적: 평가 체계를 **이원 트랙**(구현 검증 / 플랫폼 품질 검증)으로 색인.
>       기존 파일 위치는 보존, 카테고리만 명시.

---

## 이원 트랙 원칙

평가에는 두 가지가 있다:

| 트랙 | 질문 | 자동화 | 도구 |
|---|---|---|---|
| **구현 검증** (Implementation Eval) | "만든 기능이 기술적으로 제대로 작동하는가?" | 자동 가능 | pytest, jsonschema, curl, Playwright |
| **플랫폼 품질** (Product Quality Eval) | "AI가 만든 영상기획 결과물이 실제로 쓸 만한가?" | 부분 자동 + 사람 리뷰 | golden_set, human rubric, LLM-as-judge |

둘은 분리하되 완전히 따로 놀면 안 된다. AI 기능이 추가될수록 두 트랙 모두 필요.

---

## 1. 구현 검증 (Implementation Eval)

**무엇을 보는가:** 기술적 동작·인터페이스·회귀.

### 1.1 일상 체크리스트

| 파일 | 용도 | 주 사용 시점 |
|---|---|---|
| `tests/smoke_test_checklist.md` | end-to-end 시나리오 8단계 | 매 Slice 완료 시 |
| `tests/regression_checklist.md` | 회귀 점검 항목 | Slice 진입 / 종료 시 |

### 1.2 형식·계약 검증

| 파일 | 용도 | 주 사용 시점 |
|---|---|---|
| `docs/contracts/api_contract.md` | API 엔드포인트 명세 (참조용) | 엔드포인트 구현 시 |
| `docs/contracts/output_schema.md` | 응답 JSON 구조 (참조용) | schema validation 시 |
| `docs/contracts/error_response_contract.md` | 오류 코드/형식 | 오류 처리 구현 시 |

### 1.3 운영 결과

| 폴더 | 용도 |
|---|---|
| `eval/qa_reports/` | qa-check Skill 실행 결과 누적 |
| `eval/regression_results/` | 회귀 테스트 결과 누적 |
| `eval/cost_snapshots/` | 비용 측정 결과 누적 |
| `eval/security_reviews/` | 보안 점검 결과 누적 |

### 1.4 보조 점검 기준

| 파일 | 용도 | 주 사용 시점 |
|---|---|---|
| `eval/regression_eval.md` | 회귀 점검 기준 정의 | CI 설계 시 |
| `eval/security_eval.md` | 보안 점검 기준 (자동 가능 부분) | Phase 9~10 |
| `eval/accessibility_checklist.md` | WCAG 자동 검사 가능 부분 | Phase 11+ |

### 1.5 Skill 매핑

```
qa-check          → 1.1, 1.3 (10 카테고리 중 8개가 구현 검증)
eval-run          → 1.1, 1.3
bug-triage        → 1.3 + docs/bug_reports/
cost-review       → 1.3 (cost_snapshots)
security-review   → 1.3 (security_reviews) + 1.4 (security_eval)
```

---

## 2. 플랫폼 품질 (Product Quality Eval)

**무엇을 보는가:** AI 출력의 실용성·창의성·브랜드 적합성.

### 2.1 기준 케이스

| 파일 | 용도 | 주 사용 시점 |
|---|---|---|
| `eval/golden_set.md` | 정답 입출력 11개 (GS-001~GS-011) | 회귀 + 신규 prompt 검증 |
| `eval/failure_cases.md` | 실패 출력 패턴 5개 (FC-001~) | Critic / Rewriter 학습 |

### 2.2 평가 차원

| 파일 | 평가 차원 | 주 사용 시점 |
|---|---|---|
| `eval/video_planning_eval.md` | 종합 평가 (5차원 가중치) | Critic Agent 평가 시 |
| `eval/hook_quality_eval.md` | 후킹 강도 | Slice 3 (Critic) 이후 |
| `eval/target_fit_eval.md` | 타겟 적합도 | Slice 3 이후 |
| `eval/execution_feasibility_eval.md` | 실제 촬영 가능성 | Slice 3 이후 |
| `eval/brand_consistency_eval.md` | 브랜드 톤 일치 | Phase 4+ (Brand Memory) |

### 2.3 사람 리뷰

| 파일 | 용도 | 주 사용 시점 |
|---|---|---|
| `eval/human_review_rubric.md` | 사람 평가 rubric | Slice 3 완료 / Phase 종료 시 |
| `eval/confidence_score.md` | 신뢰도 점수 산출 | Critic 결과 가공 시 |

### 2.4 보조 품질 기준

| 파일 | 용도 |
|---|---|
| `eval/failure_taxonomy.md` | 실패 분류 체계 (오류 vs 품질미달 vs 거부) |
| `eval/ux_eval.md` | UX 인지·반응성 평가 (구현+품질 혼합) |
| `eval/design_review_checklist.md` | 화면 디자인 리뷰 |
| `eval/design_reviews/` | 디자인 리뷰 결과 누적 |

### 2.5 Skill 매핑

```
eval-design       → 2.1, 2.2, 2.3
eval-run          → 2.1, 2.2 (실행 시 1.1과 병행)
prompt-version-review → 2.1 + golden_set 회귀
design-review     → 2.4 (design_review_checklist + design_reviews)
ai-architecture-review → 2.2 (평가 가중치 검토 시)
```

---

## 3. 운영 메타 (둘 다 아닌 메타 평가)

| 파일 | 용도 |
|---|---|
| `eval/phase_eval.md` | Phase별 평가 프레임 (구현+품질 통합 회고) |

`phase-complete` Skill에서 사용.

---

## 4. Phase별 비중 가이드

| Phase | 구현 Eval 비중 | 플랫폼 품질 Eval 비중 | 이유 |
|---|---|---|---|
| **Phase 1** (MVP 기본 플로우) | **70%** | **30%** | 골격 증명 우선, 품질은 최소치만 |
| Phase 2~3 (PWA 설계/UI) | 60% | 40% | UX 품질 본격 평가 시작 |
| Phase 4 (FastAPI 백엔드) | 50% | 50% | MOA Lite 본격, 양쪽 동급 |
| Phase 5~6 (DB/Auth, AI IO) | 40% | 60% | 인프라 안정 후 AI 품질 집중 |
| Phase 7 (RAG Lite) | 30% | 70% | RAG 품질이 핵심 가치 |
| Phase 8 (MOA Lite) | 30% | 70% | 4 Agent 품질 검증 핵심 |
| Phase 9~10 (피드백/통합) | 50% | 50% | 운영 안정성 + 사용자 가치 균형 |

---

## 5. Phase 1 권장 사용

### 5.1 꼭 해야 할 구현 Eval

```
✅ /api/v1/generate 응답 확인           ← Slice 1
✅ output_schema 검증                    ← Slice 1 (jsonschema validation)
✅ Intent Filter 동작 (INV-001)          ← Slice 2 (golden_set GS-001~003)
✅ Critic 평가 5차원 점수 채움           ← Slice 3
✅ RAG fallback 동작                     ← Slice 4
✅ Supabase 저장 확인                    ← Slice 5
✅ 프론트 카드 렌더링 확인               ← Slice 6
✅ 에러 카드 표시                        ← Slice 7
✅ Smoke test 8단계 (전체)               ← Phase 1 종료 직전
```

### 5.2 최소 해야 할 플랫폼 품질 Eval

```
✅ Golden Set 11개 (이미 작성 완료)              ← eval/golden_set.md
✅ Bad Case 5개 (Phase 1에서 신규 작성)          ← eval/failure_cases.md
✅ Critic 평가 5차원 기준 검토 (Slice 3 직후)    ← eval/video_planning_eval.md
✅ 사람 리뷰 1회 (Phase 1 종료 직전, 샘플 5개)   ← eval/human_review_rubric.md
```

**Phase 1에서 안 해도 되는 것:**
- Hook / Target Fit / Brand Consistency 개별 평가 → Phase 4+ (Critic revise 추가 시)
- LLM-as-judge 자동화 → Phase 7+ (eval-run Skill 본격화)
- 회귀 자동화 CI → Phase 10 (배포 단계)

---

## 6. 운영 절차

### 6.1 Slice 진입 시

```
1. Slice acceptance.md 항목 확인
2. 본 INDEX.md §5.1 / §5.2 중 해당 항목 확인
3. 작업 시작
```

### 6.2 Slice 완료 시

```
1. 구현 Eval: 자동 테스트 실행 (pytest, jsonschema)
2. 결과를 eval/qa_reports/ 또는 eval/regression_results/에 저장
3. 품질 Eval (해당 시): golden_set / failure_cases 비교
4. 결과를 eval/regression_results/에 저장
5. 다음 Slice 진입
```

### 6.3 Phase 종료 시

```
1. qa-check Skill 전체 10 카테고리 실행
2. eval/phase_eval.md 프레임으로 회고 작성 (meta-retrospective)
3. eval/qa_reports/phase-{N}-final_{date}.md 작성
```

---

## 7. 관련 문서

- `tests/smoke_test_checklist.md`
- `tests/regression_checklist.md`
- `docs/contracts/output_schema.md`
- `docs/contracts/api_contract.md`
- `docs/contracts/error_response_contract.md`
- `docs/decisions/eval_dual_track.md` (ADR-009)
- `.claude/skills/qa-check/SKILL.md` v1.1.0
- `.claude/skills/eval-design/SKILL.md`
- `.claude/skills/eval-run/SKILL.md`

---

## 8. 변경 이력

- 2026-05-26: Phase 1 진입 시 신규 작성 (eval 이원 트랙 색인 + Phase별 비중 가이드)
