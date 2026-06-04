# Contract Change Log — CC-031: PATCH/DELETE /me/domains·/me/series (Phase 24)

- 반영일: 2026-06-04
- 상태: approved → 반영 완료 (Phase 24 빌드 승인 포함, Phase 19/22 me-endpoint 패턴 동형 additive)

## 반영 내용 (api_contract.md §8.7)
- **PATCH /me/domains/{id}** `{name}` → `{ok, domain}` / **DELETE /me/domains/{id}** → `{ok, deleted}`. 소유검증 domain→brand→user. DELETE 시 하위 series **cascade**(Supabase FK ON DELETE CASCADE / in-memory 명시).
- **PATCH /me/series/{id}** `{name}` → `{ok, series}` / **DELETE /me/series/{id}** → `{ok, deleted}`. 소유검증 series→domain→brand→user(3-hop).
- Status: 401(익명)/404(미소유)/422(빈 name). 교차 사용자 변경·삭제 0(RLS).

## 정합 (docs↔code)
| 코드 | contract |
|---|---|
| DomainRepo/SeriesRepo update_name·delete (graceful) | §8.7 PATCH/DELETE ✅ |
| me.py PATCH/DELETE + _owns_domain/_owns_series + 라우터 cascade | §8.7 소유검증·cascade ✅ |
| schemas MeDomain/MeSeriesUpdateRequest + MeMutationResponse | §8.7 body/응답 ✅ |

## Rollback
§8.7 PATCH/DELETE 4줄 + §24 CC-031 제거(additive). 코드 revert. 생성/조회/그래프 무영향.

## 영향
- migration 0(series FK 0001 재사용). graph builder 무변경(편집/삭제는 read 가 자동 반영). hermetic pytest 714→735(+21).
