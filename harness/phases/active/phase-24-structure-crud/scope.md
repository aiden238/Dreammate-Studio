# Phase 24 — Scope

## 포함 (build)
- **S1 backend**:
  - `DomainRepo.update_name(domain_id, name)` + `delete(domain_id)`; `SeriesRepo.update_name`/`delete`. (BrandMemoryRepo update/delete 패턴 — graceful, in-memory + Supabase).
  - domain 삭제 시 하위 series 처리: in-memory cascade(graceful) + Supabase FK(on delete) 의존. series 삭제는 단순.
  - `PATCH /me/domains/{id}` (body `{name}`) + `DELETE /me/domains/{id}` + `PATCH/DELETE /me/series/{id}`. 소유검증(_owns_domain / _owns_series=series→domain→brand→user).
  - 401 익명 / 404 미소유 / 422 빈 name / graceful(500 금지).
  - 단위 test(편집/삭제 + 소유검증 404 + RLS + cascade + anon).
- **S2 frontend**:
  - /brain "지식 구조" 섹션의 각 domain/series에 ✏️ 편집(인라인 name) + 🗑 삭제(확인) + refetch. api(updateDomain/deleteDomain/updateSeries/deleteSeries).
  - ★ 라이브 데모(편집/삭제 → 그래프·트리 반영). CC(api_contract §8.7) + close.

## 예상 파일 변경
```
editable:
  backend/fastapi/db/repositories/{domain_repo,series_repo}.py (update/delete 추가)
  backend/fastapi/routers/me.py (PATCH/DELETE endpoints + 소유검증)
  backend/fastapi/schemas/graph.py (요청/응답)
  apps/web/app/brain/page.tsx + components/brain/* + lib/api.ts (편집/삭제 UI)
  tests/ + phase/state/meta
read-only(→contract-change): docs/contracts/api_contract.md §8.7
forbidden: 위저드 연결 / video 노드 / 개인 PKM 출처 migration / 신규 데이터모델 / archive
```

## 검증
- behavior-preserving: 생성/조회/그래프 집계 무변경. 기존 pytest 714 green + scenario_sim 36 + audit 0.
- S1: 편집(name 변경 반영) + 삭제(domain→하위 series 함께 사라짐) + 소유검증(타인 404) + RLS + anon 401 단위 test.
- S2: typecheck/lint + ★ 라이브 /brain 편집/삭제 → 그래프/트리 반영.
