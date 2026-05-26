# handoff_log.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 0+
priority: high
estimated_final_lines: 120
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 0에서 첫 context-compact Skill 실행 이후 바로 엔트리 누적이 시작되는 파일이다.
형식만 확정하고 대기 중이며, 첫 handoff 발생 즉시 기록 착수한다.

## Scope (TBD)

본 파일이 다룰 범위:
- context-compact Skill 실행 출력 요약 누적 (세션 전환 이력)
- `meta/handoffs/` 디렉토리 내 handoff 파일 인덱스 역할
- 세션 전환 날짜 / Phase / 이유 / handoff 파일 경로 기록
- 세션 재개 시 이전 handoff 빠르게 조회하기 위한 색인 기능
- handoff 품질 평가 (다음 세션에서 재개 용이했는지 회고)
- Sprint별 누적 handoff 수 추이 (context 압박 빈도 측정)

## Known Dependencies (when filled in)

- `meta/handoffs/` — handoff 파일 실제 저장 위치
- `HANDOFF.md` — 현재 세션 handoff 문서 (가장 최신)
- `context-compact` Skill — handoff 생성 트리거
- `logs/log_index.md` — 로그 인덱스에 본 파일 등록
- `PHASE_REGISTRY.md` — Phase 태그 기준

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- 첫 context-compact Skill 실행 완료 (Phase 0에서 이미 발생 가능)
- `meta/handoffs/` 디렉토리에 첫 handoff 파일 생성 시

## 예시 엔트리 형식 (fill-in 시 참고)

```markdown
## HANDOFF-20260526-001

- **날짜**: 2026-05-26
- **Phase**: 0 (S5 Sprint)
- **이유**: 컨텍스트 80% 도달 → context-compact Skill 실행
- **파일**: meta/handoffs/handoff_20260526_S5.md
- **요약**: S5-1 (24 파일), S5-2 (20 파일) 완료. S5-3 보류 중.
- **다음 세션 진입점**: S5-3 (harness-audit + Phase 0 archive + commit)
- **품질 평가**: 양호 (다음 세션에서 재개 용이)
```

## Related Skill / Phase

- Skill: context-compact
- Phase: 0+ (현재 Phase 0부터 즉시 사용)
- 책임자: AI / 운영자
