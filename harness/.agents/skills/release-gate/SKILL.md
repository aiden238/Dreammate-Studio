# Skill: release-gate

## 1. Purpose

배포 전 품질 게이트를 수행한다.

## 2. When to Use

- 관련 작업을 시작하기 전
- Phase 완료 전
- 구조 변경 또는 품질 검토가 필요할 때

## 3. Required Inputs

- PROJECT_STATE.md
- PHASE_REGISTRY.md
- 현재 active Phase 문서
- 관련 docs/contracts 문서

## 4. Required References

- instruction_index/routes.yaml
- docs/contracts/mvp_non_goals.md
- 관련 eval 문서

## 5. Procedure

1. 현재 Phase와 Scope를 확인한다.
2. Non-Goals를 확인한다.
3. 필요한 contracts를 확인한다.
4. 작업 또는 검토를 수행한다.
5. 결과와 리스크를 기록한다.
6. contracts 변경이 필요하면 직접 수정하지 않고 제안서를 만든다.

## 6. Forbidden Actions

- archive 기본 참조 금지
- contracts 직접 변경 금지
- Phase 범위 밖 기능 추가 금지
- 영상 제작 기능을 MVP에 추가 금지
- 사용자 데이터를 바로 global RAG에 저장 금지

## 7. Output Format

```md
# release-gate Result

## 1. Summary
## 2. Checked References
## 3. Findings
## 4. Risks
## 5. Required Changes
## 6. Next Actions
```

## 8. Done Definition

검토 결과가 실행 가능한 next action으로 정리되어 있다.
