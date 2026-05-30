# Contract Change Proposal: Phase 8 Slice 4 — prompt_registry semver 정식화 + Critic v1.1.0 adapter

- 제안일: 2026-05-29
- 제안자: Claude (Phase 8 Slice 4 sub-agent)
- 대상 contract: `ai_system/prompts/prompt_registry.md` + `docs/contracts/agent_io_contract.md`
- 변경 종류: 수정 (semver 정식화 + P-007 v1.0.0 → v1.1.0)
- 긴급도: 보통
- 선행 결정: ADR-029 (`docs/decisions/phase_8_prompt_registry_semver.md`) — 사용자 결정 (Conservative adapter, Phase 6 canonical 불변) 이미 승인됨.
- 선행 Skill: prompt-version-review (★ 첫 정식 트리거 — ADR-029 §prompt-version-review 결과)

## 변경 사유

ADR-029 에서 결정된 P-007 Critic 0–5↔0–1 conservative adapter 와 prompt_registry semver
정식화를 contract 에 반영한다. P-007 prompt(LLM-facing 0–5)는 불변, code-side
`normalize_to_canonical` helper 가 0–1 canonical 로 정규화(미강제 주입 → 회귀 0).
P-001~P-008 + AUX + P-EVAL-1 각 prompt 에 Semver/활성 정책을 명시해 단일 출처(SoT)
정합을 문서화한다.

## 변경 내용 (요약)

### prompt_registry.md
- 각 P-XXX 항목에 `#### Semver / 활성 정책` 블록 추가 (P-EVAL-1 §Semver 패턴 일관 확장).
- P-007 Version v1.0.0 → v1.1.0 + `#### 0–5 ↔ 0–1 conservative adapter (ADR-029)` 섹션 추가.
- P-008 Version v1.0.0 → v1.1.0 (Phase 6 ADR-019 — 기존 코드 반영, registry 표기 정정).
- §13 변경 관리 / §14 Open Questions #2 갱신.

### agent_io_contract.md
- §5 Critic v1.1.0 adapter 명시 (0–5 LLM 산출 → code-side 0–1 canonical, Phase 6 정합).
- §8 / §0 orchestrator 중개 명시 (ADR-027 — moa_orchestrator.generate_plan, moa_policy §2 정합).
- §20 변경 이력 v1.2.0 entry.

## 영향 받는 영역

- [ ] API 응답 형식
- [ ] DB 스키마
- [x] Agent IO (Critic v1.1.0 adapter 명시 — 동작 불변)
- [ ] Output Schema (Phase 6 canonical 불변 — NG5)
- [ ] 프론트 컴포넌트 (PlanCard 0줄 ★)
- [x] Prompt (P-007 v1.1.0 + semver 정식화)
- [ ] RAG 파이프라인
- [ ] 평가 / golden_set (golden_set 회귀는 Phase 9+ — NG7)
- [ ] 보안 / 권한

## 영향 받는 파일 목록

```
ai_system/prompts/prompt_registry.md      (수정 — semver 정식화 + P-007 v1.1.0)
docs/contracts/agent_io_contract.md       (수정 — Critic v1.1.0 + orchestrator 중개)
ai_system/orchestration/moa_policy.md     (수정 — §2 moa_orchestrator.py cross-ref)
backend/fastapi/agents/critic.py          (PROMPT_VERSION v1.1.0 + normalize_to_canonical)
backend/fastapi/tests/test_critic.py      (version assert 1줄 + 주석 — 의도된 delta)
backend/fastapi/tests/test_e2e_slice1.py  (critic detail assert 1줄 + 주석 — 의도된 delta)
backend/fastapi/tests/test_prompt_registry_consistency.py (신규)
docs/decisions/phase_8_prompt_registry_semver.md (ADR-029 §Amendment)
```

## Rollback 방안

- registry semver 표기는 문서 변경이므로 git revert 로 즉시 복원.
- critic.py: `PROMPT_VERSION = "v1.0.0"` 복원 + `normalize_to_canonical` 제거 (additive helper 라 제거 시 회귀 0).
- `P-007@v1.x.x` detail 문자열은 critic.PROMPT_VERSION 에서 파생 → 상수 복원 시 자동 롤백.

## 마이그레이션 필요 여부

- [ ] DB 마이그레이션
- [ ] 기존 데이터 변환
- [ ] 사용자 통지
- [ ] 외부 API 클라이언트 통지

(없음 — output schema 불변, deprecated 0–5 필드 병행 유지 → backward-compat 100%.)

## 승인 기준

- 사용자 결정(Conservative adapter, Phase 6 canonical 불변)은 ADR-029 에서 이미 승인됨.
- 본 변경은 그 결정의 **문서 반영(formalization)** 이며 의미 변경 없음 (P-007 prompt 텍스트 불변,
  output schema 불변). → ADR 승인에 근거해 반영 진행.

## 결정

- [x] 승인 (ADR-029 선행 결정 기반)
- 결정자: 사용자 결정(2026-05-29, ADR-029) + Slice 4 dispatch
- 결정일: 2026-05-29
- 메모: golden_set 회귀(prompt-version-review §4) 및 A/B 활성화(§5 major)는 Phase 9+/11+ (NG3/NG7).
