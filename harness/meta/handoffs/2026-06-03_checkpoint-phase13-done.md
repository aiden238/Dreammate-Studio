# Session Checkpoint — Phase 13 done + PARKED proposals

> 작성: 2026-06-03 (긴 세션 체크포인트). canonical = PROJECT_STATE.md / PHASE_REGISTRY.md.
> origin/main = **3feb068**, 로컬=원격 clean. pytest **499**. active phase **없음**(Phase 13 archived, Phase 14 미진입).

## 0. 새 세션 첫 행동
1. `PROJECT_STATE.md` 상단(Phase 13 done, 다음=Phase 14 pending) 읽기.
2. `PHASE_REGISTRY.md` Phase 14 행 + "★ PARKED 제안" 블록 읽기.
3. 본 handoff 읽기 → Phase 14 결정/작업.

## 1. 이번 세션 완료 (전부 commit·push)
- **B안(Phase 11 확장)**: 3-provider(GPT/Claude/Gemini) gateway 연결 + 3-plan alias + 펜스 stripping + gated 다중-provider 경로. 라이브 입증.
- **doc-sync**: GPT 검토 반영, "Phase 12 B안" 코드주석 drift 정정.
- **Phase 12 (검증)**: 깊이 격차 실측 compact 0.231 vs rich 1.000 = 4.3x. golden_set 15→25 + depth_actionability 차원. done+archive.
- **Phase 13 (출력 확장, compact→rich)**: S1 스키마 / S2 프롬프트(P-006 v1.1.0) / S3 gated wiring(`rich_output_enabled`) / S4 Critic depth(P-007 v1.2.0, 88점 함정 해소) / S5 frontend PlanCard rich / S6 cost+종료. ★ **라이브 화면 rich 입증** + 깊이 운영 0.231→**1.000**(≥0.8). done+archive. pytest 471→**499**.
- **품질 점수 숨김**: /plan `SHOW_QUALITY_SCORE=false` (사용자 요청, 복원 가능).
- **PARKED proposals 2건**(코드 0): commercial-viral-mode-design.md / pkm-rag-orchestrator-design.md.

## 2. 현재 제품 상태 (정확히)
- **실동작 생성 경로 = 랜딩 `/` 하나뿐** (textarea → POST /generate → /plan). 위저드(/new/quick·/new/discovery)는 **mock**(백엔드 미연결, 다른 sessionStorage 키).
- **rich 출력 = gated, 커밋 default OFF** (운영 기본 compact byte-identical). ON = `RICH_OUTPUT_ENABLED=true` (라이브 데모로 입증됨).
- 로컬 서버는 **정리됨**(종료). 재기동: 백엔드 `Temp/run_local_backend.py`(+`RICH_OUTPUT_ENABLED=true` 원하면), 프론트 `cd apps/web && npm run dev`.

## 3. ★ Phase 14 = 진짜 다음 우선순위 (pending_user_decision)
> PARKED proposals(commercial_viral/PKM-RAG)의 **선행조건이 곧 다음 할 일**.
1. **rich 실사용 검증** — 만든 rich 카드를 실제로 써보고 가치 판단(+ Phase 12 S4 human review kit `eval/human_review/2026-06-02_phase-12-s4-review-kit.md` 채점).
2. **위저드 ↔ 백엔드 실연결** — /new/* mock → 실생성(랜딩 / 외 흐름 완성). `/plans/start`·`/plans/{id}/wizard/{step}`·`/plans/{id}/generate` 배선.
3. **rich default 전환 결정** — gated OFF→ON 여부(cost·품질 합의 후).
- 기타 후보: 배포 Gate B~G / B안 정식화 잔여(B-RES-2 ADR, B-RES-3 contract-change) / 4계층 linkage.

## 4. PARKED 미래 (검증 후에만)
- **Commercial Viral Mode** (`meta/proposals/2026-06-03_commercial-viral-mode-design.md`): 4-tier(compact/rich/director/commercial_viral) + 10섹션 + scene 7필드 + critic 8차원. provisional P15/P18~19. ★ default ON 금지, PKM/RAG 데이터레이어 의존.
- **PKM/RAG Orchestrator** (`meta/proposals/2026-06-03_pkm-rag-orchestrator-design.md`): 6 scope + Trend Snapshot + retrieval orchestrator. provisional P16~17/P20~21. ★ 5단계 비충돌, user_locked 최우선, 자동 promotion 금지.
- 둘 다 **proposal-first, 코드 0, 선행조건(§3) 통과 전 빌드 금지**.

## 5. Gotcha (재개자 필수)
- behavior-preserving: OFF default byte-identical = **pytest 499 가 회귀 게이트**.
- slice = sub-agent + P-X1 §SELF-VERIFICATION + 매 slice commit·push. push 전 키 점검(`git diff origin/main..HEAD | grep sk-/AIza`)=0.
- .env CWD-상대 로딩 / cp949 콘솔(PYTHONIOENCODING=utf-8 + ASCII) / get_settings lru_cache(override 시 cache_clear) / LF→CRLF 경고 무시.
- rich gated: `rich_output_enabled`(config). frontend rich 슬롯 = PlanCard 조건부(값 있을 때만).
- 키는 .env(gitignore)에만. 사용자 노출 키는 compromised로 간주.

## 6. baseline
pytest **499** / origin **3feb068** / Skill 21 / agent 6 / output_schema rich 12슬롯 + commercial 제안 / critic 8~9차원(+commercial 8 제안) / golden_set 25(+commercial 5 제안).
