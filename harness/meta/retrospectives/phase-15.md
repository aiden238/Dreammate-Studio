# Phase 15 회고 — director 모드 (output_mode 3rd tier)

> 2026-06-03 | 제품 phase (출력 tier 확장). project-1 PARKED 제안서 기반. 로드맵 ① director.

## 1. 한 일
`output_mode` 를 compact/rich/**director** 3-tier 로 일반화 + director(rich + 연출/리텐션 슬롯) gated/additive 추가.
- S1 enum+스키마(DirectorScene + model_dump_for_mode) / S2 P-006 v1.2.0 / S3 wiring / S4 critic retention_design v1.3.0 / S5 frontend / S6 director Plan-read fix + 라이브 검증 + cost + close.
- pytest 508→**536**. CC-017~020. 신규 endpoint/agent 0.

## 2. 잘된 것
- ★ **제안서 기반 진입**: project-1 PARKED commercial-viral 제안서의 director tier 를 그대로 구현 — open issue #1(슬롯 경계)·#2(flag→enum) 를 entry/전체기획안에서 확정 후 착수 → scope 흔들림 0.
- ★ **byte-identical 3중 안전**: model_dump_for_mode(모드별 제외) + effective_output_mode(backward-compat 매핑) + gated → compact/rich 회귀 0(기존 508 수정 0). Phase 13 패턴(P-GATED-OUTPUT-CHANGE-001) 계승.
- ★ **라이브 검증이 버그 2개 포착**: Intent 오반려 + director Plan-read 누락 — 자동 테스트(536)는 통과했는데 라이브에서만 드러남(테스트가 Plan 구성 read 를 안 봤음).

## 3. 실수 / 학습 (정직)
- ★ **director Plan-read wiring 누락**(S3): 새 출력 슬롯을 스키마(S1)·프롬프트(S2)·직렬화(S3)까지 wiring 했지만 **Plan 구성(LLM dict→Plan model) read 를 빠뜨림** → director 슬롯이 항상 빈 출력. rich 때도 동일 구조였는데 director 만 누락. → **학습: 새 출력 필드 = 스키마+프롬프트+직렬화+`Plan 구성 read`+critic+frontend 6곳 모두 wiring**. (S3 acceptance 에 "Plan 구성 read" 명시 누락이 근본.)
- ★ **자동 테스트가 못 잡음**: 단위 테스트(model_dump/wiring)는 Plan 구성 read 를 검증 안 함 → 라이브에서야 발견. → 새 슬롯에 **end-to-end(LLM dict→응답) 통합 테스트** 권장.
- ★ **진단 오판 2회**: director 빈 슬롯을 "모델 비순응"→"max_tokens 절단"으로 추정(둘 다 보조 요인이긴 함)했다가 실제는 Plan-read 누락. → 빈 출력 = 모델 의심 전에 **구성/파싱 경로부터** 확인.

## 4. 메트릭
- pytest 508→**536**(+28). 프론트 build 12 routes / scenario_simulation 36/36. 신규 endpoint/agent 0. 키 0.
- CC-017(스키마)/018(P-006)/019(P-007)/020(cost). 커밋 ~9(entry/plan/S1~S6/fix/close).

## 5. 다음에 가져갈 것
- ★ **director = 초안 수준**(사용자): 기획 브리프 경계 부합 — 대본-ready 가 아님. 깊이/품질 보강 = commercial_viral(10섹션) + PKM/RAG 데이터레이어(로드맵 ③). director 는 그 디딤돌(스키마/프롬프트/critic 확장 패턴 1차 검증 완료).
- **Intent 오반려 개선**(다음 작업): P-001 완화 + 차단→가이드.
- **Plan-read 회귀 가드** + 검증 보강(human review, 로드맵 ②).

## 6. 신규 패턴 후보
- **P-OUTPUT-SLOT-WIRING-001**: 새 출력 슬롯 추가 시 6곳(스키마·프롬프트·직렬화·**Plan 구성 read**·critic·frontend) 전부 wiring + end-to-end 통합 테스트 (Plan-read 누락 재발 방지).
- **P-LIVE-VERIFY-001**: 출력 변경 phase 는 자동 테스트 green ≠ 동작 — 라이브 e2e 필수(단위 테스트 사각 = Plan 구성 read).
- P-GATED-OUTPUT-CHANGE-001 update(3rd tier director — model_dump_for_mode 일반화) + P-CONTRACT-FIRST-001 update(CC-017~020).
