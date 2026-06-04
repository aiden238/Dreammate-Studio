# Phase 24 — 진입 4점검 (phase-start §6)

## 1. Assumptions
### 1.1 확정
- DomainRepo/SeriesRepo(Phase 21 read + Phase 22 create) 존재 → update/delete 추가.
- 패턴 재사용: BrandMemoryRepo.update_entry/delete_entry(Phase 19) + me.py _owns_brand/_owns_domain(Phase 22) + PKM 큐레이션 PATCH/DELETE(Phase 19 S4) 동형.
- 그래프 집계(Phase 21)가 편집/삭제 결과 자동 반영(read) → 집계 로직 변경 0.
- **audit_naming 통과 (2026-06-04, 0 drift)**.
### 1.2 불확실
- U1 domain 삭제 시 하위 series cascade — in-memory 는 명시 cascade(graceful), Supabase 는 FK(on delete cascade/set null) 의존. 스키마 0001 FK 동작 확인 필요(없으면 in-memory 만 보장 + 명시).
- U2 series 소유검증 = series→domain→brand→user 3-hop(_owns_series 신규).

## 2. Simplest Slice (3회 압축)
```
1차: backend(repos update/delete + endpoints) + frontend(UI) + 라이브.
2차: backend update/delete + PATCH/DELETE endpoints + 소유검증 + tests; 프론트는 S2.
3차: DomainRepo.update_name/delete + PATCH/DELETE /me/domains/{id}(소유검증) — 단위 test.
     (series 동반.) ← S1 = backend 편집·삭제.
```
→ S1(backend 편집·삭제+endpoints+소유검증+tests+CC) → S2(frontend UI + 라이브 + close).

## 3. Surgical Scope
- editable: db/repositories/{domain,series}_repo + routers/me.py + schemas/graph.py + apps/web(brain/components/api) + tests + phase/state/meta.
- read-only(→contract-change): api_contract.md §8.7.
- forbidden: 위저드 연결 / video / 개인 PKM 출처 migration / migration / archive.
- ★ Sub-agent P-X1 §SELF-VERIFICATION 의무.

## 4. Verification
- S1: 편집(name 반영) + 삭제(domain→series cascade) + 소유검증(타 domain/series 404) + RLS + anon 401 + 빈 name 422. graceful(500 금지).
- 각 슬라이스: behavior-preserving(기존 pytest 714) + scenario_sim 36 + audit 0.
- S2: ★ 라이브 /brain 편집/삭제 → 트리/그래프 반영.
