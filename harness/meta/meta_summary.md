# meta_summary.md — 메타 하네스 요약 (라우터)

> 위치: `meta/meta_summary.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: meta/ 폴더 전체 + .claude/skills/meta-retrospective + .claude/skills/harness-audit

---

## 0. 메타 하네스 정의

> **메타 하네스 = 하네스를 개선하는 하네스다.**

이 프로젝트는 두 layer로 동작한다.

```
Layer 1 (영상기획 AI 에이전트): 사용자에게 영상기획 결과를 제공하는 시스템.
Layer 2 (메타 하네스):           Layer 1이 시간이 갈수록 더 좋아지게 만드는 시스템.
```

Layer 2 (이 문서가 다루는 영역)는 다음 절차로 작동한다.

```
회고 → 패턴 추출 → 학습 → 개선 제안 → 검토 / 승인 → 반영 → 회귀 측정 → 다음 회고
```

---

## 1. 메타 하네스 파일 인덱스

본 폴더(`meta/`)의 모든 파일과 한 줄 요약.

```
self_improvement_loop.md           5단계 루프 (회고 → 패턴 → 제안 → 검토 → 반영) 정의.
guardrails.md                       3 layer (INPUT/PROCESS/OUTPUT) 가드레일.
human_review_policy.md              자동 vs 인간 검토 결정 기준 + SLA.
rollback_policy.md                  4 대상 (prompt/contract/skill/code) 롤백 절차 + 트리거.
error_taxonomy.md                   7 카테고리 에러 메타 분석 (빈도 / 심각도 / 회복).
lessons_learned.md                  반복 패턴에서 추출된 학습 (Phase 진입 시 review 의무).
harness_improvement_proposals.md    하네스 개선 제안 (HIP-NNN, P0/P1/P2 우선순위).
patterns.md                         시간 누적 패턴 (5회 이상 반복 시 등록).
security_metrics.md                 보안 측정 누적 (Phase 7+).
skill_usage_log.md                  Skill 사용 빈도 (Phase 7+).
meta_summary.md (이 문서)           메타 하네스 라우터 + 상호 관계 + 사용 흐름.

서브 폴더:
handoffs/         세션 간 인계 (context-compact 시 사용).
proposals/        제안서 임시 저장 (활성 작업 중).
retrospectives/   회고 (Phase 종료 / 큰 사고 시).
validations/      multi-llm-validation 결과 저장.
```

---

## 2. 파일 간 상호 관계

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   retrospectives/  ─────→  patterns.md  ─────→  lessons_     │
│        ↑                                          learned.md │
│        │                                          │          │
│        │                                          ↓          │
│   meta-retrospective                          (Phase 진입    │
│   Skill                                        시 review)    │
│        │                                          │          │
│        │                                          ↓          │
│        └─────────────────────→  harness_improvement_         │
│                                  proposals.md                │
│                                          │                   │
│                                          ↓                   │
│                                  검토 (multi-llm-validation) │
│                                          │                   │
│                                          ↓                   │
│                                  contract-change Skill       │
│                                          │                   │
│                                          ↓                   │
│                                  적용 → 회귀 측정            │
│                                          │                   │
│                                          ↓                   │
│   ←─────────  retrospectives/ 신규 회고  ──────────          │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

각 파일의 역할:

```
retrospectives/        개별 사고 / Phase 종료 회고 (raw 기록)
patterns.md            3+ 회 반복 패턴 (시간 누적)
lessons_learned.md     5+ 회 반복 패턴에서 추출된 학습 (Phase review 의무)
harness_improvement_proposals.md  학습 → 변경 제안 (P0/P1/P2)
guardrails.md          시스템 안전장치 (가드레일 정의)
rollback_policy.md     변경이 잘못됐을 때 되돌리는 절차
human_review_policy.md 자동 vs 인간 검토 결정
error_taxonomy.md      에러 분류 + 메타 분석
security_metrics.md    보안 측정 누적
skill_usage_log.md     Skill 사용 통계
```

---

## 3. 사용 흐름 (Phase 종료 시점 예시)

```
Step 1: Phase 종료 직전
  → phase-complete Skill 호출
  → acceptance 검증 + archive 이동

Step 2: Phase 종료 직후
  → meta-retrospective Skill 호출
  → retrospectives/YYYY-MM-DD-phase-N.md 작성
  → 5단계 분석 (컨텍스트 / 결정 / 결과 / 학습 / 다음 조치)

Step 3: 회고 → 패턴
  → 신규 패턴 발견 시 patterns.md 추가
  → 5회 이상 반복된 패턴은 lessons_learned.md로 승격

Step 4: 학습 → 제안
  → 영향 high 학습은 즉시 HIP 작성
  → harness_improvement_proposals.md 신규 항목

Step 5: 검토
  → multi-llm-validation 필요한지 §HIP-004 정량 기준 검토
  → 사용자 승인 / 반려 / 보류 / 조건부

Step 6: 반영
  → contract-change Skill 절차
  → 적용 + 회귀 측정

Step 7: 다음 Phase 진입
  → phase-start Skill
  → lessons_learned.md 중 영향 high review
  → 본 Phase에 적용 가능한 학습 추출
```

---

## 4. 메타 하네스의 트리거

본 메타 시스템은 다음 시점에 작동.

```
주기 트리거:
- Phase 종료 시 (필수)
- 분기별 (권장)
- 연간 (전체 review)

이벤트 트리거:
- 큰 사고 (보안 / 비용 / 데이터 노출)
- 반복 실패 패턴 발견
- Sprint 종료 시 sanity script
- 사용자 명시 요청

수동 트리거:
- "회고하고 싶다" / "메타 개선" 키워드
- 큰 결정 직전 multi-llm-validation
- Phase 진입 시 phase-start
```

---

## 5. Skill 매핑

메타 하네스 작업에 사용되는 Skill.

```
meta-retrospective       회고 작성 / 패턴 추출 / 제안 생성
harness-audit            구조 점검 / 깨진 참조 / placeholder 누락
multi-llm-validation     큰 결정의 다중 모델 교차 검증
contract-change          변경의 절차 통과 강제
phase-complete           Phase 종료 정리 + meta-retrospective 호출
phase-start              Phase 진입 시 lessons review 의무
prompt-version-review    prompt 변경의 회귀 / 롤백
```

→ `.claude/skills/INDEX.md`, `instruction_index/priority_rules.md`

---

## 6. 메타 측정 (전체 시스템 건강도)

본 폴더의 작동 효과를 측정하는 통합 지표.

```
1. 회고 작성 빈도 (Phase 종료마다 + 분기)
   - 목표: 작성률 95% 이상

2. 패턴 → 학습 전환 빈도
   - patterns.md 신규 등록 → lessons_learned.md 승격 사이클
   - 목표: 평균 30일 이내

3. 학습 → 제안 → 적용 사이클 시간
   - high 영향: 14일 이내
   - 평균: 60일 이내

4. 반복 실패 감소 추세
   - 같은 패턴 30일 내 재발 = 적용 실패
   - 목표: 재발률 10% 이하

5. 자동화 비율 (Skill 자동 트리거 / 수동 호출)
   - 목표: 80% 이상 자동 트리거

6. SLA 준수율 (제안서 결정)
   - P0: 95%
   - P1: 90%
   - P2: 80%
```

---

## 7. 메타 하네스 자체의 회고 (메타-메타)

```
1년 1회 본 폴더 자체의 회고:

- 본 시스템이 작동하는가 (효과)
- 본 시스템이 부담스럽지 않은가 (효율)
- 본 시스템이 핵심을 놓치고 있지 않은가 (적용 범위)
- 본 시스템 자체에 누락된 영역은 없는가 (gap)

방법:
- meta-retrospective Skill의 "system mode"로 호출
- 1년 누적 patterns / proposals / lessons 통계 분석
- multi-llm-validation으로 외부 시각 추가
- 결과는 본 문서 §11 갱신
```

---

## 8. 사용 시나리오 (3가지)

### 시나리오 A: Phase 0 종료 시

```
1. phase-complete Skill (acceptance 검증)
2. meta-retrospective Skill (Phase 0 회고)
3. Phase 0 학습 5건 → lessons_learned.md L-001~L-005
4. HIP-001~005 진행 결정 검토
5. Phase 1 진입 (phase-start Skill)
6. Phase 1에서 학습 review (의무)
```

### 시나리오 B: 보안 사고 직후

```
1. 즉시 롤백 (rollback_policy.md §3.1)
2. 24시간 내 retrospective 작성
3. 7일 내 patterns 갱신
4. 14일 내 HIP 신규 제안 (보안 강화)
5. multi-llm-validation 권장
6. 적용 + 회귀 측정 + 사후 모니터링 30일
```

### 시나리오 C: 분기별 정기 점검

```
1. harness-audit Skill 실행
2. 신규 issue 발견 → patterns.md 누적
3. meta-retrospective 분기 모드
4. 누적 proposals review (보류된 것 재검토)
5. 다음 분기 우선순위 결정
6. PROJECT_STATE.md "최근 변경" 갱신
```

---

## 9. 자주 묻는 질문 (FAQ)

```
Q: 회고와 학습의 차이?
A: 회고는 raw 기록 (retrospectives/). 학습은 5+ 회 반복에서 추출된 핵심 (lessons_learned.md).
   회고는 매번, 학습은 가끔.

Q: 패턴과 학습의 차이?
A: 패턴은 3+ 회 반복 (patterns.md). 학습은 패턴에서 "다음에 다르게" 추출된 것 (lessons_learned.md).
   패턴은 관찰, 학습은 결심.

Q: 제안서와 contract 변경의 차이?
A: 제안서는 "바꾸자는 안" (harness_improvement_proposals.md).
   contract 변경은 제안서가 승인된 후 실제 contract 파일 수정.

Q: 가드레일과 롤백의 차이?
A: 가드레일은 사고 예방 (guardrails.md).
   롤백은 사고 발생 후 회복 (rollback_policy.md).

Q: 인간 검토와 multi-LLM의 차이?
A: 인간 검토는 사람이 결정 (human_review_policy.md).
   multi-LLM은 여러 AI 모델의 합의 (multi-llm-validation Skill).
   둘 다 가능 (큰 결정은 multi-LLM → 인간 최종).
```

---

## 10. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 5+:  본 라우터의 시각화 (Mermaid 다이어그램 추가).
Phase 11+: 운영자 대시보드에서 본 폴더 진행 시각화.
Phase 21+: AI 기반 자동 패턴 / 학습 / 제안 생성 (단 결정은 사람).
연 1회:    §7 메타-메타 회고.
```

---

## 11. Open Questions

1. retrospectives → patterns → lessons 자동 변환 가능성 — 현재 수동.
2. 본 폴더의 파일 수가 11개. 더 추가될지 통합될지 — 1년 후 재검토.
3. 메타 하네스 자체의 회고 (§7)를 언제 처음 할지 — Phase 10 종료 시.
4. 사용자 1명 운영 시 본 시스템이 너무 무거운지 — 경량 mode 옵션.
5. 본 라우터가 CLAUDE.md / AGENTS.md / .claude/skills/INDEX.md와 중복 영역.

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      파일 인덱스 (11개), 상호 관계 다이어그램, 사용 흐름 7 단계,
                      트리거, Skill 매핑, 측정, 3 시나리오, FAQ.
```
