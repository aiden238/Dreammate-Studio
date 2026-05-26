# regression_checklist.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: medium
estimated_final_lines: 100
last_updated: 2026-05-26
```

## Why Placeholder?

golden_set이 활성화되고 prompt 변경 이력이 쌓이기 전까지 회귀 체크리스트의
실제 항목을 확정할 수 없다. Phase 1 golden_set 정식 운영 이후 작성한다.

## Scope (TBD)

본 파일이 다룰 범위:
- golden_set 기반 회귀 테스트 항목 전체 목록
- prompt 변경 시 트리거되는 회귀 체크 (Critic 점수 비교)
- contract 변경 시 트리거되는 회귀 체크 (output_schema 호환성)
- RAG 검색 결과 일관성 회귀 (retrieval score 변화량 임계)
- output_schema 버전 호환성 회귀 (필드 추가/제거/타입 변경)
- 회귀 실패 시 롤백 절차 (meta/rollback_policy.md 연계)
- 자동 회귀 vs. 수동 회귀 구분 기준

## Known Dependencies (when filled in)

- `eval/regression_eval.md` — 회귀 평가 기준
- `eval/golden_set.md` — 기준 케이스 목록
- `docs/contracts/output_schema.md` — 스키마 버전 추적
- `meta/rollback_policy.md` — 회귀 실패 시 롤백 절차
- `prompt-version-review` Skill — prompt 변경 연동
- `eval-run` Skill — 회귀 자동 실행
- `logs/eval_log.md` — 회귀 결과 누적 기록

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 1 완료 + golden_set 10케이스 이상 활성화
- 첫 prompt 변경 (prompt_registry.md 버전 bump) 발생

## 예시 체크리스트 항목 형식 (fill-in 시 참고)

```
## Prompt 변경 회귀

- [ ] golden_set 전체 재실행 (기준 점수 대비 ±5% 이내)
- [ ] Critic 점수 중앙값 유지 (기존 중앙값 -0.1 이하 허용)
- [ ] output_schema 필드 누락 없음
- [ ] Planning Agent 응답 시간 기준 이내 (p95 < 3s)

## Contract 변경 회귀

- [ ] 기존 API 응답 구조 호환성 확인
- [ ] output_schema 버전 호환 레이어 동작 확인
```

## Related Skill / Phase

- Skill: regression_eval, prompt-version-review
- Phase: 1+
- 책임자: AI / 운영자
