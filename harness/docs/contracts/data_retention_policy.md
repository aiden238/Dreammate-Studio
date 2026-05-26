# data_retention_policy.md

> ⚠️ **PLACEHOLDER** — 본 contract는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 contract로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 7+
priority: high
estimated_final_lines: 220
last_updated: 2026-05-26
```

## Why Placeholder?

MVP Phase 0~6은 인프라/구현 단계로 실 외부 사용자 데이터를 본격 수집하지 않음. Phase 7+ 첫 외부 사용자 데이터 수집 시점부터 법적·운영적 책임이 발생하므로 그때 정량 정책으로 고정한다. 그 전까지는 `error_response_contract.md` §9.3의 잠정 보존 기간(errors.log 1년, agent_io_logs 1년, audit 3년)이 가이드.

## Scope (TBD)

본 contract가 다룰 범위:

- 사용자 데이터 보존 기간 (테이블별)
- agent_io_logs.input_payload PII 비식별화 시점 (현재 90일 잠정)
- 로그 보존 기간 (errors.log / intent_filter_logs / audit_log)
- 사용자 삭제 요청 절차 (GDPR Article 17, 개인정보보호법 36조)
- 4계층(Brand/Domain/Series/Video) cascade 삭제 정책
- soft delete 후 hard delete 시점 (현재 영구 soft만)
- 백업 보존 기간 + 백업 안의 삭제 요청 처리
- 감사 로그 (audit_log) 별도 보존 (3년 잠정)
- rag_chunks의 출처 데이터 삭제 시 chunk 처리 (재임베딩 vs 삭제)
- brand_memory_entries의 사용자 잠금 / 삭제 절차
- 데이터 이동성 (export, JSON/CSV)
- 익명화 정책 (k-anonymity, l-diversity 검토)
- 미성년자 데이터 처리 (Phase 11+ 추가 검토)
- 결제 데이터 보존 (Phase 11+ paid tier 진입 시)

## Known Dependencies (when filled in)

외부 표준:
- GDPR (EU) Article 5, 6, 17, 20
- 개인정보보호법 (대한민국) §15, §21, §36, §37
- CCPA / CPRA (캘리포니아, Phase 21+ 진입 시)

내부 의존 contract:
- `docs/contracts/db_schema.md` (소프트 삭제 컬럼 / cascade 정책)
- `docs/contracts/privacy_contract.md` (placeholder, PII 정의)
- `docs/contracts/user_consent_contract.md` (placeholder, 동의 항목)
- `docs/contracts/llm_security_contract.md` §3.2 (PII 마스킹 패턴)
- `docs/contracts/error_response_contract.md` §9.3 (잠정 보존 기간)
- `docs/contracts/event_log_contract.md` (placeholder, 이벤트 로그)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 7+ 진입 (외부 사용자 데이터 수집 시작 시점)
- 또는 사용자 삭제 요청 첫 발생 시
- 또는 EU 사용자 진입 시점 (GDPR 적용)
- 또는 데이터 보안 사고 발생 시 (긴급)

## Related Skill / Phase

- Skill: `security-review` (보존/삭제 항목 카테고리)
- Phase: 7+
- 책임자: AI(초안) + 사용자(검토) + 외부 법무 자문(Phase 11+ paid 진입 시)
