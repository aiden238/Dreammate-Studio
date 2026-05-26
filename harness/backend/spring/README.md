# backend/spring

> ⚠️ **PLACEHOLDER** — 본 파일은 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 21+
priority: low
estimated_final_lines: 150
last_updated: 2026-05-26
```

## Why Placeholder?

Phase 1-20은 FastAPI 단독으로 운영된다. Spring Boot는 백엔드 성능 한계 또는
Java 인력 확보 시점에 진입 여부를 결정한다. 현재는 아키텍처 선택지 보존 목적의
폴더만 유지한다.

## Scope (TBD)

본 파일이 다룰 범위:
- Spring Boot 백엔드 전체 구조 (FastAPI에서 마이그레이션 또는 추가 서비스)
- Kotlin vs. Java 언어 선택 결정 기준 (Phase 21 시점 재검토)
- GraphQL vs. REST API 전략 (FastAPI와 역할 분리 기준)
- 회원 / 권한 / 결제 / 팀 / 프로젝트 관리 담당 서비스 범위
- FastAPI와의 내부 통신 방식 (gRPC / HTTP / 이벤트 버스)
- JVM 기반 성능 최적화 포인트 (GraalVM Native Image 검토)
- CI/CD (GitHub Actions + Gradle, JVM 컨테이너 최적화)

## Known Dependencies (when filled in)

- `docs/decisions/backend_strategy.md` — FastAPI vs. Spring 역할 분리 결정
- `phases/planned/java_migration_plan.md` — 점진 전환 전략
- `backend/fastapi/README.md` — FastAPI 현재 담당 범위 (분리 기준)
- `docs/contracts/api_contract.md` — API 스펙 (Spring 담당 부분)
- `docs/contracts/tech_stack_contract.md` — JVM 버전, 빌드 도구 확정
- Spring Boot, Kotlin/Java, Gradle/Maven (Phase 21 시점 확정)

## Fill-In Trigger

다음 조건 충족 시 본 파일 작성 착수:
- Phase 21 백엔드 확장 결정 (`docs/decisions/backend_strategy.md` 업데이트)
- Java/Kotlin 인력 확보 또는 FastAPI 성능 한계 명시적 도달

## 예시 서비스 분리 구조 (fill-in 시 참고)

```
FastAPI (AI + RAG + LLM 계층)
    ↕ Internal HTTP / gRPC
Spring Boot (비즈니스 핵심 계층)
├── 회원/인증 서비스     # OAuth2, JWT
├── 권한/팀 서비스       # RBAC
├── 결제 서비스          # 구독 플랜
└── 프로젝트 관리 서비스 # 기획안 저장/공유
```

## Related Skill / Phase

- Skill: N/A
- Phase: 21+
- 책임자: 운영자
