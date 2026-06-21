# harness_improvement_proposals.md — 하네스 개선 제안

> 위치: `meta/harness_improvement_proposals.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `meta/self_improvement_loop.md` (5단계 루프), `meta/patterns.md`, `meta/lessons_learned.md`
> 참조: `.claude/skills/harness-audit/SKILL.md`, `.claude/skills/meta-retrospective/SKILL.md`

---

## 0. 제안서 정의

> **하네스 개선 제안 = 시스템 자체를 어떻게 더 좋게 만들지 정형 기록한 문서다.**

본 문서는 제안서 표준 + 진행 중인 제안서 목록을 담는다.

---

## 1. 제안서 작성 표준

각 제안서는 다음 8 섹션을 포함한다.

```
## HIP-{NNN} {짧은 제목}

### 배경
무엇이 문제인가 (현재 상태). 어떤 패턴 / 학습에서 출발했는가.
- 관련 patterns: P-N
- 관련 lessons: L-N

### 제안
무엇을 어떻게 바꿀 것인가 (변경 후 상태).
구체적으로 어떤 파일 / 절차 / Skill을 어떻게 바꿀 것인가.

### 영향 분석
- 영향 파일: (파일 목록)
- 영향 절차: (Skill / 작업 흐름)
- 영향 사용자: (있다면)
- 영향 비용: (있다면)
- 영향 일정: (있다면)
- back-compat 이슈: 있음 / 없음

### 대안
다른 옵션은 무엇이 있는가. 왜 본 제안이 우선되는가.
- 대안 A: ...
- 대안 B: ...
- 본 제안의 우위: ...

### 우선순위
P0 (즉시) / P1 (다음 Phase) / P2 (장기, 분기 단위)

### 검증 / 회귀 평가
어떻게 효과를 측정할 것인가.
- 측정 지표: ...
- 측정 시점: ...
- 통과 기준: ...

### 결정
승인 / 반려 / 보류 / 조건부 승인
- 결정 일자: YYYY-MM-DD
- 결정자: (사용자 / multi-llm 합의 등)
- 결정 사유: ...

### 적용 결과 (적용 후 작성)
- 적용 일자: YYYY-MM-DD
- 효과: ...
- 부작용: ...
- 회귀 통과 여부: ...
- 후속 조치: ...
```

---

## 2. 우선순위 정의

```
P0 (즉시):
- 보안 위협 / 데이터 노출 위험
- 비용 폭주 / 비용 한도 우회
- 사용자 차단 수준의 버그
- 회귀 90% 미만으로 하락
SLA: 24~72시간 내 결정 + 7일 내 적용

P1 (다음 Phase):
- 현재 Phase 안에 적용 (가능한 경우)
- 또는 다음 Phase 진입 시 적용
SLA: 30일 내 결정 + 60일 내 적용

P2 (장기):
- 분기 단위 검토
- Phase 11+ 또는 21+에 적용
- 영향이 크지만 즉각적이지 않음
SLA: 90일 내 결정 + 다음 분기 검토
```

---

## 3. 검토 절차 (multi-llm-validation 권장 케이스)

다음 제안은 multi-llm-validation Skill을 거치는 것이 권장.

```
multi-LLM 필수:
- 큰 contract 변경 (api / db_schema / output_schema)
- 가격 모델 변경
- 영구 제외 항목 변경 (mvp_non_goals.md 영향)
- Phase 진입 결정 (특히 Phase 11+)

multi-LLM 권장:
- prompt major version bump
- Skill 추가 / 삭제 / 통합
- 새 카테고리 (에러 / failure / 가드레일) 추가

multi-LLM 불필요 (단일 검토 충분):
- 작은 typo 수정
- 명명 통일
- 도구 / script 작성
- placeholder marker 보강
```

→ `.claude/skills/multi-llm-validation/SKILL.md`

---

## 4. 승인 / 반려 / 보류 처리

```
승인:
1. 제안서 §결정 섹션 갱신 (승인 + 일자 + 사유)
2. 적용 작업 task 생성
3. 적용 후 §적용 결과 섹션 작성
4. 회귀 측정 후 PROJECT_STATE.md 갱신

반려:
1. 제안서 §결정 섹션 갱신 (반려 + 일자 + 사유)
2. 반려 사유 명시 (대안 추천 가능)
3. 제안자에게 피드백 (사용자 직접 결정 시)
4. 제안서는 영구 보존 (history)

보류:
1. 제안서 §결정 섹션 갱신 (보류 + 이유 + 재검토 시점)
2. 보류 기한 명시 (30/60/90일)
3. 기한 도달 시 자동 재검토 알림
4. 보류 기한 무기한이면 사실상 반려와 동일 (지양)

조건부 승인:
1. 조건 명시 (예: "회귀 95% 이상 통과 시")
2. 적용 모니터링 기간 (예: "30일 모니터링 후 정식 채택")
3. 조건 미충족 시 자동 롤백 또는 재검토
```

---

## 5. harness-audit Skill의 출력 통합 위치

`harness-audit` Skill 실행 시 발견된 issue 중 일부는 본 문서로 제안서 변환.

```
harness-audit 발견 →
  - critical issue: 즉시 P0 제안서 작성
  - high issue: P1 제안서 작성
  - medium / low issue: meta/patterns.md 누적 후 5회 누적 시 P2 제안서

변환 절차:
1. harness-audit 결과 분석
2. 같은 영역 issue 그룹화
3. 그룹별 HIP 생성
4. 우선순위 자동 분류 (issue 등급 기준)
5. 검토 대기 큐 추가
```

→ `.claude/skills/harness-audit/SKILL.md`

---

## 6. 진행 중 제안서 (Phase 0 시드)

본 문서는 Phase 0에서 발견된 제안서 5개로 시작.

### HIP-001 9줄 stub 표준 placeholder marker

```
### 배경
docs/contracts/ 폴더의 16개 파일이 9줄 stub 상태.
"나중에 채울" 의도였으나 무한정 미루어짐.
관련 patterns: P-001 (9줄 stub 누적 경향)
관련 lessons: L-001

### 제안
9줄 stub 파일에 다음 표준 placeholder marker 추가:
- ⚠️ PLACEHOLDER 경고 헤더
- status YAML (status, fill_in_phase, priority, estimated_final_lines)
- Why Placeholder?
- Scope (TBD)
- Known Dependencies (when filled in)
- Fill-In Trigger
- Related Skill / Phase

### 영향 분석
- 영향 파일: docs/contracts/ 16개 stub
- 영향 절차: 모든 contract-change Skill 절차에 placeholder marker 검증 추가
- back-compat: 영향 없음 (추가만)

### 대안
A. 모든 stub을 즉시 deep 작성: 시간 부족.
B. stub 그대로 두기: 정합성 위험 (L-001 학습).
C. placeholder marker (본 제안): 작업 가능 + 정합성 유지.

### 우선순위
P0

### 검증
- harness-audit에서 9줄 stub 잔존 0건 확인
- 다음 Phase 진입 시 placeholder marker가 fill_in_trigger 기준 자동 알림

### 결정
승인 (2026-05-26).
사유: Sprint S3 진행 중 표준 형식 합의.

### 적용 결과
- 적용 일자: 2026-05-26 (Sprint S3-3)
- 효과: 11개 stub 파일에 적용. 8개는 deep 작성.
- 부작용: 없음
- 회귀: harness-audit 통과
```

### HIP-002 Skill INDEX 갱신 강제

```
### 배경
Sprint S2에서 Skill 통합 시 INDEX.md 갱신 누락 가능성 발견.
description 키워드 충돌이 자동 트리거 실패의 주 원인.
관련 patterns: P-003 (Skill 키워드 충돌)
관련 lessons: L-002

### 제안
모든 Skill 추가 / 변경 / 삭제 시 .claude/skills/INDEX.md 동시 갱신 강제.
- contract-change Skill 절차에 INDEX 검증 추가
- harness-audit Skill에 description 키워드 충돌 검증 추가
- INDEX.md 표 자동 갱신 script 작성 (선택)

### 영향 분석
- 영향 파일: .claude/skills/INDEX.md, .claude/skills/*/SKILL.md
- 영향 절차: contract-change Skill, harness-audit Skill

### 대안
A. 자동화 script만: 사용자 검토 부재 위험.
B. 수동 + 검증 (본 제안): 안전.
C. 그대로: 키워드 충돌 재발 위험.

### 우선순위
P0

### 결정
승인 (2026-05-26).
사유: Sprint S2 종료 시 적용.

### 적용 결과
- 적용 일자: 2026-05-26 (Sprint S2)
- 효과: INDEX 정합 100% 유지.
- 부작용: 없음
```

### HIP-003 네이밍 표준 contract 검토

```
### 배경
"Planner" vs "Planning" 명명 충돌이 8 파일 영향.
관련 patterns: P-002 (명명 충돌)
관련 lessons: L-003

### 제안
docs/contracts/에 naming_standard.md (또는 product_terminology.md) 추가.
- agent 명: Intent, Planning, Critic, Rewriter (확정)
- mode 명: Discovery, Quick (확정)
- 데이터 계층 명: User / Brand / Domain / Series / Video Project (확정)
- 영구 제외: "영상 제작 AI" 호명 금지 ("영상기획 AI 에이전트")
- 향후 추가될 명칭은 본 contract에 등록

### 영향 분석
- 영향 파일: 새 contract 1개 + 기존 모든 contract / Skill 갱신
- 영향 절차: 모든 작성 시 본 contract 참조

### 대안
A. 명시적 contract (본 제안): 일관성 보장.
B. CLAUDE.md / AGENTS.md에 흩어진 정의 유지: 충돌 재발 위험.

### 우선순위
P1 (Phase 1 진입 시)

### 결정
보류 (2026-05-26). 재검토: Phase 1 진입 시.
사유: Phase 0 범위 외. 단 Phase 1 시작 시 즉시 작성.
→ ★ **반려·흡수 종결 (2026-06-05, HIP-009 S3)**: naming_standard contract 별도 신설 대신 `scripts/audit_naming.ps1`(harness-audit §6.5 + qa-check cat 11)이 plan_candidates/video_projects/critic_evaluation/rag_references 명명 일관성을 매 phase 자동 강제 → 의도 충족. canonical 용어 SoT = audit_naming NAMING_POLICY. 신규 contract 불요.
```

### HIP-004 multi-llm-validation 트리거 정량 기준

```
### 배경
multi-llm-validation Skill 호출이 주관적 (큰 결정인지 판단 모호).
관련 patterns: P-004 (단일 모델 편향)
관련 lessons: L-004

### 제안
multi-llm-validation 필수 조건 정량화:
- 영향 파일 5개 이상
- 영향 사용자 100명 이상
- 비용 영향 월 $100 이상
- 보안 / 컴플라이언스 영향
- prompt major version bump
- 가격 변경

위 중 1개라도 해당 시 자동 트리거.

### 영향 분석
- 영향 파일: .claude/skills/multi-llm-validation/SKILL.md
- 영향 절차: 모든 큰 결정의 검토 흐름

### 대안
A. 정량 기준 (본 제안): 명확.
B. 주관 유지: 불일치 위험.

### 우선순위
P1 (Phase 1 진입 시)

### 결정
보류 (2026-05-26). 재검토: Phase 5+ (사용자 / 비용 실데이터 후).
사유: 사용자 수 / 비용 임계 기준은 실 데이터 없으면 무의미.
→ ★ **승인·정의 (2026-06-05, HIP-009 S3)**: HIP-006 텔레메트리(agent_io_logs) + cost-review(006-S2)로 비용 실데이터원 확보 → multi-llm-validation 필수 임계 정량화: ① 영향 파일 ≥5 ② prompt major bump ③ 가격/보안/영구제외(mvp_non_goals) 변경 ④ cost-review 월 추정 비용 임계 초과. 1+ 해당 시 트리거. → ★ **반영 완료 (2026-06-05)**: `multi-llm-validation` SKILL **v1.1.0** §트리거 조건에 "필수 정량 임계" 4종 추가(Skill=contract, contract-change 정합).
```

### HIP-005 Sprint 종료 자동 PROJECT_STATE 검증

```
### 배경
PROJECT_STATE.md 갱신 누락 시 다음 세션 진입 시 컨텍스트 손실.
관련 lessons: L-005

### 제안
Sprint 종료 시 sanity script가 PROJECT_STATE.md 갱신 여부 자동 검증:
- migration_progress.current_sprint가 끝난 Sprint 번호인지
- last_completed_action에 Sprint 내용 반영됐는지
- last_updated 일자가 오늘 일자인지
- 미갱신 시 commit 차단

### 영향 분석
- 영향 파일: harness/scripts/sanity_end_*.ps1
- 영향 절차: 모든 Sprint 종료

### 대안
A. 자동 검증 (본 제안): 강제력.
B. 수동 체크리스트: 누락 위험.

### 우선순위
P1 (Sprint S5 종료 시)

### 결정
보류 (2026-05-26). 재검토: Sprint S5-3에서 적용 검토.
사유: 본 Sprint (S5-1)는 deep 작성 우선.
→ ★ **반려·흡수 종결 (2026-06-05, HIP-009 S3)**: Sprint 단위 운영 종료(현재 phase 단위). PROJECT_STATE 갱신 강제는 qa-check **cat 12(운영 도달성, 008-S1)** + phase-complete acceptance + `scripts/sanity_end_*.ps1` 에 흡수 → 별도 자동검증 스크립트 불요.
```

---

## 6.5 신규 제안서 (2026-06-05 harness-audit 발 — HIP-006~010)

> 출처: `meta/audits/2026-06-05.md` (이 하네스 최초 완주 audit). 발견 high 3 + 제품 운영 갭 → 5 제안서.
> 핵심 진단: 하네스가 "서사/문서 척추(alive)"와 "운영/자기개선 척추(dead)"로 분리. 죽은 부분의 공통 원인 = **현실 데이터 접지선 부재**.
> ★ 결정 상태: 전부 **검토 대기** (2026-06-05 작성, 사용자 결정 대기). 본 문서 작성 = "쓰는 것"이지 "적용"이 아님(self_improvement_loop §7 예외).

### HIP-006 텔레메트리 발신기 (`agent_io_logs` 실제 기록)

```
### 배경
self_improvement_loop §1.2가 패턴 마이닝 입력으로 'agent_io_logs'를 선언했으나,
backend grep 결과 이를 기록하는 코드가 0건. 데이터원이 이름만 존재.
이 단일 누락이 cost-review / cost_snapshots / patterns 자동마이닝 / skill_usage_log /
HIP-004(정량임계)를 동시에 구조적으로 무력화.
- 관련 audit: 2026-06-05 §3 (근본원인), high H2
- 관련 patterns: (P-신규 후보 — "telemetry 부재로 인한 측정 machinery 동결")

### 제안
LLM 호출 1건당 1줄 텔레메트리 발신부 추가:
{ts, request_id, prompt_id, model, input_tokens, output_tokens, cost_est, latency_ms, success, fallback}.
- 1차: JSONL append (backend/fastapi 생성 경로 — moa_orchestrator/llm gateway 단일 지점) — 가장 작은 레버.
- 2차: db_schema의 agent_io_logs 테이블 실제 write 연결 (RLS 포함).
- cost-review / eval/cost_snapshots / patterns 마이닝이 이 데이터를 소비하도록 배선.

### 영향 분석
- 영향 파일: backend/fastapi/llm/gateway.py 또는 orchestration/moa_orchestrator.py(단일 지점) + config(flag)
- 영향 절차: cost-review(데이터 확보) / meta-retrospective(patterns 입력) / harness-audit §6
- 영향 비용: 로깅 자체 비용 무시 가능 / 오히려 비용 폭주 조기탐지 가능
- back-compat: 없음 (additive, gated default-off 가능 — behavior-preserving 규율 정합)

### 대안
A. JSONL 발신(본 제안 1차): 최소 변경, CI/로컬에서도 작동.
B. 곧장 DB 테이블: RLS/migration 운영 의존 → §B 갭에 막힘. (2차로 미룸)
C. 그대로: cost/patterns/usage 영구 측정 불가. (반대)

### 우선순위
P0 — 죽은 측정 machinery 4종의 단일 해소 레버 + 비용 폭주(배포 리스크) 방어 선행조건.

### 검증 / 회귀 평가
- 측정 지표: 생성 1회당 로그 1행 생성 / cost-review가 실 토큰·비용 집계 산출
- 측정 시점: 구현 직후 + 다음 phase 종료
- 통과 기준: agent_io 로그 행 > 0 AND cost-review가 0 아닌 비용 리포트 산출

### 결정
승인 → S1 구현 완료 (2026-06-05, 사용자 지시 "실제 구현 착수"). 결정자: 사용자.

### 적용 결과
- 적용 일자: 2026-06-05 (S1 — 발신기 + gateway 배선)
- 구현: `backend/fastapi/observability/agent_io_log.py`(`log_agent_io` + `estimate_cost_usd`, db_schema §7.1 정합 필드) + config `agent_io_log_enabled`(default False)/`agent_io_log_path` + `gateway.complete` 단일 chokepoint 배선(latency 측정 + success/error record) + `.gitignore`(logs/telemetry/).
- 효과: `agent_io_logs` "이름만 존재"(audit §3) → **실 기록 가능**(flag ON 시 LLM 호출 1건 = 1 JSONL 행). cost-review/patterns 자동마이닝/HIP-004 의 데이터원 확보 — H2 부분 해소.
- 부작용: 0 — gated default-off + graceful(로깅 실패가 생성 차단 X). pytest **779→784**(+5 신규, 기존 779 수정 0 = behavior-preserving 증거) + scenario_sim 36/36.
- 회귀 통과: ✅ (full backend 784 passed)
- **S2 (2026-06-05, cost-review reader)**: `backend/fastapi/observability/cost_report.py`(`load_agent_io_records`/`aggregate_agent_io`/`render_cost_markdown`/`build_cost_snapshot`) + test 5 → pytest 784→**789**. 텔레메트리 JSONL → 집계(호출/성공실패/토큰/비용/모델·agent별/latency) → `eval/cost_snapshots/{date}.md` 렌더. **cost-review Skill 데이터 소비 경로 확보**(죽었던 cost_snapshots 부활 capability — 실 스냅샷은 flag ON 운영 데이터로 생성).
- **S3 (2026-06-05, 기본 경로 계측 + DB 적재 경로)**: gateway 만 계측되던 갭 해소 — **critic·planning 직접 호출부에 텔레메트리 배선**(`usage_tokens` 방어적 추출 + prompt_id 기록) + `agent_io_log_to_db`(gated sub-flag) → Supabase `agent_io_logs` 적재 경로(graceful) + test 4 → pytest 802→**806**. ★ JSONL=인프라 0(flag만), DB 적재=Supabase DB만(서버 배포 불필요). OFF byte-identical.
- 후속(handoff): flag ON(env) + 실 LLM(키)로 데이터 생성 + Supabase agent_io_logs 적재 활성 — 전부 ops. 추가 call site(intent/rewriter/_run_planning_single 병렬)는 동일 패턴 후속.
```

### HIP-007 품질 신호의 현실 접지 (critic 낙관편향 보정 + human N>0)

```
### 배경
품질 게이트(Critic)가 전수 approve(낙관편향, Phase 23 자인 "88점 함정"). 즉 하네스가
좋은 기획 vs 나쁜 기획을 구별 못 함. human 실채점 3회 이월 0건. 실 LLM 회귀는 CI에 없음
(mock + 1회 baseline). → Phase 13~26의 모든 "품질 향상"이 미검증 가설.
- 관련 audit: 2026-06-05 §6 (제품 §D) / PROJECT_STATE §D
- 관련 contract: eval/human_review_rubric.md (rubric 존재), eval/human_review/ (kit 존재)

### 제안
하네스의 "원래 목적(근거 기반 품질 검증)"을 실제 작동시키는 3택 중 최소 1:
- (a) human blind 채점 N=5 1회 실행 — kit 이미 존재, 가장 빠른 현실 접지.
- (b) critic 보정 — adversarial/calibrated judge(결함을 일부러 찾게) + anchor 재조정.
- (c) 실 LLM golden_set 회귀를 정기 트리거(현재 mock-only) — HIP-006 텔레메트리와 비용 연동.
권장 순서: (a) 먼저(즉시 신호 확보) → (b)/(c)로 자동화.

### 영향 분석
- 영향 파일: eval/human_review/* / .claude/skills/eval-run·eval-design / ai_system/prompts(critic P-007)
- 영향 절차: eval-run / eval-design / prompt-version-review(critic bump 시)
- back-compat: (a) 코드 0 / (b) prompt bump = prompt-version-review 절차

### 대안
A. human N=5 먼저(본 제안): 측정도구 신뢰 회복의 최단경로.
B. critic 자동보정만: 여전히 LLM이 LLM을 채점(순환) — human 1회로 calibrate 필요.
C. 현행 자동 gate 유지: 절대 품질 보증 불가(반대).

### 우선순위
P0 — L2 제품 목적의 심장. 측정도구 불신 상태에서는 이후 모든 품질작업이 가설.

### 검증 / 회귀 평가
- 통과 기준: human 채점 N≥5 1회 완료 AND critic 점수와 human 점수의 상관/괴리 측정치 기록
- 측정 시점: 1회 실행 직후 (eval/regression_results 또는 eval/human_review에 저장)

### 결정
승인 → S1 구현 (2026-06-05). 결정자: 사용자. (S2 real-eval 경로 진행 / S3 human N=5 = handoff)

### 적용 결과
- **S1 (2026-06-05, critic 낙관편향 보정)**: config `critic_calibration_enabled`(default False)/`critic_calibration_min_score` + `critic.py` `CALIBRATION_PREAMBLE`(anti-optimism 엄격 채점) + `CALIBRATION_KEY_DIMS`(모드별 핵심차원) + `_derive_verdict` **핵심차원 게이트**(평균이 approve 라도 핵심차원<min 이면 approve→revise) + prompt_registry **P-007 v1.5.0**(gated, 직교) + test 6 → pytest 789→**795**. ★ "88점 함정"의 평균-희석 한계(depth 가 평균에 묻힘)를 게이트로 직접 차단. gated default-off → OFF byte-identical(기존 critic 32 test 무영향, consistency 12 PASS).
- **S2 (2026-06-05, real-eval 정식 트리거 경로)**: `backend/fastapi/eval/run_eval.py`(`run_and_report` + `build_real_llm_caller` + CLI `python -m backend.fastapi.eval.run_eval [--real]`) — golden_set eval 을 한 명령으로 실행하고 `eval/regression_results/{trigger}.md` 기록. mock 기본(CI 가능, 비용 0) + real opt-in(키 존재 시, 부재 시 graceful mock fallback — 실 호출 0). test 3 → pytest 795→**798**. "1회성 baseline → 반복 가능 정식 경로" 해소.
- 후속: S3 human N=5(handoff, kit 존재) + real 실행(키 제공 = ops/CI 비밀) + critic 보정 효과 real 측정.
```

### HIP-008 "done"의 정의에 운영 도달성(operational reachability) 포함

```
### 배경
현재 완료 기준 = pytest green + flag-OFF byte-identical. 너무 관대해 도달 불가능한 기능이
26 phase째 축적: flag 전부 default False / 홈·네비 링크 없음 / RAG match_approved_knowledge
SQL func 미정의(retrieval 실작동 0) / PlansRepo in-memory 휘발 / migration Supabase 미적용.
- 관련 audit: 2026-06-05 §6 (제품 §A/B/C) / PROJECT_STATE §A·§B·§C

### 제안
phase acceptance 체크리스트에 1줄 추가: "실 환경에서 사용자가 도달 가능하고 실제로 동작한다".
구체:
- staging 1개 + 배포 스크립트(현재 0) + env_contract 실값.
- match_approved_knowledge SQL func 정의(RAG 운영 활성).
- PlansRepo 영속(in-memory 탈피) — 2회 이월 해소.
- 최소 1개 flag ON 도달 경로(홈 → /new 위저드 진입 링크 + AppShell 네비 구현).

### 영향 분석
- 영향 파일: phase-complete/qa-check SKILL(acceptance 항목) + backend repos + db/migrations + apps/web(홈/네비)
- 영향 절차: qa-check(release gate) / phase-complete(acceptance 검증)
- back-compat: acceptance 기준 강화(향후 phase) — 과거 phase 소급 아님

### 대안
A. acceptance에 도달성 추가(본 제안): "문서상 완성" → "실제 작동" 방향 보정.
B. 배포 phase를 따로(Gate B~G): 맞지만, 기준 자체를 안 바꾸면 도달불가 누적 재발.
C. 현행 유지: capability가 계속 어둠 속에 쌓임(반대).

### 우선순위
P1 — PROJECT_STATE가 스스로 추천한 🅐(실사용 경험 잇기)와 정합.

### 검증 / 회귀 평가
- 통과 기준: 신규 사용자가 홈→위저드→실 3안까지 도달(flag ON 경로) AND 서버 재시작 후 plan 영속
- 측정 시점: 적용 phase 종료 라이브 데모

### 결정
승인 → S1+S2 구현 (2026-06-05). 결정자: 사용자. (S3 PlansRepo 영속 / S4 홈·네비 진행)

### 적용 결과
- **S1 (2026-06-05, done 정의 강화)**: `qa-check` SKILL **v1.3.0** 카테고리 12 "운영 도달성(Operational Reachability)" 추가 — 사용자 진입 경로 / flag ON 경로 / 영속·운영 의존 명시 또는 명시적 이월 강제. "behavior-preserving + green 만으로 done 금지". phase-complete 가 qa-check 를 호출 → phase 종료 acceptance 에 자동 포함. audit §A/B/C 의 "동작 ≠ 도달" 게이트.
- **S2 (2026-06-05, RAG retrieval 활성)**: `db/migrations/0008_match_approved_knowledge.sql` — retrieval 이 호출하나 미정의였던 RPC 함수 정의(approved_knowledge cosine top-k, RPC 계약 정합 + brand/auth 격리). RAG "graceful-empty(함수 미정의)" → 동작 가능. ★ Supabase 적용은 운영자(NG11) — SQL 작성 완료, pytest 영향 0(retrieval test 는 RPC mock).
- **S3 (2026-06-05, plan 영속)**: `orchestration/moa_orchestrator.py` `_persist_plan_envelope`(gated `plans_repo_enabled` default False, PlansRepo upsert=update→없으면 create, graceful) + config flag + test 4 → pytest 798→**802**. OFF=in-memory only byte-identical(기존 798 무수정). 실영속은 Supabase 설정(ops). PlansRepo(기존)·graceful 패턴 재사용.
- **S4 (2026-06-05, 홈 진입)**: `apps/web/app/page.tsx` 에 "단계별로 기획하기" 진입 카드(→ `/new`, `/new/branding`) + stale footer("후속 Phase 추가") 교정. typecheck+lint pass. ★ 범위=홈 진입 링크(도달성 핵심) — full AppShell(탭바/사이드바)은 deferred(component_map 주석). 시각 e2e=headless 한계.
- ★ HIP-008 **S1~S4 완료** (done게이트 + RAG RPC + 영속 + 홈진입). 운영 적용(Supabase migration/flag ON)·full AppShell·실 e2e = ops/후속.
```

### HIP-009 메타-메타 루프 정식화 (★ meta_factory validation_workflow reflexive 적용)

```
### 배경
회고 34건이 쌓이나 하네스 개선 제안(HIP)으로 전환되는 경로가 죽음 — 본 문서가 HIP-005(Phase 0)
에서 26 phase 동안 동결. self_improvement_loop §11 Open Q5("루프 자체의 회고를 누가/언제")가
미정의라 정확히 그 부분이 죽음. harness-audit는 meta/audits/ 부재 = 한 번도 완주 못 함.
- 관련 audit: 2026-06-05 §4·§5, high H3
- 관련 자산: meta/factory/validation_workflow.md(6검증, harness-audit/eval-run/contract-change/INDEX cross-ref 완비)

### 제안
메타-메타 루프를 손으로 만들지 말고 ★ meta_factory를 reflexive하게 승격(사용자 지침 "정신 살리기"):
- 정기 트리거 명문화: self_improvement_loop §5가 이미 정의한 "분기별 / N phase마다" harness-audit
  완주를 실제 발동(=본 2026-06-05 audit가 첫 발동).
- 엔진: meta/factory/validation_workflow.md의 6검증을 "우리 하네스의 living blueprint"에 정기 실행
  → 별도 평가체계 신설 0(이미 cross-ref). harness-factory Skill(proposal-only)로 진입.
- 누적 회고 → 패턴(meta/patterns.md) → HIP 변환을 그 트리거에 묶기(self_improvement_loop §1.3 재가동).
- 묶여 있던 보류 HIP-003/004/005 결착(승인/반려) — 특히 004는 HIP-006 텔레메트리 후 재평가.

### 영향 분석
- 영향 파일: meta/harness_improvement_proposals(본 문서) / meta/audits/ / self_improvement_loop §5 트리거 / harness-audit SKILL(meta/audits 운영 명문화)
- 영향 절차: harness-audit / harness-factory(validation_workflow reflexive) / meta-retrospective
- back-compat: 없음 (절차 활성화 + 기존 cross-ref 재사용)

### 대안
A. meta_factory를 reflexive 엔진으로 승격(본 제안): dormant 자산을 살림 + 메타-메타 루프 동시 해소.
B. harness-audit를 손으로 정기 실행만: 자산 중복 + meta_factory 계속 dormant.
C. 그대로: 자기개선 루프 영구 정지(반대).

### 우선순위
P1 — H3 직접 해소 + meta_factory 정신 보존(사용자 지침).

### 검증 / 회귀 평가
- 통과 기준: meta/audits/에 정기 audit 2회차 생성 AND HIP-003/004/005 결정 완료 AND
  validation_workflow 6검증이 우리 하네스 blueprint에 1회 실행 기록
- 측정 시점: 다음 정기 트리거 도달 시

### 결정
검토 대기 (2026-06-05 작성). 결정자: 사용자.

### 적용 결과
(적용 후 작성)
```

### HIP-010 유령/동결 정리 (★ meta_factory generation으로 self-map 파생 — 폐기 아닌 자동화)

```
### 배경
손유지 불가가 입증된 자산이 stale/유령으로 잔존: instruction_index(Phase 1 동결, deprecated
plan_options + P-AUX-3 누락), 빈 eval 채널(cost_snapshots/design_reviews/security_reviews/
qa_reports + bug_reports), harness-audit의 lookup_table.yaml 부재 참조, dreammate_current_
harness_blueprint(Phase M0 동결: pytest 339 vs 실제 779).
- 관련 audit: 2026-06-05 §1·§2·§5, high H1 + medium M1·M2 + low L1

### 제안
"되살리기"가 아니라 ★ meta_factory generation으로 "파생/정리":
- self-map 파생: instruction_index를 손유지 대신 meta_factory의 living blueprint에서 파생
  (또는 routers+Skill 자동트리거가 이미 작동하므로 공식 격하). 우선 dreammate_current_harness_
  blueprint를 Phase 26 실측으로 갱신 = living blueprint 첫 갱신.
- 유령 채널: cost_snapshots는 HIP-006 후 실데이터로 부활 / design·security·qa_reports는
  Skill 출력의 실제 위치(회고 §B, meta/security_reviews)로 재지정하거나 폴더 공식 폐기(contract-change).
- 즉시 수정: harness-audit SKILL의 lookup_table.yaml → catalog.yaml.
- 미사용 Skill(cost-review/bug-triage/phase-review): 폐기 vs 활성화를 with-without(validation 검증4) 근거로 결정.

### 영향 분석
- 영향 파일: instruction_index/* / meta/factory/blueprints/dreammate_current_harness_blueprint.md / .claude/skills/harness-audit/SKILL.md / 빈 eval 폴더 README
- 영향 절차: harness-factory(generation/living blueprint) / contract-change(Skill·폴더 폐기 결정)
- back-compat: 격하/폐기는 사용자 결정 게이트 통과 후 (harness-audit 금지사항 정합)

### 대안
A. living blueprint 파생(본 제안): 손유지 부담 제거 + meta_factory 정신 보존.
B. instruction_index 수기 갱신: 또 죽음(이미 입증).
C. 전부 폐기: meta_factory 정신·자산 손실(사용자 지침 위배).

### 우선순위
P2 — HIP-006/009 선행 후 정리가 자연스러움(텔레메트리·living blueprint 인프라 위에서).

### 검증 / 회귀 평가
- 통과 기준: dreammate blueprint가 Phase 26 실측 반영 AND lookup_table 참조 수정 AND
  빈 채널 4종의 처분(부활/재지정/폐기) 결정 기록
- 측정 시점: HIP-006/009 적용 후 정기 audit 2회차

### 결정
검토 대기 (2026-06-05 작성). 결정자: 사용자.

### 적용 결과
(적용 후 작성)
```

---

## 7. 진행 상태 요약 표

| HIP | 제목 | 우선순위 | 결정 | 진행 |
|---|---|---|---|---|
| 001 | 9줄 stub placeholder marker | P0 | 승인 | 적용 완료 |
| 002 | Skill INDEX 갱신 강제 | P0 | 승인 | 적용 완료 |
| 003 | 네이밍 표준 contract | P1 | **반려·흡수** | audit_naming 으로 충족 (2026-06-05 HIP-009) |
| 004 | multi-LLM 트리거 정량 기준 | P1 | **적용 완료** | multi-llm-validation SKILL v1.1.0 반영 (2026-06-05) |
| 005 | Sprint 종료 자동 검증 | P1 | **반려·흡수** | qa-check cat12+sanity 흡수 (2026-06-05) |
| 006 | 텔레메트리 발신기 (agent_io_logs) | P0 | **S1~S3 구현** (운영활성=ops) | 2026-06-05 (pytest 806, gated) |
| 007 | 품질 신호 현실 접지 (critic+human) | P0 | **S1+S2 구현** (S3=human handoff) | 2026-06-05 (pytest 798) |
| 008 | "done" 정의에 운영 도달성 | P1 | **S1~S4 구현** (운영적용=ops) | 2026-06-05 (pytest 802, qa-check v1.3.0) |
| 009 | 메타-메타 루프 = meta_factory reflexive | P1 | 검토 대기 | 2026-06-05 audit 발 |
| 010 | 유령/동결 정리 = self-map 파생 | P2 | 검토 대기 | 2026-06-05 audit 발 |

---

## 8. 새 제안 추가 절차

```
1. 패턴 / 학습에서 출발 점 식별
2. HIP-{NNN} 번호 부여 (마지막 + 1)
3. §1 표준 8 섹션 작성
4. multi-llm-validation 필요한지 §3 기준으로 판단
5. 우선순위 결정 (P0/P1/P2)
6. 본 문서에 추가
7. §7 진행 상태 표 갱신
8. 검토 큐에 추가 (검토자 알림)
```

---

## 9. 측정 지표 (제안서 관리)

```
1. 작성 제안서 수 (분기당)
   - 목표: 평균 5~10건

2. 결정 SLA 준수율
   - P0: 24~72시간 (목표 95%)
   - P1: 30일 (목표 90%)
   - P2: 90일 (목표 80%)

3. 적용 후 회귀 통과율
   - 목표: 95% 이상

4. 반려율
   - 50% 이상이면 제안 품질 낮음 시그널
   - 5% 이하면 제안이 너무 안전 (도전 부족)

5. 보류 누적
   - 동일 제안서 60일 이상 보류 = 강제 재검토
```

---

## 10. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 5+:  제안서 자동 분류 (P0/P1/P2) — 영향 분석 자동.
Phase 11+: 운영자 대시보드에 제안서 상태 시각화.
Phase 21+: AI 기반 제안서 자동 작성 (단 결정은 사람).
연 1회:    오래된 보류 제안서 review + 폐기 / 진행 결정.
```

---

## 11. Open Questions

1. 제안서 번호 (HIP-NNN)가 새 카테고리 추가 시 충돌 가능 — prefix 검토.
2. 보류 무기한 vs 60일 자동 반려 — 정책 결정 필요.
3. multi-llm-validation 필수 조건이 너무 까다로우면 작업 지연.
4. 제안서 적용 후 회귀 측정의 정량 기준 — 영역마다 다름.
5. 적용 결과 섹션의 작성 SLA — 적용 후 14일 이내 등.

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      제안서 8 섹션 표준, 우선순위 (P0/P1/P2), multi-LLM 권장 기준,
                      Phase 0 시드 5건 (HIP-001~005), 진행 상태 표.
v1.1.0 (2026-06-05): harness-audit 최초 완주(meta/audits/2026-06-05.md) 발 — §6.5 신규
                      제안서 5건 (HIP-006~010) append + §7 표 확장. 26 phase 만의 HIP 재가동.
                      핵심: 현실 접지선(텔레메트리/품질/도달성) + meta_factory reflexive 승격.
                      전부 검토 대기 (사용자 결정). HIP-003/004/005 결착 경로를 HIP-009/006에 연결.
```

---

## 2026-06-10 — harness-audit Phase 2 (상세: meta/audits/2026-06-10.md)

PASS (critical 0 / high 0; stub 0 / instruction_index 0 / naming 0 drift). medium 4 proposal — proposal-first, contract-change/사용자 결정 대상:

- **HIP-A: routes.yaml ↔ skill 이중라우팅 정리** — 2-track 명문화 또는 통합(routes.yaml 장식화 중). [contract-change + INDEX]
- **HIP-B: default-off "죽은 게이트" 4 처리** (A7 audit) — `critic_calibration` 활성/측정(가치 高, 88점 함정) · `cross_validation` 의사결정 승격 or sunset(현 logging-only) · `multi_provider_plans` Claude-JSON robustness+provider 안정 선결(A11: 다양성 real but 취약) · `agent_io_log_to_db` 유지. [사용자 결정 + 측정]
- **HIP-C: skill 통합·격하** (11실사용/6잠재/4dead) — eval(design+run)·rag(design+update) 통합 / phase-review·context-compact 격하 / **bug-triage 강제 게이트화**(버그가 절차 우회 중). [contract-change skill]
- **HIP-D: 검토형 skill 산출물 drift** — security-review·design-review가 SKILL.md 의무 산출물 경로 비움 → 요구 완화 or 강제. [contract-change]
- low: rag-update related `knowledge/candidate_knowledge/` = Supabase 테이블 → 경로 표기 정정.

★ 자정작용(완료): `scripts/skill_usage_report.py`(A8, skill_usage 자동집계 졸업) + `BOUNDARIES.md`/`CODEOWNERS`/`check_boundaries.py`(경계 기계화) + (이전) cost_report.py.

---

## 2026-06-21 — HIP-A~D 결착 (project-2 잔여 결정, 사용자 승인)

> 트리거: "studio project-2 이어서" 세션 — project-2(2026-06-09~10)가 남긴 HIP-A~D를 결착.
> 근거: critic 품질 연구 아크(2026-06-21, branch phase-29-agent-ux)의 실측이 HIP-B의 핵심 가정을 갱신함.
> 결정 = 사용자 승인. 런타임 default 변경 0(전부 gated 유지) — 본 섹션은 **결정 기록 + 일부 contract-change**.

### HIP-B — default-off "죽은 게이트" 4개 (결착 ✅)

A11/critic-arc 실측이 HIP-B 작성 시점의 가정("calibration 활성=88점 함정 fix")을 뒤집음 — calibration 단독은 verdict 0건 변경. 따라서 결착을 아래로 갱신:

1. **`critic_calibration_enabled` → RETAIN(폐위 아님), cross-provider judge의 보완으로 co-activate.**
   - 근거: calibration 단독은 점수만 0.35 당기고 verdict 0건 변경(`eval/regression_results/2026-06-21-cross-provider-judge.md`). 진짜 88점 함정 fix = `critic_judge_provider=anthropic`(Phase 31). 단 judge=anthropic 시 calibration preamble가 Claude 채점을 더 엄격하게 만들어 **보완 가치 有** → sunset 하지 않고 judge와 짝으로 활성하는 레버로 유지.
   - 상태: 둘 다 gated default-off/openai 유지(런타임 불변). 활성은 prompt-version-review(major) 시 **쌍으로**.
2. **`cross_validation_enabled` → SUNSET(deprecated).**
   - 근거: orchestrator에 logging-only(Envelope 0 변경, `moa_orchestrator.py`)로 묻혀 의사결정에 반영 안 됨. 그 "다른 provider로 교차검증" 의도는 Phase 31 cross-provider judge(`critic_judge_provider`)가 **실제 verdict 차단으로 정식 구현**함 → 중복. deprecated 표기, 코드 제거는 후속(behavior-preserving이라 급하지 않음).
3. **`multi_provider_plans_enabled` → DEFER(OFF 유지, 문서화).**
   - 근거: A11 다양성 real(pairwise 0.959→0.680)이나 취약(provider 503/JSON robustness). 호출자 0(`run_planning_multi_provider_3` 미배선). 활성 = orchestrator 분기(S2b-2b) + Claude JSON robustness + provider fallback 선결 → 측정으로 product 필요 입증 시 진행. (Phase 31 `_judge_via_anthropic`가 AnthropicAdapter+json_mode를 이미 실행해 일부 de-risk됨.)
4. **`agent_io_log_to_db` → KEEP.** 선택 sub-flag, Supabase 배포 시 토글. 변경 없음.

### HIP-C — skill 통합·격하 (부분 결착 ✅, 격하 보류)

- **실행**: `bug-triage` 강제 게이트화(버그수정 절차 우회 위험 차단) + `eval-design`+`eval-run` 병합 + `rag-design`+`rag-update` 병합. [contract-change(skill), 본 세션 반영]
- **보류**: `phase-review`·`context-compact` 격하 — `skill_usage_report.py` 한계(tool-call=0 ≠ dead; body-injection 사용 미집계)로 신호 부족 → 격하 전 신호 추가 수집. [HOLD]

### HIP-A — routes.yaml ↔ skill 2-track (보류 → 후속)
### HIP-D — 검토형 skill 산출물 drift (보류 → 후속)

- HIP-A/D는 본 세션 미결착(decision-only/contract-change). 후속 세션에서 routes 2-track 명문화 + 산출물 요구 완화 결정.
