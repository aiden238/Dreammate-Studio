# 세션 핸드오프 — critic 품질 연구 아크 (2026-06-21)

> 다음 새 세션이 이 문서만 읽고 이어받도록 작성. 모든 산출물은 **브랜치 `phase-29-agent-ux`**
> 에 커밋됨(main 미머지). worktree `C:/Users/songb/dreammate-p27/harness` (경로는 harness 기준).
> ⚠️ 이전 세션이 31MB+ 로 매우 무거워 종료 → 본 핸드오프로 컨텍스트 리셋 후 재개 권장.

---

## 0. TL;DR — 지금 어디 / 다음 무엇

**이번 아크 = "88점 함정"(critic 낙관편향) 정량 규명 → cross-provider judge로 해소 →
개선 출력물 before/after 측정.** 3대 발견 전부 커밋·문서화 완료. 발표용 패키지 완성.

**다음 액션 (우선순위):**
1. **rater B(팀원 human 채점) 도착 시** → `python scripts/analyze_blind_ab.py --key eval/human_review/2026-06-15-calib-ab-key.json --rater <A.json> --rater <B.json>` → inter-rater κ + 정식 N=2 리포트. (현재 rater A N=1 예비만.)
2. **P-006 생성 프롬프트 변경** → B0/B1 리포트 §7 stub 기반 `prompt-version-review` 절차. 검증된 표면 레버(후크 각색·고유명/숫자 구체화·타깃 "예:" 명시)만, **할루시네이션 라벨 강제 + 과확장 금지 가드** 포함.
3. **differentiation = 별도 RAG/PKM grounding 트랙** (B0/B1이 입증: 개념층 차별화는 프롬프트로 안 됨, 실데이터 연결 필요).
4. **CODEX 독립 교차검증** (핸드오프 `meta/handoffs/2026-06-21-codex-improved-output-ab.md` 준비됨, `-codex` 산출물명).
5. **Phase 28/29/30 정식 close** (P0 이월: archive 이동 + 회고). + research 커밋 **main 머지/푸시**.
6. (선택) **consensus-min** 배선(OpenAI+Claude 더 엄격한 verdict 채택, 안전 default 후보).

---

## 1. 이번 세션 성과 (커밋)

| 커밋 | 내용 |
|---|---|
| `c82ed9b` | blind 채점 도구(HTML) + 10케이스 실 LLM 생성 (gen_blind_ab_cases.py) |
| `98edc37` | rater A N=1 예비 리포트 — 88점 함정 사람 ground truth 확정 |
| `72b57a9` | **cross-provider Claude judge** — gated 배선(`critic_judge_provider`) + 측정 + 테스트 + 리포트 |
| `eca5706` | CODEX 독립 교차검증 핸드오프 (B0 vs B1) |
| `6b52d3f` | **B0/B1 특이성 개입** before/after — Δ+0.33 측정 + 정직한 한계 |

(이전 세션 머지 HEAD = `af345ae` = main. research 5커밋은 phase-29-agent-ux 에만 = **main 미반영**.)

---

## 2. ★ 핵심 자산 — 검증된 계측기 (cross-provider Claude judge)

- **무엇**: 같은 plan을 OpenAI 생성 → **Claude(claude-sonnet-4-6) 독립 채점**. self-review 편향이
  깨져 사람과 정렬됨.
- **검증**: 같은 10 plan에서 사람(rater A) 2.18/5 vs Claude judge 2.71/5 → **평균괴리 0.53**.
  기존 gpt-4o critic은 4.45(false-approve 10/10 "88점 함정")였음. **→ Claude judge = 사람 정렬
  자동 계측기**. 이후 모든 품질 측정의 기준 도구.
- **production 배선** (gated, default OFF = byte-identical):
  - `config.critic_judge_provider` (default `"openai"` / `"anthropic"`).
  - `agents/critic.py::_judge_via_anthropic` (AnthropicAdapter + registry `claude-sonnet`).
  - ANTHROPIC_API_KEY 없으면 ValueError(안전 차단). 테스트 `tests/test_critic_cross_provider.py` (4). 전체 pytest 835 green.
  - ★ DEFAULT를 anthropic으로 전환 = 모델 교체(major) → prompt-version-review 대상. realuse 프로파일 미포함.

---

## 3. 연구 발견 3종 (전부 문서화)

1. **88점 함정 정량 확정** — critic 89점 vs 사람 44점(45점 괴리), false-approve 10/10.
   calibration(HIP-007) 단독으론 verdict 0건도 못 뒤집음(점수만 0.35 보정).
   → `eval/regression_results/2026-06-15-critic-calib-ab-preliminary.md`
2. **cross-provider judge가 verdict 차단** — Claude judge가 approve 10건 전부 뒤집음
   (8 revise·2 reject), false-approve 10/10→0/10, 사람괴리 2.27→0.53.
   → `eval/regression_results/2026-06-21-cross-provider-judge.md`
3. **개선 출력물 before/after (B0 vs B1)** — 특이성 강화 rewrite로 B0 2.71→B1 3.04(Δ+0.33),
   적대적 4-lens 전원 "진짜"(가밍 0). 단 **표면층만**(hook +0.8) **개념층 정체**(differentiation
   +0.2, 8/10 불변), approve 0→0, 회귀 1건, 할루시네이션(라벨로 자인). **rewrite 불가 3종 =
   COT 대화·진짜 딥리서치·2nd-brain 유저특화**. → `eval/regression_results/2026-06-21-improved-output-ab.md`
   - **시사**: 표면 특이성은 후처리로 개선되나, 진짜 차별화는 **RAG/PKM grounding 없이는 불가**
     함을 단일 변인으로 격리 입증.

---

## 4. 핵심 파일 지도

**연구 데이터/도구** (`eval/human_review/`, `scripts/`):
- `2026-06-15-calib-ab-cases.json` — 10케이스(input + B0 plan + hidden A0/A1).
- `2026-06-15-calib-ab-claude.json` — B0의 cross-provider judge 결과(재사용 기준선).
- `2026-06-15-calib-ab-scores-A.json` — 사람 rater A 점수 + 코멘트(개입 설계 근거).
- `2026-06-15-calib-ab-key.json` — A0/A1. **rater B 도착 시 analyze_blind_ab.py 입력.**
- `2026-06-21-b1-specificity-rescore.json` — B1 plan 본문 + B0/B1 점수.
- `scripts/cross_provider_judge_rescore.py` — Claude 채점 로직 원본(재사용 시드).
- `scripts/gen_improved_ab.py` / `b1_specificity_rewrite.py` — B1 생성/채점.
- `scripts/analyze_blind_ab.py` — 2-rater κ 분석(**rater 정확히 2개 필요**).

**production 배선**: `backend/fastapi/config.py`(critic_judge_provider) · `agents/critic.py`(_judge_via_anthropic) · `tests/test_critic_cross_provider.py`.

**핸드오프**: `meta/handoffs/2026-06-21-codex-improved-output-ab.md`(CODEX 독립실행) · 본 문서.

---

## 5. 제약 (반드시 유지)

- **API 키(OPENAI/ANTHROPIC/SUPABASE/GEMINI)는 `backend/fastapi/.env`에만**. 채팅/코드/커밋/로그
  평문 절대 금지. .env 확인 시 키 이름/SET 여부만.
- **실 LLM·Supabase 호출 = 비용** → opt-in 필요.
- **production 코드 0 변경 원칙**(연구는 스크립트 + eval 산출물만). critic/planning 프롬프트
  변경은 prompt-version-review 절차로만.
- **two-worktree**: `dreammate-p27`(= 작업 정본, 브랜치 phase-29-agent-ux) vs OneDrive 트리
  (브랜치 phase-27, **research 커밋 미반영**). 정렬 필요 시 머지 순서 조율(재분기 주의).
- 기본 브랜치(main) 직접 커밋 금지 — feature 브랜치 사용.

---

## 6. 주의/미해결

- research 5커밋이 **main 미머지** — 사용자 "main 머지/푸시" 패턴이므로 다음에 확인.
- B0/B1: B0 plan 본문 미보존(점수만) → word-diff 불가. judge 단일·N=10·temp 0.1 단일실행
  (분산 미추정). 측정 중 5/10 절단(max_tokens) 보정 confound. → 정식화 시 N↑·재현.
- Phase 28/29/30 phases/active 미정리(active=phase-27만). 척추 스킬(phase-complete/meta-retrospective) dormant.
