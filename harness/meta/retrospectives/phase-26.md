# Phase 26 회고 — 4계층 video 노드 + 개인 PKM 출처 (기능마감 완결)

> 2026-06-04 | 제품 phase | additive/graceful | ★ video 라이브 PASS | 🅑 완결

## 1. 무엇을 했나
🅑 기능마감 잔여 2개 완결:
- **S1 video 노드**: VideoProjectRepo(신규, SeriesRepo 패턴) + /me/videos CRUD(소유검증 4-hop) + me.py 그래프 has_video + graph.py type/kind/summary. → User→Brand→Domain→Series→**Video** 전 계층.
- **S2 개인 PKM 출처**: migration 0007(pkm_entries +source_plan_id) + PkmRepo.add_entry +source_plan_id + 추출 훅 배선 + me.py `_append_source_provenance` 공유 헬퍼(개인+브랜드 PKM 둘 다).
- **S3 frontend**: /brain 트리 series 하위 video CRUD UI + 라이브 데모.

## 2. 핵심 성과 / 검증
- ★ **video 라이브 PASS**: video 생성/편집/삭제 + 그래프 has_video + summary.videos + 미소유 404. 4계층 완전체.
- 개인 PKM 출처: 유닛 6 + Phase 21 브랜드 PKM(라이브 검증됨)과 **동일 공유 헬퍼** → 동작 보증.
- behavior-preserving: video 0/출처 없음 → 기존 그래프 byte-identical. hermetic pytest 749→**779**(S1 +24, S2 +6) + scenario_sim 36/36 + audit 0 + typecheck/lint. CC-033(video)/034(pkm source).

## 3. 학습 / 패턴
- **계층 확장의 기계적 미러링**: brand→domain→series→video 가 같은 repo/CRUD/그래프/UI 패턴의 반복 → video 추가가 거의 복붙(SeriesRepo→VideoProjectRepo, _owns_series→_owns_video). 계층 모델 + 일관 패턴의 배당.
- **provenance 공유 헬퍼**: 브랜드 PKM source 로직(Phase 21)을 `_append_source_provenance`로 추출 → 개인 PKM 에 재사용(중복 0, dedup 공유). 두 번째 사용처가 생길 때 헬퍼화하는 정형.
- **migration additive**: source_plan_id 를 ADD COLUMN IF NOT EXISTS(idempotent) + default None → 기존 동작 불변. brand_memory(0005) 정합.
- read-write 분리: 그래프 builder(read)가 video/출처를 자동 반영 → 생성/출처 추가가 builder 0 수정.

## 4. 정직한 한계 / 이월
- video 자동 생성(generate→video 자동 연결) 미포함 — /brain 수동 CRUD 만(후속).
- 개인 PKM 출처 = 피드백→추출 실 사이클 라이브 미실행(유닛+공유 헬퍼로 검증). migration 0007 실 적용은 운영(Supabase push, NG11).
- series 삭제 시 video.series_id=null(고아) — ON DELETE SET NULL(0001). 정리는 후속.
- 데스크톱 그래프 노드 시각(headless 한계).

## 5. 산출물
- backend: repositories/video_repo(신규)+pkm_repo(source) + migrations/0007 + me.py(video CRUD+그래프+공유 source 헬퍼) + plans.py(추출 훅) + schemas/graph.py(video)
- frontend: /brain video CRUD + api(createVideo 등) + types
- contract: CC-033(api /me/videos) + CC-034(db_schema pkm source_plan_id)
- tests +30(749→779): test_me_video(24) + test_personal_pkm_source(6)
- 라이브 데모 리포트 + 회고/closing

## 6. 다음
- ★ 🅑 기능마감 완결(domain/series 생성·편집·삭제 + video + 브랜딩 자동연결 + PKM 출처). /brain 4계층이 완전한 지식 구조.
- 다음 후보: 품질 후속(🅒 human 실채점 등) / 배포 Gate B~G / generate→video 자동연결·고도화.
