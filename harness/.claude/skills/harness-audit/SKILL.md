---
name: harness-audit
description: |
  하네스 전체를 정기 감사한다. 9줄 stub 잔존, 깨진 contract 참조, Skill
  description 키워드 충돌, 미사용 Skill, instruction_index 깨진 entry 등을
  체계적으로 점검한다. Phase 0 완료 시점, 메이저 Phase 종료 직후, "전체
  한 번 봐줘" 류 요청 시 트리거한다.
  키워드: "하네스 감사", "harness audit", "구조 점검", "전체 검토",
  "stub 점검", "Skill 충돌 검사".
applies_to: [claude]
phase: [phase-0, phase-10, phase-20, ongoing]
related_contracts:
  - migration_procedure.md
related_state:
  - PROJECT_STATE.md
  - PHASE_REGISTRY.md
  - instruction_index/
  - meta/harness_improvement_proposals.md
  - meta/skill_usage_log.md
version: v1.2.0
---

# harness-audit

하네스 자체(폴더 구조·Skill·contract 참조·문서 stub·routing yaml)의 건강도를 한 번에 점검하는 절차.

## 트리거 조건

- Phase 0 완료 시점 (Sprint S5 최종 검증)
- 매 메이저 Phase 종료 시 (10, 20)
- staleness 신호 누적 (Skill 장기간 미트리거, contract 미참조)
- 사용자가 "전체 한 번 봐줘" / "하네스 점검" 요청
- 새 Skill 또는 contract 대량 추가 직후

## 사용하지 않는 경우

```
- 단일 Phase 진행 상태 점검 → phase-review
- 단일 contract 변경 → contract-change
- 단일 Skill 회고 → meta-retrospective
- AI 시스템 구조만 → ai-architecture-review
```

## 절차

### 1. 상태 파일 로드

```
1. PROJECT_STATE.md
2. PHASE_REGISTRY.md
3. migration_procedure.md (Phase 0 기간에만)
4. instruction_index/routes.yaml
5. instruction_index/dependency_map.yaml
6. instruction_index/catalog.yaml + instruction_index/priority_rules.md  # (구 'lookup_table.yaml' 은 미생성 — catalog 가 문서 인벤토리, HIP-010 S1 교정)
7. meta/skill_usage_log.md (있다면)
```

### 2. 9줄 stub 카운트

`docs/contracts/` 와 `ai_system/` 하위에서 줄 수 < 30 인 파일을 모두 식별. 목표는 `Phase 0 완료 시 0`. 그 외에는 `[STUB]` 또는 `[PHASE-X]` placeholder marker가 있어야 함.

```
- 카운트
- 파일별 이유 (해당 Phase 미진입 / 누락)
- placeholder marker 부재 시 즉시 critical
```

### 3. Skill description 키워드 충돌

`.claude/skills/*/SKILL.md` 의 frontmatter `description` 필드에서 트리거 키워드를 추출, 같은 키워드가 둘 이상 Skill에 있으면 충돌.

```
- 추출: 인용부호로 묶인 한국어/영어 키워드
- 같은 키워드 → 즉시 한쪽 Skill에서 제거 또는 더 구체화
```

### 4. Skill의 related_contracts 실존 확인

각 Skill frontmatter의 `related_contracts:` / `related_state:` 경로가 모두 실제 파일로 존재하는지. 미존재 시 critical (자동 트리거 시 파일을 못 찾음).

### 5. instruction_index 정합성

- `routes.yaml`의 각 entry의 target 파일 실존
- `dependency_map.yaml`의 노드/엣지가 PHASE_REGISTRY와 일치
- `catalog.yaml`의 document 경로 실존 + role 정합 (구 'lookup_table.yaml' 은 미생성 — 키워드 충돌은 §3 Skill description 추출 + `.claude/skills/INDEX.md` 키워드 표 교차로 확인, 별도 lookup_table 불요)

### 6. Skill 사용 로그 분석

`meta/skill_usage_log.md`가 있으면:

- 6개월 이상 0회 트리거 Skill → 폐기 후보
- 한 세션에서 3회+ 트리거 패턴 → 자동화/스크립트화 후보
- 트리거됐는데 description 키워드 변경 직후라면 추적 리셋

로그 파일이 없으면 본 감사에서 생성을 제안.

### 6.5 Contract 명명 일관성 (audit_naming) — v1.1.0 추가

`scripts/audit_naming.ps1`을 실행해 contract / code / frontend 간 핵심 명명 일관성을 자동 검사한다.

**배경**: P-DRIFT-001 패턴 (sub-agent 분산 작성 시 명명 drift 사후 발견, `meta/patterns.md`) 대응.

**실행**:
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -File scripts/audit_naming.ps1
```

**검사 대상** (NAMING_POLICY 정의):
- `plan_candidates` (deprecated: `plan_options`)
- `video_projects` (deprecated: camelCase 변형)
- `critic_evaluation` (deprecated: 잘린 snake_case / camelCase)
- `rag_references` (deprecated: camelCase 변형)

**판정**:
- 종료 코드 0 + "0 drift detected" → 통과
- 종료 코드 1 + drift 파일/라인 출력 → critical (즉시 contract-change Skill 트리거)

**whitelist 자동 적용**:
- `phases/archive/**` (역사 보존)
- `eval/qa_reports/**` (역사 보존)
- `meta/**` (회고 / 패턴 / 제안 보존)
- `docs/contract_changes/**` (결정 기록)

**새 명명 추가 시**: NAMING_POLICY 배열에 entry 추가 (canonical / deprecated / scope / rationale / whitelist).

### 7. 발견사항 분류

각 항목을 다음 4단계로:

```
critical : 시스템 동작 불가 (Skill 자동 트리거 실패, 깨진 참조)
high     : 정책 위반 또는 큰 누락 (stub에 marker 없음)
medium   : 정합 어긋남 (description 키워드 충돌 1쌍)
low      : 개선 권장 (사용 로그 미운영)
```

### 8. 제안서 작성

`meta/harness_improvement_proposals.md` (append) + `meta/audits/{date}.md` (full 결과)

다음 액션을 항목별로 명시:
- 어떤 Skill을 트리거할지 (`contract-change`, `meta-retrospective` 등)
- 사용자 결정이 필요한 항목 (폐기 후보 등)

## 출력 형식

```
[harness-audit 결과] 2026-05-24
범위: 하네스 전체 (155+ 파일)

critical (0):
  -
high (1):
  - docs/contracts/llm_security_contract.md (9줄, placeholder marker 없음) → Sprint S3 우선 보강
medium (2):
  - Skill description: design-review 와 ai-architecture-review 모두 "UX 점검" 키워드 → design-review에서만 유지
  - instruction_index/routes.yaml: target "eval/security_eval.md" 실존하지 않음 → 갱신 또는 제거
low (1):
  - meta/skill_usage_log.md 미존재 → 다음 Sprint 부터 운영

종료 조건: critical 0 / high 0
이번 감사: critical 0 / high 1 → S3 액션 필요
```

## 금지 사항

- 파일을 직접 삭제 (제안만)
- Skill description 직접 수정 (`contract-change` 절차)
- contract 본문 수정 (`contract-change` 절차)
- 사용자 결정 없이 폐기 Skill 단행

## 자주 발생하는 실수

1. **stub 카운트만 보고 OK 처리**: placeholder marker 존재 여부까지 확인해야 함. 그래야 의도된 stub인지 판단 가능.
2. **description 키워드를 frontmatter 외에서 추출**: 본문 키워드는 무시. frontmatter `description:` 블록만.
3. **사용 로그 없다고 low 처리**: 사용 로그가 없으면 본 감사 자체의 신뢰도가 낮다. 운영 시작 제안은 항상 포함.
4. **routes.yaml만 보고 정합 확인**: dependency_map / catalog 도 함께 확인.
5. **audit_naming 결과 무시 (v1.1.0)**: §6.5 자동 도구가 drift를 발견하면 critical. PascalCase 클래스명과 snake_case JSON 필드명 혼동에 의한 false positive는 case-sensitive 검사 + NAMING_POLICY whitelist로 이미 회피됨.

## 변경 이력

- v1.0.0 (Phase 0 S5): 7단계 (상태 / stub / Skill / contract 참조 / instruction_index / 사용 로그 / 분류)
- v1.1.0 (2026-05-27 Phase 1 회고 P1 적용): §6.5 audit_naming 단계 + scripts/audit_naming.ps1 도구 추가 (P-DRIFT-001 대응)
- v1.2.0 (2026-06-05 HIP-010 S1): §1/§5/자주실수4 의 부재 파일 'lookup_table.yaml' 참조 → 실재 'catalog.yaml'(+priority_rules) 로 교정. 키워드 충돌 점검은 §3 + INDEX.md 표로 일원화(별도 lookup_table 불요). meta/audits/2026-06-05.md M1 해소.

## 종료 조건

- 4단계 분류 완료, 모든 high+ 항목에 후속 Skill 매핑됨
- `meta/audits/{date}.md` 저장
- `meta/harness_improvement_proposals.md`에 append
- critical 0 / high 0 이면 PASS, 아니면 사용자에게 결정 요청
