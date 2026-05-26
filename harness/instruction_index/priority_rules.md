# priority_rules.md — Skill / 문서 우선순위 규칙

> 위치: `instruction_index/priority_rules.md`
> 상태: Phase 0 Sprint S5 deep 작성
> 참조: `CLAUDE.md`, `AGENTS.md`, `.claude/skills/INDEX.md`

---

## 0. 본 문서의 위치

본 문서는 **Skill 충돌 시 우선순위**와 **문서 참조 시 우선순위**를 정형화한다.
CLAUDE.md / AGENTS.md의 우선순위 표를 단일 진실 소스로 통합한다.

---

## 1. Skill 우선순위 (충돌 시)

```
context-compact        > 다른 모든 Skill           # 컨텍스트 부족은 항상 최우선
contract-change        > 다른 절차 Skill           # contract 변경은 항상 절차 통과
multi-llm-validation   > 단일 검토 Skill           # 큰 결정은 다중 검증 우선
phase-start            > 다른 절차 Skill           # Phase 컨텍스트 확보 먼저
phase-complete         > meta-retrospective       # 종료 정리 후 회고
harness-audit          > 일상 운영 Skill           # 정기 감사 결과는 절차에 반영
```

### 1.1 충돌 해결 알고리즘

```
1. 트리거된 Skill 목록 수집 (description 키워드 매칭)
2. 위 우선순위 표 적용
3. 동일 우선순위 → INDEX.md 순서대로
4. 모두 동일 → 사용자에게 선택지 제공
```

### 1.2 우선순위 예시

**예시 A**: 컨텍스트 90% 도달 + Phase 종료 시점
- 후보: `context-compact`, `phase-complete`
- 결정: **context-compact 먼저** (handoff 보존) → 새 세션에서 phase-complete

**예시 B**: prompt 변경 + contract 변경 동시 필요
- 후보: `prompt-version-review`, `contract-change`
- 결정: **contract-change 먼저** (contract 안에 prompt 정의 포함)

**예시 C**: 큰 아키텍처 변경 + 단일 모델 검토
- 후보: `ai-architecture-review`, `multi-llm-validation`
- 결정: **multi-llm-validation 먼저** (단일 모델 편향 방지)

---

## 2. 문서 참조 우선순위

문서 간 정보 충돌 시 참조 우선순위:

```
docs/contracts/         # 모든 결정의 정본
  > phases/active/      # 현재 Phase 컨텍스트
  > PROJECT_STATE.md    # 현재 작업 위치
  > product/            # 제품 정의
  > ai_system/          # AI 구조
  > knowledge/          # RAG 지식
  > eval/               # 평가 체계
  > meta/               # 메타 / 회고
  > phases/archive/     # 아카이브 (기본 참조 금지)
```

### 2.1 contracts 절대 우선

- contract는 **단일 진실 소스 (single source of truth)**
- 다른 문서가 contract와 모순 시 → contract 우선
- contract 변경은 항상 `contract-change` Skill 절차

### 2.2 phases/archive/ 기본 미참조

- 완료된 Phase의 문서는 archive로 이동
- 일상 작업에서 archive는 참조하지 않음
- 회고 / 패턴 분석 시에만 명시적 호출

---

## 3. 트리거 우선순위 (description 키워드)

여러 Skill의 description 키워드가 동시 매칭될 때:

### 3.1 정확 매칭 > 부분 매칭
- "phase complete" → `phase-complete`
- "phase 종료" → `phase-complete`
- 단일 단어 "phase" → 모호, 사용자 의도 확인

### 3.2 컨텍스트 키워드 가중치
- 현재 active Phase 단계 (start/middle/end)에 따라 가중치 다름
- Phase 진입 직후 → `phase-start` 우선
- Phase 50% 도달 → `phase-review` 우선
- Phase 90% 도달 → `phase-complete` 우선

---

## 4. INDEX.md와의 관계

`.claude/skills/INDEX.md`는 전체 Skill 목록 + applies_to 그룹화를 담는다.
본 파일은 충돌 시 결정 규칙을 담는다.

- INDEX.md 변경 시 본 파일 갱신 확인
- 본 파일 변경 시 INDEX.md priority 섹션 동기화

---

## 5. 예외 케이스

### 5.1 사용자 명시적 호출
- 사용자가 `/{skill-name}` 또는 명시적으로 Skill을 부르면 우선순위 무시
- 단, `context-compact`는 자동 트리거 시 사용자 호출 위에 (안전망)

### 5.2 보안 / 오류 인시던트
- `security-review`, `bug-triage`는 정상 흐름 일시 정지하고 우선 처리
- `rollback-policy` (meta/rollback_policy.md) 발동 시 모든 Skill 중단

---

## 6. 관련 Skill / 문서

- `.claude/skills/INDEX.md`: Skill 카탈로그
- `CLAUDE.md`: 기획 / 검토 모델 라우터
- `AGENTS.md`: 구현 / QA 모델 라우터
- `harness-audit`: 우선순위 표 vs 실제 트리거 결과 정합성 점검

---

## 7. Open Questions

1. **자동 트리거 충돌 빈도 측정**: 어떤 키워드 쌍이 자주 동시 매칭되는지 데이터 수집 (Phase 4+)
2. **사용자 의도 명시 UI**: 충돌 시 선택지 제공 UI 위치 (chat / sidebar / modal)
3. **우선순위 정책 변경 절차**: 본 파일 변경 시 multi-llm-validation 필수?
4. **메타 Skill (harness-audit, meta-retrospective)의 self-trigger 방지**: 자신을 audit 대상으로 포함할지 정책
5. **Phase별 우선순위 차이**: Phase 0 (현재) vs Phase 7+ (보안) 진입 시 우선순위 가중치 변경 필요한지

---

## 8. 변경 이력

- 2026-05-26: Phase 0 S5에서 placeholder 해소, 통합 우선순위 규칙 정의
