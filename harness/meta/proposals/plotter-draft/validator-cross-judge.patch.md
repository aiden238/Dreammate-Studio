# Patch 초안 — plotter cross-provider judge / consensus-min (ADR-0033)

> ★ **초안** — plotter repo(`app/llm/models.py`, `app/agents/validator.py`)에 적용 후 plotter에서 테스트. Dreammate에선 실행/검증 불가(원격). gated default-off → OFF면 현행 byte-identical.

## 1. `app/llm/models.py` — cross-judge 매핑 + flag (추가)

```python
import os  # 파일 상단에 없으면

# ── Phase-32 수렴 (ADR-0033): cross-provider judge (gated) ──────────────
# D1-C 재고 — Dreammate 측정(in-provider judge false-approve 10/10, cross 0/10, ko 사람정렬)으로
# ADR-0031 "B로 cross-model 편향 남으면 재고" 트리거 충족. default off=현행 byte-identical.
CROSS_JUDGE_ENABLED = os.getenv("CRITIC_CROSS_JUDGE", "").strip().lower() in ("1", "true", "on")

# 생성 provider 와 *다른* provider 의 flagship 을 cross judge 로 (blind-spot 교차).
_CROSS_JUDGE: dict[str, str] = {
    "openai":    "anthropic/claude-opus-4-8",
    "gemini":    "anthropic/claude-opus-4-8",
    "anthropic": "openai/gpt-4o",
}

def cross_judge_model(provider: str | None) -> str | None:
    """provider 별 cross-provider judge 모델 (CROSS_JUDGE_ENABLED 일 때만). None=미적용/graceful."""
    if not CROSS_JUDGE_ENABLED or not provider:
        return None
    return _CROSS_JUDGE.get(provider)
```

## 2. `app/agents/validator.py` — consensus-min (in-provider ∧ cross, 더 엄격)

현 `validator_node`의 단일 judge 채점부를 헬퍼로 추출 후, cross judge 를 추가로 돌려 **AND** 결합.

```python
# (1) 채점 1회를 헬퍼로 추출 — 기존 validator_node 본문의 call_llm~passed 계산을 그대로 이동.
async def _judge_pass(state, *, judge_model, call_llm_fn, settings, meta, score_threshold) -> tuple[bool, dict]:
    """judge_model 1회 채점 → (passed, score_block). 기존 로직 동일(추출만)."""
    result = await call_llm_fn(
        model=judge_model, response_format=JSON_OBJECT_FORMAT,
        messages=[{"role": "system", "content": SYSTEM_PROMPT},
                  {"role": "user", "content": json.dumps(state.candidates, ensure_ascii=False)}],
        temperature=JUDGE_TEMPERATURE, max_tokens=MAX_TOKENS, meta=meta, settings=settings,
    )
    try:
        parsed = extract_json(result.text); raw_scores = parsed["scores"]
    except (json.JSONDecodeError, TypeError, KeyError):
        return False, {"error": "F8_prompt_collapse", "raw": result.text}
    scored = []
    for item in raw_scores:
        cs = score_candidate(item.get("layer1_json", {}), item.get("layer2a_json", {}))
        scored.append({"candidate_idx": item.get("candidate_idx"),
                       "layer1_json": item.get("layer1_json", {}),
                       "layer2a_json": item.get("layer2a_json", {}), **cs})
    grp = group_result([s["mean_5pt"] for s in scored], score_threshold)
    weak = weak_axes(scored, score_threshold)
    target_sec = _target_length_sec(state.intent)
    if any(structure_pacing_issues(c, target_sec) for c in (state.candidates or [])):
        if "structure" not in weak:
            weak = [*weak, "structure"]
    passed = grp["threshold_pass"] and not weak
    return passed, {"judge_model": judge_model, "scores": scored, **grp,
                    "threshold_pass": passed, "weak_axes": weak}

# (2) validator_node 에서 in-provider + (옵션) cross-provider 결합.
async def validator_node(state, *, ..., judge_model=MODEL_JUDGE, cross_judge_model_id=None,
                         call_llm_fn=call_llm, settings=None, score_threshold=3.0) -> PipelineState:
    meta.prompt_version = PROMPT_VERSION
    in_pass, in_block = await _judge_pass(state, judge_model=judge_model, call_llm_fn=call_llm_fn,
                                          settings=settings, meta=meta, score_threshold=score_threshold)
    passed = in_pass
    state.scores = in_block
    # consensus-min (ADR-0033, gated): cross judge 추가 → 둘 다 통과해야 pass(더 엄격, 단조).
    if cross_judge_model_id and in_block.get("error") != "F8_prompt_collapse":
        cross_pass, cross_block = await _judge_pass(
            state, judge_model=cross_judge_model_id, call_llm_fn=call_llm_fn,
            settings=settings, meta=meta, score_threshold=score_threshold)
        passed = in_pass and cross_pass            # ★ consensus-min = AND(더 엄격)
        state.scores = {**in_block, "consensus_min": True,
                        "in_provider_pass": in_pass, "cross_pass": cross_pass,
                        "cross_block": cross_block, "threshold_pass": passed}
    state.threshold_pass = passed
    return state
```

## 3. 배선 (driver)

`validator_node` 호출측(파이프라인 드라이버)에서 provider를 알면:

```python
from app.llm.models import cross_judge_model
# resolve_models(choice) -> (agent_model, judge_model, provider)
agent_model, judge_model, provider = resolve_models(choice)
state = await validator_node(state, judge_model=judge_model,
                             cross_judge_model_id=cross_judge_model(provider), ...)
```

graceful: `cross_judge_model()`이 None(flag off / 키 없음)이면 cross 미실행 = 현행.

## 4. 테스트 stub (`tests/test_validator.py` 추가)

```python
# consensus-min: in_pass=True, cross_pass=False → 전체 fail(더 엄격) — fake call_llm_fn 2회 분기.
# gate off(CRITIC_CROSS_JUDGE 미설정 / cross_judge_model_id=None) → 단일 judge, byte-identical.
# 키 부재 graceful: cross_judge_model_id=None → cross 미실행.
```

## 5. 측정 (적용 후)
- 같은 골든셋에서 `CRITIC_CROSS_JUDGE` off(in-provider) vs on(consensus-min) **false-approve·사람괴리** 비교(사전동결 임계).
- Dreammate 결과(in 10/10 → cross 0/10)와 대조 — plotter ko 도메인에서 재현되는지.

## 6. 주의
- 비용: consensus-min = judge 2회 → 일일 가드(NF-M01) 내 확인.
- **결정적 게이트(structure_pacing_issues)와 직교** — 이미 plotter에 있으니 cross judge만 추가하면 "결정적 게이트 + cross judge" 풀세트 완성(Dreammate calib-ab-preliminary:43 설계).
- MoA(generation diversity, exp4 기각)와 무관 — judge 레이어.
