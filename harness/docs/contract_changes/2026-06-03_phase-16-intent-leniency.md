# Contract Change Log — Phase 16 P-001 Intent 완화 + 차단 UX 가이드

> ID: CC-021 | Status: **decided + applied** (2026-06-03) | Date: 2026-06-03
> Decision: Intent(P-001) 오반려 해소 — 콘텐츠 토픽 **기본 수용**(애매하면 수용), 명백한 도메인 밖만 거부. + 차단 시 **재작성 가이드(구체 예시)** UX.
> 대상: `backend/fastapi/agents/intent.py`(SYSTEM_PROMPT + PROMPT_VERSION v1.0.0→v1.1.0) · 차단 메시지(generate.py / moa_orchestrator) · `apps/web/lib/errors.ts`(INV-001 fallbackBody)
> Author: Claude (Phase 16) | 근거: 사용자 피드백 — 맨 토픽("대학생활 TIP")이 정보질문으로 오반려됨
> Skill: prompt-version-review + contract-change

## 1. 변경 요약
| 대상 | 변경 |
|---|---|
| `intent.py` SYSTEM_PROMPT | 거부 예시 "단순 정보 검색(위키/뉴스)" 제거 → **콘텐츠 토픽 기본 수용**(맨 토픽도 영상 아이디어로 간주) + 애매하면 수용 + 정보형/팁/리뷰도 영상기획. 거부 = 명백한 도메인 밖(날씨/코딩/잡담)만. |
| `intent.py` PROMPT_VERSION | **v1.0.0 → v1.1.0** (semver minor — 분류 정책 완화, output schema(intent_ok/reason) 불변) |
| `generate.py` / `moa_orchestrator.py` INV-001 user_message | "다른 방식으로 도와드릴까요?" → **재작성 가이드 + 구체 예시**("예: '대학생활 꿀팁 30초 쇼츠'...") |
| `apps/web/lib/errors.ts` INV-001 fallbackBody | 동일 가이드(구체 예시)로 갱신 |

## 2. 회귀 안전
- Intent **output schema 불변**(intent_ok/reason). 분류 동작만 완화(수용↑).
- pytest 536→**537**(신규 prompt-leniency 가드 1). 모든 Intent 테스트는 run_intent **mock** → 프롬프트 변경 무영향. 의도 delta: P-001 version 단언 v1.0.0→v1.1.0 (test_intent + test_prompt_registry_consistency).
- ★ INV-001 user_message 문자열 단언 테스트 없음 → 메시지 변경 회귀 0.

## 3. 라이브 검증 (run_intent 직접)
```
PASS  "대학생활에 필요한 지식들(TIP들)"  ← 사용자 원래 차단 입력, 이제 통과
PASS  "대학생활 팁" / "자취 요리"          ← 맨 토픽 수용
BLOCK "오늘 날씨 어때"                     ← 도메인 밖 거부 유지
BLOCK "이 코드 디버깅 해줘"                ← 도메인 밖 거부 유지
```
→ 오반려 해소 + off-domain 거부 유지 확인.

## 4. 미결 / 후속
- registry 정식 매핑 drift: intent 는 registry P-AUX-1(intent_filter)이 정식 home이나 코드 PROMPT_ID="P-001"(Phase 1 임시). 본 CC 는 코드 상수 bump + 테스트 미러까지. 정식 P-AUX-1 정렬은 별도(pre-existing drift).
- 위저드 mock 카드(P-002~005)는 본 변경 무관(per-step 실 LLM = PARKED PKM/RAG).

## 5. Rollback
- intent.py SYSTEM_PROMPT/PROMPT_VERSION + INV-001 메시지 + errors.ts git revert → v1.0.0(엄격) 복귀.

## 6. 변경 이력
- 2026-06-03: Phase 16 — P-001 v1.0.0→v1.1.0 Intent 완화(CC-021) + INV-001 재작성 가이드 UX.
