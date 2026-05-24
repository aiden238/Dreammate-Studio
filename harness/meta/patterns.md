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

(현재 0건 — Phase 0 진행 중. 첫 회고는 Sprint S0 종료 후.)
