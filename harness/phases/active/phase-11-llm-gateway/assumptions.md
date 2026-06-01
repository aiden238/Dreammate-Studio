# Phase 11 — Assumptions

## A. 제품 phase 성격 + 가속 빌드
- ★ 런타임 변경 有(제품 phase) — A9(런타임 0) 미적용. 대신 **behavior-preserving**(기존 0 수정 + 신규/additive + gated default-off) + pytest 381→435 가 게이트.
- ★ **가속 빌드**: 코드 S1·S2·S3 가 entry 문서 작성 전에 선완료·commit·push(pytest 435). 본 entry 는 retroactive 정식화 — 코드 0 변경, 문서만.

## B. behavior-preserving 가정 (핵심)
- gateway 는 **신규 레이어** — agents 미연결(Stage A 후속, NG7). 기존 agents 는 여전히 `client or OpenAI(...)` 직접 호출 → 기존 동작 100% 보존.
- cross_validation 은 **순수 함수**(자동 연결 없음) + orchestrator gated hook(default OFF). 발화 시에도 **로깅만** → Envelope/output_schema/응답 0 변경.
- monkeypatch 보존: moa_orchestrator 는 `plans_router.run_*` 를 call-time namespace 해석 → 테스트 fixture 보존. cross-validation hook 도 late-import(순환 회피 + monkeypatch 용이).

## C. gated default-off 가정 (S3)
- `cross_validation_enabled` default **False** → §5.5 hook 미발화 → /generate Envelope = Phase 10 byte-identical.
- 활성 = 명시적 flag(`CROSS_VALIDATION_ENABLED`) + GOOGLE 키 opt-in. CI/기존 사용자 흐름 미실행.
- 모든 예외 graceful(`logger.exception`) → 교차검증 실패가 기존 흐름 절대 차단 X.

## D. graceful provider 가정 (S1·S2)
- 키 없으면 gateway `LLMError("missing key")` graceful + cross_validate `CrossCheck(available=False)` 흡수 → 파이프라인 무영향(NG1).
- Gemini 503(transient) / 빈출력(thinking 모델) / JSON 파싱 실패 → 전부 graceful CrossCheck(available=False).
- ★ Gemini model_id = `settings.cross_validation_model`(default gemini-3.5-flash) → `.env` 1줄로 교체(fallback gemini-3-flash-preview / gemini-2.5-flash).

## E. cost_control 가정 (CC-010)
- ★ **additive** 확장 — 기존 user tier(무료/유료) + 호출당/세션당/일일 상한 + cost_saving 보존. tier×mode→alias 표 + cross_validation 비용(Gemini 1회, gated)만 추가.
- cross_validation_enabled=True 시 호출당/세션당 상한에 Gemini 1회분 **additive 반영 권고**(제안서 §18.D). default OFF 면 비용 증가 0.

## F. 키/보안 가정 (★ 사용자 지침 계승)
- 실 키(OPENAI/ANTHROPIC/GOOGLE)는 .env user-provided + .gitignore. **파일/commit/채팅 평문 절대 금지**. registry 는 env 참조만(키 비포함).
- ★ 3개 키는 이전 노출 후 사용자 재발급 — 추가 노출 금지(handoff §3).

## G. Slice 분리 (선완료)
- S1(gateway 골격) → S2(cross_validation + Gemini 튜닝) → S3(orchestrator gated hook). 각 단계 behavior-preserving 게이트(pytest green, Envelope byte-identical). sub-agent sequential.

## H. 리스크 & 완화
| 리스크 | 완화 |
|---|---|
| gateway 도입이 기존 381 test/monkeypatch 깸 | gateway 는 신규 레이어(agents 미연결). cross-validation gated OFF + late-import. pytest 381 green 게이트 |
| alias 해석 값 drift(≠현 default) | resolve_model 단위 test 로 byte-identical 강제(A2) |
| cross-validation 발화가 Envelope 변동 | 로깅만 — orchestrator §5.5 는 Envelope 조립 전/후 무관 + graceful. test_integration_mvp 가드(A6) |
| Gemini 503/빈출력 | graceful CrossCheck(available=False) → 파이프라인 무영향. fallback model 가능 |
| flagship 기본 호출 누수 | premium_review gated/A안 미구현(NG2). cross_validation = Gemini flash 저가 1회 |
| MOA agent 수 증가 유혹 | cross_validation = Critic 추가 pass(설계 명문). agent 6 불변 |
| 키 노출 | registry env 참조만 + .env gitignore + push 전 `git diff | grep sk-/AIza` 점검 |
| 가속 빌드라 entry 누락 | ★ 본 retroactive entry 가 정식화(코드 0 변경) |
