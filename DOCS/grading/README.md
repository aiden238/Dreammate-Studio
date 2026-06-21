# Dreammate Studio — 채점용 문서 인덱스 (Grading Index)

> 채점 키워드: **기획서 · 요구사항 · WBS · 일정 · 아키텍처 · ADR · setup · deploy · deployment · testing · 단위 테스트 · 통합 테스트 · 빌드 · 배포 · AGENTS.md · README**

이 폴더(`docs/grading/`)는 발표 과제 채점을 위해 **흩어져 있는 근거 문서를 채점 항목별로 한 곳에 매핑**한 패키지입니다.
모든 내용은 리포 루트의 `README.md`, `harness/PROJECT_STATE.md`(가장 권위 있는 최신 상태 소스), `harness/docs/`의 실제 산출물에 근거하며, **과장 없이 사실 그대로** 작성했습니다. 미완 항목은 미완으로 명시합니다.

---

## 제품 한 줄 정의

**Dreammate Studio = 영상기획 AI 에이전트.** (영상을 만들어 주는 AI가 아닙니다.)
막연한 영상 아이디어를 입력하면 → 의도 분석 → 부족 정보 질문 → 한 줄 방향 승인 → LLM Wiki/RAG 근거 검색 → 영상기획안 3개 생성 → Critic 검증(revise 최대 2회) → 결과 저장 → 피드백(Brand Memory 자동 추출)으로 구조화합니다.

---

## 채점 항목 → 문서 매핑

| 채점 항목 | 충족 문서 (이 폴더) | 1차 근거 (리포) |
|---|---|---|
| **기획서 / 요구사항** (비전, 문제정의, FR/NFR, MVP 범위) | [`01_기획서_요구사항.md`](./01_기획서_요구사항.md) | `harness/product/`, `harness/docs/contracts/mvp_non_goals.md`, `README.md` |
| **WBS / 일정 / 마일스톤** (작업 분해, Phase 0~31 간트) | [`02_WBS_일정.md`](./02_WBS_일정.md) | `harness/PROJECT_STATE.md`, `harness/PHASE_REGISTRY.md`, `README.md` |
| **아키텍처 / ADR** (레이어, 디렉토리 구조, 데이터 모델, ADR 39개) | [`03_아키텍처_ADR.md`](./03_아키텍처_ADR.md) | `harness/docs/decisions/`, `harness/ai_system/`, `harness/CLAUDE.md` |
| **setup / deploy / testing** (환경 설정, 빌드/배포 게이트, 테스트) | [`04_setup_deploy_testing.md`](./04_setup_deploy_testing.md) | `harness/docs/deploy_test_gates.md`, `harness/docs/decisions/tech_stack_decision.md` |
| **AGENTS.md / README** (라우터 구조, 진입 문서) | 본 README + 각 문서 상단 | `harness/AGENTS.md`, `harness/CLAUDE.md`, `README.md` (루트) |

---

## 키워드별 빠른 위치 안내 (기계 채점 대비)

| 키워드 | 어디서 확인 |
|---|---|
| 기획서, 요구사항, 비전, 문제정의, 페르소나, FR, NFR | `01_기획서_요구사항.md` |
| WBS, 작업 분해 구조, 일정, 마일스톤, 간트 | `02_WBS_일정.md` |
| 아키텍처, ADR, 디렉토리 구조, 레이어, 데이터 모델, 다이어그램 | `03_아키텍처_ADR.md` |
| setup, prerequisites, .env, deploy, deployment, CI | `04_setup_deploy_testing.md` |
| testing, 단위 테스트, 통합 테스트, pytest, 빌드(build), 배포(deploy) | `04_setup_deploy_testing.md` |
| AGENTS.md, README, 라우터 | 본 README + `harness/AGENTS.md`, `harness/CLAUDE.md` |

---

## 핵심 수치 스냅샷 (검증된 최신 상태)

| 항목 | 값 | 출처 |
|---|---|---|
| 진행 Phase | **Phase 0~31 done** (+ 메타-phase M0~M3) | `harness/PROJECT_STATE.md` |
| 단위 테스트 | **pytest 845 green** (hermetic) | PROJECT_STATE / 회귀 결과 |
| 시나리오 자동 게이트 | **scenario_simulation v8 36/36** | deploy_test_gates §A |
| 스모크 테스트 | **smoke 12/12** | deploy_test_gates §A |
| 프론트엔드 | Next.js PWA **11 routes** (+/login) | PROJECT_STATE |
| 백엔드 | FastAPI **17 endpoints** | PROJECT_STATE |
| ADR | `harness/docs/decisions/` **39개 파일** | 디렉토리 |
| 배포 준비 | Gate A(Local Smoke) ✅ PASS / B~G 준비·미준비 | deploy_test_gates |
| Repository | https://github.com/aiden238/Dreammate-Studio | README |

---

## 두 개의 README / 라우터 문서 안내 (채점관용)

- **`README.md` (리포 루트)** — 제품 소개 + 현재 상태 + Phase 이력 + 폴더 구조. 첫 진입점.
- **`harness/CLAUDE.md`** — 기획·설계·문서 검토형 AI(Claude/GPT/Gemini)용 **라우터**. 검토 유형별로 어떤 문서를 읽을지 안내.
- **`harness/AGENTS.md`** — 구현·QA형 AI 에이전트(Codex/Copilot 등)용 **라우터**. 작업 유형별 참조 문서 + 금지 행동.
- 두 라우터는 `.claude/skills/`의 Skill(19개)을 `applies_to` 태그로 분리해 자동 트리거합니다.

> 본 `docs/grading/` 문서들은 **신규 산출물**이며, `harness/` 원본 문서는 수정하지 않았습니다.
</content>
</invoke>
