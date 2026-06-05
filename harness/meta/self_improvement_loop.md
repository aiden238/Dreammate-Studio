# self_improvement_loop.md — 자기개선 루프

> 위치: `meta/self_improvement_loop.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `meta/meta_summary.md` (메타 라우터), `meta/patterns.md`, `meta/lessons_learned.md`
> 참조: `.claude/skills/meta-retrospective/SKILL.md`, `.claude/skills/harness-audit/SKILL.md`

---

## 0. 자기개선 루프 정의

> **자가개선은 자동 수정이 아니다.** 항상 회고 → 패턴 → 제안 → 검토 → 승인 → 반영의 절차를 따른다.

목적: 하네스(이 프로젝트의 자기 정의)와 운영 절차를 시간이 갈수록 개선한다.
원칙: AI가 제안하고 사용자가 결정한다. 자동 적용 금지.

---

## 1. 5단계 루프

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ 1. 회고      │ →  │ 2. 패턴 추출 │ →  │ 3. 제안 생성 │
└──────────────┘    └──────────────┘    └──────────────┘
                                                  │
┌──────────────┐    ┌──────────────┐              ▼
│ 5. 반영      │ ←  │ 4. 검토 승인 │ ←  ────────────
└──────────────┘    └──────────────┘
```

### 1.1 회고 (Retrospective)

```
Skill:    meta-retrospective
입력:     Phase 종료 / 큰 사고 / 반복 실패 발견
산출물:   meta/retrospectives/YYYY-MM-DD-{topic}.md
포함:     무엇이 잘 됐는지 / 무엇이 안 됐는지 / 왜 / 다음에 무엇을
빈도:     Phase 종료 시 (필수) + 분기별 (권장) + 사고 직후 (즉시)
```

### 1.2 패턴 추출 (Pattern Mining)

```
입력:     누적된 retrospectives + meta/error_taxonomy.md + agent_io_logs
산출물:   meta/patterns.md (반복 패턴 기록)
판단 기준: 3회 이상 반복되면 패턴으로 등록
유형:
- 기술적 패턴 (예: "LLM JSON parse 실패가 Critic에서 자주 발생")
- 설계 패턴 (예: "9줄 stub이 점점 쌓이는 경향")
- 프로세스 패턴 (예: "Phase 진입 시 PROJECT_STATE 확인 누락")
- 인간 패턴 (예: "큰 변경 시 multi-llm-validation 빼먹는 경향")
```

### 1.3 제안 생성 (Improvement Proposal)

```
Skill:    meta-retrospective (제안 생성) → harness-audit (구조 점검)
입력:     meta/patterns.md + meta/lessons_learned.md
산출물:   meta/harness_improvement_proposals.md 신규 항목
형식:     배경 / 제안 / 영향 분석 / 대안 / 결정 후보 (P0/P1/P2)
```

### 1.4 검토 / 승인 (Review)

```
검토자:   사용자 (최종 결정자)
큰 변경:  multi-llm-validation Skill 권장 (Claude / GPT / Gemini 교차 검증)
결정 결과: 승인 / 반려 / 보류 / 조건부 승인
승인 후:  meta/harness_improvement_proposals.md의 상태 갱신
```

### 1.5 반영 (Apply)

```
실행자:   AI (Claude Code 등) 또는 사용자
절차:     contract-change Skill (절차 통과)
적용 후:  PROJECT_STATE.md 갱신 + harness-audit 재실행
회귀 평가: 적용 결과를 다음 회고에서 검증 → 1단계 루프 재진입
```

---

## 2. 발견 패턴 → meta/patterns.md 누적

`meta/patterns.md`는 본 루프의 핵심 데이터 저장소.

```
파일 형식:
## P-{NNN} 패턴명
- 발견 횟수: N
- 첫 관측: YYYY-MM-DD
- 마지막 관측: YYYY-MM-DD
- 카테고리: technical / design / process / human
- 영향: high / medium / low
- 설명: 무엇이 반복되는가
- 가설: 왜 반복되는가
- 제안: 어떻게 해결할까 (또는 "제안 작성 중")
- 관련 proposals: P-N (있으면 링크)
```

예시 (시드):

```
## P-001 9줄 stub 누적 경향
- 발견 횟수: 16건 (Phase 0 발견)
- 카테고리: design
- 영향: high
- 설명: 새 contract 파일 작성 시 시간 부족으로 9줄 stub 상태 유지.
- 가설: 작업 우선순위에서 후순위로 밀림.
- 제안: 9줄 stub은 placeholder marker 표준 형식 강제 (Phase 0 S3 적용).
```

---

## 3. 개선 제안 → meta/harness_improvement_proposals.md

상세 형식은 `meta/harness_improvement_proposals.md` §1.

```
제안서 골격:
- 제안 번호: HIP-{NNN}
- 우선순위: P0 (즉시) / P1 (다음 Phase) / P2 (장기)
- 제안자: AI (Claude/GPT/Gemini) 또는 사용자
- 배경: 어떤 패턴/문제에서 출발했는가
- 제안 내용: 무엇을 바꾸는가
- 영향 분석: 어디에 영향 가는가 (파일 / 절차 / 사용자)
- 대안: 다른 옵션은 무엇이 있는가
- 결정: 승인 / 반려 / 보류
- 적용 결과: (적용 후 작성) 효과 / 부작용
```

---

## 4. 학습 → meta/lessons_learned.md

상세 형식은 `meta/lessons_learned.md` §1.

```
학습 형식:
## L-{NNN} {제목}
- 날짜: YYYY-MM-DD
- 컨텍스트: 어디서 어떤 상황이었는가
- 결정: 무엇을 결정했는가
- 결과: 어떻게 됐는가
- 학습: 다음에 무엇을 다르게 할까
- 분류: technical / design / process / human
- 관련 patterns: P-N
- 관련 proposals: HIP-N
```

---

## 5. 주기 / 트리거

본 루프는 다음 시점에 진입한다.

```
트리거 1: Phase 종료 시 (필수)
  → phase-complete Skill 직후 meta-retrospective 자동 호출
  → 1단계 회고부터 시작

트리거 2: 분기별 (권장)
  → 3개월마다 누적 retrospectives + patterns 검토
  → harness-audit Skill로 구조 점검 + 새 patterns 발견

트리거 3: 큰 사고 직후 (즉시)
  → 데이터 노출 / 비용 폭주 / Golden Set 회귀 실패 등
  → 24시간 내 회고 + 7일 내 제안

트리거 4: 반복 실패 패턴 발견 시
  → patterns.md에 5회 이상 누적된 패턴 발견 시
  → 자동으로 1단계 회고 + 3단계 제안 생성

트리거 5: 사용자 요청
  → "회고하고 싶다" / "메타 개선해줘" 등 키워드
```

---

## 5.1 메타-메타 루프 — "루프 자체의 점검" (HIP-009, 2026-06-05)

> §11 Open Q5("본 루프 자체의 회고를 누가/언제") 해소. 회고(1단계)는 매 phase 살아있으나
> **하네스 자신**의 개선(3단계 HIP)은 Phase 0 이후 동결됐었다(`meta/audits/2026-06-05.md` §4).
> 본 절이 그 메타-메타 점검의 **주기·엔진·산출**을 고정한다.

```
주기(트리거):
- 매 5 product phase 종료마다 (정기) + 분기 1회 + 사용자 "하네스 점검" 요청
- staleness 신호 누적(Skill 장기 미트리거 / contract·index 미갱신) 시 즉시

엔진:
- harness-audit Skill 완주 → meta/audits/{date}.md  (★ 산출물 필수 — 부재 시 "미완주")
- ★ meta/factory validation_workflow 6검증을 우리 하네스 living blueprint
  (meta/factory/blueprints/dreammate_current_harness_blueprint.md)에 reflexive 실행
  → meta/factory/outputs/improvement_reports/   (meta_factory = 폐기 아닌 자기유지 엔진 승격)

산출 → 반영:
- 발견 → HIP 변환(meta/harness_improvement_proposals.md) → 본 5단계 루프 1단계 재진입
- 보류 HIP 60일+ → 강제 재검토 (§8 측정지표 정합)
```

---

## 6. Skill 통합

본 루프는 다음 Skill을 직접 호출한다.

```
1단계: meta-retrospective Skill
       - retrospective 작성 표준 절차 강제
       - 출력: meta/retrospectives/YYYY-MM-DD-*.md

2단계: harness-audit Skill (선택)
       - 정기 구조 감사 (Phase 0/10/20)
       - patterns 발견

3단계: meta-retrospective Skill (제안 모드)
       - 패턴 → 제안 변환
       - 출력: meta/harness_improvement_proposals.md

4단계: multi-llm-validation Skill (큰 결정만)
       - Claude / GPT / Gemini 교차 검증
       - 출력: meta/validations/YYYY-MM-DD-*.md

5단계: contract-change Skill (반영 시)
       - 절차 통과 강제
       - 출력: docs/contract_changes/ 또는 meta/proposals/
```

→ `.claude/skills/INDEX.md` 우선순위 표 정합

---

## 7. 자동 수정 금지 원칙

다음은 본 루프에서 **반드시 금지**.

```
✗ AI가 retrospective 결과만 보고 직접 contract / skill 변경
✗ patterns 누적만 보고 자동 proposal 적용
✗ 사용자 승인 없이 PROJECT_STATE.md 갱신
✗ multi-llm-validation 없이 큰 결정 (가격 / 보안 / 영구 제외) 변경
```

예외: AI 산출물(retrospective / patterns / proposals 작성 자체)은 사람 승인 없이 가능.
이는 "쓰는 것"이지 "적용하는 것"이 아니기 때문.

---

## 8. 측정 지표 (루프 효과 측정)

```
1. retrospectives 작성 빈도
   - 목표: Phase 종료마다 1건 + 분기 1건 (연 4건)

2. patterns 발견 빈도
   - 누적 추세: 분기당 평균 3~5건 신규 등록 정상.

3. proposals 처리율
   - 작성된 proposals 중 승인/반려/보류 결정 비율.
   - 목표: 30일 내 결정 90%, 보류 10% 이하.

4. 학습 → 변경 → 회귀 통과 사이클 시간
   - 학습 → 제안: 7일 이내
   - 제안 → 결정: 30일 이내
   - 결정 → 적용: 14일 이내
   - 적용 → 회귀 통과: 7일 이내

5. 반복 실패 감소 추세
   - 같은 패턴이 2회 이상 재발 시 루프 실패.
   - 분기별 재발율 측정.
```

---

## 9. Phase 0 시드 자료

본 루프는 Phase 0 진행 중 발견한 다음 사례에서 시작.

```
시드 1: 9줄 stub 누적 (16건)
  → patterns P-001 등록 → placeholder marker 표준 적용

시드 2: Skill 25개 폭증 → 통합 필요
  → proposals HIP-001 → Skill 20개 통합 (Sprint S2)

시드 3: GPT 골격과 우리 deep 콘텐츠 간 명명 불일치 (Planner vs Planning)
  → patterns P-002 → Sprint S4-3에서 통일

시드 4: docs/contracts/ 9줄 stub과 깊은 contract 혼재
  → proposals HIP-002 → 8 deep + 11 placeholder (Sprint S3)
```

→ 자세한 시드 학습은 `meta/lessons_learned.md` 참조

---

## 10. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 5+:  본 루프의 자동화 가능 부분 식별 (patterns 자동 발견 등).
Phase 11+: 운영자 대시보드에 본 루프 진행 상태 시각화.
Phase 21+: AI 기반 자동 proposal 작성 (Claude 등으로) — 단 승인은 여전히 사람.
```

---

## 11. Open Questions

1. patterns 발견의 임계 (3회 / 5회)가 적절한지 — 데이터 누적 후 조정.
2. 큰 변경의 정의 (multi-llm-validation 필수 임계) — 비용 영향 X원 이상 등 정량 기준 필요.
3. retrospectives의 표준 형식이 너무 무거우면 작성률 떨어짐 — light template 옵션.
4. 자동 수정 금지 원칙이 반대로 적용 지연을 일으킬 위험 — 긴급 patch 절차 별도 정의 필요.
5. 본 루프 자체의 회고를 누가/언제 하는지 — 메타-메타 루프 정의. → ★ **HIP-009 해소** (2026-06-05, §5.1): harness-audit 정기 트리거 + meta/factory validation_workflow reflexive + meta/audits/.

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      5단계 루프, 5 트리거, Skill 통합, 측정 지표,
                      Phase 0 시드 자료 4개.
v1.1.0 (2026-06-05 HIP-009 S1): §5.1 메타-메타 루프(루프 자체 점검) cadence 추가 —
                      harness-audit 정기 + meta/factory validation_workflow reflexive +
                      meta/audits/. §11 Open Q5 해소.
```
