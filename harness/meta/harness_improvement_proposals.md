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
```

---

## 7. 진행 상태 요약 표

| HIP | 제목 | 우선순위 | 결정 | 진행 |
|---|---|---|---|---|
| 001 | 9줄 stub placeholder marker | P0 | 승인 | 적용 완료 |
| 002 | Skill INDEX 갱신 강제 | P0 | 승인 | 적용 완료 |
| 003 | 네이밍 표준 contract | P1 | 보류 | Phase 1 |
| 004 | multi-LLM 트리거 정량 기준 | P1 | 보류 | Phase 5+ |
| 005 | Sprint 종료 자동 검증 | P1 | 보류 | Sprint S5-3 |

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
```
