# Phase 26 — video 노드 + 개인 PKM 출처 라이브 데모

> 2026-06-04 | mock 백엔드(Phase 26) | mock-user-1 | API

## 판정: ★ PASS

### ① video CRUD (4계층 마지막)
| 호출 | 결과 |
|---|---|
| 브랜딩 select 자동 domain/series (Phase 25) | domain/series 생성 |
| **POST /me/videos** {series_id, title} | "흑임자 라떼 신메뉴 소개" 생성 |
| **PATCH /me/videos/{id}** | 200 → "흑임자 라떼 런칭 D-1" + 그래프 **video 노드** + **has_video 엣지 1** + summary.videos 1 |
| **DELETE /me/videos/{id}** | 200 → video 0, summary.videos 0 |
| 미소유 video PATCH | **404** (RLS 4-hop video→series→domain→brand→user) |

→ ★ **User→Brand→Domain→Series→Video 전 4계층 CRUD + 그래프 가시화 완성.**

### ② 개인 PKM 출처 엣지 (유닛 검증)
- migration 0007(pkm_entries +source_plan_id) + PkmRepo.add_entry(+source_plan_id) + 추출 훅(source_plan_id=plan_id) + me.py 공유 `_append_source_provenance`(브랜드 PKM 과 동일 로직, source_ids dedup 공유).
- 유닛 6건 PASS: add_entry source 기록 / 추출 훅 plan_id 기록 / 그래프 개인 PKM sourced_from→source / 개인+브랜드 동일 plan dedup(1 source 노드, 2 엣지) / 출처 없으면 byte-identical.
- ★ 그래프 로직은 Phase 21 브랜드 PKM 출처(라이브 검증됨)와 **동일 헬퍼** → 개인 PKM 도 동작 보증. (피드백→추출 실 사이클 라이브는 비용/다단계로 유닛 대체.)

## 결론
- 4계층 완전체(video까지) + 개인/브랜드 PKM provenance(공유 헬퍼). additive/graceful(video 0/출처 없음 → 기존 그래프 byte-identical). hermetic pytest 749→779. CC-033/034.
- 비고: migration 0007 실 적용은 운영(Supabase push, NG11) — in-memory/test 즉시 동작.
