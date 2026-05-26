# data_contract.md

> ⚠️ **PLACEHOLDER** — 본 contract는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 contract로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 4+
priority: medium
estimated_final_lines: 220
last_updated: 2026-05-26
```

## Why Placeholder?

MVP Phase 0~3은 내부 데이터(사용자 입력 + LLM 생성 + RAG)만 다룬다. Phase 4+ 외부 시스템 연동(예: 영상 분석 도구, 외부 brand asset import, 분석 export)이 시작되는 시점에 표준 데이터 스키마를 고정한다. 그 전까지는 `db_schema.md` + `output_schema.md` + `rag_data_contract.md`로 충분.

## Scope (TBD)

본 contract가 다룰 범위:

- 외부 데이터 inflow 표준:
    - Brand asset import (로고/색상/폰트 메타데이터)
    - 영상 메타데이터 import (기존 YouTube 채널 분석 결과 등)
    - 외부 RAG seed (운영자 수동 입력 외에 API import)
    - 사용자 업로드 (이미지 reference, 영상 미리보기, Phase 5+)
- 외부 데이터 outflow 표준:
    - 영상 기획안 export (JSON, PDF, Markdown)
    - final_output 외부 시스템 전송 (Webhook, Phase 11+)
    - eval 결과 export (분석 도구 연동, Phase 11+)
- 데이터 흐름 분리 명시:
    - 외부 데이터 (inflow/outflow)
    - 내부 생성 데이터 (LLM 응답)
    - 사용자 선택 데이터 (discovery_choices)
    - 피드백 데이터 (feedback_events)
    - RAG 지식 (rag_chunks)
- 외부 시스템 연동 인증:
    - API key 관리 (env_contract와 정합)
    - OAuth 위임 (third-party 영상 도구 연동, Phase 11+)
- 데이터 버전 관리:
    - 외부 스키마 변경 시 호환성 정책
    - 버전 mismatch 처리 절차
- 외부 데이터의 PII 검사 (inflow 시점에 llm_security §3.2 적용)
- 데이터 일관성 (외부 ↔ 내부 sync 정책)
- 외부 RAG seed의 quality_filter 통과 절차
- 백업 / 복원 시 외부 데이터 일관성

## Known Dependencies (when filled in)

외부 표준:
- JSON Schema 2020-12
- OpenAPI 3.1 (API import 스펙)
- IPTC / EBU 영상 메타데이터 표준 (Phase 11+)

내부 의존 contract:
- `docs/contracts/api_contract.md` (외부 API 진입점)
- `docs/contracts/db_schema.md` (외부 데이터 저장 위치)
- `docs/contracts/rag_data_contract.md` (외부 seed import 흐름)
- `docs/contracts/llm_security_contract.md` §3.2 (inflow PII 검사)
- `docs/contracts/privacy_contract.md` (placeholder)
- `docs/contracts/env_contract.md` (placeholder, API key 관리)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 4+ 진입 (외부 시스템 연동 시작 시점)
- 또는 Brand asset import 기능 첫 구현 시점
- 또는 영상 메타데이터 outflow 요청 발생 시
- 또는 third-party API 연동 첫 결정 시점

## Related Skill / Phase

- Skill: `contract-change` (외부 스키마 변경은 항상 절차 통과)
- Phase: 4+
- 책임자: AI(초안) + 사용자(검토)
