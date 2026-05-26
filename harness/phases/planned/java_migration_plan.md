# java_migration_plan.md

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 21+
priority: low
estimated_final_lines: 160
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 1-20은 FastAPI(Python) 단독 운영이 기본 전략이다.
백엔드 성능 한계 또는 Java/Kotlin 인력 확보 시점에 전환 여부를 결정하며,
현재 계획을 구체화하는 것은 시기상조다.

## Scope (TBD)

본 파일이 다룰 범위:
- FastAPI(Python) → Spring Boot(Java/Kotlin) 마이그레이션 또는 추가 서비스 결정
- Kotlin vs. Java 언어 선택 기준 (생태계, 팀 역량, 성능)
- 점진 전환 전략 (서비스별 분리 vs. 일괄 교체)
- FastAPI 유지 범위 확정 (AI/LLM 계층은 Python 유지 고려)
- 성능 비교 벤치마크 기준 (TPS, latency, 메모리 사용량)
- JVM 최적화 방안 (GraalVM Native Image, 컨테이너 크기 최소화)
- CI/CD 파이프라인 확장 (Gradle + GitHub Actions)

## Known Dependencies (when filled in)

- `docs/decisions/backend_strategy.md` — FastAPI vs. Spring 역할 분리 결정
- `backend/spring/README.md` — Spring Boot 구조 (작성 시점에 병행)
- `backend/fastapi/README.md` — FastAPI 현재 범위 (분리 기준)
- `docs/contracts/api_contract.md` — Spring 담당 API 스펙
- `docs/contracts/tech_stack_contract.md` — JVM 버전 확정
- 운영 메트릭 (TPS, 응답 시간, 에러율) 데이터

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- FastAPI 백엔드 TPS 또는 응답 시간 한계 명시적 도달 (기준 2주 이상 초과)
- 또는 Java/Kotlin 전문 인력 확보 결정 (채용 완료)

## 예시 전환 판단 매트릭스 형식 (fill-in 시 참고)

```
| 기준              | FastAPI 유지 | Spring 전환 |
|-------------------|--------------|-------------|
| AI/LLM 계층       | 유지         | -           |
| 회원/인증         | 고려         | 선호        |
| 결제/구독         | 고려         | 선호        |
| RAG 검색          | 유지         | -           |
| 비즈니스 로직     | 고려         | 선호        |
```

## Related Skill / Phase

- Skill: N/A
- Phase: 21+
- 책임자: 운영자
