# Phase 22 — 진입 4점검 (phase-start §6)

## 1. Assumptions
### 1.1 확정
- domains/series 테이블(0001) + read repo(Phase 21 DomainRepo.list_for_brand / SeriesRepo.list_for_domain) 존재.
- BrandRepo.get_or_create_default insert 패턴(Supabase insert→id / in-memory uuid4 / graceful) + me.py _owns_brand_entry 소유검증 패턴 재사용.
- Phase 21 그래프 집계가 domain/series 를 자동 반영 → 생성만 하면 /brain 그래프에 표시(집계 로직 변경 0).
- **audit_naming 통과 (2026-06-04, 0 drift)**.
### 1.2 불확실
- U1 series 소유검증 = domain→brand→user 2-hop. DomainRepo 가 brand_id 만 가지므로 "user 의 brand 들의 domain 들"을 모아 검증.
- U2 라이브 데모 시 mock in-memory store 공유(Phase 17 런처 monkeypatch 패턴) — domain/series repo 도 공유 필요.

## 2. Simplest Slice (3회 압축)
```
1차: backend(repos create + endpoints) + frontend(UI) + 라이브.
2차: backend create + POST endpoints + 소유검증 + tests; 프론트는 S2.
3차: DomainRepo.create + POST /me/domains(brand 소유검증) — 단위 test(생성+404+anon).
     (series 는 같은 패턴 동반.) ← S1 = backend create+endpoint.
```
→ S1(backend create+endpoints+소유검증+tests+CC) → S2(frontend UI + 라이브 데모 + close).

## 3. Surgical Scope
- editable: db/repositories/{domain,series}_repo(create) + routers/me.py + schemas + apps/web(brain/api/types) + tests + phase/state/meta.
- read-only(→contract-change): api_contract.md §8.
- forbidden: migration / video 생성 / domain·series 편집·삭제 / 위저드 연결 / archive.
- ★ Sub-agent P-X1 §SELF-VERIFICATION 의무.

## 4. Verification
- S1: create → list 반영 + 소유검증(타인 brand→404 / 타인 domain→404) + RLS + anon 401 + 빈 name 422 단위 test. graceful(repo 실패 시 500 금지).
- 각 슬라이스: behavior-preserving(기존 pytest 698) + scenario_sim 36 + audit 0.
- S2: ★ 라이브 — /brain 에서 domain/series 생성 → 그래프 4계층 노드 표시.
