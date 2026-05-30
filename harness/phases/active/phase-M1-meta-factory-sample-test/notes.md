# Phase M1 — Notes

## 진입 맥락
- Phase M0(ADR-035)로 meta_factory machinery(generation 11단계 + validation 6검증 + schema/templates/blueprint + harness-factory Skill)를 만들었으나 **"문서·skeleton만" 상태** — 실작동 미증명.
- GPT M0 검토(점수: 구조 9 / proposal-first 9 / runtime 보호 9 / validation 8.5 / Claude·Codex 7 / 문서정합 7)에서 doc-sync 4건 수정 완료(commit 9f98df3) 후, 다음 단계로 **Sample Test(dry-run) 1회**가 타당하다고 합의.

## GPT 검토 반영 (기획 재조정 3건 + 분리)
| 보완 | 반영 위치 |
|---|---|
| ① with/without 비교 **수치화** (6 지표, 주관 금지) | goals G4 표 / acceptance A4 / multi_slice S2-2 / non_goals NG8 |
| ② 판정 **PASS/FAIL/PENDING/GAP 4상태** (첫 dry-run 실패 정상, with_without·eval-run PENDING 예상) | acceptance §4상태 / non_goals NG9 / assumptions C |
| ③ **outputs 외 변경 0 강제** + phase 기록은 **별도 doc-sync 분리** | scope §변경허용·금지 + §별도 doc-sync / multi_slice Wave3 / non_goals NG10 / MG1 |
| 분리 | **M1 meta-phase 로 독립** (제품 phase 아님, Phase 10 전에 끼워넣음) |

## 도메인 선택 근거 (팟캐스트)
- 인접: 브랜드/타깃/톤/후킹/시리즈/에피소드 공통.
- 차이: 시각자료→대화흐름, 썸네일→오프닝 멘트/질문, 영상 flow→오디오 segment.
- → 6 패턴/scaffold 재사용성 1차 검증에 최적. 완전 이질 도메인은 실패 원인 분석 곤란(NG6).

## ★ 안전 게이트 요약
```
A9   : FastAPI/Next.js/Supabase 0줄
MG1  : dry-run 변경이 meta_factory/outputs/TEST/** 외부 0줄 (★ 본 phase 신규 게이트, TEST 격리)
MG3  : P-X1 52연속 (S1·S2)
분리 : dry-run(sub-agent, outputs only) ↔ doc-sync(main, 별도 commit)
```

## 산출물 맵
```
meta_factory/outputs/TEST/                          ★ TEST 폴더 (sample-test 전용, active 아님)
  README.md                          (TEST 폴더 라벨/규칙)
  podcast/
    _without_baseline.md            (without 팔)
    domain_brief.md                 (with 입력)
    harness_blueprint.md            (with 출력 + validation 3필드)
    scaffolds/{agent,skill,contract,eval,phase,project_state}_draft.md
  sample_test_podcast_validation.md  (6검증 4상태 + with/without 6지표 + 5gaps 재현 + GAP + 제안)
```
> 실 산출 영역(outputs/generated_harnesses, outputs/improvement_reports)과 분리 — 본 dry-run 은 TEST/ 에만 쓴다.

## 결정 대기 / 옵션
- ADR-036(첫 dry-run 방법·결과) 작성 여부 = doc-sync 단계에서 선택 (retrospective 로 충분하면 생략 가능).
- 본 entry 는 dry-run **전** 계획 산출물. 사용자 "진행" 시 entry commit → S1 dispatch.

## 다음 단계 (M1 이후)
- improvement_reports 의 GAP → 다음 meta-phase 의 machinery 보강 입력.
- machinery 가 인접 도메인에서 충분히 작동 확인되면, 이후 이질 도메인 / 실 LLM 평가(검증 5 실측)로 확대 (별도 phase, payoff deferred 해제 시점 재검토).
- Phase 10 (MVP 제품 통합 테스트) 는 본 meta-phase 와 독립적으로 진행 가능.
