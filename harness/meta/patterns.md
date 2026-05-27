# meta/patterns.md

> 🚧 Placeholder (Phase 0 진입 직후 생성. 첫 retrospective 발생 시점부터 누적)

## 목적

meta-retrospective Skill이 회고를 거듭하면서 식별하는 **반복되는 패턴**(반복 실패 / 반복 성공 / 위험 신호)을 한곳에 누적한다.

회고는 개별 사건의 5 Whys + 액션을 담고, 이 파일은 패턴화된 인사이트만 모은다.

## 작성 트리거

- `meta-retrospective` Skill이 같은 카테고리의 회고를 3회 이상 누적했을 때
- harness-audit Skill 실행 시 발견한 구조적 패턴
- 사용자가 명시적으로 "이건 패턴이다"라고 지적했을 때

## 항목 형식

```markdown
### Pattern P-{NN}: {짧은 이름}

- **유형**: 반복 실패 | 반복 성공 | 위험 신호 | 운영 인사이트
- **최초 식별**: {YYYY-MM-DD}
- **관련 회고**: meta/retrospectives/{...}
- **요약**: 1–3줄
- **권장 대응**:
  - {액션 1}
  - {액션 2}
- **연관 Skill / Contract**: {목록}
```

## 보존 정책

- 영구 보존 (회고와 별도)
- 패턴이 해소되면 "Resolved" 표기만 추가, 삭제 금지

## 인덱스

### Pattern P-DRIFT-001: sub-agent 분산 작성 시 contract 명명 drift 사후 발견

- **유형**: 반복 실패 → **Mitigated** (2026-05-27)
- **최초 식별**: 2026-05-26 (Phase 1)
- **관련 회고**: meta/retrospectives/phase-1.md §근본 원인 (5 Whys)
- **요약**: contract를 sub-agent 분산으로 작성하면 contract 내부 cross-reference (예: API body 키 = DB 테이블 = TS interface) 명명 일관성이 자동 검증되지 않아 다음 Phase 구현 중 발견됨. Phase 1에서 CC-001 (`plan_options` / `plans` / `plan_candidates` 3-way drift).
- **적용된 대응 (2026-05-27)**:
  - ✅ scripts/audit_naming.ps1 신규 작성 (NAMING_POLICY + whitelist)
  - ✅ harness-audit v1.1.0 §6.5 audit_naming 단계 추가 (P1)
  - ✅ phase-start v1.2.0 §6.1 Contract cross-reference 점검 추가 (P2)
  - ✅ qa-check v1.2.0 카테고리 11 Contract Drift 추가 (P3)
- **다음 재평가 시점**: Phase 2 종료 시 — 새 contract 추가/변경 시 audit_naming이 실제로 신규 drift를 잡았는지 회고
- **연관 Skill / Contract**: harness-audit, phase-start, qa-check, contract-change, audit_naming.ps1

### Pattern P-SLICE-001: Simplest Slice 3회 압축 원칙 채택

- **유형**: 반복 성공 (Phase 1 7 Slices 모두 적용, 회귀 0)
- **최초 식별**: 2026-05-26 (Phase 1)
- **관련 회고**: meta/retrospectives/phase-1.md §잘된 것
- **요약**: "이 phase 작동 가능 최소 단위" 도출 시 "더 줄일 수 있는가?"를 3회 반복 → 디버깅·rollback 비용 최소화. Phase 1 Slice 1을 5 파일로 시작 → 7 Slices로 점진 확장.
- **권장 대응**: phase-start v1.1.0 §6.2 채택 완료 — 후속 Phase 모두 적용
- **연관 Skill / Contract**: phase-start §6.2

### Pattern P-GRACEFUL-001: 외부 의존성 실패 graceful 패턴이 testability ↑

- **유형**: 운영 인사이트 (반복 성공)
- **최초 식별**: 2026-05-26 (Phase 1 Slice 4/5)
- **관련 회고**: meta/retrospectives/phase-1.md §배운 것
- **요약**: 외부 의존성(RAG/DB/LLM) 실패 시 사용자 차단 0건 + 응답 200 + validation.warnings로 자기설명. 부작용: pytest로 모든 실패 케이스 mock 자동화 가능 → testability ↑.
- **권장 대응**:
  - Phase 4+ MOA Lite revise loop도 동일 패턴 채택
  - error_response_contract.md에 graceful 패턴 가이드 명시
- **연관 Skill / Contract**: error_response_contract, agent_io_contract

### Pattern P-FOLDER-PARALLEL-001: sub-agent 병렬 dispatch 폴더 분리 표준

- **유형**: 반복 성공 (Phase 1 Wave 1/4 적용, 충돌 0)
- **최초 식별**: 2026-05-26 (Phase 1)
- **관련 회고**: meta/retrospectives/phase-1.md §잘된 것
- **요약**: 같은 폴더 변경 sub-agent 병렬은 충돌 위험. 다른 폴더(backend/ vs apps/web/)는 충돌 0. multi_slice_plan.md §2 충돌 분석 매트릭스 패턴 효과적.
- **권장 대응**: phases/active/{phase}/multi_slice_plan.md template에 충돌 분석 매트릭스 섹션 표준화
- **연관 Skill / Contract**: phase-start §6.3 Surgical Scope, multi_slice_plan template
