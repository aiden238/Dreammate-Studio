# Phase 24 — domain/series 편집·삭제 라이브 데모 (/brain CRUD 완성)

> 2026-06-04 | mock 백엔드(Phase 24) + 프론트 재기동 | mock-user-1 | API + 브라우저 DOM

## 판정: ★ PASS (end-to-end)

### ① 백엔드 CRUD API
| 호출 | 결과 |
|---|---|
| 생성(POST domain+series) | 200 |
| **PATCH /me/domains/{id}** rename | 200 → 그래프 라벨 "수정된 도메인명" 반영 |
| **PATCH /me/series/{id}** rename | 200 → "수정된 시리즈명" 반영 |
| 미소유 domain PATCH | **404** (RLS 소유검증) |
| **DELETE /me/domains/{id}** | 200 → domain 삭제 + **하위 series cascade**(둘 다 사라짐, summary 0/0) |

### ② 브라우저 /brain 렌더 (DOM)
"지식 구조 (4계층)" 섹션: 도메인 2(카페 브이로그/신메뉴 소개) + 시리즈 2(아침 오픈 루틴/단골 인터뷰) + 각 항목 **✏️편집 / 🗑삭제** 버튼 + 생성 입력(+도메인/+시리즈). ✏️ 9 / 🗑 9 (= PKM 5 + 도메인 2 + 시리즈 2). ★ 기존 PKM 카드·큐레이션 무변경.

## 결론
- ★ /brain 4계층 구조 **CRUD 완성**: 생성(Phase 22) + 큐레이션 PKM(Phase 19) + **편집·삭제(Phase 24)**. domain 삭제 → series cascade 동작.
- 편집/삭제는 Phase 21 그래프 read 가 자동 반영(builder 무변경). RLS 소유검증(미소유 404).
- 비고: 데스크톱 그래프 노드 시각은 headless 한계(Phase 19/21 동일) — 구조 섹션 렌더 + API + 그래프 데이터는 확인.
