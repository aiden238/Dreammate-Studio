# AGENTS.md — Dreammate Studio 통합 운영 규약 (단일 md 하네스)

> **이 한 파일이 곧 운영 정책입니다.** Codex · Claude Code · Copilot 등 어떤 코딩 에이전트가 들어와도
> 이 문서 하나로 **agents(역할) · skills(자동 트리거) · rules(규칙) · commands(절차)** 를 모두 라우팅합니다.
> 이것이 본 프로젝트의 **"나만의 기법" — 단일 md로 agent/skills/rules/commands를 통합한 하네스**입니다.
>
> 상세 라우팅 본문은 `harness/AGENTS.md`(구현·QA) / `harness/CLAUDE.md`(기획·설계)로 분리되어 있고,
> 본 루트 문서는 그 둘을 묶는 **단일 진입점(single entry point)** 입니다.

---

## 0. 30초 요약 (에이전트가 가장 먼저 읽는 부분)

- 제품: **영상기획 AI 에이전트** (영상 제작 도구 아님).
- 작업 전 항상 `harness/PROJECT_STATE.md`로 현재 Phase를 확인한다.
- 모든 결정의 **단일 진실 소스 = `harness/docs/contracts/`**. 직접 수정 금지 → `contract-change` 스킬 절차.
- 스킬은 `.claude/skills/`의 **키워드 자동 트리거**. 수동 호출 불필요.
- 범위 밖(영상 제작/자동 편집/자동 업로드) 구현 금지.

---

## 1. AGENTS — 누가, 무엇을 (역할 라우팅)

| 에이전트 유형 | 라우터 문서 | 담당 |
|---|---|---|
| 기획 · 설계 · 검토형 (Claude/GPT/Gemini) | `harness/CLAUDE.md` | 비전·아키텍처·평가체계·ADR |
| 구현 · QA · 테스트형 (Codex/Copilot/Claude Code) | `harness/AGENTS.md` | 프론트·백엔드·AI 파이프라인·RAG |

> **듀얼 라우터 + 단일 진입점**: 본 파일(AGENTS.md)이 두 라우터를 묶는다.
> 작업 유형이 분명하면 해당 라우터로, 불분명하면 본 파일 §0 규칙을 따른다.

---

## 2. SKILLS — 언제, 어떻게 (자동 트리거 스킬 21종)

`.claude/skills/<name>/SKILL.md` 단일 폴더. `applies_to` 태그로 적용 모델을 분리(`[claude]`/`[agents]`/양쪽).
**description 키워드 매칭으로 자동 발동** — 사용자가 명령어를 외울 필요가 없다(= commands를 스킬이 흡수).

| 상황(키워드) | 자동 발동 스킬 |
|---|---|
| contract/스키마/정책 변경 | `contract-change` (절차 강제) |
| 평가·회귀·golden_set | `eval-run` |
| RAG·지식 추가·승격 | `rag-update` (5단계 승격) |
| 프롬프트 변경·모델 변경 | `prompt-version-review` (semver) |
| 큰 결정·교차검증 | `multi-llm-validation` (Claude·GPT·Gemini) |
| Phase 시작/종료 | `phase-start` / `phase-complete` |
| 보안·PII·prompt injection | `security-review` |
| 비용·토큰 | `cost-review` |
| 버그·예외 | `bug-triage` |
| 회고·하네스 개선 | `meta-retrospective` / `harness-audit` |
| 하네스 생성(메타) | `harness-factory` (proposal-only) |
| 컨텍스트 압축·핸드오프 | `context-compact` (최우선) |

> 충돌 시 우선순위: `context-compact` > `contract-change` > `multi-llm-validation` > `phase-start` > `phase-complete`.

---

## 3. RULES — 절대 규칙 (rules 통합)

1. `harness/docs/contracts/`는 **직접 수정 금지** → `contract-change` 제안·승인 절차.
2. **현재 active Phase만** 우선 참조. `phases/archive/`는 기본 참조 금지.
3. MVP 범위 밖 기능(영상 제작·자동 편집·TTS·자동 업로드) 구현 금지.
4. API 응답 스키마 임의 변경 금지.
5. 사용자 데이터를 바로 global RAG에 넣지 않는다 → `rag-update` **5단계 승격** 필수.
6. `--no-verify`(skip hooks) 금지(명시 허가 없이는).
7. **키·자격증명은 저장소에 포함하지 않는다**(`.env`는 user-provided).
8. 큰 설계 결정은 **ADR(`harness/docs/decisions/`)로 기록**한다.

---

## 4. COMMANDS — 절차(명령) = 스킬 호출

별도의 슬래시 커맨드 셋을 두지 않고, **모든 절차를 스킬로 통합**한다. 대표 절차:

```text
새 작업 진입   → phase-start  (PROJECT_STATE → 현재 Phase scope 확인)
contract 변경  → contract-change (제안 → 검토 → 승인 → 반영)
품질 게이트    → eval-run + qa-check (golden_set 회귀, 임계값 차단)
배포 전 점검   → qa-check (MVP 범위·스키마·모바일·로그)
작업 마감      → phase-complete → meta-retrospective (문서 동기화 + 회고)
```

---

## 5. KNOWLEDGE — 암묵지 관리 (최신 LLM Wiki)

- `harness/knowledge/llm_wiki/` — **최신 LLM 기반 암묵지**(영상기획·후킹·평가기준 등)를 직접 정리·운영.
- `harness/knowledge/rag/` — RAG 정책(메타데이터·검색·품질필터·승격).
- 원칙: **검증된 지식만** 승격(5단계)해 RAG에 반영 → 모델 환각·오염 방지.

---

## 6. 진입 순서 (요약)

```text
1. AGENTS.md (이 파일)            ← 통합 규약/라우팅
2. harness/PROJECT_STATE.md       ← 현재 Phase
3. harness/AGENTS.md 또는 CLAUDE.md ← 작업 유형별 상세 라우터
4. 관련 harness/docs/contracts/*   ← 단일 진실 소스
5. 관련 .claude/skills/*/SKILL.md  ← 자동 트리거 스킬
```

---

## 7. 문서 지도 (채점·온보딩 공용)

| 보고 싶은 것 | 경로 |
|---|---|
| 기획서·요구사항 | `docs/grading/01_기획서_요구사항.md` |
| WBS·일정 | `docs/grading/02_WBS_일정.md` |
| 아키텍처·ADR | `docs/grading/03_아키텍처_ADR.md` |
| setup·deploy·testing | `docs/grading/04_setup_deploy_testing.md` |
| 발표 슬라이드 | `docs/index.html` (GitHub Pages) |
| 발표 대본(5분) | `docs/발표대본_5분.md` |

> 본 프로젝트는 **단일 md(AGENTS.md)로 agent·skills·rules·commands·knowledge를 통합**하고,
> 실제 운영은 `.claude/skills` 자동 트리거 + `docs/contracts` 단일 진실 소스 + multi-LLM 교차검증으로 굴린다.
> 이것이 1인 운영에서도 일관성과 회귀 안전성을 만든 **본인만의 기법**이다.
