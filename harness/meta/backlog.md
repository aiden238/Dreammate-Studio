# BACKLOG — 이월/미완 항목 통합 (2026-06-05 최초 정리)

> 여러 phase closing_notes·retrospective·eval 리포트에 흩어진 이월(deferred)·미완·발견 결함을 한 곳에 종합.
> 출처 표기 + 심각도(높음/중간/낮음) + 반복 이월 횟수. PROJECT_STATE §실사용 준비도 와 정합.
> 갱신 규칙: 항목 해소 시 ✅ + 처리 phase 표기. 새 이월은 phase-complete 시 여기 추가.

---

## 🔴 높음 (제품 신뢰성·실사용에 직결)

| # | 항목 | 내용 | 출처 | 반복 |
|---|---|---|---|---|
| B-1 | **핵심 기능 default OFF** | rich/director/commercial(output_mode=compact) + PKM 주입·추출 + 브랜딩 자동시드 전부 flag OFF → 실사용자 미경험. env ON 검토 + 단계 활성 정책 필요. | config.py / 기능완성도 조사 | — |
| B-2 | **홈/네비 미완(실사용 진입)** | 홈(`/`)=Phase 1 textarea, 위저드/브랜딩 진입 링크 없음. AppShell 네비 미구현(component_map 정의만). | apps/web/app/page.tsx, component_map.md | — |
| B-3 | **PlansRepo plan 영속 미완** | 생성 plan이 `_plan_store`(in-memory)만 → 재시작 시 휘발. orchestrator→PlansRepo 배선 필요. | Phase 17·19 closing | **2회** |
| B-4 | **match_approved_knowledge SQL function 미정의** | RAG retrieval(rag/retrieval.py:96)이 rpc 호출하나 함수 없음 → 운영 RAG graceful-empty(동작 안 함). | 0004 migration / retrieval.py | — |
| B-5 | **human 실채점 0건** | critic 낙관 편향(전수 approve)이라 자동 gate=절대품질 아님. kit·LLM 기준선 준비됐으나 사람 채점 미실시 → 품질 근거 약함. | Phase 12 S4·16 S3·23 S2 | **3회** |
| B-6 | **commercial 데이터레이어 부재** | market_context/audience_psychology = LLM 추측(disclaimer만). PKM/RAG 실데이터 enrichment 미구현. | Phase 20 closing | — |
| B-7 | **rate_limit 미구현** | 정책 문서 487줄 / 코드 0 → free tier 비용 무제한·brute force 미방어. 운영 필수. | rate_limit_policy.md | — |

## 🟠 중간 (운영·검증 품질)

| # | 항목 | 내용 | 출처 | 반복 |
|---|---|---|---|---|
| M-1 | **migration 0001~0007 운영 미적용** | Supabase 수동 적용(NG11). 0007 포함. RLS 정책 실 DB 미검증(pgtap/수동). | Phase 26 closing / deploy_test_gates | — |
| M-2 | **프론트 시각 e2e 미확인** | /brain 그래프·commercial 렌더 등 headless ResizeObserver/screenshot 한계로 미검증. 실 브라우저 필요. | Phase 19·20·21·22~26 closing | **4회+** |
| M-3 | **실 LLM 회귀 CI 부재** | CI=mock-deterministic(구조만). 실 LLM은 1회 baseline(Phase 23)만. 회귀 탐지 약함. | Phase 23 retro | — |
| M-4 | **test hermeticity (.env Supabase)** | pytest가 `.env` 실 Supabase 키 의존 → SUPABASE_*="" 전제로만 결정적. autouse fixture 강제 미적용. | conftest / 품질 조사 | — |
| M-5 | **광고 입력-유래 누수** | GS-022("역대급 보온력") 입력 과장이 plan에 잔존. Intent/planning 입력측 광고 필터 강화 필요. | Phase 23 baseline | — |
| M-6 | **SSE async worker 부재** | SSE progress=in-process 동기 → 30~60초 생성 중 EventSource timeout 리스크 + 멀티프로세스 공유 불가. | sse.py / progress_store.py | — |
| M-7 | **배포 자동화/env 문서** | 배포 스크립트(CI/CD) 0, env_contract placeholder, secret 주입 절차 없음. Gate B 전제. | deploy_test_gates / env_contract.md | — |

## 🟢 낮음 (마감·고도화)

| # | 항목 | 내용 | 출처 |
|---|---|---|---|
| L-1 | generate→video 자동 연결 | 현재 video=/brain 수동 CRUD만. plan 생성→video 자동 연결 미구현. | Phase 26 closing |
| L-2 | 범용 Discovery/Quick step → domain/series 캡처 | 현재 브랜딩 세션 경로만 자동연결. 범용 step 위저드 재설계 별건. | Phase 25 closing |
| L-3 | series 삭제 시 video 고아 정리 | ON DELETE SET NULL → 고아 video. 정리 로직 후속. | Phase 26 closing |
| L-4 | video_projects 저장 경로 정리 | legacy insert_video_project(ADR-023) deprecated. 공식 폐기 or 신규 통합. | video_project.py |
| L-5 | rich default 전환 결정 | gated OFF 유지 중. 비용(3~5배)·품질 합의 후 default 전환 검토. | Phase 13~ |
| L-6 | B안 정식화 잔여 | 멀티프로바이더 ADR/contract 정식화 잔여(B-RES-2/3). | Phase 11 B안 |

---

## 해소됨 (참고)
- ✅ Intent 오반려 → CC-021(P-001 v1.1.0 콘텐츠 토픽 수용 + 차단→가이드 UX) 처리됨.
- ✅ 위저드↔백엔드 실연결 → Phase 14. 브랜딩→4계층 자동 → Phase 25.
- ✅ video 노드 / 개인 PKM 출처 → Phase 26.
- ✅ **B-1 핵심 기능 default OFF → Phase 27 S1** (`APP_PROFILE=realuse` 단일 스위치 = 실사용 핵심 루프 ON, 코드 default 보존).
- ✅ **B-2 홈/네비 → HIP-008(홈 진입 카드) + Phase 27 S2** (AppShell 지속 네비 전 페이지). 데스크톱 사이드바 full 만 잔여(낮음).
- ✅ **B-3 PlansRepo plan 영속 → HIP-008 S3 배선 + Phase 27 S1/S4** (realuse=plans_repo ON, test 4). 실 영속 검증=실-런(U-1).
- ✅ **B-4 match_approved_knowledge → HIP-008 S2** (0008 SQL) + Phase 27 S4(apply 스크립트/verify). 실 적용=ops.
- ✅ **B-7 rate_limit → Phase 27 S3** (generation 신원별 fixed-window→429, gated, test 5). 분산=후속(M-6/U-2).
- ✅ **M-1 migration 운영 적용 → Phase 27 S4** (apply_migrations.py 0001~0008 + README). 실 적용=ops.
- 🔸 **B-5 human 실채점** — kit + 실-런 런북 준비됨, 사용자 액션(실-런 후). (3회 이월 유지)

## 우선순위 제안 (영향순) — Phase 27 후 갱신
1. ~~B-1 + B-2~~ ✅ Phase 27 / ~~B-3 + B-4~~ ✅ Phase 27 / ~~B-7 + M-1~~ ✅ Phase 27.
2. **실 라이브 데모 + B-5** (품질 근거): 사용자 opt-in 실-런(실 LLM+Supabase) → human 실채점 회수.
3. **배포 Gate B~G** (M-7 배포 스크립트 + 실 staging): 인프라 user-provided. 잔여 B-6(commercial 데이터레이어)/M-2~M-6/L-1~L-6.
