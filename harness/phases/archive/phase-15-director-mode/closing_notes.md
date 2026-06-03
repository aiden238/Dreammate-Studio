# Phase 15 — Closing Notes (director 모드, output_mode 3rd tier)

> 종료: 2026-06-03 | director API 라이브 검증 PASS + 사용자 브라우저 확인 후 phase-complete.

## acceptance 최종 판정
| ID | 항목 | 판정 | 근거 |
|---|---|---|---|
| A1 | output_mode enum 일반화(backward-compat) | ✅ | config + effective_output_mode + test (S1) |
| A2 | director 스키마 슬롯(additive) | ✅ | DirectorScene + Plan 3슬롯 + DIRECTOR_FIELDS + output_schema §8.1 v1.3.0 + agent-io-check (S1, CC-017) |
| A3-PP | compact/rich byte-identical | ✅ | model_dump_for_mode + pytest 508→536(기존 508 수정 0) |
| A4 | P-006 director 프롬프트 v1.2.0(gated) | ✅ | DIRECTOR_SYSTEM_PROMPT + prompt_registry v1.2.0 (S2, CC-018) |
| A5 | gated wiring(output_mode 분기) | ✅ | planning/critic/orchestrator/generate/plans 분기 (S3) + ★ S6 director Plan-read 수정(ce6cf99) |
| A6 | Critic director 차원(gated) | ✅ | retention_design + DIMENSIONS_DIRECTOR(10) + P-007 v1.3.0 + agent-io-check (S4, CC-019) |
| A7 | frontend director 조건부 | ✅ | PlanCard director 3섹션 + lib/types DirectorScene (S5) |
| A8 | director depth 측정 + cost | ✅ | director 라이브 검증(슬롯 충족 + critic 10차원) + cost_control §15 (S6, CC-020) |
| A9 | 키 0 | ✅ | 평문 키 commit 0 |

→ **A1~A9 전부 PASS** (라이브 API 검증으로 director end-to-end 동작 확인).

## 라이브 검증 중 발견·수정 (정직 기록)
1. **Intent 오반려**: 맨 토픽("대학생활 TIP")을 Intent(P-001)가 "정보 질문"으로 오분류 → INV-001 차단. **별개 UX 이슈** — S6 종료 후 다음 작업(Intent 완화 + 가이드).
2. **director Plan-read wiring 누락**(핵심): generate.py + moa_orchestrator(×2)가 LLM dict 에서 rich 만 읽고 director 3필드 미read → 항상 빈 출력. S3 wiring 에서 빠진 부분. → director read 추가(fix ce6cf99). 보조: 프롬프트 강화 + max_tokens 3500.
   - ★ 학습: 새 출력 슬롯 추가 시 **스키마(S1)·프롬프트(S2)·직렬화(S3)뿐 아니라 Plan 구성 read 도 함께 wiring** 해야 한다(rich 때도 동일했어야).

## 후속 / 미결 (사용자 플래그)
- ★ **director 품질 보강**: 사용자 — "초안 수준, 대본 직접 쓰기엔 부족". = product_boundary("기획 브리프") 부합. 깊이/품질 보강 = 이후 phase(commercial_viral 10섹션 + PKM/RAG 데이터레이어). 로드맵 ③.
- **Intent 오반려 개선**(다음 작업): P-001 완화(콘텐츠 토픽 기본 수용) + 차단→가이드 UX.
- **director Plan-read 회귀 테스트**: 현재 라이브 API + 536 으로 검증. 단위 가드 테스트는 후속 권장.
- 검증 보강(human review 실채점 + 전수 eval) = 로드맵 ②.

## 산출물
- 커밋: entry(e70489d)/plan(cd45030)/S1(d411bd1)/S2(c70a78c)/S3(97aa571)/S4(3df172a)/S5(2ee269c)/S6 fix(ce6cf99) + close.
- 신규 endpoint/agent 0 (기존 Planner/Critic mode 확장). pytest 508→536. CC-017/018/019/020.
