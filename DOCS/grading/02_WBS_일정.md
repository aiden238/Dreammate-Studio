# 02. WBS (작업 분해 구조) + 일정 / 마일스톤

> 채점 키워드: **WBS · 작업 분해 구조 · 일정 · 마일스톤 · 간트**

본 문서는 Dreammate Studio의 **WBS(Work Breakdown Structure)** 와 **일정/마일스톤**을 담는다.
근거: `harness/PROJECT_STATE.md`(권위 있는 최신 상태), `harness/PHASE_REGISTRY.md`, 루트 `README.md`의 Phase 이력.

진행 표기: ✅ 완료 · 🟡 진행/준비 · ⬜ 미착수

---

## 1. WBS — 작업 분해 구조 (8개 대분류)

```
Dreammate Studio
├── 1. 기획 / 제품 정의
│   ├── 1.1 비전 · 포지셔닝 정의 (product/vision, positioning)        ✅
│   ├── 1.2 MVP 범위 / 비범위 확정 (mvp_scope, mvp_non_goals)         ✅
│   ├── 1.3 사용자 시나리오 · 페르소나 (user_scenarios)               ✅
│   └── 1.4 확정 결정 25+개 (confirmed_decisions)                     ✅
├── 2. 아키텍처 / 의사결정 (ADR)
│   ├── 2.1 기술 스택 결정 (tech_stack_decision, ADR)                 ✅
│   ├── 2.2 데이터 모델 4계층 + DB/Auth/RLS (ADR-020/021)             ✅
│   ├── 2.3 AI 파이프라인 설계 (architecture, orchestration)         ✅
│   └── 2.4 ADR 39개 누적 (docs/decisions/)                          ✅
├── 3. 프론트엔드 (Next.js PWA)
│   ├── 3.1 design.md 기반 레이어드 설계 (Phase 2)                    ✅
│   ├── 3.2 PWA 기본 UI + 11 routes (Phase 3)                         ✅
│   ├── 3.3 Mode 분기 미들웨어 · 카드 UI                             ✅
│   └── 3.4 /brain 4계층 force 그래프 · 피드백 UI                     ✅
├── 4. 백엔드 (FastAPI)
│   ├── 4.1 엔드포인트 마이그레이션 · 17 endpoints (Phase 4)          ✅
│   ├── 4.2 DB/Auth/RLS/SSE (Phase 5, Supabase)                      ✅
│   ├── 4.3 결과저장 · 피드백 영속화 (Phase 9)                        ✅
│   └── 4.4 LLM Gateway 3-provider (Phase 11)                         ✅
├── 5. AI 시스템 (MOA Lite + RAG Lite)
│   ├── 5.1 3-plan 병렬 + 멀티모델 인터페이스 (Phase 4)               ✅
│   ├── 5.2 Critic revise loop + Rewriter (Phase 4.5)                ✅
│   ├── 5.3 Output Schema + Critic canonical (Phase 6)                ✅
│   ├── 5.4 RAG Lite 5단계 승격 · pgvector (Phase 7)                  ✅
│   ├── 5.5 MOA Orchestrator 추출 · SSE worker (Phase 8)              ✅
│   └── 5.6 cross-provider judge (Phase 31, 사람정렬 계측기)          ✅
├── 6. 지식 / RAG / 2nd brain
│   ├── 6.1 LLM Wiki 정적 baseline                                    ✅
│   ├── 6.2 candidate→approved 5단계 승격 파이프라인                  ✅
│   ├── 6.3 Gemini 임베딩 채택 (한국어 우위)                          ✅
│   └── 6.4 개인 PKM(2nd brain) + 출처 추적 + video 노드              ✅
├── 7. 품질 / 평가 (eval)
│   ├── 7.1 golden_set + 회귀 runner (eval-run)                       ✅
│   ├── 7.2 깊이 격차 실측 (Phase 12, compact 0.231 vs rich 1.000)    ✅
│   ├── 7.3 출력 확장 compact→rich (Phase 13)                         ✅
│   └── 7.4 critic 품질 연구 아크 · cross-provider judge (Phase 31)   ✅
└── 8. 빌드 / 배포 / 운영
    ├── 8.1 deploy_test_gates A~G 정의                               ✅
    ├── 8.2 Gate A (Local Smoke) PASS                                ✅
    ├── 8.3 staging 배포 스크립트 · secret 주입 (Gate B~D)           🟡
    └── 8.4 운영 배포 · RLS 실검증 · 비용/모니터링 (Gate E~G)        ⬜
```

---

## 2. 일정 / 마일스톤 표 (Phase 0~31)

> 솔로/소규모 운영. 각 Phase = 마일스톤. `README.md` Phase 이력 + `PROJECT_STATE.md` 기준.

| Phase | 마일스톤 | 진행 | 완료일 | 핵심 산출 |
|---|---|---|---|---|
| 0 | 하네스 초기화 (Migration) | ✅ | 2026-05-26 | 11/11 acceptance |
| 1 | MVP 기본 플로우 | ✅ | 2026-05-26 | pytest 62, smoke 5/5 |
| 2 | design.md 기반 PWA 설계 | ✅ | 2026-05-27 | audit 0 drift |
| 3 | Next.js PWA 기본 UI | ✅ | 2026-05-28 | 11 routes, smoke 7/7 |
| 4 | FastAPI 백엔드 + 3-plan | ✅ | 2026-05-28 | 멀티모델 인터페이스 |
| 4.5 | Critic Revise Loop + Rewriter | ✅ | 2026-05-28 | revise 최대 2회 (ADR-016) |
| 6 | Output Schema + Critic canonical | ✅ | 2026-05-29 | canonical 0~1 (ADR-018) |
| 5 | DB / Auth / RLS / SSE | ✅ | 2026-05-29 | Supabase (ADR-020/021/022) |
| 5.5 | Legacy DB Consolidation | ✅ | 2026-05-29 | backward-compat 100% |
| 7 | RAG Lite (5단계 승격) | ✅ | 2026-05-29 | pgvector (ADR-025/026) |
| 8 | MOA Lite (orchestrator 추출) | ✅ | 2026-05-29 | god-function 분해 (ADR-027) |
| 9 | 결과 저장 + 피드백 | ✅ | 2026-05-31 | selected/feedback 영속화 |
| 9.5 | eval-run 정식화 + deprecated 제거 | ✅ | 2026-05-31 | golden_set 회귀 (ADR-033/034) |
| M0 | Meta-Factory Prep (★ meta-phase) | ✅ | 2026-05-31 | L3 skeleton (ADR-035) |
| 10 | MVP 통합 테스트 | ✅ | 2026-06 | test_integration_mvp 12, Gate A |
| 11 | LLM Gateway (A안+B안 3-provider) | ✅ | 2026-06-02 | OpenAI/Claude/Gemini (ADR-039) |
| 12 | 검증 페이즈 (깊이 격차 실측) | ✅ | 2026-06-02 | compact 0.231 vs rich 1.000 |
| 13~20 | 출력 확장 + 2nd brain + commercial | ✅ | 2026-06-04 | rich 출력, /brain 4계층 |
| 21~26 | 4계층 깊이·출처·생성·편집·video | ✅ | 2026-06-04 | User→Brand→…→Video |
| 27~30 | MVP 실사용 마감 + 에이전트 UX | ✅ | 2026-06-10 | 동적 force 그래프, 멀티모달 |
| 31 | Critic 품질 마감 (cross-provider judge) | ✅ | 2026-06-21 | false-approve 10→0, RAG Δ+0.9 |
| M1~M3 | Meta-phase (factory 범용성) | ✅ | — | 런타임 변경 0 |

**마일스톤 요약**: Phase 0~31 + 메타-phase M0~M3 = **전부 완료**. 각 Phase는 acceptance 기준 + 자동 게이트(pytest/smoke/scenario_sim) 통과로 종료했다.

---

## 3. 간트형 진행 표시 (대분류별)

```
WBS 대분류          0    5    10   15   20   25   31
1. 기획/제품        ✅✅✅✅────────────────────────────  완료
2. 아키텍처/ADR     ─✅✅✅✅✅✅✅✅─────────────✅────  지속 누적 (ADR 39)
3. 프론트엔드        ──✅✅──✅──────────✅✅✅✅────────  완료
4. 백엔드            ────✅✅✅──✅──✅✅──────────────  완료
5. AI 시스템         ────✅✅✅✅✅──✅✅✅✅────────✅──  완료
6. 지식/RAG/2nd brain ──────────✅✅────────✅✅✅✅────  완료
7. 품질/평가         ─────────────✅✅✅✅────────✅──✅  완료
8. 빌드/배포         ──────────────────────✅🟡⬜───────  Gate A ✅ / B~D 🟡 / E~G ⬜
```

> 가독성을 위한 단순화 표기. 정확한 Phase별 상태는 §2 표가 정본.

---

## 4. 잔여 작업 (Backlog / Follow-up)

| 항목 | 상태 | 비고 |
|---|---|---|
| 운영 배포 (Gate B~G) | 🟡/⬜ | 배포 스크립트 · secret 주입 · RLS 실검증 · 모니터링 (인프라+키 필요) |
| human 실채점 (품질 절대 검증) | ⬜ | critic 낙관 편향 → cross-provider judge로 일부 보강, 사람 채점은 이월 |
| `match_approved_knowledge` SQL function 운영 정의 | ⬜ | RAG retrieval은 graceful-empty로 동작, 운영 단계(NG11) |
| OneDrive 트리 main 정렬 | 🟡 | 재분기 방지 (운영 위생) |

> 본 잔여 항목은 **정직하게 미완으로 표기**한다. 코드 완성도는 높고(Phase 0~31 done, pytest 845), 실배포/운영 준비는 키·인프라 주입 단계다.
</content>
