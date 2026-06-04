# Contract Change Log — CC-032: branding/select 4계층 자동 시드 (Phase 25)

- 반영일: 2026-06-04
- 상태: approved → 반영 완료 (Phase 25 빌드 승인, Phase 18 branding select 부수효과 additive 확장)

## 반영 내용 (api_contract.md §8.6)
- **POST /branding/select** 응답에 `domain_id`/`series_id` **additive Optional** 추가. 같은 gate(`branding_pkm_seed_enabled`)+authed 에서 선택 topic→domain, format→series 를 brand 하위에 자동 시드(멱등 get_or_create, graceful) → 위저드 거치면 /me/pkm-graph 4계층 자동 채움.
- 미생성/익명/flag OFF → domain_id/series_id null + 기존 키(ok/seeded) byte-identical.

## 정합 (docs↔code)
| 코드 | contract |
|---|---|
| DomainRepo/SeriesRepo get_or_create(멱등) | §8.6 멱등 ✅ |
| plans.py _auto_create_domain_series(gated/graceful) + branding/select 호출 | §8.6 자동 시드 ✅ |
| schemas/plans.py BrandingSelectResponse +domain_id/series_id | §8.6 응답 additive ✅ |

## Rollback
§8.6 응답 추가분 + §24 CC-032 제거(additive). 코드 revert. brand_memory 시드(Phase 18) 무영향.

## 영향
- migration 0(domains/series 0001 재사용). 그래프 builder 무변경(자동 생성 데이터는 read 가 반영). hermetic pytest 735→749(+14).
- ★ 범용 Discovery/Quick step 위저드는 본 CC 무관(domain/series discrete 캡처 안 함 — 별건). 브랜딩 세션 경로만.
