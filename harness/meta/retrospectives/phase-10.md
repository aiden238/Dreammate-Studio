# Phase 10 회고 — MVP 통합 테스트 (제품 phase, scope C)

> 종료일: 2026-05-31
> 유형: 제품 phase (런타임 변경 有, ~12~15h) — meta-phase detour(M0~M3) 종료 후 제품 복귀
> 결과: ✅ A1~A10 + MG1~MG4 PASS / MVP end-to-end 통합 PASS(결함 0) / pytest 339→381 / 배포 Gate A 통과
> 트리거: phase-complete v1.2.0 §7

---

## 1. 무엇을 했나 (4 Slice + entry)
- **entry**: multi-llm-validation formal 10th (V1~V6 PASS).
- **S1 (7fa5b00)**: MVP end-to-end 통합 test(12) + smoke_test_phase_10(12) + scenario_sim v8(36). pytest 339→351. 전 흐름 정상 연결.
- **S2 (436b224)**: P-AUX-2 brand_memory_extractor agent(heuristic, graceful, PII) + CC-008(agent_io v1.4.0) + additive wiring. pytest 351→365.
- **S3 (56b541c)**: 실 LLM eval mode capability(default mock) + RAG eval_rubric v1.0.0 + golden_set 11→15 + CC-009. pytest 365→381.
- **S4 (close)**: 배포 게이트 A~G + ADR-038 + 회고 + archive.

## 2. 핵심 결과
- **MVP end-to-end 통합 PASS** — Discovery+Quick→3안→Critic revise canonical→save→select→feedback→SSE 전 흐름 chaining 검증, **연결 결함 0**. 9.5 phase 누적이 실제로 연결됨을 입증.
- **pytest 339 → 381** (+42: 통합 12 + P-AUX-2 14 + eval 16). 기존 339 green(의도된 eval delta 제외 — golden_set 11→15 count 단언 + real NotImplementedError→graceful fallback, CC-009 문서화).
- **P-AUX-2 활성** — heuristic 추출(LLM 0, 비용 0), feedback hook additive(proposed-only), agent-io-check PASS. Phase 9 준비 → 실현.
- **eval 성숙** — 실 LLM mode capability(opt-in, default mock) + RAG rubric + golden_set 15 + eval-run mock gate PASS.
- **배포 Gate A 통과** + B~G 준비/정의.

## 3. 잘된 것
1. **behavior-preserving 일관** — 4 Slice 모두 기존 endpoint/agent 0 수정(신규 추가 + additive hook). 기존 339 green. P-BEHAVIOR-PRESERVING-001 정신을 제품 통합 phase 로 확장.
2. **통합 test 가 연결성 입증** — 개별 단위 test 가 못 잡는 piece 간 연결을 chaining 으로 검증, 결함 0 확인 → 배포 자신감.
3. **eval mode 화해** — "범위 C 실 LLM 활성" + "mock 유지"의 표면 모순을 capability(구축) vs default(실행) 로 깔끔히 분리. 비용 0 유지 + 실 LLM opt-in 경로 확보.
4. **P-AUX-2 heuristic 선택** — ADR-031 confidence 규칙이 결정적이라 LLM 불요 → 비용 0 + 결정적 test. 과한 LLM 도입 회피.
5. **키 0 / PII 마스킹** — 실 키 커밋 0(placeholder만), 추출 PII 마스킹(단일 출처 재사용).

## 4. 아쉬운 것 / 한계
1. **실 LLM eval 미실행** — capability 만(default mock). 실 품질 baseline 은 Gate D(키 주입) 시점. 표현·구축까지.
2. **통합 mock-deterministic** — 실 Supabase/LLM 통합은 Gate B/C 실 환경. 본 phase 는 흐름 연결성(mock)까지.
3. **P-AUX-2 proposed-only** — 자동 INSERT 0(안전). 실 brand memory promotion 은 Phase 11+.
4. **Gate E/G 미준비** — 운영 인프라/키/사용자 모집 단계.

## 5. 패턴
- **P-INTEGRATION-MVP-001 (신규 후보)** — 누적 phase 를 end-to-end chaining test 로 통합 검증(개별 단위 test 위에 연결성 레이어) + smoke/scenario 통합 게이트. behavior-preserving.
- **P-BEHAVIOR-PRESERVING-001 update** — 제품 통합 phase 에서도 기존 0 수정 + 신규/additive 만(4 Slice).
- **P-CONTRACT-FIRST-001 update** — CC-008(agent_io P-AUX-2) + CC-009(eval) 누적 10회.
- **P-X1-EFFECT-001 update (60연속)** — S1·S2·S3 sub-agent (S4 close main).
- **P-CAPABILITY-DEFAULT-OFF-001 (신규 후보)** — "활성"(capability 구축) vs "default 실행" 분리로 비용/안전 모순 화해 (실 LLM eval mode).

## 6. 다음 단계
- **배포 Gate B~G** — staging→알파→베타(실 LLM opt-in)→제한사용자→비용/성능→운영. 키·인프라 user-provided + 운영 phase.
- **Phase 11+**: 4계층 full linkage / SSE async worker / prompt A/B / 자동 promotion / 실 LLM eval default 전환 / M3 새 GAP 3(G9/G10/G11) 반영.

## 7. 메타 정합
- 제품 로드맵 복귀(meta detour 종료) — MVP 통합 완료 + 배포 게이트 정의.
- behavior-preserving + eval default mock + 키 0 + PlanCard/component_map 0줄 — 안정화 phase 규율 유지.
- ★ Phase 1~10 = MVP end-to-end 통합 완료 + 배포 Gate A 통과.
