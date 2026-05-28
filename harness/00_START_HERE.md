# START HERE

## 프로젝트 정의

이 프로젝트는 영상 제작 AI가 아니라 **영상기획 AI 에이전트 플랫폼**이다.

한 줄 정의:

> 사용자의 목적·타겟·브랜드 톤을 정리하고, LLM Wiki와 RAG로 근거를 찾은 뒤, 검증 에이전트가 기획 품질을 평가·개선하는 영상기획 특화 AI 에이전트.

## 핵심 흐름

본 제품은 **Hybrid UX**: Discovery Wizard(신규/콜드스타트용 5단계 카드) + Quick Mode(같은 Series 추가 시). 두 모드는 같은 generate_plan 파이프라인으로 수렴.

```text
사용자 입력
→ 의도 분석 (Discovery 또는 Quick 자동 분기)
→ 부족한 정보 질문 (Discovery: 5 카드, Quick: 1–2 질문)
→ 한 줄 기획 방향 승인
→ LLM Wiki / RAG 검색
→ 영상기획안 3개 생성 (P-006 plan_candidates)
→ Critic Agent 검증 (revise 최대 2회)
→ 개선안 반영
→ 결과 저장
→ 사용자 선택·피드백 저장 (Brand Memory 자동 추출)
```

## 반드시 지킬 원칙

1. AGENTS.md와 CLAUDE.md는 지침 본문이 아니라 라우터로 사용한다.
2. PROJECT_STATE.md에는 최신 상태만 압축 기록한다.
3. phases/archive/는 기본 참조하지 않는다.
4. docs/contracts/는 무단 변경하지 않는다.
5. contract 변경은 docs/contract_changes/ 또는 meta/proposals/에 먼저 제안한다.
6. 구조는 처음부터 크게 만들고, 내용은 Phase 진행에 따라 얇게 채운다.
7. 영상 제작, 자동 편집, TTS/BGM, 자동 업로드는 MVP에 넣지 않는다.

## 첫 진입 시 읽을 문서

1. `PROJECT_STATE.md` (현재 active Phase, migration_progress 확인)
2. `PHASE_REGISTRY.md`
3. `product/mvp_scope.md`
4. `docs/contracts/mvp_non_goals.md`
5. `phases/active/{current-phase}/` 폴더 전체 (goals, scope, non_goals, acceptance, dependencies)
6. 현재 작업에 필요한 contracts

## 현재 active Phase

**🟡 Phase 7 (RAG Lite) — pending planning** (Phase 5.5 ✅ done 2026-05-29)

Phase 5.5 ✅ done (2026-05-29). 다음 Phase 7 (RAG Lite — candidate_knowledge 5단계 MVP) 기획 시작 대기 (사용자 명시: "Phase 5.5 진행 후 페이즈 7 기획 시작").

- Phase 5.5 archive: `phases/archive/phase-5.5-legacy-db-consolidation/` (참조 가능 — closing_notes + 회고 + Phase 7 진입 baseline)
- Phase 5 archive: `phases/archive/phase-5-db-auth/` (참조 가능 — DB/Auth/RLS/SSE baseline)
- Phase 6 archive: `phases/archive/phase-6-output-schema-stabilization/` (참조 가능 — contract 안정화 baseline)
- Phase 4.5 archive: `phases/archive/phase-4.5-critic-revise-loop/` (참조 가능 — Critic revise loop + Rewriter baseline)
- Phase 4 archive: `phases/archive/phase-4-fastapi-extension/` (참조 가능 — backend + frontend baseline)
- Phase 3 archive: `phases/archive/phase-3-pwa-impl/` (참조 가능 — frontend baseline)
- Phase 2 archive: `phases/archive/phase-2-pwa-design/` (참조 가능 — design spec baseline)
- Phase 1 archive: `phases/archive/phase-1-mvp-basic-flow/` (참조 가능 — backend baseline)
- Phase 0 archive: `phases/archive/phase-0-migration/` (참조 금지)

**다음 phase**: **Phase 7 (RAG Lite — candidate_knowledge 5단계 MVP, 12~16h)** 기획 시작 (사용자 명시)

**Phase 7 진입 권장 Skill**:
1. **phase-start v1.3.0** (entry, 4점검 — 9번째 trigger)
2. **multi-llm-validation formal self V형식 + external placeholder** (네 번째 트리거)
3. **rag-design Skill ★ 첫 정식 트리거** (RAG architecture 결정)
4. **contract-change** (rag_data_contract.md 갱신 또는 신규)
5. 진행 중: **rag-update** (5단계 승격 절차 강제)
6. 종료 시: **phase-complete v1.2.0** + **meta-retrospective**

**Phase 7 진입 전 권장**:
1. ADR-024 (Phase 7 RAG scope evolution) 재확인
2. candidate_knowledge 5단계 MVP scope 재확인 (사용자 결정 4)
3. (옵션) External validation × 3 진짜 외부 검토 (사용자 외부 GPT/Gemini, Phase 5.5 §개선 제안 §2)
4. phase-start v1.3.0 4점검
5. multi-llm-validation formal self (네 번째 트리거)

**Phase 5.5 핵심 성과**:
- **P-X1 §SELF-VERIFICATION 26연속 PASS** (Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 4 + Phase 5 5 + Phase 5.5 4)
- **PlanCard.tsx 18연속 0줄** (Phase 4 4 + Phase 4.5 5 + Phase 6 3 + Phase 5 5 + Phase 5.5 1)
- **component_map.md 28연속 0줄** (Phase 2 6 + Phase 3 5 + Phase 4 4 + Phase 4.5 4 + Phase 6 3 + Phase 5 5 + Phase 5.5 1)
- **Legacy DB 옵션 A 채택** (ADR-023 — 공존 + deprecated note + Phase 7+ 지연 통합)
- **ADR-024 Phase 7 RAG scope evolution** (candidate_knowledge 5단계 MVP + 확대 지점 A~F)
- **External validation × 3 self-strengthen** (V-form 합의 추정 PASS — Phase 4.5 V1~V4 + Phase 6 V1~V5 + Phase 5 V1~V6)
- **Brand Memory Phase 9+ confirmation** (NG2 + ADR-024 §Brand Memory cross-ref)
- **legacy backward-compat 100%** (Phase 1 baseline 보호 + Phase 5 baseline 보호 동시 달성)
- pytest 170 → **172/172** (+2 legacy deprecation 검증) + smoke 12/12 (재실행) + scenario_sim v2 10/10 (P-X2 네 번째)
- 신규 패턴: P-LEGACY-CONSOLIDATION-001 (신규 후보) + P-X1-EFFECT-001 update (26연속) + P-VALIDATION-FORMAL-001 update (self-strengthen V-form sub-pattern)
- mini-phase consolidation 패턴 효과 입증 (실측 ~4-5h)
- 사용자 결정 5건 1:1 mapping 완료 (legacy 옵션 A / external 강화 / Phase 7 Lite / 5단계 MVP 전부 / Brand Memory Phase 9+)
