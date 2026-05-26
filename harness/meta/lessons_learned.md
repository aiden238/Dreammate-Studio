# lessons_learned.md — 학습 사항

> 위치: `meta/lessons_learned.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `meta/self_improvement_loop.md` (5단계 루프), `meta/patterns.md`
> 참조: `meta/retrospectives/` (학습 시드), `.claude/skills/meta-retrospective/SKILL.md`

---

## 0. 학습 정의

> **학습은 개별 사고를 패턴으로 추출한 것이다.**

본 문서는 시간 누적으로 쌓이는 시스템의 기억이다. 사고 자체는 `meta/retrospectives/`, 패턴은 `meta/patterns.md`, 학습은 본 문서.

```
사고 → 회고 (retrospectives/) → 패턴 (patterns.md) → 학습 (lessons_learned.md)
```

---

## 1. 학습 기록 형식

```
## L-{NNN} {짧은 제목}
- 날짜: YYYY-MM-DD
- 컨텍스트: 어디서 어떤 상황이었는가 (2~3줄)
- 결정: 무엇을 결정했는가
- 결과: 어떻게 됐는가 (성공 / 실패 / 부분 성공)
- 학습: 다음에 무엇을 다르게 할까 (1줄 핵심)
- 분류: technical / design / process / human
- 영향: high / medium / low
- 관련 patterns: P-N (있으면)
- 관련 proposals: HIP-N (있으면)
- 관련 retrospectives: 파일 경로
```

학습 등록 기준:

```
1. retrospectives 작성 후 "다음에 다르게 할 것" 항목 추출
2. patterns에서 5회 이상 반복된 패턴
3. 사용자 또는 AI가 명시적 학습으로 기록 요청
```

---

## 2. 분류 체계

```
technical: 기술적 학습 (LLM / RAG / DB / 인프라)
design:    설계 학습 (UX / 아키텍처 / 데이터 모델)
process:   프로세스 학습 (Skill / 절차 / 검토)
human:     인간 학습 (실수 / 협업 / 의사소통)
```

각 분류별 우선순위:

```
technical → 다음 비슷한 구현 시 직접 적용
design    → 다음 Phase 진입 시 review
process   → Skill 갱신 / 절차 강화
human     → 일하는 방식 자체 변경 (큰 영향)
```

---

## 3. Phase 0 학습 시드 (5건)

본 문서는 Phase 0 진행 중 발견된 학습으로 시작.

### L-001 9줄 stub 누적은 설계 부채

```
- 날짜: 2026-05-26
- 컨텍스트: GPT 골격 도입 시점에 docs/contracts/ 16개 파일이 9줄 stub.
- 결정: Phase 0 진행 중 모두 보강하기로 결정.
- 결과: Sprint S3에서 9 deep + 11 placeholder marker 적용 (정확한 보강).
- 학습: 9줄 stub은 "나중에"가 아니라 즉시 placeholder marker로 명시.
       placeholder marker가 있으면 진행 가능, 없으면 작업 막힘.
- 분류: design
- 영향: high
- 관련 patterns: P-001 (9줄 stub 누적 경향)
- 관련 proposals: HIP-001 (placeholder marker 표준화)
- 관련 retrospectives: meta/retrospectives/(미작성, S5-3에서 작성 예정)
```

### L-002 Skill 25 → 20 통합은 description 키워드 충돌이 우선

```
- 날짜: 2026-05-26
- 컨텍스트: Sprint S2에서 GPT 골격의 15 Skill + 우리 14 Skill = 25개 폭증.
- 결정: 5개 폐기 + 우리 14 유지 + GPT origin 6 재작성 = 20개로 통합.
- 결과: description 키워드 충돌 0건 + 자동 트리거 정상 동작.
- 학습: Skill 통합 시 본문 내용보다 description 키워드 충돌이 더 위험.
       같은 키워드가 두 Skill에 있으면 자동 트리거 실패.
- 분류: process
- 영향: high
- 관련 patterns: P-003 (Skill 키워드 충돌)
- 관련 proposals: HIP-002 (Skill INDEX 갱신 강제)
```

### L-003 Planner → Planning 명명 통일 (8 파일 영향)

```
- 날짜: 2026-05-26
- 컨텍스트: GPT 골격은 "Planner", 우리 deep contract는 "Planning" 혼재.
- 결정: Sprint S4-3에서 "Planning"으로 통일.
- 결과: 8 파일에서 rename 적용. 일관성 회복.
- 학습: 명명 충돌은 첫 Sprint에 발견하고 즉시 통일.
       나중에 통일하면 영향 파일이 기하급수적 증가.
       검색 키워드 매칭 등 자동 분석에서 누락 발생.
- 분류: technical + design
- 영향: medium
- 관련 patterns: P-002 (명명 충돌)
- 관련 proposals: HIP-003 (네이밍 표준 contract 추가 검토)
```

### L-004 multi-LLM 분담은 시간 절약보다 검증 가치

```
- 날짜: 2026-05-26
- 컨텍스트: Claude Code (Anthropic) / Codex (GPT) / Copilot Code 분담.
- 결정: 큰 결정은 multi-llm-validation, 일상 작업은 단일 모델.
- 결과: 큰 결정 (Skill 통합 / 아키텍처) 시 multi-LLM이 시간은 더 들지만
       오류 발견율 높음. 단일 모델 단독 결정은 위험.
- 학습: multi-LLM은 시간 절약 도구가 아니라 단일 모델 편향 감소 도구.
       선택은 작업 크기 기준 (큰 결정 = 다중 / 일상 = 단일).
- 분류: process + human
- 영향: high
- 관련 patterns: P-004 (단일 모델 편향)
- 관련 proposals: HIP-004 (multi-llm-validation 트리거 정량 기준)
```

### L-005 PROJECT_STATE 갱신 의무가 정합성 핵심

```
- 날짜: 2026-05-26
- 컨텍스트: Sprint마다 migration_progress 필드 갱신 의무화.
- 결정: 매 Sprint 종료 시 PROJECT_STATE.md 갱신 + sanity script.
- 결과: 부분 완료 상태가 명확히 추적됨. 다음 세션 진입 시 컨텍스트 회복 빠름.
- 학습: 큰 문서일수록 "현재 상태" 단일 source of truth가 중요.
       PROJECT_STATE.md가 그 역할. 갱신 누락 = 전체 정합성 흔들림.
- 분류: process
- 영향: high
- 관련 patterns: 없음 (단일 결정)
- 관련 proposals: HIP-005 (Sprint 종료 자동 PROJECT_STATE 검증)
```

---

## 4. 학습 활용 (다음 Phase 진입 시)

본 문서는 정적 기록이 아니라 **다음 Phase 진입 시 review 의무**.

```
Phase X 진입 시 review:

1. phase-start Skill 호출
2. PROJECT_STATE.md 확인
3. 본 lessons_learned.md 중 영향 = high 항목 review
4. 본 Phase에 적용 가능한 학습 추출
5. Phase 작업 시 학습 적용

예시 (Phase 1 진입 시):
- L-001: contract 작성 시 placeholder marker 강제 적용
- L-002: 새 Skill 추가 시 description 키워드 충돌 검사
- L-005: PROJECT_STATE 갱신을 Sprint 종료 절차에 포함
```

---

## 5. meta-retrospective Skill의 출력 통합

retrospective 작성 시 "다음에 다르게 할 것" 섹션이 본 문서로 자동 통합.

```
meta-retrospective Skill 출력:
- meta/retrospectives/YYYY-MM-DD-{topic}.md (개별 회고)
- 그 중 "lesson_learned" 섹션 → meta/lessons_learned.md로 추가

통합 절차:
1. retrospective 작성 완료
2. lesson_learned 섹션을 본 문서 형식으로 변환
3. L-{NNN} 번호 부여 (마지막 + 1)
4. 관련 patterns / proposals 링크
5. PROJECT_STATE.md "최근 학습" 섹션 갱신 (선택)
```

→ `.claude/skills/meta-retrospective/SKILL.md`

---

## 6. 학습 우선순위 / 적용 빈도

```
적용 빈도 (Phase별):
- 영향 high: 모든 Phase 진입 시 필수 review
- 영향 medium: 분기별 review
- 영향 low: 연간 1회 review

학습 우선순위 (적용 시 어떤 것부터):
- technical: 다음 비슷한 코드 작업 시 즉시
- design: 다음 Phase 설계 시 review
- process: 매 Sprint 시작 시 review (절차 영향)
- human: 매 회고 시 review (행동 변화 영향)
```

---

## 7. 학습 → 변경 사이클

학습은 결국 시스템 변화로 이어져야 의미가 있다.

```
학습 등록 → 변경 후보 식별 → 제안서 작성 → 검토 → 반영 → 회귀 측정

예시 (L-001):
1. 학습: "9줄 stub은 즉시 placeholder marker로"
2. 변경 후보: docs/contracts/template에 placeholder marker 표준 추가
3. 제안서: HIP-001 작성
4. 검토: 사용자 승인
5. 반영: Sprint S3에서 16 파일에 적용
6. 회귀: harness-audit에서 9줄 stub 잔존 0건 확인

학습 → 반영 까지 시간 (목표):
- high 영향: 7일 이내
- medium 영향: 30일 이내
- low 영향: 90일 이내 또는 다음 분기
```

---

## 8. 학습 갱신 vs 새 학습

```
새 학습 등록 (L-{N+1}):
- 처음 발견된 패턴
- 기존 학습과 다른 컨텍스트

기존 학습 갱신 (L-{N} 갱신):
- 같은 학습의 추가 증거 (영향 변경)
- 학습 적용 결과의 후속 관찰

기존 학습 폐기:
- 환경이 바뀌어 더 이상 유효하지 않음
- 단 폐기 시에도 기록 유지 (history)
- archived: true 표시
```

---

## 9. 측정 지표

```
1. 학습 누적 빈도
   - 분기당 평균 3~5건 등록 정상.
   - 0건이면 회고가 부족, 10건 이상이면 환경 불안정.

2. 학습 → 반영 사이클 시간
   - high 영향: 7일 이내 목표
   - 평균: 30일 이내 목표

3. 학습 재발 빈도
   - 같은 학습이 30일 내 재등록 = 반영 실패 시그널

4. Phase 진입 시 학습 review 준수율
   - phase-start Skill에서 review 단계 통과율
   - 목표: 100%

5. 분류별 분포
   - 분류 한쪽 치우침 = 다른 영역 모니터링 강화 필요
```

---

## 10. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 5+:  학습 → 반영 자동화 (HIP 자동 작성).
Phase 11+: 운영자 대시보드에 학습 진행 시각화.
Phase 21+: AI 기반 학습 추출 (retrospectives → lessons 자동 변환).
연 1회:    전체 학습 review + 폐기 후보 식별.
```

---

## 11. Open Questions

1. 학습 등록 기준 (5회 반복)이 너무 늦은지 — 3회로 조정 가능성.
2. 학습이 너무 추상적이면 적용 어려움 — 구체성 기준 필요.
3. 학습 폐기 후 history는 영구 유지 vs 분기별 압축.
4. 분류 체계 (4개)가 충분한지 — security 별도 추가 필요성.
5. AI가 자동 추출한 학습 vs 사람 명시 학습 가중치 차이 두어야 하는지.

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      학습 형식, 분류 체계, Phase 0 시드 5건,
                      학습 활용 / meta-retrospective 통합, 측정 지표.
```
