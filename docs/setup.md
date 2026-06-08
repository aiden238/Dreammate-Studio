# Dreammate Studio — 환경 설정 / 빌드 / 테스트 / 배포 (setup.md)

> 발표 "개발자 기본 소양"(환경설정·빌드·테스트·배포·CI/CD) 대비 문서.
> 다른 환경에서 그대로 따라 하면 백엔드·프론트가 기동되도록 정직하게 정리했습니다.
> 모든 명령의 기준 경로는 레포 루트(`Dreammate-Studio/`)이며, 실제 코드는 `harness/` 아래에 있습니다.

---

## 0. 한눈에 — 구성 요소

| 영역 | 위치 | 스택 |
|---|---|---|
| 백엔드 (API + AI 엔진) | `harness/backend/fastapi/` | Python · FastAPI 0.115 · Pydantic v2 · OpenAI/Anthropic/Gemini SDK |
| 프론트 (PWA) | `harness/apps/web/` | Node · Next.js 14.2 · React 18 · Tailwind · @xyflow/react |
| DB / Auth | Supabase (PostgreSQL 15 + pgvector) | migration `0001`~`0008` |
| 발표 사이트 | `docs/` | 정적 HTML/CSS (GitHub Pages) |

> ★ 핵심 설계 원칙: **graceful degradation**. 키(OpenAI/Supabase)가 없어도 백엔드는 기동되고
> 테스트는 통과합니다(저장은 in-memory로 휘발, LLM 호출은 mock). 실제 생성·영속은 키가 있을 때만.

---

## 1. 사전 요구사항

- Python **3.11+** (백엔드)
- Node.js **18+** / npm (프론트, `next build`는 Node 20 권장)
- (선택) Supabase 프로젝트 + `psql` 또는 Supabase SQL Editor — 실제 영속·RAG에 필요
- (선택) OpenAI API Key — 실제 기획안 생성에 필요

---

## 2. 백엔드 — 환경 설정 & 실행

```bash
# 1) 가상환경 + 의존성
cd harness/backend/fastapi
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2) 환경변수 (.env) — 생성 없이도 기동되나, 실제 생성에는 키 필요
#    backend/fastapi/.env 에 작성 (이 파일은 .gitignore — 키는 절대 커밋 금지)
#    OPENAI_API_KEY=sk-...
#    SUPABASE_URL=...  SUPABASE_ANON_KEY=...  SUPABASE_SERVICE_KEY=...   # 영속 원할 때만

# 3) 기동 (기준 경로 = harness/)
cd ../../                # → harness/
python -m uvicorn backend.fastapi.main:app --reload --port 8000
# health check
curl http://localhost:8000/health
```

### 2.1 실사용 프로파일 (핵심 루프 한 번에 켜기)

기본값은 안전을 위해 핵심 기능(director 깊이, PKM 주입/추출, 브랜딩 시드, plan 영속)이 **OFF**입니다.
실사용 데모 시에는 단일 스위치로 켭니다:

```bash
# 방법 A — 환경변수 한 줄
APP_PROFILE=realuse python -m uvicorn backend.fastapi.main:app --port 8000

# 방법 B — 준비된 스크립트 (Windows PowerShell)
powershell -ExecutionPolicy Bypass -NoProfile -File harness/scripts/run_realuse_local.ps1
```

→ `output_mode=director` + Brand/Personal PKM 주입·추출 + 브랜딩 시드 + `plans_repo` ON.
참고: `harness/backend/fastapi/.env.realuse.example` (개별 flag 설명 포함).

---

## 3. 프론트엔드 — 환경 설정 & 실행

```bash
cd harness/apps/web
npm install
npm run dev          # http://localhost:3000

# 빌드 / 정적 검증
npm run build        # Next.js 14 프로덕션 빌드 (14개 라우트)
npm run typecheck    # tsc --noEmit
npm run lint         # next lint
```

> 백엔드 주소는 `.env.local` (`harness/apps/web/.env.local.example` 참고)로 지정합니다.

---

## 4. 데이터베이스 — 마이그레이션 (Supabase)

모든 마이그레이션은 **멱등**(`IF NOT EXISTS` / `CREATE OR REPLACE`) → 재실행 안전합니다.

```bash
cd harness
python scripts/apply_migrations.py --list      # 적용 순서 확인 (오프라인)
# DATABASE_URL=postgresql://postgres:<pw>@db.<ref>.supabase.co:5432/postgres
python scripts/apply_migrations.py --apply      # 0001~0008 순서대로 적용
python scripts/apply_migrations.py --verify     # RPC/테이블 존재 검증
```

| # | 파일 | 내용 |
|---|---|---|
| 0001 | `init` | 4계층 코어 (brands/domains/series/video_projects/plans) |
| 0002 | `revise_history` | Critic revise 이력 |
| 0003 | `rls_policy` | RLS 사용자 격리 |
| 0004 | `rag_5stage` | RAG 5단계 + pgvector |
| 0005 | `feedback_selection` | feedback_events / selected_plans / brand_memory |
| 0006 | `pkm_entries` | 개인 PKM |
| 0007 | `personal_pkm_source` | 개인 PKM 출처 |
| 0008 | `match_approved_knowledge` | RAG retrieval RPC |

> psql 미설치 시: Supabase SQL Editor 에 `0001`→`0008` 순서대로 붙여넣기. 상세: `harness/backend/fastapi/db/migrations/README.md`.

---

## 5. 테스트

```bash
# 백엔드 — hermetic(키 불필요, mock-deterministic). 기준 경로 = harness/
cd harness
python -m pytest                 # 814 케이스 통과 (Phase 27 기준)
python -m pytest -q              # 간단 출력

# 시나리오 시뮬레이션 (회귀 게이트)
python scripts/scenario_simulation.py     # 36/36

# 프론트 — 정적 검증
cd apps/web && npm run typecheck && npm run lint && npm run build
```

- 테스트 설정: `harness/pyproject.toml` (`testpaths=backend/fastapi/tests`, `pythonpath=.`).
- **모든 테스트는 키 없이 실행**됩니다(외부 호출 mock). → 비용 0, 결정적.
- 한계(정직): 실 LLM 품질 회귀는 CI에 없고, human 실채점은 아직 0건입니다(Phase 28+ 예정).

---

## 6. 빌드 & 배포

| 대상 | 빌드 | 배포 | 상태 |
|---|---|---|---|
| 발표 사이트(`docs/`) | 정적 | **GitHub Pages 자동** (`.github/workflows/pages.yml`, `main`의 `docs/**` push 시) | ✅ 운영 중 |
| 프론트(`apps/web`) | `npm run build` | (Vercel 등) | 🚧 미연결 |
| 백엔드(`fastapi`) | — (인터프리터) | (Render/Fly/Cloud Run 등 + Supabase) | 🚧 미연결 |

> 발표 사이트 URL은 GitHub Pages 설정에 따라 `https://aiden238.github.io/Dreammate-Studio/` 형태로 게시됩니다.

---

## 7. CI / CD (정직)

- **현재 있는 것**: `.github/workflows/pages.yml` — `main`에 `docs/**`가 push되면 발표 사이트를 GitHub Pages로 자동 배포.
- **현재 없는 것(정직)**: 테스트(pytest)·빌드를 자동 실행하는 CI는 **아직 없습니다.** 품질 게이트는 로컬에서 hermetic pytest(814) + scenario_simulation(36/36) + audit으로 수동 통과시킵니다.
- **다음 단계**: pytest + `npm run build`를 GitHub Actions로 올리는 것이 가장 우선순위 높은 보강 항목입니다(발표 Q&A D-20 대비).

---

## 8. 문제 해결 (FAQ)

- `ModuleNotFoundError: fastapi` → 가상환경 활성화 + `pip install -r requirements.txt`.
- 패키지명 충돌(우리 패키지 이름이 `fastapi`) → 테스트는 반드시 `harness/`에서 실행(`pythonpath=.`).
- 기획안이 mock로 나옴 → `.env`에 `OPENAI_API_KEY` 설정 확인.
- 저장이 재시작 시 사라짐 → Supabase 키 + migration `0001`~`0008` 적용 + `plans_repo`(realuse) 필요.
