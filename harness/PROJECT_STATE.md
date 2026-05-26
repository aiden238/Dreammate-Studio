# PROJECT_STATE

## 현재 상태

영상기획 AI 에이전트 플랫폼의 **하네스 마이그레이션(Phase 0) 완료**.
GPT 155-파일 하네스 골격 + 자체 18-파일 깊은 콘텐츠 + S0~S5 6 Sprint 작업으로 운영 가능한 하네스 완성.
다음 단계는 Phase 1 MVP 기본 플로우 진입 준비.

## 현재 Active Phase

**Phase 1. MVP 기본 플로우** — 🟡 implementation-complete (2026-05-26)
- 7 Slices 모두 commit + push 완료
- pytest 62/62 통과 / Frontend tsc + lint + build 0 errors
- 진입 점검: phase-start v1.1.0 §6 4점검 (assumptions.md)
- 다음 단계: smoke test 8단계 (사용자 manual) → meta-retrospective → phase-complete
- Phase 0 archive: `phases/archive/phase-0-migration/` (참조 금지)

## migration_progress

```yaml
current_sprint: completed
current_sprint_step: 6
total_steps_in_sprint: 6
last_completed_action: "Phase 1 전체 7 Slices 구현 완료 — pytest 62/62 + Next.js build 0 errors. Slice 1~7 모두 commit + push. backend/fastapi/ 28 파일 + apps/web/ 30 파일 + eval/qa_reports/ 9 reports."
next_action: "Phase 1 마무리: smoke test 8단계 (사용자 manual) → meta-retrospective → phase-complete Skill → phases/archive 이동"
blocker: null
phase_0_status: completed
phase_0_completion_date: 2026-05-26
phase_1_status: implementation_complete
phase_1_entry_date: 2026-05-26
phase_1_implementation_complete_date: 2026-05-26
phase_1_current_slice: null  # 모두 완료
phase_1_completed_slices: [1, 2, 3, 4, 5, 6, 7]
phase_1_total_slices: 7
phase_1_pytest_count: 62
phase_1_frontend_pages_built: 5
phase_1_backend_endpoints: 2  # /api/v1/generate + /health
phase_1_qa_reports: 9  # entry + slice 1~7 + smoke_test_instructions
total_commits: 15  # S0~S5(6) + Phase 1 pre-check + entry checks + eval dual-track + slice 1 + multi_slice_plan + 7 slices
last_updated: 2026-05-26
```

## 확정 방향

### 제품 / UX
- 영상 제작 AI가 아닌 **영상기획 AI 에이전트**
- 4계층 데이터 모델: User → Brand → Domain → Series → Video Project
- Hybrid UX: **Discovery Wizard** (신규/콜드스타트, 5단계 카드) + **Quick Mode** (같은 Series 추가)
- Discovery 단계당 카드 5장 (4장 추천 + 1장 "직접 입력")
- 한 호출당 plan 후보 **3개** 생성 → 사용자가 1개 선택
- Intent Filter (영상기획 외 입력 차단)

### 기술 스택
- **MVP**: Next.js 14 PWA + FastAPI + Supabase(PostgreSQL + pgvector)
- **LLM**: gpt-4o-mini 기본, gpt-4o 일부 (Critic 등)
- **Phase 21+**: Expo React Native, Spring Boot, Custom RAG
- 영상 자동 편집 / TTS / BGM / 자동 업로드 → MVP 제외 (영구)

### AI 시스템
- **MOA Lite**: Intent → Planner → Critic → Rewriter
- **Critic revise 최대 2회** (무한 루프 차단)
- **RAG Lite**: candidate_knowledge 5단계 승격 (pending → filtered → evaluated → approved → promoted)
- **prompt-version-review**: semver + golden_set 회귀 + A/B (major 시 10%→50%→100%)
- PII 마스킹 + 프롬프트 인젝션 차단 (Step 1, Step 2 자동 검사)

### 운영
- Brand Memory 자동 추출 + 사용자 검토 가능
- 광고적 표현 차단 단어 검사 ("최고의", "혁신적인" 등)
- 30–60초 생성 대기 시 4단계 progress stepper + 부분 결과 즉시 노출

## confirmed_decisions (25)

```
[ 1] Discovery + Quick 하이브리드 UX (1.6x 비용 수용)
[ 2] Mode 자동 분기: 신규/Brand 없음 → Discovery, 기존 Series → Quick
[ 3] Discovery 단계당 카드 5장 (4추천 + 1직접입력)
[ 4] 3개 plan 후보 생성 (P-006 plan_candidates)
[ 5] Critic revise 최대 2회 (무한 루프 차단)
[ 6] 4계층 데이터 모델 (Brand/Domain/Series/VideoProject)
[ 7] Intent Filter (영상기획 외 입력 차단)
[ 8] Brand Memory 자동 추출 + 사용자 검토 가능
[ 9] 광고적 표현 차단 단어 검사
[10] 30–60초 생성 대기 시 4단계 progress + 부분 결과 노출
[11] Skill 14 → 20 (이번 세션, GPT 흡수 후)
[12] Skill 폴더: .claude/skills/ 단일 + applies_to 태그
     (v1.2.0 변경: .agents/.claude 분리 → 단일.
      이유: Claude Code Skill 자동 트리거는 .claude/skills/만 인식)
[13] 22 Phase 등록 (1~10 MVP, 11~20 안정화, 21~30 확장)
[14] Phase 0 = 마이그레이션 자체 (지금 active)
[15] context-compact가 모든 Skill 위 최우선
[16] multi-llm-validation 워크플로 (Claude/GPT/Gemini 교대)
[17] agent.html은 토큰 최적화 압축 레이어 (안정화 후 빌드)
[18] RAG candidate_knowledge 5단계 승격 파이프라인
[19] PII 마스킹 + 프롬프트 인젝션 차단 (자동 검사 2단계)
[20] prompt 변경 semver + 회귀 + A/B (major 시 10%→50%→100%)
[21] agent_html_spec v1.1.0 갱신 — v1.2.0 단일 폴더 결정으로 불필요해짐
[22] placeholder marker 표준 형식 (16개 stub 일관 적용)
[23] Sprint별 git commit + sanity script (시작/종료)
[24] PROJECT_STATE.migration_progress 필드로 부분 완료 감지
[25] Claude Code / Codex / Copilot Code 분담 (multi-llm-validation 활용)
```

## 주요 리스크

- `output_schema.md` 불명확 → Sprint S3에서 깊은 작성 (300줄+)
- Golden Set 부족 → Sprint S4에서 시드 10케이스 작성
- LLM 보안 contract 9줄 stub → Sprint S3 우선 보강
- 사용자 데이터 승격 정책 미흡 → Phase 7+ (rag-update Skill 절차로 강제)
- 9줄 stub 16개 (docs/contracts/) → Sprint S3에서 8 보강 + 8 placeholder marker

## 다음 액션

```
Phase 1 마무리 (구현 완료 → 정식 phase-complete까지):

1. Manual smoke test 8단계 (사용자 환경)
   → 가이드: eval/qa_reports/phase-1-smoke-test-instructions_2026-05-26.md
   → 백엔드: uvicorn + .env 설정 / 프론트: npm run dev
   → INV-001 차단 + 정상 응답 + (선택) Supabase 저장 확인

2. Phase 1 final QA report 작성
   → eval/qa_reports/phase-1-final_2026-05-26.md
   → qa-check Skill v1.1.0 전체 10 카테고리 적용

3. Contract drift 정리
   → plan_options (api_contract §4.2) vs plan_candidates (db_schema, Slice 5 구현)
   → contract-change Skill 절차로 통일 결정

4. meta-retrospective Skill 실행
   → meta/retrospectives/phase-1.md 작성
   → 4점검 (assumptions.md 불확실 U1~U5 검증 결과 포함)

5. phase-complete Skill 실행
   → PHASE_REGISTRY Phase 1 → done, Phase 2 → active
   → phases/active/phase-1-mvp-basic-flow/ → phases/archive/ 이동
```
