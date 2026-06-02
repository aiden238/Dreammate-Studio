# Phase 13 — Acceptance (A1~A10 + MG1~MG3)

| ID | 항목 | 검증 | Slice |
|---|---|---|---|
| **A1** | **스키마 확장(additive)** — `Plan` 에 결핍 feature 슬롯 추가(hook_variants[]/beat visual·dialogue·caption/shots[]/thumbnail/title_candidates[]/cta/references[]/length_variants/target_audience/tone), ★ 전부 Optional default None/[] → 기존 7필드·소비자 회귀 0 | output.py diff + output_schema CC + agent-io-check PASS | S1 |
| **A2** | **output_schema contract-change(additive)** — Plan rich 슬롯 정식 등록 + CC 로그 | `docs/contract_changes/*phase-13-output-schema*` + agent_io_contract 정합 | S1 |
| **A3** | **프롬프트 확장 + P-006 bump(prompt-version-review)** — planning rich 프롬프트(rich 슬롯 채움) + P-006 v1.0.0→v1.1.0 + golden_set 회귀. ★ 기존 compact 프롬프트 보존 | prompt_registry P-006 semver + 회귀 PASS + CC 로그 | S2 |
| **A4** | **gated wiring(default OFF)** — config `rich_output_enabled` default **False** + generate/orchestrator gated 분기 | config diff + ON/OFF 분기 test | S3 |
| **A5-PP** | **flag OFF byte-identical(behavior-preserving)** — ★ `rich_output_enabled=False` 면 기존 compact 출력 100% 동일(Envelope byte-identical) | OFF 경로 회귀 test + pytest green | S3·S6 |
| **A6** | **Critic depth 반영(88점 함정 해소)** — Critic 평가에 depth_actionability 차원 additive(얕으면 감점) + P-007 bump | Critic 점수 분포(compact 얕음 감점 / rich 충족) + prompt-version-review | S4 |
| **A7** | **frontend rich 렌더(conditional)** — PlanCard(+ types·api)에 rich 필드 표시, ★ rich 있을 때만 — 기존 compact 렌더 회귀 0 + design-review | tsc 0 + build routes + design-review 7원칙 PASS | S5 |
| **A8** | **depth 재측정: 0.231 → ≥0.8** — golden_set depth_actionability(CC-011) rich 경로 재측정 목표 달성 | `eval/regression_results/phase-13-*` depth ≥0.8 | S6 |
| **A9** | **cost 재조정** — cost_control_policy rich 토큰 ↑ × 3안 재조정 + B안 잔여 B-RES-1 통합(contract-change) | cost_control_policy diff + CC 로그 | S6 |
| **A10** | **키 0** — flag ON 라이브 데모는 사용자 승인 비용, 키 평문 commit 0 (.env user-provided) | `git diff \| grep sk-/AIza` 0 | S6 |

## MG1~MG3 (메타)
| ID | 항목 | 검증 |
|---|---|---|
| **MG1** | multi-llm-validation self-form (12th, V1~V6) — Phase 13 진입 타당성(gated 롤아웃 / additive 스키마 / 첫 출력 변경 안전성) | `meta/validations/2026-06-02_phase-13-pre-entry_self.md` |
| **MG2** | contract-change — output_schema(Plan rich additive, S1) + prompt_registry(P-006/P-007 bump, S2/S4) + cost_control(S6) ★ 전부 additive/behavior-preserving | CC 로그 + prompt-version-review |
| **MG3** | P-X1 §SELF-VERIFICATION 연속 유지 — flag OFF byte-identical + 키 0 + 각 Slice sub-agent forbidden 검사 | sub-agent/commit 검사 (전 Slice) |

## ★ behavior-preserving 게이트 (A5-PP — Phase 13 핵심)
```
rich_output_enabled = False (default) → 기존 compact 출력 byte-identical (Envelope 불변)
  - generate/orchestrator OFF 경로 = 기존 단일 compact 흐름 100% 동일
  - 기존 7필드(name/concept/hook/flow/pros/risks/approach_label) 직렬화 회귀 0
  - 기존 compact SYSTEM_PROMPT 보존(rich 는 별도 ON 경로)
  - 기존 소비자(PlanCard·orchestrator·Critic) — rich 슬롯 Optional → 무영향
검증: pytest 전부 green (기존 471 + 신규 rich/gated test) + OFF byte-identical 회귀
```

## ★ depth 재측정 게이트 (A8 — 이번 phase 의 중심 산출)
```
입력: golden_set 25 (Phase 12) · depth_actionability rubric (CC-011, 13 feature 0/1)
  rich 경로 (rich_output_enabled=True) 출력 → depth_actionability 재채점
목표: depth 0.231 (Phase 12 compact baseline) → ≥0.8 (rich 운영 경로)
산출: eval/regression_results/phase-13-* (depth 재측정 + compact↔rich 대조)
★ 기획 브리프 경계 유지 (완성 대본 아님) + rich 데이터 = 실 운영 슬롯(측정 전용 아님)
```

## ★ P-006 / P-007 prompt bump 게이트 (A3·A6 — prompt-version-review)
```
P-006 (planning) v1.0.0 → v1.1.0 (rich 변형) — golden_set 회귀 + gated 단계 활성 + compact 보존
P-007 (critic)   bump (depth_actionability 차원 additive) — 기존 점수 체계 회귀 0
prompt-version-review 경유: semver 부여 + golden_set 회귀 + A/B·단계 활성 + 이전 버전 deactivation 일정
```

## 회귀 baseline (Phase 12 → Phase 13)
| 지표 | Phase 12 final | Phase 13 (목표) |
|---|---|---|
| pytest | 471 | **471 + 신규(rich/gated/depth) green** (기존 471 수정 0 — flag OFF byte-identical) |
| 운영 출력 | compact (depth 0.231) | **rich 경로 depth ≥0.8** (flag ON) / **compact byte-identical** (flag OFF default) |
| `Plan` 스키마 | 7필드 | **+rich 슬롯 (전부 Optional additive)** |
| P-006 prompt | v1.0.0 | **v1.1.0** (rich, prompt-version-review) |
| Critic depth | 미반영(88점 함정) | **depth_actionability 차원 반영** (얕으면 감점) |
| frontend | compact 렌더 | **rich conditional 렌더** (/generate 화면) |
| cost_control | (Phase 11 CC-010) | **rich 토큰 재조정 + B-RES-1 통합** |
| 키 commit | 0 | **0 유지** |

## qa-check (Phase 13 — release gate)
- 제품 phase(런타임 有) — MVP 범위(기획 브리프, product_boundary) + output_schema/agent_io 정합 + flag OFF byte-identical(behavior-preserving) + 모바일 화면(rich 카드) + 키 0 게이트. ★ 첫 출력 변경이므로 gated(default OFF) + additive 가 핵심 안전 장치.
