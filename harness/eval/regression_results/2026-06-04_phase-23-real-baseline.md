# Phase 23 S1 — golden_set 실 LLM 전수 품질 baseline

> 2026-06-04 | OUTPUT_MODE=rich | planning=gpt-4o-mini / critic=gpt-4o
> golden_set 25 케이스 (실행 ok 18 / skip·error 7) | Temp/run_eval_baseline.py (레포 밖)

## 집계
- **overall_score (critic 9차원 평균, 0~5)**: mean=4.414 min=4.0 max=4.7778 (n=18)
- **depth_actionability (critic 9차원, 0~5)**: mean=4.222 min=4 max=5 (n=18)
- **verdict 분포**: {'approve': 18}
- **P0 케이스**: 7개 중 reject 아님 7 (P0 pass 100%)
- **광고 위반**: 1 / **차단어 위반**: 0

## 케이스별
| case | prio | overall | depth | verdict | ad | blk | name |
|---|---|---|---|---|---|---|---|
| ?1 | P0 | 4.2222 | 4 | approve | 0 | 0 | 대학생 창업 동아리 탐구 |
| ?2 | P0 | 4.3333 | 4 | approve | 0 | 0 | 동아리 신입 모집 |
| ?3 | P0 | 4.4444 | 4 | approve | 0 | 0 | 오늘의 점심 추천 |
| ?4 | P0 | 4.2222 | 4 | approve | 0 | 0 | 창업 동아리 소개 |
| ?5 | P0 | 4.6667 | 5 | approve | 0 | 0 | 일상의 작은 변화 |
| ?6 | P0 | 4.7778 | 5 | approve | 0 | 0 | 자취 생활의 현실 |
| ?7 | P1 | — | — | skip_no_input | — | — | — |
| ?8 | P1 | — | — | skip_no_input | — | — | — |
| ?9 | P1 | — | — | skip_no_input | — | — | — |
| ?10 | P0 | — | — | error_ValueError | — | — | — |
| ?11 | P2 | 4.5556 | 4 | approve | 0 | 0 | 대학생 창업 동아리 탐방 |
| ?12 | P1 | 4.3333 | 4 | approve | 0 | 0 | 홈트레이닝 기초 |
| ?13 | P1 | 4.4444 | 4 | approve | 0 | 0 | 성장 일기 |
| ?14 | P1 | — | — | skip_no_input | — | — | — |
| ?15 | P2 | 4.3333 | 4 | approve | 0 | 0 | 작은 베이커리의 신메뉴 |
| ?16 | P1 | 4.5556 | 4 | approve | 0 | 0 | 자취 김치볶음밥 |
| ?17 | P2 | 4.5556 | 4 | approve | 0 | 0 | 직장인 데일리 메이크업 |
| ?18 | P1 | 4.4444 | 5 | approve | 0 | 0 | 최신 스마트폰 리뷰 |
| ?19 | P2 | 4.5556 | 5 | approve | 0 | 0 | 코어운동 15초 쇼츠 |
| ?20 | P1 | 4.4444 | 4 | approve | 0 | 0 | 수도권 감성 여행 |
| ?21 | P2 | 4.3333 | 4 | approve | 0 | 0 | 중학생 영어단어 외우기 |
| ?22 | P0 | 4.0 | 4 | approve | 1 | 0 | 신상 텀블러 보온력 |
| ?23 | P1 | — | — | skip_no_input | — | — | — |
| ?24 | P1 | — | — | skip_no_input | — | — | — |
| ?25 | P1 | 4.2222 | 4 | approve | 0 | 0 | 모험의 시작 |

## 결론
- ★ 실 LLM 전수 baseline 확정 — 이후 회귀는 본 수치 대비 (overall/depth 하락 + P0 reject + 광고/차단 위반 게이트).
- depth_actionability 는 rich 출력에 대한 critic 9차원 실 채점(mock 미채점 차원). 운영 코드 0 수정(behavior-preserving).

## 해석 / 한계 (정직)
- ★ **critic 낙관 편향 주의**: overall 4.41/depth 4.22, **18/18 전부 approve** — 점수가 일관되게 높다. 이는 LLM-as-judge(critic)가 자기 출력을 후하게 평가하는 "88점 함정" 성향(프로젝트 기존 인지)을 보여준다. **절대 품질의 증거가 아니라 회귀 기준선**으로 읽어야 함 → 외부 검증(S2 human review)이 상호보완.
- **광고 위반 1건 (?22 = GS-022 텀블러)**: 입력 자체가 "역대급 보온력"(광고 표현)인 케이스 → plan 이 입력의 과장을 완전히 못 걷어냄. 광고 표현 필터의 입력-유래 누수 = 개선 포인트(후속).
- **skip 6 / error 1**: skip 6 은 P-001/P-002 카드 프롬프트 케이스(user_message 없음 — planning 대상 아님). error 1(?10 = GS-010)은 planning LLM 이 plan 미반환(1회 변동) → 재시도 시 회복 가능성. baseline 은 planning 대상 18 케이스로 산정.
- **라벨 ?N**: golden_set_loader 반환 dict 의 case_id 키 불일치로 위치 인덱스(?1~?25) 표기 — 수치/순서는 GS-001~025 와 동일(코스메틱, 재실행 비용 회피로 미보정).
- 본 baseline = **rich · 케이스당 1안 · gpt-4o-mini/gpt-4o**. 3안(parallel_3) 전수·compact 대조·human 채점은 후속(S2/이월).
