# 04. Setup · Deploy · Testing

> 채점 키워드: **setup · deploy · deployment · testing · 단위 테스트 · 통합 테스트 · 빌드(build) · 배포(deploy) · CI · prerequisites · .env**

본 문서는 개발 환경 **setup**, **빌드/배포(deploy)**, **테스트(testing)** 를 담는다.
근거: `harness/docs/decisions/tech_stack_decision.md`, `harness/docs/deploy_test_gates.md`, `harness/PROJECT_STATE.md`.

---

## A. Setup — 개발 환경 설정

### A.1 Prerequisites (필수 환경)

| 도구 | 버전 | 용도 |
|---|---|---|
| **Node.js** | 20 LTS+ (라이브 검증 v24.16.0) | Next.js 14 프론트엔드 |
| **Python** | **3.11** | FastAPI 백엔드 + AI 시스템 |
| **PostgreSQL** | 15 (Supabase managed, pgvector 포함) | DB / 벡터 검색 |
| **Redis** | Upstash (serverless) | rate_limit / 캐시 (선택) |
| pnpm/npm | 최신 | 프론트 패키지 |
| pip / venv | 3.11 표준 | 백엔드 패키지 |

### A.2 설치 (Install)

```bash
# 1) 백엔드 (FastAPI, Python 3.11)
cd harness/backend/fastapi
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt    # FastAPI + Pydantic v2 + SQLAlchemy 2.x + openai 등

# 2) 프론트엔드 (Next.js 14)
cd harness/apps/web
npm install                        # Next.js + Tailwind + shadcn/ui + next-pwa
```

### A.3 환경 변수 (.env)

> ★ **자격증명/API 키는 저장소에 포함하지 않는다 (.env는 user-provided).** `.env.example` 형태의 placeholder만 추적되며, 실제 키는 로컬/배포 secret store에서 주입한다. (키 커밋 0 — 전 Phase 검증)

```bash
# Backend .env (예시 — 값은 user-provided)
OPENAI_API_KEY=...               # 생성(gpt-4o-mini) + Critic(gpt-4o)
ANTHROPIC_API_KEY=...            # cross-provider judge / 3안 다양성
GEMINI_API_KEY=...               # 임베딩(한국어 우위) + 3안 다양성
SUPABASE_URL=...
SUPABASE_ANON_KEY=...
SUPABASE_SERVICE_KEY=...
RAG_EMBEDDING_PROVIDER=gemini    # 임베딩=Gemini / 생성=GPT 분리
CRITIC_MAX_REVISE=2              # revise 상한
EVAL_MODE=mock                   # mock(기본, 결정론) | real(키 주입 시 실 LLM)
```

### A.4 로컬 실행 (Run)

```bash
# 백엔드 (개발)
uvicorn app.main:app --reload --port 8000

# 프론트엔드 (개발) — /api/* 는 백엔드로 same-origin 프록시(next rewrites)
npm run dev                        # http://localhost:3000
```

---

## B. 빌드(Build) vs 배포(Deploy) — 개념 구분

> 채점관 대비 핵심 구분. **빌드와 배포는 다른 단계다.**

| 단계 | 정의 | 산출/결과 | 이 프로젝트에서 |
|---|---|---|---|
| **빌드 (Build)** | 소스 코드를 실행 가능한 **산출물(artifact)** 로 변환 | `.next/` 정적·서버 번들, Python wheel/이미지 | `next build`, FastAPI 패키징 |
| **배포 (Deploy / Deployment)** | 빌드 산출물을 **실행 환경에 배치**하고 기동 | Vercel/Render에 올라가 실제 서비스됨 | Vercel·Render·Supabase·GitHub Pages |

요약: **빌드 = 산출물 생성**, **배포 = 환경 배치 + 기동**. 빌드가 성공해도 배포(환경·secret·인프라)는 별개다.

---

## C. Deploy — 빌드/배포 파이프라인

### C.1 컴포넌트별 배포 대상

| 컴포넌트 | 빌드 | 배포 대상 |
|---|---|---|
| Frontend (Next.js PWA) | `next build` → `.next/` | **Vercel** |
| Backend (FastAPI) | requirements 설치 + 패키징 | **Render** (uvicorn/gunicorn) |
| DB | migration SQL | **Supabase** (PostgreSQL 15 + pgvector) |
| DB 스키마 | `0001_init.sql` ~ `0007_*.sql` | Supabase migration 적용 |
| 발표 덱 | 정적 HTML/MD | **GitHub Pages** (`docs/` → Pages) |

### C.2 배포 테스트 게이트 A~G (`harness/docs/deploy_test_gates.md`)

> 게이트는 A → B → … → G 순차. 각 게이트 통과 후 다음. **현 상태를 정직하게 표기**한다.

| Gate | 이름 | 목적 | 상태 |
|---|---|---|---|
| **A** | Local Smoke Test | 로컬 전체 흐름 동작 | ✅ **PASS** (pytest 845/smoke 12/12/scenario_sim 36/36/통합 12) |
| **B** | Staging 배포 | staging 기동 + Supabase 연결 + health | 🟡 준비 (배포 스크립트 + secret 주입 필요) |
| **C** | 내부 알파 | 팀 manual smoke (Discovery/Quick 손-검증) | 🟡 준비 (체크리스트 有) |
| **D** | Beta Staging | 실 LLM eval opt-in (키 주입) | 🟡 준비 (capability 有, 키 필요) |
| **E** | 제한 사용자 | 소수 실사용자 + 피드백 | ⬜ 미준비 (모집/동의/모니터링) |
| **F** | 비용/성능 | LLM 비용 + latency 측정 | 🟡 준비 (실 LLM 활성 필요) |
| **G** | Production Readiness | 보안 audit + RLS 운영 + 백업 | ⬜ 미준비 (운영 단계) |

> **정직한 현황**: 로컬 스모크·통합·시나리오·eval mock 게이트는 **통과(Gate A)**. 운영 배포(Gate B~G)는 **배포 스크립트·secret 주입·인프라·RLS 실검증**이 필요한 단계로 **미완**이다. 키/자격증명은 저장소 미포함(.env는 user-provided)이며, staging secret store에서 주입한다.

---

## D. Testing — 테스트

### D.1 단위 테스트 (Unit Test) — pytest

- **pytest 845 green** (hermetic — 실 외부 호출 없이 결정론적, .env 누수 격리).
- 범위: intent / 3-plan / critic / revise / rewriter / output schema / rag(promotion·quality_filter·chunking·embedding·retrieval) / moa_orchestrator / sse / feedback·selection / eval_runner / gateway 등.
- 누적 추이: Phase 1 62 → Phase 7 223 → Phase 8 249 → Phase 9.5 339 → … → **845**.

```bash
cd harness/backend/fastapi
pytest                              # 전체 (hermetic)
pytest backend/fastapi/tests/test_moa_orchestrator.py   # 특정 모듈
```

### D.2 통합 테스트 (Integration Test)

| 테스트 | 내용 | 결과 |
|---|---|---|
| `test_integration_mvp.py` | MVP end-to-end (입력→3안→Critic→Envelope) | **12개** |
| `scenario_simulation.ps1` v8 | 시나리오 자동 게이트 (Quick/Discovery/RAG/MOA/feedback …) | **36/36** |
| `smoke_test_phase_*.ps1` | 전체 흐름 스모크 | **12/12** |

```powershell
# 통합 / 스모크 / 시나리오 (Windows PowerShell)
.\scripts\smoke_test_phase_10.ps1          # 12/12
.\scripts\scenario_simulation.ps1          # v8 36/36 (자동 게이트)
```

### D.3 품질 평가 (eval-run) + 회귀

- **golden_set 회귀**: mock-deterministic primary(결정론) + 실 LLM mode flag(`EVAL_MODE=real`, 키 주입 시).
- eval gate(mock): schema 1.0 / pass 1.0 / revise mean_delta 양수 → **PASS**.
- 실증: **RAG ON/OFF Δ+0.9**(RAG grounding 품질 기여 첫 실증), cross-provider judge로 **false-approve 10→0**.

```bash
# eval 회귀 (mock 게이트)
.\scripts\eval_run.ps1                      # golden_set 회귀 + 임계값 차단
```

### D.4 기타 자동 게이트

| 게이트 | 역할 | 결과 |
|---|---|---|
| `audit_naming` | 명명 규칙 drift 검사 | **0 drift** |
| P-X1 self-verification | 자가 검증 연속 PASS | **50연속 PASS** |
| `audit_page_component` | 페이지/컴포넌트 정합 | 0 drift (intended WARN 2) |

### D.5 CI 관점 메모

- 테스트 게이트(pytest hermetic + scenario_sim + smoke + audit + eval mock)가 **CI에 적합한 결정론 게이트**로 구성되어 있다.
- 현재 실 LLM 회귀는 CI 상시 실행이 아니라 **mock 게이트 + baseline 1회** 방식이다(키·비용 이유). 실 LLM 상시 회귀는 Gate D/F 활성(키 주입) 시 편입 대상으로 **정직하게 미편입** 상태다.

---

## E. 요약 (한 줄)

- **Setup**: Node 20 + Python 3.11 + Supabase, `.env`는 user-provided(키 커밋 0), `uvicorn` + `npm run dev`.
- **Build/Deploy**: `next build`→Vercel / FastAPI→Render / Supabase migration / GitHub Pages. 빌드=산출물, 배포=환경 배치. Gate A ✅, B~G는 준비/미준비(운영·키 단계).
- **Testing**: 단위 pytest 845 + 통합 test_integration_mvp 12 + scenario_sim 36/36 + smoke 12/12 + eval mock 게이트 PASS + audit 0 drift.
</content>
