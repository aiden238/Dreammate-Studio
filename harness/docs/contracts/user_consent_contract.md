# user_consent_contract.md

> ⚠️ **PLACEHOLDER** — 본 contract는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 contract로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 7+
priority: high
estimated_final_lines: 200
last_updated: 2026-05-26
```

## Why Placeholder?

MVP Phase 0~6은 본 하네스 운영자 1인의 자기 테스트. 외부 사용자 가입 흐름 활성화 시점부터 동의 절차가 필요하므로 그때 정량 정책으로 고정한다. 그 전까지는 외부 가입 흐름 자체가 비활성.

## Scope (TBD)

본 contract가 다룰 범위:

- 동의 항목 분류:
    - 필수 (서비스 제공 불가능 시): 회원가입, 영상기획 데이터 처리
    - 선택 (서비스 일부 기능): 사용자 행동 분석, Brand Memory 자동 추출, RAG 후보 승격
    - 마케팅 (별도 명시 동의): 신기능 안내, 이메일 마케팅 (Phase 11+)
- 동의 UI 표준:
    - 가입 시 동의 화면 컴포넌트 (개별 토글, 전체 동의 별도 안내)
    - 동의 항목별 설명문 (한국어 친근체, 50자 이내 요약 + "자세히 보기")
    - 미성년자 (만 14세 미만) 법정대리인 동의 절차
    - 동의 시각 기록 (auth.users + user_consents 테이블, 필요 시 생성)
- 동의 철회 절차:
    - 설정 페이지 (마이페이지) 토글
    - 철회 즉시 처리 + 결과 안내
    - 필수 항목 철회 = 회원 탈퇴와 동의 (안내 필수)
- 동의 버전 관리:
    - 약관 / 처리방침 버전 변경 시 재동의 절차
    - 변경 사항 명시 + 변경 전후 비교
- 동의 로그 (audit_log와 정합):
    - user_id, consent_item, version, granted/revoked, timestamp
- 미성년자 동의:
    - 만 14세 미만: 법정대리인 동의 의무
    - 만 19세 미만: 일부 항목 제한
- 동의 없는 데이터의 처리 정책:
    - 분석 옵트아웃 시 event_log_contract와 정합
    - Brand Memory 자동 추출 비동의 시 P-AUX-2 호출 자체 스킵
- 외부 LLM provider (OpenAI 등) 데이터 전송 동의

## Known Dependencies (when filled in)

외부 표준:
- GDPR (EU) Article 6, 7, 8, 21
- 개인정보보호법 (대한민국) §15, §16, §22, §22의2
- 정보통신망법 §50 (만 14세 미만)
- 표준 개인정보 처리방침 (행정안전부 가이드)

내부 의존 contract:
- `docs/contracts/privacy_contract.md` (placeholder, PII 처리 본체)
- `docs/contracts/data_retention_policy.md` (placeholder)
- `docs/contracts/api_contract.md` §4 (Auth, 가입 흐름)
- `docs/contracts/db_schema.md` §3.1 (user_profiles + user_consents 신규 테이블)
- `apps/web/design.md` (가입 흐름 UI)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 7+ 진입 (외부 사용자 가입 흐름 활성화 시점)
- 또는 약관 / 처리방침 첫 외부 공개 시점
- 또는 EU 사용자 진입 시점
- 또는 paid tier 진입 시점 (Phase 11+)

## Related Skill / Phase

- Skill: `security-review` (consent 카테고리)
- Phase: 7+
- 책임자: AI(초안) + 사용자(검토) + 외부 법무 자문(가입 흐름 출시 전 필수)
