# Phase 14 — Non-Goals (명시적 제외)

| ID | 제외 항목 | 사유 / 이연처 |
|---|---|---|
| NG1 | **per-step 실 LLM 카드 생성** (P-001 brand / P-002 domain / P-003 series / P-004 target / P-005 direction 등) | 위저드 중간 step 의 추천 카드를 실 LLM 으로 생성하는 것은 **PARKED PKM/RAG Orchestrator**(provisional P16~17) 영역. Phase 14 는 입력 수집 → 최종 실 생성 배선까지. 중간 step 카드는 현행 휴리스틱/mock UX 유지(입력 수집용). |
| NG2 | **rich default OFF→ON 전환** | Phase 14 후보 A(별도 결정 — cost+품질 합의 필요). 위저드는 `rich_output_enabled` 현재값(OFF default)을 **상속만** 한다. |
| NG3 | **랜딩 `/` 경로 변경** | behavior-preserving — `app/page.tsx` / `/generate` / `dreammate.slice6.plan` 동작 불변(byte-identical). |
| NG4 | **완성 대본 / 영상 제작·편집·TTS·BGM** | product_boundary 영구 non-goal — 위저드 산출도 "기획 브리프". |
| NG5 | **배포 Gate B~G (staging 등)** | Phase 14 후보 C(별도). 본 phase 는 로컬 실연결까지. |
| NG6 | **PKM/RAG · Commercial Viral 빌드** | PARKED — proposal-first, 선행조건(본 위저드 실연결 포함) 통과 전 빌드 금지. |
| NG7 | **SSE async worker / wizard step 실시간 진행 스트리밍 고도화** | Phase 8 SSE 골격 재사용 범위 외 신규 async 워커는 제외(13~20 밴드). 위저드 generate 는 기존 sync 경로. |
| NG8 | **위저드 multi-step 상태의 Supabase 영속화 / 4계층 linkage** | in-memory `_plan_store` 재사용(기존 Phase 4 구조). 영속화·4계층 linkage 는 별도(13~20). |

★ NG1 이 가장 중요 — "위저드 실연결"을 **최종 생성 배선**(Scope A)으로 한정하고, **step별 지능형 추천**(per-step LLM)은 데이터 레이어(PKM/RAG)가 생긴 뒤로 이연한다. 이게 project-1 분석 + PARKED 의존성과 정합.
