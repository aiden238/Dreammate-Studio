# Phase 10 — Non-Goals

| ID | 항목 | 사유 |
|---|---|---|
| **NG1** | 영상 제작/편집 · TTS · BGM · 자동 렌더링 | ★ MVP **영구** non-goal (product_boundary — 영상기획 AI, 제작 아님) |
| **NG2** | 실 LLM eval **default 활성** | ★ 사용자 결정 — capability(경로 wire + 문서)만, default mock-deterministic 유지. 실 LLM run = opt-in(키) |
| **NG3** | 4계층 full linkage (plan_options/video_projects idealized schema 연결) | Phase 11+ (누적 2회 Phase 5+9 — 통합 phase 범위 밖) |
| **NG4** | SSE full async worker (background task) | Phase 11+ (누적 2회 Phase 5+8 — best-effort single-process 유지) |
| **NG5** | prompt A/B 실행 인프라 / multi-provider 동적 라우팅 | Phase 11+ |
| **NG6** | 사용자 데이터 자동 promotion (rag-update 두 번째 실행) | Phase 11+ (적재 경로만 — 실 promotion 별도) |
| **NG7** | 새 product UX 기능 (새 화면/플로우) | 통합·안정화·배포준비 phase — 신규 기능 0 |
| **NG8** | 기존 endpoint 응답 schema 파괴적 변경 | behavior-preserving — 신규 추가만 (G7) |
| **NG9** | PlanCard.tsx / component_map.md 수정 | 35/45연속 0줄 유지 — 통합 테스트는 page/wrapper 레벨, 신규 컴포넌트 없음 |
| **NG10** | Meta-Factory machinery 추가 변경 | detour(M0~M3) 종료 — M3 새 GAP 3은 백로그(별도) |
| **NG11** | Supabase SQL function `match_approved_knowledge` 실 정의 (운영) | 운영 배포 단계 — 본 phase 는 준비 게이트까지 |

## ★ 핵심 원칙
1. **통합·안정화·준비**: 신규 product 기능 0. end-to-end 검증 + P-AUX-2(준비된 것 활성) + eval 성숙 + 배포 준비.
2. **behavior-preserving**: 기존 endpoint/test 동작 불변 — 신규 추가만 (pytest 339 기존 수정 0).
3. **eval default mock**: 실 LLM mode 는 capability 만 (NG2). CI 게이트는 mock-deterministic.
4. **MVP 경계 영구 준수**: 영상 제작 미포함 (NG1).

## 회피 패턴
- ❌ "통합 김에 4계층 연결도" → NG3
- ❌ "eval mode 만들었으니 실 LLM 도 돌려보자(default)" → NG2 (opt-in 만)
- ❌ "P-AUX-2 김에 자동 promotion 도" → NG6
- ❌ 기존 endpoint 응답 필드 변경 → NG8 (behavior-preserving)
- ❌ PlanCard/component_map 수정 → NG9
