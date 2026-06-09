# BOUNDARIES.md — 프로젝트(런타임) ↔ 지침(하네스) 경계 (canonical, 이동 없는 명시적 표시)

> 위치: `harness/BOUNDARIES.md` (repo 루트는 그 상위 `Dreammate_Studio/`)
> 목적: 코드와 지침이 **한 트리에 형제로 공존**하는 구조를, 디렉토리 이동 없이 **기계가 읽을 수 있는 경계**로 명시한다.
> 근거: `meta/factory/factory_contract.md` 규칙1(L1 read-only) — 본 문서는 그 정책을 디렉토리/툴 레이어에서 legible하게 만든다.
> 강제: `.github/CODEOWNERS`(PR 가시성) + `harness/scripts/check_boundaries.py`(diff 게이트). 둘 다 additive — 기존 동작 0 변경.

---

## L1 — Product Runtime (실행 산물 / 결정론 코어)

```
harness/backend/fastapi/**      # FastAPI 백엔드 (159 .py — MOA orchestrator/RAG/agents/llm/db)
harness/apps/web/**             # Next.js PWA 프론트
harness/packages/**             # 공유 패키지
harness/backend/fastapi/db/migrations/**   # DB 스키마 (Supabase 적용 대상)
```

**불변식**
- 메타-하네스(`meta/factory/**`)와 자율 에이전트(향후 shell)는 L1을 **읽기만** 한다 — 한 줄도 직접 수정 금지(factory_contract 규칙1).
- L1 변경은 `docs/contracts/`(L2)의 계약을 따른다. contract와 어긋나는 L1 변경 금지.
- L1은 hermetic(재현가능)·결정론 코어 — 비결정론(LLM 자유선택)을 코어 제어흐름에 넣지 않는다.

## L2 — Guidance / Harness (지침 / 거버넌스)

```
harness/ai_system/**            # 아키텍처·orchestration·prompt_registry
harness/docs/contracts/**       # 계약 (변경은 contract-change Skill 절차)
harness/docs/contract_changes/** harness/docs/decisions/**
harness/knowledge/**            # RAG 정책·LLM Wiki
harness/eval/**                 # 평가·골든셋·회귀결과
harness/meta/**                 # 회고·패턴·self_improvement·factory (메타-하네스)
harness/phases/**               # phase 스펙 (goals/scope/non_goals/acceptance...)
harness/instruction_index/**    # routes.yaml / catalog.yaml / dependency_map.yaml
harness/product/**              # 비전·포지셔닝·MVP scope
harness/.claude/skills/**       # 21 Skill (변경은 contract-change 절차)
harness/CLAUDE.md harness/AGENTS.md harness/PROJECT_STATE.md harness/PHASE_REGISTRY.md
```

**불변식**
- L2의 `docs/contracts/**`·`.claude/skills/**` 변경은 **직접편집 금지** — `contract-change` Skill(제안→검토→승인→반영) 경유.
- 메타-하네스 산출물(HIP 초안·blueprint·scaffold)은 **proposal-first** — `meta/proposals/`·`meta/factory/outputs/`에만 쓰고 자동 적용 0.

## 경계 위생 규칙 (커밋 단위)

1. **계약 격리**: `docs/contracts/**` 변경은 L1 구현 변경과 **별도 커밋**으로 분리(contract-change governance). 한 커밋에 섞지 않는다.
2. **런타임 변경 가시화**: L1(`backend/fastapi`·`apps/web`·`migrations`) 변경 커밋은 PR에서 CODEOWNERS로 표시되고 `check_boundaries.py`가 보고한다.
3. **지침↔코드 혼합 경고**: 한 커밋이 L1 런타임 + L2 거버넌스를 동시에 크게 건드리면 경고(레이어 혼합 = git diff 노이즈 + 계약변경 격리 약화).

## 강제 메커니즘 (현재)

| 레이어 | 도구 | 상태 |
|---|---|---|
| 정책 | `meta/factory/factory_contract.md` 규칙1 (L1 글롭 + git-diff 체크) | 기존 |
| 가시성 | `.github/CODEOWNERS` | ★ 신설(본 작업) |
| 게이트 | `harness/scripts/check_boundaries.py` (pre-commit/CI 연결 가능, default advisory) | ★ 신설(본 작업) |
| 문서 | 본 `BOUNDARIES.md` | ★ 신설(본 작업) |

> 향후: `check_boundaries.py`를 pre-commit hook 또는 CI에 `--strict`로 연결하면 경계가 리뷰어 선의가 아니라 자동 게이트로 작동한다.
