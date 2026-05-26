# test_index.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: medium
estimated_final_lines: 120
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 1 첫 endpoint가 구현되기 전까지 테스트 카테고리 구조가 확정되지 않는다.
테스트 인덱스는 실제 코드 구조가 나온 뒤에야 의미있는 분류가 가능하다.

## Scope (TBD)

본 파일이 다룰 범위:
- pytest (백엔드) / vitest (프론트엔드) 테스트 인덱스 총괄
- 단위(unit) / 통합(integration) / E2E / smoke 테스트 카테고리 구분
- 각 테스트 파일 경로 + 목적 + 담당 모듈 매핑
- 테스트 실행 명령어 (로컬 / CI 환경 별도 명시)
- 커버리지 측정 기준 및 임계값 (unit ≥ 80%, integration ≥ 60%)
- 신규 테스트 추가 절차 및 네이밍 컨벤션
- 실패한 테스트 처리 정책 (skip vs. block deploy)

## Known Dependencies (when filled in)

- `backend/fastapi/README.md` — 테스트 대상 엔드포인트 목록
- `packages/shared-types/README.md` — 타입 정의 테스트 범위
- `eval/regression_eval.md` — 회귀 평가와 테스트 인덱스 연계
- `eval/golden_set.md` — golden set 기반 통합 테스트 케이스
- `qa-check` Skill — 테스트 실행 자동화 훅
- `eval-run` Skill — eval 실행 파이프라인 연계
- CI/CD 파이프라인 설정 (Phase 1+)

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 1 첫 FastAPI endpoint 구현 시작 (최소 1개 라우터 존재)
- pytest 설정 파일 (`pyproject.toml` 또는 `pytest.ini`) 생성 완료

## 예시 인덱스 엔트리 형식 (fill-in 시 참고)

```
| 파일 경로                              | 카테고리    | 담당 모듈        | 실행 명령                     |
|----------------------------------------|-------------|------------------|-------------------------------|
| tests/unit/test_intent_agent.py        | unit        | Intent Agent     | pytest tests/unit/            |
| tests/integration/test_planning_flow.py| integration | MOA Lite         | pytest tests/integration/     |
| tests/e2e/test_video_plan.py           | E2E         | 전체 파이프라인  | pytest tests/e2e/             |
| tests/smoke/test_health.py             | smoke       | API 헬스체크     | pytest tests/smoke/ -m smoke  |
```

## Related Skill / Phase

- Skill: qa-check, eval-run
- Phase: 1+
- 책임자: AI / 운영자
