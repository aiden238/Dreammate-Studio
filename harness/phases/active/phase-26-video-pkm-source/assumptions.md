# Phase 26 — 진입 4점검 (phase-start §6)

## 1. Assumptions
### 1.1 확정
- video_projects 테이블(0001: id/series_id FK ON DELETE SET NULL/auth_user_id/title/status) 존재. legacy repo 는 deprecated(ADR-023) → 신규 VideoProjectRepo(SeriesRepo 패턴).
- pkm_entries source_plan_id 부재(0006) → migration 0007 additive(brand_memory 는 0005 보유). 추출 훅(plans.py:446) plan_id 인자 가용. PkmRepo.add_entry 확장(BrandMemoryRepo 패턴).
- 그래프 source 노드/sourced_from(Phase 21) + 브랜드 PKM 출처 로직(me.py:303-321) 개인 PKM 재사용(source_ids dedup 공유). graph.py type "source"/kind "sourced_from" 이미 존재.
- **audit_naming 통과 (2026-06-04, 0 drift)**.
### 1.2 불확실
- U1 video 소유검증 4-hop(video→series→domain→brand→user) — _owns_series(3-hop) 확장.
- U2 migration 실 적용은 사용자/운영(NG11) — in-memory/test 는 즉시 동작, Supabase 는 0007 push 후.
- U3 series FK ON DELETE SET NULL(video) — series 삭제 시 video.series_id=null(고아). 본 phase 는 video 직접 삭제만(cascade 고려 후속).

## 2. Simplest Slice (3회 압축)
```
1차: video + pkm-source + frontend + 라이브.
2차: S1 video backend / S2 pkm-source backend / S3 frontend+close.
3차: VideoProjectRepo.list_for_series + me.py 그래프 has_video 노드 + graph.py video type — 단위 test(graceful empty).
     ← S1 = video backend(repo+그래프+스키마).
```
→ S1(video backend) → S2(개인 PKM 출처 backend) → S3(frontend + 라이브 + close).

## 3. Surgical Scope
- editable: db/repositories/video_repo(신규)+pkm_repo + db/migrations/0007 + routers/me.py+plans.py + schemas/graph.py + apps/web + tests + phase/state/meta.
- read-only(→contract-change): api_contract.md(/me/videos) · db_schema.md(pkm source_plan_id).
- forbidden: legacy video_project.py 재활성 / generate→video 자동 / 신규 데이터모델 / archive.
- ★ Sub-agent P-X1 §SELF-VERIFICATION 의무.

## 4. Verification
- S1: video CRUD + 소유검증(타 video 404) + 그래프 has_video + graceful(video 0=기존 불변) 단위.
- S2: 추출 훅 source_plan_id 기록(add_entry) + 그래프 개인 source 엣지 + migration idempotent(IF NOT EXISTS) + gated/익명 skip 단위.
- 각 슬라이스: behavior-preserving(기존 pytest 749) + scenario_sim 36 + audit 0.
- S3: ★ 라이브 video CRUD + 개인 PKM 출처 표시.
