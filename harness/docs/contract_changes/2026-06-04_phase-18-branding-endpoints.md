# Contract Change Log — Phase 18 브랜딩 세션 endpoint + /new 진입

> ID: CC-023 | Status: **decided + applied** (2026-06-04) | Date: 2026-06-04
> Decision: 브랜딩 세션(Akinator 주제발굴) endpoint 3종 + agent P-AUX-3 + `/new` 진입 변화를 contract 에 additive 반영.
> 대상: `docs/contracts/api_contract.md` §8.6(신규) · `ai_system/prompts/prompt_registry.md`(P-AUX-3, S1에서 등록) · `apps/web/page_map.md`(/new + /new/branding)
> 근거: Phase 18 `meta/proposals/2026-06-04_branding-session-akinator-design.md` + 사용자 결정
> 절차: contract-change (api_contract additive) + prompt-version-review(P-AUX-3 — S1) + docs-sync(page_map)

## 1. 변경 요약
| 대상 | 변경 |
|---|---|
| `api_contract.md` §8.6 | **신규** 브랜딩 endpoint 3종(next/finalize/select) additive. 기존 §8.1~8.5 무변경. |
| `prompt_registry.md` | P-AUX-3 topic_discovery v1.0.0 (S1에서 additive 등록 — prompt-version-review). |
| `page_map.md` | `/new` redirect-only → mode picker(주제 추천받기 진입 추가, override redirect 보존) + `/new/branding` 신규 라우트. |

## 2. 영향 받는 영역
- [x] API 응답 형식 (신규 endpoint, additive)
- [x] Prompt (P-AUX-3 신규, S1)
- [x] 프론트 (page_map: /new + /new/branding)
- [ ] DB 스키마 (변경 0 — brand_memory/pkm 재사용)

## 3. 회귀 안전
- additive only: 기존 endpoint/라우트 byte-identical. 신규 endpoint gated(branding_pkm_seed_enabled default OFF) / auth-optional.
- pytest 608→641(+33: S1 12 + S2 11 + S4 9 + S3/consistency 등, 기존 0 수정) + scenario_sim 36/36 + audit 0 + typecheck/lint.

## 4. /new 동작 변화 (명시)
- 기존 `/new`는 redirect-only(page_map). 3번째 진입(주제 추천받기) 노출 위해 **mode picker 화면**으로 변경. ★ 딥링크 override(`?quick`/`?new`)는 즉시 redirect **byte-identical 보존**. 신규 노출 = 의도된 변화.

## 5. Rollback
- §8.6 + P-AUX-3 + /new picker + 브랜딩 라우트 revert + flag 제거. 전부 additive라 부분 rollback 안전.

## 6. 변경 이력
- 2026-06-04: Phase 18 — 브랜딩 endpoint 3종 + P-AUX-3 + /new 진입(CC-023).
