# Proposal: 2nd Brain 시각화 — 마이페이지 PKM 도식화

> 날짜: 2026-06-04 | 유형: **설계 제안 (proposal-only)** — 코드/contract/migration 0 변경. 전부 "제안".
> 대상 phase: **Phase 19 (provisional)**
> 근거: 사용자 요청("2nd brain처럼 마이페이지에서 도식화") + moat = "쌓이는 데이터를 사용자 자산으로 가시화"
> 선행: Phase 17(PKM 축적/주입) ✅ + Phase 18(브랜딩 세션 = brand_memory source) ✅ — **도식화할 데이터 이미 구조화·축적 경로 존재**

---

## 0. 상태 / 목적 / 한 줄

- **상태**: 설계 제안. 신규 데이터 모델 아님 — **이미 저장 중인 PKM을 읽어 도식화하는 레이어**.
- **한 줄**: 마이페이지에서 사용자의 **개인 PKM + 브랜드 PKM + 4계층**을 노드/엣지 그래프(2nd brain)로 보여주고, 노드를 **큐레이션**(잠금/편집/삭제)할 수 있게 한다.
- **전략**: moat(쌓이는 독점 데이터)를 **사용자가 눈으로 보고 소유**하게 → stickiness↑. 백엔드 자산 → 사용자-facing 자산으로 격상.

## 1. 도식화 대상 (이미 존재하는 데이터)

```
User(나)
 ├─ 개인 PKM (pkm_entries, auth_user_id)      : preferred_tone🔒 / avoid_phrase / preferred_phrase … (leaf)
 ├─ Brand(s) (brands)
 │   └─ 브랜드 PKM (brand_memory_entries)       : tone/금지어/선호 (leaf)
 │       └─ Domain → Series → Video(plans)     : 4계층 (이미 스키마)
 └─ 신호(feedback_events/selected_plans)        : 어떤 피드백→어떤 PKM 추출됐는지 (엣지 출처)
```
→ 노드 = User/Brand/Series/PKM entries, 엣지 = 소유/파생(추출 출처). is_user_locked = 🔒 강조.

## 2. 기능 (★ 사용자 결정 2026-06-04 + 검토 반영)

> 결정: **하이브리드 viz**(모바일 카드/리스트 + 데스크톱 그래프) · **신규 `/brain` 전용 라우트** · **큐레이션 전부(잠금/편집/삭제) v1 포함**.
> ★ 검토 발견(design.md): 원칙 #10 "모바일 한 손 조작" + line 141 "모바일은 트리 아닌 breadcrumb" → 모바일은 그래프 대신 **카드/리스트**. (자유형 노드 그래프는 트리보다 더 모바일 부적합.)

- **읽기 API**: `GET /api/v1/me/pkm-graph` (RLS 격리 — 본인 것만) → 위 테이블들을 그래프 구조(nodes/edges)로 집계 반환. 신규 테이블 0. ★ 카드/리스트·그래프 **둘 다 소비 가능한** 구조로 설계.
- **프론트 `/brain`**(AuthGuard, AppShell 네비 진입): **반응형 하이브리드** — 모바일 = scope 섹션 **카드/리스트**(개인/브랜드/시리즈, PKM 칩), 데스크톱(≥브레이크포인트) = **노드 그래프**(react-flow, lazy-load 로 모바일 번들 영향 최소).
- **큐레이션(v1)**: 노드 **잠금(user_locked 토글)/편집/삭제** — 기존 PkmRepo/BrandMemoryRepo CRUD 재사용 + 신규 PATCH/DELETE endpoint. "내 지식 소유·관리".

## 3. 슬라이스 (provisional)
```
S1  GET /me/pkm-graph 집계 API (개인 pkm_entries + brand_memory + brands/series, RLS) + nodes/edges 스키마
S2  프론트 /brain 모바일 카드/리스트(scope 섹션, 반응형 base) — 읽기
S3  데스크톱 그래프 뷰(react-flow, ≥데스크톱 lazy-load; 모바일은 S2 카드 유지)
S4  큐레이션(잠금/편집/삭제 — PATCH/DELETE endpoint + UI, 기존 repo 재사용)
S5  출처 엣지(feedback→PKM) + 4계층 깊이 + e2e + phase-complete
```

## 4. 비목표 (NON-GOALS)
```
✗ 신규 PKM 데이터 모델 — 기존 pkm_entries/brand_memory/4계층 읽기만.
✗ 협업/공유 그래프 — 본인 PKM 한정(RLS).
✗ 자동 그래프 편집(LLM이 노드 추가) — 사용자 큐레이션 + 기존 추출 governance(≥0.9) 유지.
✗ 영상 제작 — product_boundary 계승.
```

## 5. 아키텍처 / 비충돌
- 읽기 집계 API + 프론트 viz가 핵심. 신규 테이블/migration 최소(없음 — 읽기) ~ DELETE/PATCH(S3, 기존 repo 재사용).
- RLS: 본인 auth_user_id/brand_id만(Phase 5/17 격리 재사용). 교차 노출 0.
- additive: 신규 `/brain` 라우트 + endpoint. 기존 흐름 무변경.
- viz: react-flow **데스크톱 전용 lazy-load**(`next/dynamic`, ssr:false) → 모바일 번들 영향 최소(모바일은 카드/리스트, 라이브러리 미로드). 번들 점검(design-review).
- 반응형 분기: 모바일(<브레이크포인트)=카드/리스트 / 데스크톱=그래프. 같은 /brain, 같은 API.

## 6. 리스크
| 리스크 | 방어 |
|---|---|
| 데이터 빈약 시 빈 그래프 | 온보딩 안내 + 브랜딩 세션/피드백으로 채우기 유도(Phase 18 연계) |
| viz 라이브러리 번들/성능 | 경량 라이브러리 + 노드 수 제한/페이지네이션 |
| 큐레이션 삭제 실수 | soft-delete or 확인 + user_locked 보호 |
| PII/격리 | 본인 데이터만(RLS), global_wiki 익명(원문 0, PKM/RAG 설계 계승) |

## 7. 다음
```
1. 본 제안 검토 + viz 라이브러리/페이지 위치 확정.
2. Phase 19 entry(phase-start) → S1~S4.
3. Phase 18 브랜딩 세션(채움) + Phase 17(주입)과 함께 "발굴→축적→주입→가시화" 완성.
```
