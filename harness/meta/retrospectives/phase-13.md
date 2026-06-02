# Phase 13 회고 — 출력 확장 (Output Enrichment — compact→rich)

> 종료일: 2026-06-03
> 유형: 제품 phase (런타임 有 — ★ 이 프로젝트 **첫 의도적 출력 변경**) — gated 단계 롤아웃 + additive 스키마(flag OFF byte-identical, behavior-preserving)
> 결과: ✅ compact(7필드)→rich(12 슬롯) 출력 확장을 **gated 로 안전하게** 운영 반영 — 깊이 0.231→1.000(≥0.8 PASS, OFF byte-identical) + Critic depth(88점 함정 해소) + frontend rich + ★ **라이브 입증**(/generate end-to-end rich, HTTP 200). pytest 471→**499**(기존 471 수정 0 = OFF 회귀 0). 키 0.
> 트리거: phase-complete v1.2.0 §7

---

## 1. 무엇을 했나 (Entry + 6 Slice)

- **Entry (`aaf4641`)**: Phase 12 종료(archive) + Phase 13 entry 8파일(goals/scope/non_goals/dependencies/acceptance/assumptions/multi_slice_plan/notes). gated+full 롤아웃 정의. (multi-llm-validation self 12th 는 entry 단계 deferred — §5 참조.)
- **S1 (`1665dc0`)**: output_schema rich 슬롯 — `Plan` rich 9 + `PlanFlowBeat` rich 3 = **12 슬롯 전부 Optional/additive** + `PLAN_RICH_FIELDS`/`BEAT_RICH_FIELDS` 상수 + `Plan.model_dump_compact()`(OFF byte-identical capability) + output_schema §8.1 **v1.1.0→v1.2.0** + agent-io-check **PASS(발견 0)** + 신규 test 10 → pytest 471→481. CC-012.
- **S2 (`ed1cf1f`)**: planning rich 프롬프트 — `RICH_SYSTEM_PROMPT`(12 슬롯 지시 + 브리프 경계) + `_build_rich_system_prompt_with_hint()` + `RICH_PROMPT_VERSION="v1.1.0"` + prompt_registry §7 **P-006 v1.0.0→v1.1.0**(prompt-version-review, ★ gated 공존 — deprecate 아님) + 신규 test 5 → pytest 481→486. ★ compact `SYSTEM_PROMPT`(v1.0.0) 보존 + rich 미연결(behavior-preserving, wiring=S3). CC-013.
- **S3 (`339da50`)**: gated wiring — config `rich_output_enabled` default **False** + `envelope_to_response_dict()`(`model_dump_compact()` 재사용) + planning 프롬프트 분기 + generate.py·moa_orchestrator·plans.py 직렬화 분기. **OFF=compact byte-identical**(/generate JSONResponse+header / /plans POST stored compact dict — response_model 미지정 rich 누수 차단) **ON=rich** + revise 왕복 rich 보존 + 신규 test 7 → pytest 486→493(기존 486 수정 0 = OFF byte-identical 증거). 운영 .py 6 + frontend 0. CC-014.
- **S4 (`61029cc`)**: Critic depth — critic `RICH_SYSTEM_PROMPT`(9차원 + depth rubric anchors) + `DIMENSIONS_RICH`(8+`depth_actionability`) + `RICH_PROMPT_VERSION=v1.2.0` + `run_critic` `rich_output_enabled` 분기(ON=9차원, OFF=8차원) + `_derive_verdict(dimensions=DIMENSIONS 기본)` + prompt_registry P-007 **v1.1.0(active/OFF)+v1.2.0(gated/ON)** + CriticEvaluation.dimensions 자유 dict additive + agent-io-check **PASS(발견 0)** + 신규 test 6 → pytest 493→499. **88점 함정 해소**(얕은 plan depth 낮음 → ON avg 하락). CC-015.
- **S5 (`9ec2783` + `11a2386`)**: frontend — `lib/types.ts`(PlanFlowBeat 3 + Plan 9 rich optional) + `components/PlanCard.tsx` rich **조건부 8섹션**(타깃·톤/대안후크/beat 화면·대사·자막/샷/썸네일·제목/CTA/레퍼런스/길이변형) — 값 있을 때만 렌더(compact=0개=기존 동일). 순수 additive(183/0). + 품질점수(Critic 배지) 미표시(사용자 요청, `SHOW_QUALITY_SCORE` flag). backend 0, design.md 준수(모바일/카드/제작UI 미포함).
- **S6 (본 회고)**: cost 재조정(CC-016 — rich 토큰 3~5배 × 3안 + B-RES-1 다중-provider 합산 통합) + **깊이 재측정**(운영 `run_planning()` OFF/ON 토글, OFF 0.231 / ON 1.000, ≥0.8 PASS) + phase-complete(retrospective + closing_notes + archive + REGISTRY/PROJECT_STATE done + patterns).

## 2. 핵심 결과

- **★ 첫 의도적 출력 변경을 gated 로 안전하게.** 이 프로젝트가 처음으로 "출력을 의도적으로 바꾼" phase. 그럼에도 flag(`rich_output_enabled` default False) + additive 스키마(rich 12 슬롯 전부 Optional) + compact-serialize(OFF byte-identical) 3중 안전장치로 **OFF 회귀 0**(기존 471 test 수정 0). ON=rich.
- **깊이 0.231 → 1.000 (≥0.8 PASS, 운영 입증).** Phase 12 가 측정 전용 프롬프트로 보인 잠재 1.0 을, S6 가 운영 `run_planning()` flag ON 경로로 **1.000 재현**(4/4 편차 0). OFF=0.231(Phase 12 baseline byte-identical 재확인). 격차 해소 = 운영으로 완결.
- **88점 함정 해소 (Critic depth).** Phase 12 가 발견한 "compact 가 Critic 88점 받아도 depth 미반영" 을 S4 가 gated 9차원(`depth_actionability`)으로 해소 — 얕은 plan 의 ON 종합 점수 하락.
- **frontend rich + 라이브 입증.** PlanCard 조건부 8섹션 rich 렌더 + ★ /generate end-to-end rich(HTTP 200, rich 9슬롯 + beat visual/dialogue/caption) + 화면 rich 확인.
- **behavior-preserving.** pytest 471→499(+28: S1 10 + S2 5 + S3 7 + S4 6, 기존 471 수정 0 = OFF byte-identical 증거). 운영 .py = schemas/output.py + planning.py + critic.py + config.py + generate.py + moa_orchestrator.py + plans.py(전부 additive/gated 분기). 키 0.
- **cost 정식화 (CC-016).** rich = 출력 토큰 3~5배 × 3안, gated OFF=cost 불변 / ON=rich 상한 + B-RES-1(다중-provider) 합산 주의 통합. tier(유료/opt-in) 권고.

## 3. 잘된 것

1. **gated + additive + compact-serialize 3중 안전장치로 회귀 0** — 출력을 바꾸면서도 (a) flag default OFF (b) rich 슬롯 전부 Optional (c) OFF 경로는 `model_dump_compact()`/response_model 미지정으로 rich 누수 차단 → 기존 471 test 한 줄도 수정 안 하고 ON rich 를 추가. "출력 변경 = 위험"의 통념을 안전 패턴으로 무력화 (P-GATED-OUTPUT-CHANGE-001 신규 후보).
2. **Phase 12 측정 → Phase 13 운영 반영 → S6 운영 재측정의 닫힌 루프** — Phase 12 가 "측정 전용으로 0.231→1.0 가능"을 보였고, Phase 13 이 그것을 운영에 gated 반영, S6 가 운영 `run_planning()` ON 으로 **1.000 재현 + OFF 0.231 byte-identical** 확인. 측정→반영→재측정이 한 바퀴 — 추측 아닌 데이터로 격차 해소 입증.
3. **88점 함정의 정확한 해소** — Phase 12 가 "Critic 이 깊이를 안 본다"를 발견 → S4 가 9번째 차원(`depth_actionability`) gated additive 로, 기존 8차원 `SYSTEM_PROMPT`/`DIMENSIONS`/`PROMPT_VERSION`/`normalize` 본문 무수정한 채 해소. 발견(Phase 12)과 처방(Phase 13 S4)이 1:1.
4. **prompt gated 공존(deprecate 아님)** — P-006(v1.0.0 compact active / v1.1.0 rich gated) + P-007(v1.1.0 8차원 active / v1.2.0 9차원 gated). flag 로 두 버전 공존 — 표준 deactivate 대신 gated 공존이라 OFF 경로 byte-identical. prompt-version-review semver 의 gated 변형.
5. **라이브 입증으로 "문서상 rich" → "실제 rich" 확정** — /generate end-to-end(HTTP 200, rich 9슬롯 + beat visual/dialogue/caption) + 화면 rich 직접 확인. S6 깊이 재측정(1.000)과 라이브가 서로 보강.

## 4. 아쉬운 것 / 한계

1. **rich default 전환은 미결정** — Phase 13 은 gated OFF 유지(검증·라이브 입증까지). flag default ON 전환(전 사용자 rich 노출)은 **별도 결정**(non_goal — 사용자 opt-in / Phase 14 후속). cost(CC-016 — 3~5배 × 3안) + 품질(feature 존재 ≠ 우수성) 합의 후 결정.
2. **위저드(/new/*) ↔ 백엔드 실연결 미완** — 랜딩 `/` 만 실 생성(/generate) 경로, Discovery/Quick 위저드(/new/*)는 여전히 mock. rich 라이브는 `/` 경로로 입증 — 위저드 실연결은 Phase 14 후보.
3. **feature 존재 채점의 품질 미반영** — depth_actionability 13 feature 는 슬롯 충족(0/1)만 본다. ON=1.000 = 슬롯 100% 충족이지 콘텐츠 우수성 아님("대사가 있어도 진부할 수 있음"). 품질 = human review / LLM-as-judge 보강 대상(Phase 12 S4 kit 계승, 실 채점 deferred 잔존).
4. **표본 4 + cost 추정** — S6 재측정 표본 4(Phase 12 6 의 부분집합). cost(§13~§14)는 데모 토큰 기준 추정 상향 — rich 활성 후 cost-review 실측 + 정밀 재조정 필요. 전수(25) 실 LLM eval baseline 미수행.
5. **multi-llm-validation self(12th) entry 단계 deferred** — Phase 13 entry 에서 self validation 정식 파일 생성은 deferred(entry handoff 분리 진행). 본 phase 는 작성 생략 명시 — Phase 14 진입 시 보강 가능(P-VALIDATION-FORMAL-001 연속성에 1회 공백 기록).

## 5. 패턴

- **P-GATED-OUTPUT-CHANGE-001 (신규 후보)** — 출력(직렬화 결과)을 의도적으로 변경할 때 **flag(default OFF) + additive 스키마(신규 슬롯 전부 Optional) + compact-serialize(OFF 경로 신규 슬롯 누수 차단)** 3중 안전장치로 **OFF 회귀 0**(기존 test 수정 0 = byte-identical 증거)을 보장하며 ON 에서만 rich. 첫 의도적 출력 변경(Phase 13)을 회귀 없이 안전 롤아웃. prompt 도 gated 공존(v1.0.0 active / v1.1.0 gated, deactivate 아님)으로 OFF byte-identical. → 정식 등록은 두 번째 출력 변경(flag default ON 전환 / 다른 출력 확장) 효과 재측정 후.
- **P-VALIDATION-DEPTH-GAP-001 (Phase 12 계승 — 운영 재측정 입증)** — Phase 12 가 정의한 "같은 모델·prompt/schema 설계로 출력 가치 격차 정량(compact vs rich, feature 0/1 → depth 비율)"을 Phase 13 S6 가 **운영 코드(run_planning) flag 토글로 재측정** — 측정 전용(Phase 12)이 아니라 운영 ON 0.231→1.000(≥0.8) + OFF byte-identical. 격차 정의(Phase 12) → 운영 반영(Phase 13) → 운영 재측정(S6)으로 패턴 완결.
- **P-BEHAVIOR-PRESERVING-001 update** — 출력 변경 phase 에서도 기존 471 test 수정 0(OFF byte-identical) + 신규 28(ON rich). "기존 test 수정 0 = 동작 불변 증거"가 출력 변경에도 성립(gated 덕).
- **P-CONTRACT-FIRST-001 update** — CC-012(스키마)/CC-013(프롬프트)/CC-014(wiring)/CC-015(Critic depth)/CC-016(cost) = Phase 13 만 **5 CC** additive 누적(CC-011 이후 누적 17회). 출력 변경을 contract-change 절차로 단계화.
- **P-X1-EFFECT-001 update** — Phase 13 S1~S5 (+S6 docs) sub-agent/세션 §SELF-VERIFICATION 연속 — 출력 변경에도 forbidden 0(런타임 .py 0 in S6). 누적 연속 유지.

## 6. 다음 단계 — Phase 14 (pending_user_decision)

- **rich default 전환 결정** — flag default ON(전 사용자 rich) 전환 여부. cost(CC-016 — 3~5배 × 3안, tier 유료/opt-in 권고) + 품질(feature 존재 ≠ 우수성, human review 보강) 합의 후. 현재 = gated OFF 유지.
- **위저드(/new/*) ↔ 백엔드 실연결** — Discovery/Quick 위저드 mock → 실 생성(/generate) 연결. 랜딩 `/` 만 실연결인 격차 해소(Phase 14 후보).
- **배포 Gate B~G** — staging→알파→베타(실 LLM opt-in)→제한 사용자→비용/성능→운영. 키·인프라 user-provided.
- **품질 보강** — Phase 12 S4 human review 실 채점 ↔ LLM-as-judge 신뢰도 대조 + 전수(25) 실 LLM eval baseline.
- **B안 정식화 잔여** — B-RES-2(ADR) / B-RES-3(agent_io·registry contract-change) (B-RES-1 cost = CC-016 흡수 완료).

## 7. 메타 정합

- Phase 12(검증 — "충분히 깊은가" 측정) → Phase 13(출력 확장 — 측정한 격차를 운영에 반영). 측정→반영의 연속. ★ 첫 의도적 출력 변경을 gated+additive+compact-serialize 로 회귀 없이 안전하게 — 제품 안정화 규율 유지하며 가치 확장.
- behavior-preserving(OFF byte-identical, 기존 471 수정 0) + 키 0 — 출력을 바꾸면서도 기존 동작 보존(gated default-off).
- ★ Phase 1~13 = MVP 통합(Phase 10) + LLM Gateway(Phase 11) + 검증(Phase 12) + 출력 확장(Phase 13, gated rich). 다음 = Phase 14 pending_user_decision(rich default 전환 / 위저드 실연결 / 배포 Gate B~G).
