# Retrospective: Phase 1 — MVP 기본 플로우

> 작성일: 2026-05-26
> 종류: phase
> 범위: Phase 1 (전체 — 진입 점검 → 7 Slices → CC-001 → smoke test)
> 작성자: Claude (Opus 4.7)
> 트리거: phase-complete 절차 6단계 (회고)

---

## 사실 요약

Phase 1 (MVP 기본 플로우)을 **2026-05-26 단일 일자**에 진입부터 implementation 완료까지 완수.

진입 직전 phase-start Skill을 v1.0.0 → v1.1.0으로 강화 (§6 Phase 진입 4점검 추가: Assumptions / Simplest Slice / Surgical Scope / Verification), qa-check Skill에 카테고리 10 Simplicity Check 추가. 

이후 4점검을 Phase 1에 실제 적용 — Simplest Slice 원칙(`POST /api/v1/generate` → JSON 1개)을 3회 압축으로 도출, 7 Slices로 분해.

Sub-agent 분산 실행 모델로 4 Wave 진행 (Wave 1: Slice 2+6 병렬, Wave 2: Slice 3, Wave 3: Slice 4, Wave 4: Slice 5+7 병렬). 6 sub-agent dispatch. 충돌 0건, push race 0건. pytest는 10→23→39→49→62 단계적 누적 통과.

Phase 종료 직전 CC-001 (`plans` / `plan_options` / `plan_candidates` 3-way 명명 drift)을 식별하고 contract-change 절차로 Option B (plan_candidates 통일) 적용. 자동 smoke test 5/5 PASS.

---

## 데이터

| 항목 | 값 |
|---|---|
| 기간 | 2026-05-26 단일일 (다중 세션) |
| Total commits (Phase 1) | 13 (entry checks 2 + slice 7 + CC-001 + smoke + final QA) |
| Backend 파일 | 28 (agents 4 + db 6 + rag 4 + routers 2 + schemas 3 + tests 7 + 기타 2) |
| Frontend 파일 | 30 (app 4 + components 4 + lib 4 + public 5 + configs 13) |
| QA reports | 10 (entry + slice 1~7 + smoke automated + smoke manual + final) |
| pytest 케이스 | 62 (e2e 14 + intent 8 + planning 5 + critic 13 + rag 8 + db 9 + extended 5) |
| Sub-agent dispatch | 6 (Wave 1×2 + Wave 2 + Wave 3 + Wave 4×2) |
| 식별된 deviation | 6 (endpoint sync/async, plan 수, Critic revise, RAG fallback, DB graceful, ErrorEnvelope 4-필드) |
| 식별된 drift | 1 (CC-001 plan_options/candidates/plans) — Phase 1 종료 직전 해소 |
| LLM 실호출 | 0 (Phase 1 자동 검증은 모두 mock 사용) |
| 사용자 manual 검증 항목 | 6 (smoke test §3~§8) — 사용자 환경 .env 입력 후 진행 |

---

## 분석

### 잘된 것

1. **Sub-agent 분산 + 폴더 분리 병렬화**: Wave 1/4의 2 sub-agent 병렬 실행이 폴더 분리(backend/ vs apps/web/)로 충돌 0건. 메인 세션 context 절약 효과 실증.
2. **Simplest Slice 3회 압축 원칙**: Slice 1을 "curl→JSON 1개"로 압축, 5 파일로 시작 → 디버깅·rollback 용이. 후속 Slice가 이 baseline에 점진 추가만 함.
3. **Surgical Scope 원칙 준수**: eval/ 폴더 전체 이동(Option A) 거부 → INDEX.md + failure_cases.md 추가(Option B 변형)로 82 cross-reference 무손상.
4. **graceful failure 패턴 일관 적용**: RAG (4-reason fallback), DB (4 status), Critic verdict(server-side derivation) 모두 "실패가 사용자 차단 0건" 원칙 준수.
5. **단계적 pytest 누적**: Slice별로 회귀 0건 (10→23→39→49→62), 각 Slice가 이전 acceptance를 깨지 않음.
6. **failure_cases.md → Critic 자동 차단 검증**: FC-001~005가 모두 revise/reject로 차단되는 것을 pytest로 검증 → 품질 트랙 자동화 일부 실현.
7. **CC-001 결정의 신속한 적용**: 식별 → 분석 → Option B 적용 → 62/62 pytest 회귀 0 검증을 같은 세션 내 완료.

### 안 된 것

1. **CC-001 drift를 진입 점검에서 못 잡음**: phase-start v1.1.0 §6.1 Assumptions 작성 시 "api_contract와 출력 형식이 일치한다"고 명시했으나, 실제로 `plan_options` / `plans` / `plan_candidates` 3-way 명명 차이가 존재. Slice 5 (DB persistence) 구현 sub-agent가 알려준 뒤에야 발견.
2. **fastapi 패키지 이름 충돌 사후 발견**: `backend/fastapi/` 폴더명이 외부 lib `fastapi`와 동일 → pytest 첫 실행에서 ImportError. backend/__init__.py + pyproject.toml로 해결했으나 사전 인지 가능했어야.
3. **/health endpoint의 slice 값 동기화 누락**: Slice 3에서 "3"으로 변경했으나 후속 Slice 4/5/7에서 미동기화 우려 있었음 (실제로는 Slice 5 sub-agent가 "5"로 갱신, 그러나 일관 정책 없음).
4. **PowerShell 5.1 호환 첫 작성 실패**: smoke_test_phase_1.ps1 첫 버전에서 multi-catch + 인라인 조건 표현식 사용해 파싱 오류 → UTF-8 BOM 누락도 의심 → 단순화 + BOM 보강해 해결.
5. **HTTP_422_UNPROCESSABLE_ENTITY DeprecationWarning 미해소**: Starlette upstream 이슈인데 매 pytest 마다 1 warning 표시. 코드에서 `HTTP_422_UNPROCESSABLE_CONTENT` 또는 명시 숫자 사용으로 해소 가능했음.
6. **Slice 1 임시 prompt_id `P-PHASE1-COMBINED`가 prompt_registry 미등록**: Slice 2에서 분리되며 사라졌지만, 일시적으로 registry와 코드 간 명명 불일치 존재.
7. **assumptions.md §1.2 불확실 U1~U5 검증 결과 미수집**: LLM 응답시간, gpt-4o-mini 한국어 품질, pgvector hit율 등 실측 데이터 0건 (모두 mock 사용 + 사용자 .env 입력 보류).

### 배운 것

1. **assumptions.md §1.1 "확정 가정"에 contract 정합 점검 포함 필요**: 단순히 "contract 변경 없이 구현 가능"이 아니라 "contract 내부 명명이 일관"임을 명시 검증해야 함.
2. **Python 패키지명 외부 lib 충돌 방지 가이드 필요**: tech_stack_contract.md에 "외부 lib 이름 사용 금지 또는 namespace 분리" 규칙 명시.
3. **Sub-agent 발사 시 폴더 분리 표준 패턴 유효**: 같은 폴더 동시 변경은 sequential, 다른 폴더는 parallel 안전. multi_slice_plan.md §2 충돌 분석 매트릭스가 효과적이었음.
4. **graceful failure 패턴이 testability를 높임**: RAG/DB/LLM 실패 시도 정상 200 응답 → mock으로 모든 케이스 자동화 가능. Phase 4+ MOA Lite 전체에 동일 패턴 권장.
5. **failure_cases.md를 Critic 학습에 자동 통합 가능**: FC-001~005를 pytest로 자동 검증 → "Critic 회귀" 게이트 자연스럽게 구축됨. Phase 4 revise loop 도입 시 동일 패턴 확장.
6. **PowerShell 5.1 호환 표준 필요**: UTF-8 BOM + 단순 try/catch + 인라인 조건 회피.

### 근본 원인 (5 Whys — CC-001 drift)

**문제**: `plan_options` / `plans` / `plan_candidates` 3-way 명명 drift를 Phase 1 진입 점검에서 못 잡고 Slice 5에서야 발견.

```
왜 1: phase-start v1.1.0 §6.1 Assumptions 4점검 시 contract 전체를 읽지 않고 §POST /api/v1/generate 한 섹션만 부분 읽음 (Surgical Scope 원칙)
왜 2: Surgical Scope는 "관련 부분만 읽기"인데 contract 내부 cross-reference (output_schema body 키 = api_contract response 키) 정합성은 한 섹션만 봐선 검증 불가
왜 3: harness-audit Skill에 "contract 간 핵심 명명 cross-check" 단계 없음
왜 4: Phase 0 마이그레이션 시 contract 작성을 sub-agent 분산으로 진행 (S3-1/2/3) → 각 contract 자체는 깊은 작성됐지만 contract 간 일관성 검증이 후행 점검에 의존
왜 5: harness 진입 점검 자체에 "내부 contract 일관성 자동 검증" 도구가 없음 — Phase 0에서 placeholder marker / 9줄 stub 점검은 자동화됐지만 명명 일관성은 사람 눈에 의존
```

**근본 결론**: contract 간 명명 일관성 검증을 자동화하지 않으면, sub-agent 분산 작성으로 인한 drift는 phase 진입 점검만으로는 잡히지 않는다.

### 부가 근본 원인 (영향-빈도)

| 항목 | 영향 | 빈도 | 분류 |
|---|---|---|---|
| CC-001 drift | 큼 (API/DB/FE 모두 영향) | 낮음 (Phase 1만) | 즉시 개선 → §개선 제안 1 |
| fastapi 패키지 충돌 | 보통 (테스트 실행 차단) | 낮음 (1회) | 매뉴얼 대응 + 가이드 추가 |
| /health slice 동기화 | 작음 (관측성만) | 보통 (매 Slice) | 자동화 |
| PowerShell 5.1 호환 | 작음 (한 번만 발생) | 낮음 | 무시 가능 |
| DeprecationWarning | 작음 (cosmetic) | 매 테스트 | 자동화 (low priority) |
| U1~U5 미검증 | 보통 (Phase 4+ 영향) | 낮음 | 매뉴얼 대응 (사용자 .env 입력 후) |

---

## 개선 제안

### 제안 1: harness-audit Skill에 "contract 명명 cross-check" 단계 추가 (우선순위: 높음)

- **무엇을**: harness-audit 절차에 "API ↔ DB ↔ Frontend types 핵심 명명 자동 검사" 단계 신설
- **왜**: CC-001 같은 drift는 사람 눈으로 잡기 어려움. 자동화로만 안정 점검 가능.
- **어디에**: `.claude/skills/harness-audit/SKILL.md` v1.0.0 → v1.1.0
- **구현 안**:
  - `scripts/audit_naming.ps1` (or .py) — 핵심 명명 집합(예: plan_candidates, video_projects, agent_io_logs) 정의 + 모든 .py/.ts/.md grep해 출현 위치 매트릭스 생성 + 동일 개념 다른 이름 사용 시 WARN
- **영향**: harness-audit 실행 시간 +30초, 정합성 보증 ↑
- **위험**: false positive 가능 (동음이의어) → whitelist 관리 필요
- **상태**: meta/proposals/2026-05-26_harness-audit-naming-check.md 등록 권장

### 제안 2: phase-start v1.2.0 §6.1 Assumptions에 "contract cross-reference 점검" 항목 추가 (우선순위: 높음)

- **무엇을**: §6.1 Assumptions 작성 시 "외부 contract 일관성" 명시 항목 추가
- **왜**: 4점검은 phase 진입 안정성을 담보하는데, contract 정합은 가장 큰 사후 위험. assumptions.md에 "체크했음" 또는 "체크 못함, U-X로 기록" 명시.
- **어디에**: `.claude/skills/phase-start/SKILL.md` v1.1.0 → v1.2.0 §6.1
- **변경 안**:
  ```
  추가 항목:
  - 본 Phase scope에 직간접 영향 contract 간 핵심 명명 일관성 (자동 audit 후 결과 기록)
  ```
- **영향**: phase 진입 작업 +5~10분
- **위험**: 없음 (점검 강화일 뿐)
- **상태**: meta/proposals/2026-05-26_phase-start-cross-check.md 등록 권장

### 제안 3: qa-check 카테고리 11 "Contract Drift" 추가 (우선순위: 보통)

- **무엇을**: qa-check 10 카테고리 + 신규 카테고리 11 "Contract Drift" — Phase 종료 시 사용
- **왜**: 매 Phase 종료 시점에 다시 자동 검사 → 점진적 drift 방지
- **어디에**: `.claude/skills/qa-check/SKILL.md` v1.1.0 → v1.2.0
- **영향**: qa-check 실행 시간 소폭 증가
- **위험**: 없음
- **상태**: meta/proposals/ 등록

### 제안 4: tech_stack_contract.md에 "Python 패키지명 충돌 방지" 가이드 추가 (우선순위: 낮음)

- **무엇을**: tech_stack_contract.md에 외부 lib과 동일 이름 사용 시 namespace 분리 가이드 명시
- **왜**: fastapi 충돌과 같은 사후 발견 방지
- **어디에**: `docs/contracts/tech_stack_contract.md` (v1.0 → v1.1)
- **상태**: 우선순위 낮음 (1회 발생, 해결책 이미 적용)

### 제안 5: 자동 smoke test를 phase-complete 절차에 통합 (우선순위: 보통)

- **무엇을**: phase-complete Skill 절차에 자동 smoke test 실행 단계 추가 (현재는 manual instructions 위주)
- **왜**: 자동 가능 부분(pytest + uvicorn 부트 + /health + frontend build artifact)은 매 Phase 종료 시 게이트로 사용
- **어디에**: `.claude/skills/phase-complete/SKILL.md`
- **참조**: `scripts/smoke_test_phase_1.ps1`이 이미 좋은 baseline
- **상태**: 우선순위 보통 (이미 Phase 1에서 실행했지만 절차 미명시)

### 제안 6: assumptions.md §1.2 불확실 항목 자동 추적 표 (우선순위: 낮음)

- **무엇을**: U1~UN 항목을 PROJECT_STATE.md `phase_X_unresolved_uncertainties` yaml 블록으로 자동 trackable하게
- **왜**: 매 Phase 종료 시 unresolved U-X 항목 visible — 누락 방지
- **어디에**: PROJECT_STATE.md template + phase-start §6.1 + phase-complete 절차
- **상태**: 우선순위 낮음 (관리 비용 vs 이득 균형)

---

## 다음 액션

```
- [x] 본 회고 문서 작성 완료
- [ ] 제안 1 (harness-audit naming check) → meta/proposals/ 등록
- [ ] 제안 2 (phase-start cross-check) → meta/proposals/ 등록
- [ ] 제안 3 (qa-check 카테고리 11) → meta/proposals/ 등록
- [ ] 제안 5 (phase-complete smoke test 통합) → meta/proposals/ 등록
- [ ] 사용자 검토 (4 제안의 우선순위 / 채택 여부)
- [ ] 채택안은 contract-change Skill 통해 Skill SKILL.md / contract 갱신
- [ ] meta/patterns.md에 "contract drift 사후 발견" 패턴 등록
- [ ] meta/skill_usage_log.md 갱신 (Phase 1에서 사용된 Skill 누적)
```

---

## 패턴 등록 (meta/patterns.md 후보)

| 패턴 ID | 설명 | 관련 회고 | 상태 |
|---|---|---|---|
| P-DRIFT-001 | sub-agent 분산 작성으로 인한 contract 명명 drift가 사후 발견됨 | phase-1 (CC-001) | 개선 진행 중 (제안 1, 2) |
| P-SLICE-001 | Simplest Slice 3회 압축 원칙이 첫 Slice 디버깅 비용 ↓ | phase-1 | 채택 — phase-start v1.1.0 §6.2 |
| P-GRACEFUL-001 | RAG/DB/LLM 실패 graceful 패턴 = test 자동화 ↑ | phase-1 (Slice 4/5) | 채택 — Phase 4+ 확대 적용 |
| P-FOLDER-PARALLEL-001 | sub-agent 병렬은 폴더 분리로 충돌 0 | phase-1 (Wave 1/4) | 채택 — multi_slice_plan 표준 |

---

## Skill 사용 로그 (Phase 1 동안)

| Skill | 사용 횟수 | 비고 |
|---|---|---|
| phase-start | 1 | v1.0.0 → v1.1.0 강화 후 사용 |
| qa-check | 8 | 각 Slice + 진입 + 최종 (v1.1.0 §10 Simplicity 모두 PASS) |
| contract-change | 1 | CC-001 (Option B 적용) |
| meta-retrospective | 1 (지금) | 본 문서 |
| harness-audit | 0 | Phase 종료 후 별도 실행 권장 (개선안 적용 시) |
| design-review | 0 | Phase 2 진입 시 (디자인 작업 본격화) |
| eval-design / eval-run | 0 | failure_cases.md 신규 작성은 INDEX.md + ADR로 처리 (Skill 미사용) |

---

## 변경 이력

- 2026-05-26: Phase 1 회고 최초 작성 (phase-complete 절차 6단계 자동 호출)
