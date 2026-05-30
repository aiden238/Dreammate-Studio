# ADR-033 — Phase 9.5 eval-run Harness (mock-deterministic primary + 실 LLM mode)

> Date: 2026-05-31
> Status: Accepted
> Phase: 9.5 (eval-run 정식화 + Critic deprecated 0–5 Full 제거)
> Slice: 2~3 (구현 — eval module) / Slice 1 (본 ADR 결정 + eval-design Skill 첫 정식)
> Related: ADR-018 (phase_6_critic_canonical — CriticEvaluation canonical), ADR-029 (phase_8_prompt_registry_semver — P-007 semver + normalize helper), ADR-032 (phase_9_critic_canonical_wiring — critic step canonical live), ADR-034 (phase_9_5_critic_deprecated_removal — 본 eval baseline 후 제거)
> Skill: **eval-design (★ 첫 정식 — §eval-design 결과 통합)** + eval-run (Slice 2~3 첫 정식 실행)

## Context

영상기획 AI 에이전트는 회귀 검증 자산을 보유하나 **실행 runner 가 없음**:

- `eval/golden_set.md` — 회귀 케이스 단일 출처. **GS-001 ~ GS-011 (11 케이스)** 정의 (§2). 각 케이스는 markdown 안 ` ```yaml ` 블록(case_id / mode / prompt_target / input / expected_path / expected_output{body_keys + validation + passing_criteria} / notes). priority P0/P1/P2 (§3).
- `eval/regression_eval.md` — 실행 절차/임계 정의 (5 차원 + §5 게이트 + §6 CI). 단 **runner 코드 미구현** — golden_set 케이스를 실행/비교하는 `backend/fastapi/eval/` module 없음.
- `eval/video_planning_eval.md` — 8차원 채점 정의 (§2 차원 + §5 임계값).
- Skill `eval-design` / `eval-run` 모두 **unused** (skill_usage_log: 0/0).
- revise loop effect — Phase 4.5 D6 부터 **미측정** (누적 6회 deferred).

> ★ 케이스 수 정정: entry plan 일부 문서가 "47 케이스" 로 기재되어 있으나 현 `golden_set.md` v1.0.0 §2 는 **GS-001~GS-011 (11 케이스)** 만 정의 (§0/§3 명시). 본 ADR + runner 는 실제 11 케이스를 단일 출처로 한다. 케이스 신규 추가(11 → 확대)는 NG10 (Phase 10+ — eval-run §7 절차 후속). loader 는 케이스 수에 무관하게 GS-XXX 블록을 파싱하므로 설계 영향 없음.

**Gap (Phase 9 개선 §4 + Phase 4.5 D6)**:
- golden_set 케이스를 자동 실행/채점/비교하는 runner 부재 → prompt/RAG/모델 변경 시 회귀 자동 감지 불가 (확정 결정 [20] semver 회귀 baseline 미작동).
- Critic deprecated 0–5 제거(ADR-034)의 안전망 부재 — canonical-only 품질이 deprecated 0–5 시절과 동일함을 측정할 수단 없음.

## Decision

### 1. `backend/fastapi/eval/` module 신규 (mock-deterministic primary)

| 파일 | 역할 |
|---|---|
| `eval/__init__.py` | module export |
| `eval/golden_set_loader.py` | golden_set.md → 11 GS 케이스 `{id, mode, prompt_target, input, expected_properties}` 구조화 (단일 출처 파싱) |
| `eval/runner.py` | golden_set 회귀 — **mock-deterministic primary** (실 LLM 미호출, 결정적 fixture/seed) + 실 LLM **mode flag**(`--mode=real`) + schema/structural 채점 + 비교 모드 + 임계값 게이트 |
| `eval/revise_effect.py` | revise loop 개선 효과 metric — revise attempt별 canonical overall_score(0–1) delta (mock-based) |
| `eval/report.py` | `regression_results` 출력 (eval-run §5 형식) |

- **mock-deterministic primary (사용자 결정, V1)**: runner 는 실 LLM(`run_critic`/Planning)을 호출하지 않고 결정적 mock pipeline 출력(고정 fixture/seed)을 golden_set `expected_*` 와 비교. 비결정성(temperature/모델 변동) 0 → 동일 입력 동일 결과 → **CI per-commit 가능 + 비용 0**.
- **실 LLM mode flag (문서)**: `--mode=real` 로 실 LLM 8차원 의미 채점(intent_fit 등) — 비결정적 → 운영 단계 야간 배치 (NG2). 본 phase 는 mode flag + 문서만 (실행 X).
- **출력**: `eval/regression_results/phase-9.5_{date}.md` (eval-run §5 형식 — 요약 점수 + 임계값 점검 + 결정).

### 2. §eval-design 결과 (★ eval-design Skill 첫 정식)

eval-design Skill 절차(7단계)를 적용하여 다음을 설계 — 본 ADR 에 통합.

#### 2.1 golden_set executable format (loader 설계)

```
golden_set_loader.load_golden_set() -> list[GoldenCase]
  GoldenCase = {
    id: "GS-XXX",            # case_id (GS- prefix 필터)
    mode: discovery | quick,
    prompt_target: "P-XXX" | "full_flow" | "RAG ...",
    input: { user_message, brand_context, rag_context, brand_memory },
    expected_properties: {
      body_keys: [...],      # schema 준수 검증 키
      validation: [...],     # structural 룰 (자동/비자동 분류)
      passing_criteria: [...]
    }
  }
```

- golden_set.md ` ```yaml ` 블록 → `yaml.safe_load` → `case_id` 가 `GS-` prefix 인 dict 만 케이스 수집 (§1 template 블록 / §5.2 jsonl 예시 블록 배제).
- **golden_set.md 단일 출처** (loader 는 파싱만 — 케이스 정의/수정 X). 케이스 수정은 contract-change (golden_set.md 는 contract).

#### 2.2 채점 차원

| 차원 | mock (primary) | 실 LLM mode | 비고 |
|---|---|---|---|
| **schema 준수** | ✅ 100% 필수 | ✅ | Envelope/Plan/CriticEvaluation Pydantic 검증 |
| **structural** | ✅ | ✅ | plan 3개 / hook 존재(min_length 10) / flow 비트(2~8) / 광고 단어 부재 / 차단 단어 0 / 배열 길이·정확 매칭 룰 |
| 8차원 의미 채점 (intent_fit 등) | ❌ N/A | ✅ P-007 채점 | 비결정적 — 실 LLM mode 만 (video_planning_eval §2) |
| 다양성 (cosine sim) | ❌ N/A | ✅ | 실 embedding 필요 |
| 비용 / latency | ❌ N/A | ✅ | 실 호출 필요 |

- validation 규칙 **자동/비자동 분류**: 정확 매칭/길이/배열 길이/광고·차단 단어 부재 = mock 자동. "의미 중첩 < 30% (LLM-as-judge)" / missing_info 의미 판단 = 실 LLM mode.

#### 2.3 revise effect metric

- `revise_effect`: revise attempt별 canonical overall_score(0–1) delta — `attempt 0 (초기 critic)` → `attempt 1 (revise 후 재평가)` → `attempt 2`. mock fixture 결정적 → `delta = score[n] - score[n-1]` + 방향성(증가/정체/감소) 집계. `revise_history`(ReviseAttempt — Phase 4.5 ADR-016 구조) 정합. canonical(0–1) 기준 (deprecated 0–5 불필요 — ADR-034 제거 정합). 실 effect 크기는 실 LLM mode (U5).

#### 2.4 임계값 게이트 (eval-run §6 mock 강제)

```
| 지표                    | 임계값      | 위반 시        | mock 강제 |
|------------------------|------------|----------------|-----------|
| schema 준수율           | < 100%     | 즉시 fail       | ✅        |
| 평균 canonical 점수 하락 | > 0.3      | fail            | ✅ (baseline diff) |
| 광고 표현 검출          | > 5%       | fail            | ✅ (정확 매칭) |
| 차단 단어 검출          | > 0%       | fail            | ✅ (정확 매칭) |
| P0 케이스 통과율         | < 100%     | 즉시 fail (차단) | ✅        |
| 비용 증가               | > 30%      | cost-review     | 실 LLM mode |
| latency 증가            | > 20%      | 경고            | 실 LLM mode |
| 다양성 하락             | > 0.1      | 경고            | 실 LLM mode |
```

- **차단 단어 단일 사전**: video_planning_eval brand_consistency("혁신적/최고의/완벽한/최선의/최첨단/획기적/1위/압도적") + llm_security 차단 단어 + GS-004 1차 단어 통합 참조. LLM 출력만 검사 (사용자 입력 예외 — GS-004 notes).
- 위반 시 runner verdict=fail + report blocker 기록 → CI 차단.

## Constraints

- **mock-deterministic primary ★**: runner 실 LLM 미호출 (결정적 fixture/seed) — schema/structural 차원. 의미 품질(hook 매력도 / 의도 적합도)은 대리 못 함 (U2) → 실 LLM 8차원 채점은 `--mode=real` flag + 운영 야간 배치 문서 (NG2). 비용/latency/다양성 임계값도 실 LLM mode.
- **golden_set.md 단일 출처 ★**: loader 는 golden_set.md 파싱만 (케이스 정의/수정 X). 본 phase 에서 eval/golden_set.md 수정 0 (케이스 확대 NG10 — Phase 10+). 케이스 수정 시 contract-change (golden_set.md 는 contract).
- **RAG eval_rubric Phase 10+ ★**: RAG eval_rubric → golden_set 정식화는 **Phase 10+** 이관 (NG1, 사용자 결정). 본 phase 는 golden_set 회귀 + revise effect 만.
- **회귀 0**: eval module 신규 — 기존 backend 코드 0 변경 (agents/orchestration/routers/db/schemas 불변). Slice 2~3 editable = eval/ + scripts/eval_run.ps1 + tests/test_eval_runner + test_revise_effect.
- **deprecated 제거 baseline ★**: 본 eval runner 의 canonical-only 품질 baseline 이 ADR-034 Critic deprecated 0–5 제거의 안전망 (Slice 2~3 eval → Slice 4 제거 → 동일 eval 재실행 회귀 0).

## Trade-offs

| 선택 | 채택 사유 | 미채택 후보 |
|---|---|---|
| mock-deterministic primary | CI per-commit + 비용 0 + 결정적 회귀 baseline + deprecated 제거 안전망 | 실 LLM primary — 비결정적 + 비용($0.5/회) + CI 불가 (운영 단계로 분리) |
| golden_set.md 단일 출처 | 중복 정의 0 + contract 일관 | loader 내 케이스 재정의 — drift 위험 |
| 11 케이스 그대로 | baseline 구축 충분 + scope 집중 | 케이스 확대 — NG10 (Phase 10+) |
| revise_effect mock | Phase 4.5 D6 첫 해소 + 메커니즘 회귀 | 실 revise effect — 실 LLM mode (U5) |
| 임계값 mock 4 + 실 LLM 3 | mock 가능 차원(schema/광고/차단/점수)만 강제 | 전체 mock — 비용/latency/다양성 실 호출 불가 |

## Verification

- `pytest backend/fastapi/tests/test_eval_runner.py` (Slice 2 신규):
  - `test_load_golden_set` — golden_set.md → 11 GS 케이스 파싱 (GS- prefix 필터, template/예시 블록 배제)
  - `test_mock_pipeline_deterministic` — 동일 입력 2회 동일 출력 (결정성)
  - `test_schema_compliance_100` — schema 준수율 100% 강제
  - `test_blocked_word_fails` — 차단 단어 검출 시 verdict=fail
  - `test_ad_word_threshold` — 광고 표현 > 5% fail
  - `test_threshold_gate_p0` — P0 < 100% 즉시 fail
- `pytest backend/fastapi/tests/test_revise_effect.py` (Slice 3 신규):
  - `test_revise_attempt_score_delta` — attempt 0→1→2 canonical score delta
  - `test_revise_direction` — 증가/정체/감소 방향성 집계
  - `test_no_revise_zero_delta` — revise 없는 케이스 delta=0
- `eval/regression_results/phase-9.5_{date}.md` 생성 (eval-run §5 형식) — canonical-only 품질 baseline (ADR-034 제거 안전망).
- **회귀 0**: 기존 baseline test 수정 0 (eval module 신규 추가만).

## References

- `.claude/skills/eval-run/SKILL.md` (§1 평가 종류 + §4 채점 + §5 결과 형식 + §6 임계값 — Slice 2~3 실행 근거)
- `.claude/skills/eval-design/SKILL.md` (절차 7단계 — §eval-design 결과 도출, ★ 첫 정식)
- `eval/golden_set.md` (회귀 케이스 단일 출처 — GS-001~GS-011, §1 표준 형식 + §3 우선순위 + §4 실행 정책)
- `eval/video_planning_eval.md` (8차원 채점 §2 + 임계값 §5 — 차단 단어 사전 brand_consistency)
- `eval/regression_eval.md` (회귀 5차원 + §5 게이트 + §6 CI)
- `backend/fastapi/agents/critic.py` (run_critic 0–5 / normalize_to_canonical 0–5→0–1 — revise_effect canonical 기준)
- `backend/fastapi/schemas/output.py` (Envelope/Plan/CriticEvaluation — schema 준수 검증 + ReviseAttempt)
- `meta/validations/2026-05-31_phase-9.5-pre-entry_self.md` §V1/V2/V3/V6 (mock-deterministic / loader / revise effect / 임계값)
- `docs/decisions/phase_9_5_critic_deprecated_removal.md` (ADR-034 — 본 eval baseline 후 제거)
- `phases/active/phase-9.5-eval-run/{goals,scope,non_goals,assumptions,multi_slice_plan}.md`
