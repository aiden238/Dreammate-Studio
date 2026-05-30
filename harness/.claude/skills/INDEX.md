# Skills INDEX

> 위치: `.claude/skills/INDEX.md` (canonical, v1.2.0 통합)
> 총 21개 Skill (절차 핵심 14 + 검토/감사 6 + Meta-Factory 1)
> 단일 폴더 + `applies_to` 태그로 `.agents` / `.claude` 분리 효과 유지

---

## 사용 원칙

```
1. 모든 Skill은 description 키워드 매칭으로 자동 트리거된다. 수동 호출 금지.
2. 한 작업에 여러 Skill이 매칭되면 우선순위 표(아래)를 따른다.
3. Skill 본문은 절차만 담는다. 데이터/명세는 docs/contracts/, eval/, knowledge/에 둔다.
4. Skill 추가/변경은 docs/contracts/ 변경과 동일하게 contract-change Skill 절차를 따른다.
5. 같은 description 키워드가 둘 이상 Skill에 있으면 충돌이며 즉시 수정한다.
6. .agents/skills/ 폴더는 v1.2.0에서 폐기됨 — 모든 Skill은 .claude/skills/에 통합.
```

---

## Skill 목록

### 절차 핵심 14개 (우리 깊은 버전)

| # | Skill | 트리거 키워드 | applies_to | Phase |
|---|---|---|---|---|
| 1 | phase-start | Phase 시작, 다음 phase, phase initiation | agents, claude | 모든 phase 시작 시 |
| 2 | phase-complete | Phase 종료, phase 완료, archive | agents, claude | 모든 phase 종료 시 |
| 3 | contract-change | contract 변경, schema 변경, breaking change | agents, claude | 상시 |
| 4 | bug-triage | 버그 발생, error 분류, 재현, exception | agents | 상시 |
| 5 | rag-update | RAG 지식 추가, candidate, 승격, promotion | agents, claude | phase 7+ |
| 6 | eval-run | eval 실행, 평가, golden_set, regression | agents | phase 10+ |
| 7 | qa-check | QA 검사, MVP 범위, release gate | agents | phase 9+ |
| 8 | cost-review | 비용 검토, LLM cost, token usage | agents, claude | phase 9+ |
| 9 | meta-retrospective | 회고, 메타 개선, 반복 실패 | claude | phase 종료 후 |
| 10 | design-review | design.md 검토, UX 점검, 프론트 설계 | claude | 상시 |
| 11 | security-review | 보안 검토, prompt injection, privacy | agents, claude | phase 7+ |
| 12 | prompt-version-review | prompt 변경, P-XXX, semver | agents, claude | phase 4+ |
| 13 | multi-llm-validation | multi-LLM, Claude GPT Gemini 교차검증 | claude | 상시 |
| 14 | context-compact | 컨텍스트 압축, session handoff, 대화 요약 | claude | 상시 (긴 세션) |

### 검토 / 감사 6개 (GPT origin, 우리 포맷으로 재작성)

| # | Skill | 트리거 키워드 | applies_to | Phase |
|---|---|---|---|---|
| 15 | agent-io-check | agent IO 점검, I/O 검증, agent_io_contract | agents | phase 6+ |
| 16 | ai-architecture-review | AI 아키텍처 검토, MOA review, orchestration | claude | phase 7/8, 분기 정기 |
| 17 | eval-design | eval 설계, golden_set 확장, rubric 설계 | claude | phase 6, 10+ |
| 18 | harness-audit | 하네스 감사, 구조 점검, 전체 검토 | claude | phase 0/10/20 |
| 19 | phase-review | phase 검토, scope creep, 어디까지 왔지 | claude | 모든 phase 중반 |
| 20 | rag-design | RAG 설계, custom RAG, chunking 전략 | claude | phase 7, 21+ |

### Meta-Factory 1개 (L3 Meta-Harness Factory, proposal-only)

| # | Skill | 트리거 키워드 | applies_to | Phase |
|---|---|---|---|---|
| 21 | harness-factory | 하네스 blueprint, meta_factory, harness scaffold, 도메인 하네스 생성 | claude | phase 10+ |

> harness-factory (Phase M0 Slice 3, ADR-035 + CC-006) — `meta_factory/` (L3) 진입점. domain_brief → harness blueprint 초안 + agent·skill·contract·eval scaffold 제안 + 기존 하네스 충돌 분석. ★ **proposal-only** — 생성물은 `meta_factory/outputs/` 또는 `meta/proposals/` 에 먼저 두고, validation_workflow 6 검증 + 사용자 승인 전까지 active 아님. 기존 AGENTS/CLAUDE/PROJECT_STATE/contracts/Skill 직접 수정 금지 (contract-change 경유). 키워드 **scoped** — `하네스 개선`/`메타 개선`/`회고`(meta-retrospective) + bare `하네스 감사`/`구조 점검`/`전체 검토`(harness-audit) + `phase 생성` 단독(phase-start) 침범 0.

---

## 폐기된 Skill (v1.2.0)

다음 GPT origin 5개 Skill 은 우리 자산에 흡수되어 폐기됨:

```
docs-design              → design-review SKILL에 통합 (UX/문서 검토 일원화)
frontend-design-review   → design-review SKILL에 통합
product-scope-review     → qa-check 카테고리 1 (MVP 범위) + phase-review로 분산
planning-phase-create    → phase-start SKILL이 phase 폴더 가이드 포함
meta-retrospective (GPT) → 우리 meta-retrospective 가 더 깊음, 그대로 사용
```

또한 `.agents/skills/` 폴더 전체(15개 GPT stub)는 v1.2.0에서 폐기. 모든 Skill은 `.claude/skills/`로 통합.

---

## 우선순위 충돌 해결

같은 작업에 두 Skill이 동시 매칭될 때 우선순위:

```
context-compact       > 다른 모든 Skill         # 컨텍스트 부족은 항상 최우선
contract-change       > 다른 절차 Skill         # contract 변경은 항상 절차 통과
multi-llm-validation  > 단일 검토 Skill         # 큰 결정은 다중 검증 우선
phase-start           > 다른 절차 Skill         # Phase 진입 컨텍스트 확보 먼저
phase-complete        > meta-retrospective      # 종료 정리 후 회고
security-review       > rag-update / rag-design # 보안 검토가 먼저
bug-triage            > qa-check                # 버그 분류가 먼저
prompt-version-review > eval-run                # 프롬프트 변경 시 회귀 평가 트리거
phase-review          > meta-retrospective      # 진행 중 점검이 회고보다 우선
harness-audit         > meta-retrospective      # 구조 감사 후 회고
agent-io-check        > prompt-version-review   # IO 정합이 prompt 회귀보다 먼저
ai-architecture-review > design-review          # AI 구조가 UX 검토보다 상위
harness-audit         > harness-factory         # 기존 하네스 감사가 생성보다 상위
contract-change       > harness-factory         # contract/Skill 실 변경은 항상 절차 통과
eval-run              > harness-factory          # validation 의 실 평가는 eval-run 절차가 상위
```

---

## 키워드 충돌 검토 (harness-factory #21 등록, Phase M0 Slice 3)

> harness-factory 의 description 키워드(`하네스 blueprint`, `meta_factory`, `harness scaffold`, `도메인 하네스 생성`, `agent/skill scaffold 설계`, `harness-factory`)가 기존 20 Skill 의 description 키워드와 충돌하는지 검토 (INDEX §사용 원칙 5 — "같은 키워드가 둘 이상 = 충돌"). harness-audit Skill §3(Skill description 키워드 충돌) 절차로 검토.

| 검토 대상 Skill | 소유 키워드 | harness-factory 키워드 | 충돌 |
|---|---|---|---|
| **harness-audit** (#18) | "하네스 감사", "구조 점검", "전체 검토", "stub 점검", "Skill 충돌 검사" | "하네스 blueprint", "harness scaffold", "도메인 하네스 생성" | ✅ **0** — 감사·점검 ≠ 생성·blueprint·scaffold (의미 명확 구분, bare "하네스 감사/구조 점검/전체 검토" harness-factory 미소유) |
| **meta-retrospective** (#9) | "회고", "메타 개선", "하네스 개선", "meta proposal", "프로세스 개선", "post-mortem" | "meta_factory", "도메인 하네스 생성" | ✅ **0** — 개선·회고(L2 in-place) ≠ 생성(L3). "하네스 개선"/"메타 개선" harness-factory 미소유 (factory 는 "meta_factory" 디렉토리명만) |
| **phase-start** (#1) | "Phase 시작", "다음 phase", "phase initiation" | (phase 생성 단독 미소유) | ✅ **0** — harness-factory 는 phase scaffold 를 blueprint 일부로만 제안, "phase 생성" 단독 키워드 미소유 (phase-start 영역 보존) |
| **contract-change** (#3) | "contract 변경", "schema 변경", "breaking change" | (contract scaffold 는 제안만) | ✅ **0** — harness-factory 는 contract scaffold 제안만, 실 변경은 contract-change 경유 (우선순위 표 편입) |
| **eval-run** (#6) / **eval-design** (#17) | "eval 실행"/"평가" / "eval 설계"/"rubric 설계" | (validation 5 는 eval-run 위임) | ✅ **0** — harness-factory validation 5 는 eval-run §3~§6 위임 (우선순위 `eval-run > harness-factory`) |
| 나머지 15 Skill | (각 소유 키워드) | — | ✅ **0** — 도메인 비중첩 |

**검토 결과**: harness-factory 키워드는 **scoped** (생성·blueprint·scaffold 영역 한정). 기존 20 Skill description 키워드와 **충돌 0**. 동시 매칭 가능성이 있는 3 Skill(harness-audit / contract-change / eval-run)은 우선순위 표에 관계 추가(harness-audit > harness-factory, contract-change > harness-factory, eval-run > harness-factory) — INDEX §우선순위 충돌 해결 정합. (validation_workflow 검증 2 skill conflict check 형식 정합.)

---

## applies_to 태그 의미

```
agents        : 구현/QA/수정/테스트 작업 (Claude Code, Codex 등 코딩 모델 대상)
claude        : 기획/설계/검토/문서화 작업 (대화형 Claude 대상)
agents, claude: 둘 다 (대부분 절차 Skill)
```

라우터(`CLAUDE.md`, `AGENTS.md`)는 자기 역할에 맞는 `applies_to` 태그를 가진 Skill만 인지한다. 동일 Skill 본문에 두 역할이 공존할 수 있으므로 `사용하지 않는 경우` 섹션을 항상 두어 다른 Skill로 라우팅한다.

---

## 흡수된 기존 문서

다음 문서들은 Skill 본문에 흡수되어 폐기됨:

```
eval/design_review_checklist.md         → design-review SKILL
eval/security_eval.md (절차 부분)       → security-review SKILL
eval/qa_checklist.md                    → qa-check SKILL
docs/contracts/rag_promotion_policy.md  → rag-update SKILL
docs/contracts/prompt_change_policy.md  → prompt-version-review SKILL
meta/retrospective_template.md          → meta-retrospective SKILL
meta/improvement_proposal_template.md   → meta-retrospective SKILL
phases/phase_template.md                → phase-start SKILL
phases/phase_complete_template.md       → phase-complete SKILL
docs/contract_changes/template.md       → contract-change SKILL
```

흡수 후 docs/contracts 절차 항목들은 데이터/규칙만 남기고 절차는 Skill로 이전.

---

## Skill 신규/변경 절차

```
1. contract-change SKILL을 통한다 (Skill도 contract처럼 취급)
2. meta/proposals/에 변경 제안서 작성
3. description 키워드 충돌 검토 (이 INDEX.md 표 갱신)
4. 승인 후 SKILL.md 수정
5. 변경 로그를 SKILL.md frontmatter의 version에 반영 (semver)
6. harness-audit 다음 회차에 키워드 충돌 / 깨진 참조 재확인
```

---

## 운영 메모

- INDEX.md는 Skill이 추가될 때마다 갱신한다.
- 6개월 이상 트리거되지 않은 Skill은 폐기 후보로 분류 (`meta/skill_usage_log.md` 기록).
- 같은 Skill이 한 세션에서 3회 이상 트리거되면 절차 자동화 후보 (스크립트화 검토).
- v1.2.0 결정: `.claude/skills/`가 canonical. Claude Code의 자동 트리거가 이 경로만 인식하므로 다른 위치 사용 금지.
