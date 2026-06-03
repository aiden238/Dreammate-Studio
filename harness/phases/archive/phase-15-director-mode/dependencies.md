# Phase 15 — Dependencies

## 선행 Phase (전부 done)
| Phase | 상태 | 본 phase 가 의존하는 것 |
|---|---|---|
| Phase 13 (rich gated) | ✅ done | `rich_output_enabled` + `Plan` rich 12슬롯 + `PLAN_RICH_FIELDS`/`model_dump_compact` + `RICH_SYSTEM_PROMPT`(P-006 v1.1.0) + critic `DIMENSIONS_RICH`(P-007 v1.2.0) — director 가 계승·확장 |
| Phase 14 (위저드 실연결) | ✅ done | generate 경로(/generate + /plans/{id}/generate)가 output_mode 자동 상속 → 위저드/랜딩 둘 다 director 가능 |

## 제안서 선행조건 (commercial-viral §0.2) 점검
| 조건 | 상태 | director 영향 |
|---|---|---|
| (b) 위저드 ↔ 백엔드 실연결 | ✅ Phase 14 | 충족 |
| (a) rich 실사용 검증 | 부분(라이브 동작 확인, 가치=사용자 "더 깊었으면") | director 는 gated OFF + additive(저위험)라 빌드 가능. 가치 정량화 = 로드맵 ②(검증 보강) |
| (c) human review | 미수행 → 로드맵 ② | director 자체는 OFF byte-identical(운영 무영향) → human review 는 default ON/commercial_viral 게이트(본 phase 아님) |

★ director 는 데이터레이어 **비의존**(제안서 §7.2) + gated OFF → 선행조건 (a)(c) 완전 충족 전에도 **안전하게 빌드 가능**(운영 영향 0). human review 는 director 다음(②).

## 회귀 게이트
- pytest **508** (Phase 14 baseline) = compact/rich byte-identical 회귀 게이트. 모든 director 변경 additive/gated.
- 기존 `rich_output_enabled` 동작 보존(output_mode 일반화 backward-compat).
