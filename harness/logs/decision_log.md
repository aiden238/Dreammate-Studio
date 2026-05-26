# decision_log.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 1+
priority: medium
estimated_final_lines: 130
last_updated: 2026-05-26
```

## Why Placeholder?

ADR(Architecture Decision Record) 외 일상 결정의 누적 로그는 Phase 1 운영 시작
이후 실제 결정이 발생해야 기록 형식과 첫 엔트리를 확정할 수 있다.

## Scope (TBD)

본 파일이 다룰 범위:
- ADR 파일(`docs/decisions/`)에 올리기 전 일상적 결정 누적 로그
- 결정 시점 / 배경 / 고려 대안 / 최종 선택 / 결과 기록 표준 형식
- 운영 중 발생하는 소소한 기술 결정 (라이브러리 선택, 설정값 변경 등)
- Phase별 결정 분류 태그 (phase:1, category:tech/product/ai/ux)
- 결정 번호 규칙 (DEC-YYYYMMDD-NNN 형식)
- `meta/lessons_learned.md` 로 승격 기준 (반복되거나 교훈이 큰 결정)
- 결정 번복 이력 기록 방식 (superseded_by 필드)

## Known Dependencies (when filled in)

- `docs/decisions/` — 중요 ADR 파일들 (일상 결정과 구분)
- `meta/lessons_learned.md` — 교훈으로 승격되는 결정 연계
- `logs/log_index.md` — 로그 인덱스에 본 파일 등록
- `PHASE_REGISTRY.md` — Phase 태그 기준

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 1 운영 시작 시점
- 첫 일상 결정 발생 (ADR 파일 없이 처리한 결정 최초 기록 필요 시)

## 예시 엔트리 형식 (fill-in 시 참고)

```markdown
## DEC-20260601-001

- **날짜**: 2026-06-01
- **Phase**: 1
- **카테고리**: tech
- **결정**: FastAPI 응답 캐싱에 Redis 대신 in-memory LRU 캐시 사용
- **배경**: Redis 인프라 비용 절감 필요. DAU 100명 이하에서는 메모리 캐시로 충분.
- **대안 고려**: Redis (비용 과다), 캐싱 없음 (LLM 호출 비용 증가)
- **결과**: 추후 Redis 전환 옵션 열어두되 Phase 3까지 in-memory 유지
- **관련**: docs/decisions/tech_stack_decision.md
```

## Related Skill / Phase

- Skill: meta-retrospective, harness-audit
- Phase: 1+
- 책임자: 운영자 / AI
