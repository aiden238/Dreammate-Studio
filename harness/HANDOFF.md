# HANDOFF

## 목적

역할 전환 시 필요한 정보를 압축해서 전달한다.

## 역할 흐름

```text
Planner
→ Architect
→ Implementer
→ QA
→ Docs
→ Meta
```

## Handoff 기본 형식

```md
# Handoff Note

## 1. Current Phase
## 2. Completed Work
## 3. Remaining Work
## 4. Required References
## 5. Changed Files
## 6. Test Results
## 7. Known Issues
## 8. Non-Goals
## 9. Next Role Instructions
```

## 금지

- archive 내용을 기본 포함하지 않는다.
- 불확실한 내용을 확정처럼 쓰지 않는다.
- contracts 변경을 완료된 것처럼 쓰지 않는다.
- Phase 범위 밖 작업을 다음 역할에 넘기지 않는다.
