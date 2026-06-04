# Phase 26 — 4계층 video 노드 + 개인 PKM 출처 (기능마감 완결)

## 목표
🅑 기능마감 남은 2개를 완결:
1. **video 노드 (4계층 마지막)**: VideoProjectRepo 신규 + /brain 에서 series 하위 video CRUD + 그래프 has_video → User→Brand→Domain→Series→**Video** 전 계층 가시화.
2. **개인 PKM 출처 엣지**: pkm_entries 에 `source_plan_id`(migration 0007) + 추출 훅이 출처 plan_id 기록 + 그래프 개인 PKM→source `sourced_from` 엣지(브랜드 PKM 로직 재사용) → 개인 PKM 도 "어느 기획에서 왔는지" 추적.

## 근거 (조사)
- video_projects 테이블(0001) 존재, repo 는 legacy wrapper(ADR-023 deprecated)만 → 신규 CRUD repo(SeriesRepo 패턴).
- pkm_entries 에 source_plan_id 부재(0006) → migration 0007(brand_memory 는 이미 0005 보유). 추출 훅(plans.py:446)에 plan_id 가용.
- 그래프 source 노드/sourced_from(Phase 21)·video type 만 추가 → 대부분 패턴 재사용.

## 핵심 원칙
- additive/graceful — video 0/출처 없음 → 기존 그래프 byte-identical. migration 0007 idempotent(ADD COLUMN IF NOT EXISTS).
- RLS — video 는 series→domain→brand→user 소유검증. 개인 PKM 출처는 본인 격리(기존).
- 추출 훅 출처 기록은 gated(personal_pkm_extract_enabled) 유지.

## 산출 (슬라이스)
S1(video backend: VideoProjectRepo + /me/videos CRUD + 그래프 has_video + graph.py + tests) → S2(개인 PKM 출처: migration 0007 + PkmRepo source_plan_id + 추출 훅 배선 + 그래프 개인 source 엣지 + db_schema CC + tests) → S3(frontend video CRUD + 라이브 데모 + api_contract CC + close).
