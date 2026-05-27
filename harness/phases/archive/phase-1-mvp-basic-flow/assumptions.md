# Phase 1 — Assumptions / Simplest Slice / Surgical Scope / Verification

> phase-start Skill v1.1.0 §6 Phase 진입 4점검 결과
> 작성일: 2026-05-26
> 작성자: Claude (Opus 4.7)
> 적용 대상 Phase: phase-1-mvp-basic-flow

---

## 1. Assumptions (가정)

### 1.1 확정 가정

| # | 가정 | 근거 |
|---|---|---|
| A1 | OpenAI API 가용 + gpt-4o-mini 응답시간 ≤ 30초 | OpenAI SLA, 일반 사용 패턴 |
| A2 | Supabase Free Tier로 Phase 1 전 기간 충분 | 트래픽 < 100 req/일 가정 |
| A3 | `docs/contracts/api_contract.md` POST /api/v1/generate 스펙은 변경 없이 구현 가능 | Phase 0에서 1281줄 깊은 작성 완료 |
| A4 | `output_schema.md` v1.0 envelope 구조 (meta/body/validation) 그대로 사용 | Phase 0 S3에서 668줄 확정 |
| A5 | 사용자 입력은 한국어 평문 텍스트 (이미지/파일 업로드 없음) | mvp_scope §1 |
| A6 | Critic Agent revise 없이 1회 평가만 (Phase 1) | scope.md 명시 |
| A7 | 인증 없이 익명 저장 가능 (Phase 5에서 Auth 추가) | dependencies.md |
| A8 | pgvector 미연결 시 fallback (빈 RAG 결과) 허용 | acceptance.md A3 |

### 1.2 불확실 항목 (Phase 1 진행 중 검증 필요)

| # | 불확실 항목 | 검증 방법 | 미검증 시 영향 |
|---|---|---|---|
| U1 | gpt-4o-mini 한국어 영상기획 품질 | 첫 10케이스 수동 평가 | 품질 미달이면 gpt-4o 폴백 필요 |
| U2 | 4 Agent 직렬 호출 총 소요시간 (목표 30~60초) | 실측 후 P95 확인 | 60초 초과 시 stepper UX 부적합 |
| U3 | pgvector 검색 정확도 (지식 베이스 작음) | RAG hit rate 측정 | 0% 가까우면 RAG fallback이 기본 케이스화 |
| U4 | Intent Filter의 false positive 비율 | golden_set GS-001~003 + 추가 5케이스 | 정상 입력 차단 시 UX 불가능 |
| U5 | output_schema validation 오버헤드 | 실측 응답시간 비교 | 너무 느리면 sampling validation |

**기록 위치**: 검증 결과는 `eval/regression_results/phase-1-uncertainty-*.md`에 누적.

---

## 2. Simplest Slice (최소 작동 단위)

### 2.1 압축 과정 (3회 반복)

**1차 답:**
> 입력 → Intent → Direction → RAG → Planning → Critic → DB 저장 → Next.js UI 표시

**"더 줄일 수 있는가?" (1회 반복)**

**2차 답:**
> 입력 → Intent + Planning 통합 → return JSON (DB 미저장, UI 미구현, RAG 미연결)

**"더 줄일 수 있는가?" (2회 반복)**

**3차 답:**
> `curl POST /api/v1/generate -d '{"input":"..."}'` → JSON 1개 반환

**"더 줄일 수 있는가?" (3회 반복)**

**최종 답 (더 줄일 수 없음):**

```
POST /api/v1/generate (FastAPI 단일 endpoint)
  ↓
gpt-4o-mini 1회 호출 (Intent + Planning 결합 프롬프트 1개)
  ↓
output_schema v1.0 JSON 반환
```

**파일 ≤ 5개로 구현 가능:**
- `backend/fastapi/main.py` (FastAPI 부트)
- `backend/fastapi/routers/generate.py` (POST endpoint)
- `backend/fastapi/schemas/output.py` (Pydantic 모델)
- `backend/fastapi/agents/intent_planning.py` (단일 호출 프롬프트)
- `backend/fastapi/.env.example`

### 2.2 Simplest Slice 동작 검증 방법

```bash
# Slice 1만 동작 → 통과 기준
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"input": "유튜브 채널 첫 영상 기획해줘"}'

# 기대 응답
HTTP 200
{
  "meta": { "schema_version": "1.0", ... },
  "body": { "plan_candidates": [ {...} ], ... },
  "validation": { ... }
}
```

### 2.3 Slice → Full 확장 순서

```
Slice 1 (필수): API + 단일 LLM 호출 + JSON 반환
  ↓ (검증: curl 동작)
Slice 2: Intent / Planning Agent 분리
  ↓ (검증: golden_set GS-001~003 통과)
Slice 3: Critic Agent 추가 (1회 평가)
  ↓ (검증: critic_evaluation 필드 채움)
Slice 4: RAG Lite + fallback
  ↓ (검증: rag_references 필드 채움)
Slice 5: Supabase 저장 (video_projects, plan_candidates)
  ↓ (검증: DB row 확인)
Slice 6: Next.js 진입 UI (/, /plan)
  ↓ (검증: localhost:3000 동작)
Slice 7: 진행 stepper + 오류 카드
  ↓ (검증: A1~A8 전체 통과)
```

각 Slice는 독립 commit + smoke test 통과 후 다음 Slice 진입.

---

## 3. Surgical Scope (수술적 범위)

### 3.1 editable (이 Phase에서 신규/수정)

```
backend/fastapi/
  main.py                  (신규)
  routers/generate.py      (신규)
  agents/intent.py         (신규)
  agents/planning.py       (신규)
  agents/critic.py         (신규)
  rag/retriever.py         (신규)
  schemas/output.py        (신규)
  schemas/input.py         (신규)
  db/supabase_client.py    (신규)
  config.py                (신규)
  .env.example             (신규)
  requirements.txt         (신규)
  Dockerfile               (신규, 선택)

apps/web/
  app/page.tsx             (신규)
  app/plan/page.tsx        (신규)
  app/layout.tsx           (신규)
  components/ProgressStepper.tsx  (신규)
  components/ErrorCard.tsx        (신규)
  components/PlanCard.tsx         (신규)
  lib/api.ts               (신규)
  public/manifest.json     (신규)
  next.config.js           (신규)
  package.json             (신규)
  tsconfig.json            (신규)
  tailwind.config.ts       (신규)
  .env.local.example       (신규)

phases/active/phase-1-mvp-basic-flow/
  notes.md                 (진행 메모, 누적 작성)
  work_plan.md             (작업 단위 분해)

meta/handoffs/
  2026-05-26_phase-1-entry.md (이번 진입 기록)
  YYYY-MM-DD_phase-1-*.md     (필요 시 진행 중 추가)

eval/qa_reports/
  phase-1-*.md             (smoke test 결과 등)

eval/regression_results/
  phase-1-uncertainty-*.md (불확실 항목 검증 결과)

PROJECT_STATE.md           (Phase 진행 상태 갱신)
PHASE_REGISTRY.md          (필요 시 Phase 1 진행 메타 갱신)
```

### 3.2 read-only (참조만, 변경 시 contract-change 필수)

```
docs/contracts/             ← 전부 read-only
ai_system/prompts/          ← P-001~P-008 프롬프트 read-only
ai_system/agents/           ← Agent 정의 read-only
ai_system/orchestration/    ← flow / moa_policy read-only
knowledge/                  ← RAG 데이터 read-only (rag-update Skill 별도)
product/                    ← 제품 정의 read-only
eval/golden_set.md          ← 테스트 케이스 read-only
eval/video_planning_eval.md ← 평가 기준 read-only
apps/web/design.md          ← 화면 설계 read-only
apps/web/page_map.md        ← read-only
apps/web/component_map.md   ← read-only
.claude/skills/             ← Skill 정의 read-only
instruction_index/          ← 라우팅 read-only
```

### 3.3 forbidden (절대 접근 금지)

```
phases/archive/             ← Phase 0 완료분, 기본 참조 금지
phases/planned/phase_2~30   ← 미래 Phase 영역
backend/spring/             ← Phase 21+ (현재 placeholder)
apps/mobile/                ← Phase 21+ (현재 placeholder)
packages/                   ← Phase 11+ (현재 placeholder)
_staging/                   ← 이식 소스 (역사적 보존)
```

### 3.4 위반 감지 절차

editable 외 파일 수정 필요성 발견 시:

```
1. 작업 일시 정지
2. 사용자에게 알림 ("X 파일 수정 필요, scope creep 가능성")
3. 선택지 제시:
   a) Phase 1 scope 확장 (contract-change + multi-llm-validation 필수)
   b) 후속 Phase로 이관 (work_plan.md에 기록)
   c) 우회 방법 모색 (editable 내에서 해결)
4. 결정 기록 후 진행
```

---

## 4. Verification (검증)

### 4.1 성공 기준 ↔ 검증 방법 매핑

| acceptance | 검증 항목 | 검증 방법 | 자동/수동 | 도구 |
|---|---|---|---|---|
| A1 | end-to-end 흐름 | curl + JSON schema validation | 자동 | `pytest backend/tests/e2e.py` |
| A2 | Intent Filter | golden_set GS-001~003 | 자동 | `pytest backend/tests/intent.py` |
| A3 | RAG fallback | pgvector 끊긴 상태에서 호출 | 자동 | `pytest backend/tests/rag_fallback.py` |
| A4 | Supabase 저장 | DB row count 비교 | 자동 | `pytest backend/tests/db.py` |
| A5 | Next.js 진입 | localhost:3000 manual | 수동 | 브라우저 |
| A6 | output_schema 준수 | GS-001 입력으로 schema validation | 자동 | `pytest` + `jsonschema` |
| A7 | 환경변수 문서화 | `.env.example` lint | 자동 | shell script |
| A8 | non_goals 미포함 | grep 검사 (TTS, upload 등) | 자동 | `scripts/check_non_goals.sh` |

### 4.2 자동화율 목표

```
자동화 가능 acceptance: 7/8 (87.5%)
수동만 가능 acceptance: 1/8 (A5 — UI 시각 확인)
```

수동 검증 A5도 Playwright로 부분 자동화 가능 (Phase 4+ 권장).

### 4.3 회귀 방지

각 Slice 완료 시:
- 이전 Slice의 acceptance 자동 테스트 재실행
- 실패 시 즉시 fix (다음 Slice 진입 차단)

CI 도입 시점: Phase 10 (배포 단계). Phase 1~9는 로컬 manual 실행.

### 4.4 Smoke Test (Phase 1 종료 직전)

```
1. 로컬 backend 기동: uvicorn backend.fastapi.main:app
2. 로컬 frontend 기동: cd apps/web && npm run dev
3. http://localhost:3000 접근
4. "유튜브 채널 첫 영상 기획해줘" 입력
5. /plan 페이지 자동 이동 확인
6. 기획안 카드 1개 표시 확인
7. Supabase 대시보드에서 row 생성 확인
8. 비관련 입력 ("오늘 날씨 어때?") 으로 INV-001 오류 확인
```

위 8단계가 막힘없이 끝까지 가야 phase-complete 진입 가능.

---

## 5. 4점검 요약 (한눈 보기)

| 점검 | 결과 요지 |
|---|---|
| Assumptions | 확정 8개 + 불확실 5개 (U1~U5 검증 필요) |
| Simplest Slice | curl → JSON 1개 (파일 5개) → Slice 1~7로 점진 확장 |
| Surgical Scope | editable 26개 위치 / read-only 13개 영역 / forbidden 6개 영역 |
| Verification | 7/8 자동화 (87.5%) + smoke test 8단계 |

---

## 6. 다음 단계

이 4점검 결과를 바탕으로:
1. `work_plan.md` 작성 (Slice 1~7 작업 단위 분해)
2. `meta/handoffs/2026-05-26_phase-1-entry.md` 작성 (진입 handoff)
3. `eval/qa_reports/phase-1-entry-check_2026-05-26.md` 작성 (점검 보고서)
4. `docs/decisions/phase_1_simplest_slice.md` 작성 (ADR)
5. 첫 작업 단위 선정: **Slice 1 (FastAPI 단일 endpoint + JSON 반환)**

---

## 7. 변경 이력

- 2026-05-26: Phase 1 진입 4점검 최초 작성 (phase-start v1.1.0 §6 적용)
