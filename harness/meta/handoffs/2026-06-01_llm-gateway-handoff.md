# Session Handoff — LLM Gateway (Phase 11 A안) + 누적 작업

> 작성: 2026-06-01 (컨텍스트 압축 준비)
> 목적: 긴 세션 종료/압축 후 재개를 위한 상태 보존. PROJECT_STATE/PHASE_REGISTRY/proposals 가 canonical, 본 문서는 "지금 어디까지·다음 무엇" 요약.

---

## 1. 이번 세션 누적 완료 (전부 commit·push 됨)

| 작업 | 상태 |
|---|---|
| Phase M1 (Meta-Factory dry-run, 팟캐스트) | ✅ archive |
| Phase M2 (8 GAP machinery 반영, CC-007) | ✅ archive |
| 검증5 eval-run 표본 (mock-deterministic) | ✅ |
| Phase M3 (이질 도메인 범용성 2차, 재무) | ✅ archive (새 GAP 3 백로그 improvement_reports) |
| Phase 10 (MVP 통합 테스트, scope C) | ✅ archive (pytest→381, P-AUX-2 agent, eval golden_set 11→15, 배포 Gate A) |
| **LLM Gateway 제안서** | ✅ `meta/proposals/2026-05-31_llm-gateway-design.md` (§18 A/B 단계화 + 2026-06 모델 + 키 요건) |
| **Phase 11 A안 (LLM Gateway)** | ✅ S1·S2·S3 — 아래 §2 |
| Node.js 설치 | ✅ v24.16.0 (`C:\Program Files\nodejs\`) — frontend npm 가능 |

★ origin/main = `1ee1c08`. 원격에 협업자 docs/ci 프레젠테이션 커밋 26개 공존(rebase 됨). 로컬 clean(`.env`/`사진/`/`새 텍스트 문서.txt`만 untracked).

---

## 2. ★ Phase 11 A안 (LLM Gateway) 현황 — 진행 중

**목표**(제안서 §18.A): OpenAI 보존 + Critic 교차검증만 추가(self-bias↓). agent 는 alias 만 알고 gateway 가 provider 결정 → 후속 provider 추가 = adapter+registry, agent 0 변경.

| Slice | 내용 | commit |
|---|---|---|
| S1 | `llm/` gateway 골격 (types/errors/registry/aliases/gateway + openai/gemini adapter) | e1422a6 |
| S2 | cross_validation 모듈(cross_validate+compare) + Gemini adapter 튜닝(thinking_budget=0 + 503 재시도 + text fallback) | f382b6e(rebased) |
| S3 | orchestrator gated hook (moa_orchestrator critic 단계 후, default-off, **로깅만**, Envelope 불변) | 1ee1c08 |

- **pytest 435 passed** (기존 381 + gateway 31 + cross-val 19 + wiring 4). ★ behavior-preserving — 기존 코드 0 수정, gated default-off.
- **alias 표**: planning/intent/rewriter/memory→gpt-4o-mini, critic={standard:gpt-4o, cost_saving:gpt-4o-mini}, cross_validation→gemini-cross(config `cross_validation_model`).
- **라이브 검증 완료**: gateway 경유 OpenAI 실제 생성 ✅. cross_validate Gemini 독립평가(8차원) + compare(consensus/divergence) ✅. (gemini-2.5-flash 0.7375 vs OpenAI 0.72 → consensus 입증.)
- **gated**: `cross_validation_enabled` default **False** → orchestrator hook 미발화(기존 흐름 100% 동일). True 시 critic 후 Gemini 교차검증 1회 + 로깅.

---

## 3. 키 / 모델 상태 (★ 보안)

- **`.env`** (`harness/backend/fastapi/.env`, gitignore): OPENAI / ANTHROPIC / GOOGLE 3개 — **전부 인증 OK** (`python scripts/verify_llm_keys.py`).
  - ★ 이 3개 키는 **이전에 채팅에 노출됐다가 사용자가 재발급**한 것으로 보임. 추가 노출 금지. Anthropic 오타(`ssk-ant`→`sk-ant`) **수정 완료**.
- **Gemini 모델**:
  - 커밋된 기본값 `cross_validation_model = gemini-3.5-flash` (사용자 확정).
  - ⚠️ **2026-06-01 현재 gemini-3.5-flash 503 지속**(Google 수요 급증, retryDelay 22s). graceful 처리됨.
  - **임시 fallback**: `gemini-3-flash-preview`(작동 확인) 또는 `gemini-2.5-flash`(작동). 라이브 사용 시 `.env` 에 `CROSS_VALIDATION_MODEL=gemini-3-flash-preview` 추가(임시). 3.5-flash 회복되면 제거 → 기본값 복귀.
- ★ 키는 .env 에만. 코드/commit/채팅 평문 절대 금지. registry 는 env 참조만.

---

## 4. 다음 작업 (재개 시)

> ★ 2026-06-01 update: ①②③-1 완료. 아래 1·2·3 은 ✅, 남은 것은 4(B안)·5(frontend).

1. ✅ **Gemini 3.5-flash 회복 확인** — 회복됨(기본값 그대로). 임시 override는 .env 에 쓴 적 없음(제거 불요).
2. ✅ **Phase 11 정식화** — entry 8 + closing + ADR-039 + CC-010(cost_control §11/§12 tier×mode→alias) + 회고 + archive(`phases/archive/phase-11-llm-gateway/`) + state/registry + P-X1 63. commit 3859663.
3. ✅ **full 라이브 /generate 데모** — quick wizard(start→quick.initial→clarify→direction→generate) + flag ON → 실 OpenAI 3안+Critic + gemini-3.5-flash 교차검증 → 로그 `cross_validation: model=gemini-3.5-flash gemini=0.65 openai=0.8 agreement=True -> consensus`. Envelope 불변(200, 3안 정상).
4. **B안** (제안서 §18.B) — 3-provider. 키 3개 준비됨.
   - ✅ **S1 완료** (cac2b9b + b060c2b): Anthropic adapter + registry Claude(haiku/sonnet)·Gemini + gateway 3-provider 분기 + config. pytest 435→**452**. ★ **3-provider 라이브 연결 입증**(GPT+Claude haiku/sonnet+Gemini 전부 gateway 호출 OK). 버그(sonnet prefill 미지원 400)→adapter JSON prefill 제거(system 지시문)로 수정. **둘 다 push 됨**(origin/main=b060c2b).
   - ⚠️ **관찰**: Claude haiku 는 JSON 을 ` ```json ``` ` 펜스로 감쌈(sonnet 은 clean). S2 에서 펜스 stripping 견고화 필요.
   - **남은 S2**: 3-plan 슬롯 다양화(plan_a→GPT, plan_b→Claude, plan_c→Gemini) alias 추가(registry 엔 Claude/Gemini 모델 있으나 **이를 가리키는 alias 아직 0** — `gateway.complete('claude-haiku')` 는 KeyError) + planning 경로 gated 연결 + 펜스 stripping + cost_control 재조정(신모델 5~7배). cost: registry 키만 추가됨, alias/wiring/cost 가 S2.
5. **frontend 손-검증** — Node 설치됨. `cd harness/apps/web && npm install && npm run dev` → localhost:3000 ↔ 백엔드 localhost:8000. (실 기획 생성은 OPENAI_API_KEY 필요 — .env 있음.)
6. **잡정리**: `harness/backend/fastapi/새 텍스트 문서.txt`(0바이트, 불필요) 삭제 가능.

---

## 5. 핵심 gotcha (재개자 주의)

- **behavior-preserving 필수**: 기존 endpoint/agent/test 0 수정 + 신규/additive만. pytest 435 가 baseline.
- **monkeypatch**: moa_orchestrator 는 `plans_router.run_*` 를 call-time namespace 로 호출(테스트 fixture 보존). late-import 유지.
- **cp949 콘솔**: Windows 콘솔이 cp949 → 스크립트 출력에 em-dash(—)/이모지 쓰면 UnicodeEncodeError. `set PYTHONIOENCODING=utf-8` + ASCII 출력.
- **config get_settings() lru_cache**: env override 는 import 전에 os.environ 설정.
- **원격 협업**: origin/main 에 협업자 docs/프레젠테이션 커밋이 들어옴 → push 전 `git pull --rebase` (백엔드 파일과 disjoint 라 충돌 0).
- **키 보안**: .env gitignore 확인됨. push 전 항상 `git diff | grep sk-/AIza/AQ.` 점검.

---

## 6. 참조 문서
- `meta/proposals/2026-05-31_llm-gateway-design.md` (설계 + A/B + 키/모델 + Codex 티켓)
- `scripts/verify_llm_keys.py` (키 인증 검증, 마스킹)
- `backend/fastapi/llm/` (gateway 구현), `tests/test_llm_gateway.py`/`test_llm_cross_validation.py`/`test_cross_validation_wiring.py`
- `PROJECT_STATE.md` / `PHASE_REGISTRY.md` (canonical 상태)
