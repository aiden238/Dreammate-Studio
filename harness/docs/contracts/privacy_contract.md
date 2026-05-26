# privacy_contract.md

> ⚠️ **PLACEHOLDER** — 본 contract는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 contract로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 7+
priority: high
estimated_final_lines: 280
last_updated: 2026-05-26
```

## Why Placeholder?

MVP Phase 0~6은 인프라/구현 단계로 외부 사용자 데이터를 본격 수집하지 않음. Phase 7+ 외부 사용자 첫 가입 시점부터 PII 보호 의무가 본격화되므로 그때 정량 정책으로 고정한다. 그 전까지는 `llm_security_contract.md` §3.2(PII 패턴)이 운영 가이드.

## Scope (TBD)

본 contract가 다룰 범위:

- PII 분류 (직접/간접 식별자) 정의 + 처리 원칙
- 사용자 동의 기반 처리 (user_consent_contract와 정합)
- 데이터 최소 수집 원칙 (영상기획에 필요한 것만)
- LLM에 전송되기 전 PII 마스킹 절차 (llm_security와 정합)
- agent_io_logs / feedback_events의 PII 비식별화 시점
- 사용자 권리:
    - 열람 요청 (Article 15 / 개인정보보호법 35조)
    - 정정 요청 (Article 16 / 36조)
    - 삭제 요청 / 잊혀질 권리 (Article 17 / 36조)
    - 데이터 이동성 (Article 20 / 35조의2)
    - 처리 제한 (Article 18)
    - 자동화된 의사결정 거부 (Article 22) — LLM 결과의 위치
- 익명화 / 가명화 기준 (k-anonymity, pseudonymization)
- 제3자 제공 (OpenAI 등 LLM provider) 명시 + 동의
- 국외 이전 (OpenAI 미국 서버) 고지 + 동의 (개인정보보호법 28조의8)
- 미성년자 처리 (만 14세 미만, 만 19세 미만)
- 처리 위탁 (Supabase, Vercel 등) 공개 목록
- 침해 사고 통지 절차 (사용자 + 정부, 72시간)
- DPO (Data Protection Officer) / 개인정보보호책임자 지정
- 개인정보처리방침(공개 문서) 본문 (별도 마크다운 또는 web 페이지)

## Known Dependencies (when filled in)

외부 표준:
- GDPR (EU) Article 1~99
- 개인정보보호법 (대한민국) 전부
- CCPA / CPRA (캘리포니아, Phase 21+)
- ISO/IEC 27701 (PII 관리 시스템)

내부 의존 contract:
- `docs/contracts/llm_security_contract.md` §3.2 (PII 패턴)
- `docs/contracts/user_consent_contract.md` (placeholder, 동의 항목)
- `docs/contracts/data_retention_policy.md` (placeholder, 보존/삭제)
- `docs/contracts/event_log_contract.md` (placeholder, 분석 목적 옵트아웃)
- `docs/contracts/db_schema.md` (PII 컬럼 위치)
- `docs/contracts/api_contract.md` §4 (Auth)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 7+ 진입 (외부 사용자 첫 가입 시점)
- 또는 EU 사용자 진입 시점 (GDPR 적용)
- 또는 paid tier 진입 시점 (Phase 11+)
- 또는 개인정보 침해 사고 발생 시 (긴급)

## Related Skill / Phase

- Skill: `security-review` (privacy 항목 카테고리)
- Phase: 7+
- 책임자: AI(초안) + 사용자(검토) + 외부 법무 자문(필수, Phase 11+ paid 진입 시)
