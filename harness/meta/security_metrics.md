# meta/security_metrics.md

> 🚧 PLACEHOLDER · Created: 2026-05-24 · Status: stub

## 작성 트리거

이 파일은 다음 시점에 작성된다:
- **Phase**: Phase 7 (RAG Lite) 진입 시 — 첫 보안 메트릭 수집 시작
- **Skill**: `security-review` Skill 첫 정량 점검 시
- **사유**: Phase 1~6은 인프라/MVP 골격 단계로 실 데이터 미수집. RAG/실 사용자 데이터 진입 시점부터 메트릭 의미 발생.

## 잠정 원칙 (작성 전까지)

- security-review Skill의 10 영역 결과는 `eval/security_reviews/`에 일단 누적
- 정량 지표(차단 횟수, PII 매칭률 등)는 본 파일에 통합 추적

## 작성 시 포함할 것 (미리 정의)

- [ ] Prompt injection 차단 횟수 (일 / 주 / 월 단위)
- [ ] PII 마스킹 매칭률 (false positive / false negative)
- [ ] RAG poisoning 의심 사례
- [ ] Cost spike incidents (1.5x 평균 이상)
- [ ] System prompt leakage 의심 사례
- [ ] Rate limit 위반 IP / 사용자
- [ ] Output schema validation 실패율
- [ ] Critic revise 무한 루프 차단 횟수

## 참조

작성 시 다음을 참조한다:
- `docs/contracts/llm_security_contract.md`
- `docs/contracts/rate_limit_policy.md`
- `eval/security_reviews/`
- `.claude/skills/security-review/SKILL.md`

## 메모

(빈 줄. 작성자가 채움.)
