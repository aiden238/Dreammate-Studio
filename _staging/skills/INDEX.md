# Skills INDEX

> 위치: `.skills/INDEX.md`
> 총 14개 Skill (필수 11 + 확장 3)
> 단일 폴더 + `applies_to` 태그로 .agents/.claude 분리 효과 유지

---

## 사용 원칙

```
1. 모든 Skill은 description 매칭으로 자동 트리거된다. 수동 호출 금지.
2. 한 작업에 여러 Skill이 매칭되면 우선순위 표(아래)를 따른다.
3. Skill 본문은 절차만 담는다. 데이터/명세는 docs/contracts/, eval/에 둔다.
4. Skill 수정은 docs/contracts/ 변경과 동일하게 contract-change Skill을 통한다.
5. 같은 description 키워드가 둘 이상 Skill에 있으면 충돌이며 즉시 수정한다.
```

---

## Skill 목록

### 필수 12개

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
| 9 | meta-retrospective | 회고, 메타 개선, 반복 실패 | claude | 모든 phase 종료 후 |
| 10 | design-review | design.md 검토, UX 점검, 프론트 설계 | claude | 상시 |
| 11 | security-review | 보안 검토, prompt injection, privacy | agents, claude | phase 7+ |
| 12 | prompt-version-review | prompt 변경, P-XXX, semver | agents, claude | phase 4+ |

### 확장 2개

| # | Skill | 트리거 키워드 | applies_to | Phase |
|---|---|---|---|---|
| 13 | multi-llm-validation | multi-LLM, Claude GPT Gemini 교차검증 | claude | 상시 |
| 14 | context-compact | 컨텍스트 압축, session handoff, 대화 요약 | claude | 상시 (긴 세션) |

---

## 우선순위 충돌 해결

같은 작업에 두 Skill이 동시 매칭될 때 우선순위:

```
contract-change       > 다른 모든 Skill         # contract 변경은 항상 절차 통과
security-review       > rag-update              # 보안 검토가 먼저
phase-start           > 다른 절차 Skill         # Phase 진입 컨텍스트 확보 먼저
phase-complete        > meta-retrospective      # 종료 정리 후 회고
bug-triage            > qa-check                # 버그 분류가 먼저
prompt-version-review > eval-run                # 프롬프트 변경 시 회귀 평가 트리거
multi-llm-validation  > design-review           # 멀티 모델 합의 후 단일 검토
context-compact       > 모든 Skill              # 컨텍스트 부족 신호는 항상 최우선
```

---

## applies_to 태그 의미

```
agents : 구현/QA/수정/테스트 작업 (Claude Code, Codex 등 코딩 모델 대상)
claude : 기획/설계/검토/문서화 작업 (대화형 Claude 대상)
both   : 둘 다 (대부분 절차 Skill)
```

라우터(`CLAUDE.md`, `AGENTS.md`)는 자기 역할에 맞는 `applies_to` 태그를 가진 Skill만 인지한다.

---

## 흡수된 기존 문서

다음 문서들은 Skill 본문에 흡수되어 폐기됨:

```
eval/design_review_checklist.md       → design-review SKILL
eval/security_eval.md (절차 부분)     → security-review SKILL
eval/qa_checklist.md                  → qa-check SKILL
docs/contracts/rag_promotion_policy.md → rag-update SKILL
docs/contracts/prompt_change_policy.md → prompt-version-review SKILL
meta/retrospective_template.md        → meta-retrospective SKILL
meta/improvement_proposal_template.md → meta-retrospective SKILL
phases/phase_template.md              → phase-start SKILL
phases/phase_complete_template.md     → phase-complete SKILL
docs/contract_changes/template.md     → contract-change SKILL
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
```

---

## 운영 메모

- INDEX.md는 Skill이 추가될 때마다 갱신한다.
- 6개월 이상 트리거되지 않은 Skill은 폐기 후보로 분류한다 (`meta/skill_usage_log.md` 기록).
- 같은 Skill이 한 세션에서 3회 이상 트리거되면 절차 자동화 후보 (스크립트화 검토).
