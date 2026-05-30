# Phase M1 — Assumptions

## A. 도메인 선택
- **팟캐스트 에피소드 기획 AI** 는 Dreammate(영상기획)와 **인접**하다 — 공통(브랜드/타깃/톤/후킹/시리즈/에피소드) + 차이(시각자료→대화흐름, 썸네일→오프닝 멘트/질문 설계, 영상 flow→오디오 segment). 첫 dry-run 의 실패 원인 분석이 가능한 거리. (완전 이질 도메인은 NG6.)
- 따라서 6 패턴(architecture_patterns) 중 일부(Pipeline/Supervisor/Producer-Reviewer)가 재사용 가능하다고 가정. 재사용 불가 패턴이 나오면 그것이 GAP.

## B. dry-run 의 성격
- 본 phase 는 **설계 산출물(문서)의 dry-run** 이다. 실 LLM 대량 호출/비용 평가는 하지 않는다 (NG7). 검증 5(eval-run)는 **절차 적용 가능성** 확인까지 (실측 점수 없음 → PENDING 기록).
- 첫 dry-run 은 **GAP 발견이 목적**이며 fail/pending 이 정상 결과다 (acceptance 4상태).

## C. with/without 비교의 한계 (정직하게 명시)
- **오염 위험**: meta_factory 를 아는 sub-agent 가 "without(맨손)" 산출물을 만들면 완전히 순수한 baseline 이 아니다. 완화책 — without 산출물을 **machinery 정독 전에 먼저** 작성하고, with 산출물과 분리 파일로 둔다. 그래도 잔존 오염은 한계로 기록.
- **소표본**: 1 도메인 1회. with/without 6 지표 중 일부(특히 품질·일관성 계열)는 통계적 의미가 약함 → 해당 항목 **PENDING** 가능 (GPT 보완 ② — fail 아님).
- 따라서 결론은 "machinery 가 작동/부족한 지점"의 **방향성**이지 정량 우열 단정이 아니다.

## D. 격리/안전 가정
- dry-run sub-agent 는 `meta_factory/outputs/**` 외부를 **읽기만** 한다 — machinery/기존 하네스/런타임 변경 0 (MG1/MG2/A9).
- phase 등록·회고·archive 는 dry-run 종료 후 **main 세션 별도 commit** (GPT 보완 ③) — sub-agent 권한과 분리되어 outputs 게이트가 깨지지 않는다.

## E. 산출물 위치 가정
- 생성 harness + 검증 리포트는 **`outputs/TEST/`** 에만 (★ TEST 폴더 격리 — 실 산출 영역 generated_harnesses/improvement_reports 와 분리). validation 통과 전 active 아님 (factory_contract 규칙 7).

## F. 시간/규모 가정
- S1 1.5~2.5h, S2 1~1.5h. 총 2.5~4h. 신규 Skill 0 (기존 harness-factory 사용만) → Skill 수 21 유지.

## G. 리스크 & 완화
| 리스크 | 완화 |
|---|---|
| sub-agent 가 outputs 밖에 쓰기 (MG1 위반) | forbidden 명시 + 사후 `git diff --stat` 게이트 + 위반 시 revert (P-X1) |
| machinery 가 팟캐스트에 안 맞아 blueprint 가 빈약 | 그것이 GAP — improvement_reports 기록이 목적 (실패 아님) |
| with/without 오염으로 비교 무의미 | without 먼저 작성 + 한계 명시 + 해당 지표 PENDING |
| dry-run 에 phase 운영 섞여 게이트 오염 | doc-sync 분리 (NG10) |
