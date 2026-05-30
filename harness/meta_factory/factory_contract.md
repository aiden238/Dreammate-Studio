# factory_contract.md — Meta-Factory 절대 규칙

> 위치: `harness/meta_factory/factory_contract.md`
> 상태: Phase M0 Slice 1 — L3 Meta-Factory 의 헌법 (이후 모든 meta_factory 문서의 제약 정의)
> 결정: ADR-035
> 참조: README.md (L1/L2/L3 + proposal-first), self_improvement_loop.md §0/§7 (자동 수정 금지), INDEX.md (Skill 충돌 규칙)

---

## 0. 이 문서의 위치

`factory_contract.md` 는 meta_factory(L3) 의 **헌법**이다. generation_workflow / validation_workflow / templates / blueprints / harness-factory Skill 등 모든 L3 산출물은 이 8 규칙을 위반할 수 없다. 규칙 위반이 감지되면 해당 산출물은 무효이며 되돌린다.

핵심 정신: meta_factory 는 **자동 적용 도구가 아니라 proposal-first 도구**다. 기존 `meta/self_improvement_loop.md` §0 "자가개선은 자동 수정이 아니다 — 항상 회고 → 패턴 → 제안 → 검토 → 승인 → 반영" 원칙을 "하네스 생성" 영역으로 계승한다.

---

## 1. 8 절대 규칙

### 규칙 1 — product runtime 직접 수정 금지

meta_factory 는 L1 Product Runtime(FastAPI `backend/fastapi/**` / Next.js `apps/web/**` / Supabase `db/migrations/**`) 을 **단 한 줄도 직접 수정하지 않는다** (A9). 런타임은 읽기(패턴 매핑/blueprint 역정리)만 허용한다.

### 규칙 2 — 기존 harness 직접 변경 금지

meta_factory 는 L2 Implementation Harness(AGENTS/CLAUDE/PROJECT_STATE/PHASE_REGISTRY/docs/contracts/phases/eval/기존 .claude/skills) 를 **직접 변경하지 않는다**. 변경이 필요하면 proposal 로 제출하고 사람 승인을 거친다.

### 규칙 3 — 생성 결과는 outputs/ 또는 meta/proposals/ 에 먼저 둔다

meta_factory 의 모든 생성 결과(harness blueprint / scaffold / 개선 리포트)는 `meta_factory/outputs/generated_harnesses/` 또는 `meta_factory/outputs/improvement_reports/` 또는 `meta/proposals/` 에 **먼저** 둔다. active 위치(L2 운영 경로)에 직접 쓰지 않는다 — proposal-first.

### 규칙 4 — Skill 추가/변경은 .claude/skills/INDEX.md 의 충돌 규칙을 따른다

새 Skill 추가/변경은 `INDEX.md` 의 "같은 description 키워드 둘 이상 = 충돌" 규칙 + Skill 신규/변경 절차(contract-change 경유 + 키워드 충돌 검토 + 우선순위 표 갱신)를 따른다. harness-factory Skill 의 키워드는 **scoped**(생성/설계 영역) 이며, 기존 harness-audit(감사) / meta-retrospective(개선·회고) / phase-start(phase 진입) 키워드와 충돌하지 않는다.

### 규칙 5 — contract 변경은 contract-change Skill 을 통한다

`docs/contracts/**` 또는 Skill 본문(Skill 도 contract 처럼 취급) 의 변경은 **반드시 contract-change Skill 절차**(제안 → 검토 → 승인 → 반영)를 거친다. meta_factory 가 contract 를 직접 편집하지 않는다.

### 규칙 6 — PROJECT_STATE.md 는 사용자 승인 없이 갱신하지 않는다

`PROJECT_STATE.md` (및 PHASE_REGISTRY 등 상태 문서) 는 사용자 승인 없이 갱신하지 않는다. self_improvement_loop §7 "사용자 승인 없이 PROJECT_STATE.md 갱신 금지" 와 동일.

### 규칙 7 — 생성된 harness 는 validation_workflow 를 통과하기 전 active 로 간주하지 않는다

meta_factory 가 생성한 harness 는 `validation_workflow.md` 의 6 검증(trigger validation / skill conflict / contract consistency / with-without comparison / eval-run 연동 / acceptance)을 통과하기 전까지 **active 로 간주하지 않는다**. outputs/ 에 머무른다.

### 규칙 8 — 사용자 데이터/RAG 승격/Brand Memory 자동화는 기존 정책을 따른다

사용자 데이터 처리 / RAG 지식 승격 / Brand Memory 추출 자동화는 meta_factory 가 새 경로를 만들지 않고 기존 `rag-update` Skill(5단계 승격 파이프라인) + `security-review` Skill(PII/위협 모델) 정책을 그대로 따른다.

---

## 2. 규칙 요약 표

| # | 규칙 | 대상 | 근거 |
|---|---|---|---|
| 1 | product runtime 직접 수정 금지 | L1 (backend/apps/migrations) | A9 (ADR-035) |
| 2 | 기존 harness 직접 변경 금지 | L2 (AGENTS/CLAUDE/contracts/...) | proposal-first |
| 3 | 생성 결과는 outputs/ 또는 meta/proposals/ 에 먼저 | 생성물 | proposal-first |
| 4 | Skill 추가/변경은 INDEX 충돌 규칙 | .claude/skills | INDEX §Skill 신규/변경 |
| 5 | contract 변경은 contract-change Skill | docs/contracts + Skill 본문 | contract-change |
| 6 | PROJECT_STATE 사용자 승인 없이 갱신 금지 | 상태 문서 | self_improvement_loop §7 |
| 7 | 생성 harness 는 validation 통과 전 active 아님 | 생성 harness | validation_workflow |
| 8 | 사용자 데이터/RAG 승격/Brand Memory 자동화는 기존 정책 | 데이터 파이프라인 | rag-update + security-review |

---

## 3. 위반 처리

- 규칙 위반 산출물은 **무효** — 되돌린다 (revert).
- 런타임(규칙 1) 위반 의심 시: `git diff --cached --name-only | grep -E "backend/fastapi|apps/web|db/migrations"` = 0 lines 확인.
- 기존 하네스(규칙 2) 위반 의심 시: 변경을 proposal 로 재분류 + active 경로 변경 revert.
- 모든 위반은 `meta/retrospectives/` 또는 phase notes 에 기록 후 재발 방지.

---

## 4. 정합 (기존 문화와의 관계)

- self_improvement_loop §0/§7 (자동 수정 금지) → 규칙 1/2/3/6/7 로 계승.
- INDEX §Skill 신규/변경 (contract-change + 충돌 검토) → 규칙 4/5 로 계승.
- rag-update 5단계 + security-review 위협 모델 → 규칙 8 로 계승.

→ factory_contract 는 단절적 신규 규칙이 아니라 기존 하네스 규율의 L3 영역 확장이다.
