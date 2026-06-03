# Phase 15 전체 기획안 — director 모드 (output_mode 3rd tier)

> 날짜: 2026-06-03 | 유형: **Phase 15 종합 기획안 (구현 spec)** — entry 8파일 통합 + 구체 설계
> 상태: **ACTIVE** (entry 작성·커밋 e70489d, 브랜치 phase-15-director-mode)
> 기반: project-1 PARKED 제안서 `meta/proposals/2026-06-03_commercial-viral-mode-design.md` (§2.1 4-tier / §3 P-006 / §4 critic / §6 cost / §7 단계화)
> 로드맵: **① Phase 15 director (본) → ② 검증 보강(human review + 전수 eval) → ③ PKM/RAG 데이터레이어 → (commercial_viral)**
> 절차: contract-change(output_schema/prompt_registry/cost_control) + prompt-version-review(P-006/P-007) + agent-io-check + design-review + eval-run + phase-complete

---

## 0. Framing — 왜 director, 왜 지금

- **director = output_mode 4-tier(compact<rich<director<commercial_viral) 중 3단계** — rich(제작 착수 가능)와 commercial_viral(전략급) 사이의 **중간 깊이**: 연출·리텐션 설계까지 가되 시장/브랜드/전환 전략(데이터 의존)은 제외.
- ★ **데이터레이어(PKM/RAG) 비의존 = LLM-only** → 지금 빌드 가능 (commercial_viral 만 시장/트렌드 실데이터 필요 — 제안서 보정3/§7.2).
- ★ **사용자 "더 깊은 대본기획" 1단계** — rich가 "동작하지만 더 깊었으면"으로 검증된 뒤의 자연스러운 심화.
- ★ **안전**: Phase 13 의 3중 안전장치(gated flag + additive Optional + mode별 직렬화 제외) 계승 → **compact/rich 경로 byte-identical**(behavior-preserving). 신규 endpoint/agent 0(기존 Planner/Critic 의 mode 확장).

### 선행조건 점검 (제안서 §0.2)
| 조건 | 상태 |
|---|---|
| (b) 위저드 ↔ 백엔드 실연결 | ✅ Phase 14 done |
| (a) rich 실사용 | 부분(라이브 동작 ✅ / 가치=사용자 "더 깊었으면") — director는 gated OFF+additive(저위험)라 빌드 가능, 가치 정량화=로드맵② |
| (c) human review | 미수행 → 로드맵② (director 자체는 OFF byte-identical=운영 무영향, human review는 default ON/commercial_viral 게이트) |

→ director 는 데이터 비의존 + gated OFF → (a)(c) 완전충족 전에도 **안전하게 빌드**(제안서 §7.1 "director 먼저").

---

## 1. 요약 / 목표 / 비목표

### 1.1 요약
`output_mode` 를 boolean(`rich_output_enabled`)에서 **enum(compact/rich/director)** 으로 일반화하고, **director** tier(rich 12슬롯 + 연출·리텐션 3슬롯)를 **additive Optional / gated / OFF byte-identical** 로 추가한다.

### 1.2 목표
1. output_mode enum 일반화 (backward-compat — 기존 rich_output_enabled 흡수).
2. director 슬롯 additive (`hook_system`/`retention_architecture`/`scene_breakdown[DirectorScene]`) + `DIRECTOR_FIELDS` + mode별 직렬화.
3. P-006 director 프롬프트(v1.2.0, gated 공존).
4. Critic director 차원(`retention_design`, P-007 v1.3.0, gated).
5. frontend PlanCard director 조건부 섹션.
6. director cost(rich↔commercial_viral 중간) + director depth 측정 + close.

### 1.3 비목표 (NG)
- commercial_viral 슬롯(market_context/audience_psychology/brand_positioning/commercial_conversion/platform_packaging/production_feasibility/measurement_plan + scene 상업필드) — **데이터레이어 종속**, 로드맵 후속.
- PKM/RAG 데이터레이어(로드맵③). rich/director default ON 전환. 완성 대본/영상 제작(product_boundary). 17차원 Critic(commercial). 조회수/viral 보장.

---

## 2. output_mode enum 일반화 설계 (S1 + S3, 제안서 open issue #2 확정)

### 2.1 config (S1)
```python
# config.py — additive Field (기존 rich_output_enabled 보존)
output_mode: Literal["compact", "rich", "director"] = "compact"   # 신규, default compact
rich_output_enabled: bool = False                                  # 기존 보존(backward-compat)
```
### 2.2 effective mode 매핑 (backward-compat 핵심)
```python
def effective_output_mode(settings) -> str:
    # 명시적 output_mode 우선. 미지정(compact default)이고 rich_output_enabled=True 면 rich 로 승격
    # → Phase 13/14 의 rich_output_enabled ON 동작 100% 보존.
    if settings.output_mode != "compact":
        return settings.output_mode            # "rich" | "director"
    return "rich" if settings.rich_output_enabled else "compact"
```
- ★ **backward-compat**: 기존 `rich_output_enabled=True` (output_mode 미지정) → effective "rich" = 기존 동작. `output_mode="director"` 명시 시에만 director. 둘 다 OFF → compact.
- 회귀: Phase 13/14 의 OFF/rich 경로 불변 → pytest 508 회귀 0.

---

## 3. director 스키마 설계 (S1, 제안서 open issue #1 확정)

### 3.1 DirectorScene (신규 모델, scene_breakdown 요소 — director-subset 5필드)
| 필드 | 타입 | 설명 |
|---|---|---|
| `scene_intent` | str | 이 씬의 기획 의도(왜 존재) |
| `viewer_emotion` | str | 시청자가 느끼길 의도하는 감정 |
| `retention_device` | str | 이탈 방지/호기심 유지 장치 |
| `why_this_works` | str | 작동 근거(★ 일반론 금지 — 패턴/맥락) |
| `fallback_scene` | str \| None | 약할 때 대안 씬(A/B 성격) |
★ 상업필드(brand_signal/commercial_signal) **제외** → commercial_viral(NG). scene_breakdown 은 "기획 의도/감정/근거"이지 촬영 지시 아님(product_boundary, 보정2).

### 3.2 Plan director 슬롯 (additive Optional)
```python
# schemas/output.py Plan 에 추가 (전부 Optional default — director 모드에서만 채워짐)
hook_system: list[str] = Field(default_factory=list, max_length=5,
    description="director: 첫 후크 + 재후크(re-hook) 지점 설계 (단발 hook_variants 위)")
retention_architecture: str | None = Field(default=None,
    description="director: 리텐션 구조 — 이탈 방지·호기심 갭·페이싱")
scene_breakdown: list[DirectorScene] = Field(default_factory=list,
    description="director: 씬 단위 분해 (기획 브리프 수준)")
```
### 3.3 상수 + mode별 직렬화 (byte-identical 핵심)
```python
DIRECTOR_FIELDS: frozenset[str] = frozenset({
    "hook_system", "retention_architecture", "scene_breakdown",
})

def model_dump_for_mode(self, mode: str, **kwargs) -> dict:
    """output_mode 별 직렬화 — 상위 tier 슬롯 제외 (Phase 13 model_dump_compact 일반화)."""
    exclude_plan: set[str] = set()
    exclude_beat: set[str] = set()
    if mode == "compact":
        exclude_plan = set(PLAN_RICH_FIELDS) | set(DIRECTOR_FIELDS)
        exclude_beat = set(BEAT_RICH_FIELDS)
    elif mode == "rich":
        exclude_plan = set(DIRECTOR_FIELDS)        # rich 까지만 — director 제외
    # director → 제외 0 (rich + director 전부)
    exclude = {f: True for f in exclude_plan}
    if exclude_beat:
        exclude["flow"] = {"__all__": {f: True for f in exclude_beat}}
    return self.model_dump(exclude=exclude, **kwargs)
```
- ★ **byte-identical 보장**: `mode="compact"` → PLAN_RICH_FIELDS ∪ DIRECTOR_FIELDS 제외 = Phase 12 이전과 동일. `mode="rich"` → DIRECTOR_FIELDS 만 제외 = Phase 13 rich 와 동일. 기존 `model_dump_compact()` 는 `model_dump_for_mode("compact")` 위임으로 보존.
- `output_schema.md §8.1` director 슬롯 등록 (contract-change CC) + agent-io-check.

---

## 4. P-006 director 프롬프트 설계 (S2, prompt-version-review)

### 4.1 버전 (gated 공존)
- P-006 v1.0.0(compact, active) / v1.1.0(rich, gated) / **v1.2.0(director, gated)** — `output_mode` 로 공존. compact 경로 v1.0.0 계속 active. deactivate 미적용(Phase 13 패턴).
- 구현: `agents/planning.py` `DIRECTOR_SYSTEM_PROMPT` + `DIRECTOR_PROMPT_VERSION="v1.2.0"` + `_build_director_system_prompt_with_hint`.

### 4.2 프롬프트 구조 (rich + director 3섹션)
```
[rich 계승] 기존 rich 12슬롯(후크변형/타깃/톤/beat 화면·대사·자막/샷/썸네일/제목/CTA/레퍼런스/길이변형)
[director 추가]
  - hook_system: 첫 후크 + 영상 중반 재후크(re-hook) 지점 1~2개 설계
  - retention_architecture: 이탈 구간 예측 + 호기심 갭/페이싱 장치 (1~2문단)
  - scene_breakdown: 씬별 {의도/감정/리텐션장치/근거(+대안)} — N씬(상한 가이드 §8)
[제약] JSON only · flow 2~8 · 브리프 경계(완성대본 금지) · 보장표현 금지(보정1) · 일반론 금지(why_this_works 근거)
```

---

## 5. Critic director 차원 설계 (S4, prompt-version-review)

### 5.1 차원 (gated)
```python
# agents/critic.py
DIMENSIONS_DIRECTOR = DIMENSIONS_RICH + ["retention_design"]   # 9 + 1 = 10 (director 모드 전용)
# run_critic: output_mode 분기 → compact 8(DIMENSIONS) / rich 9(DIMENSIONS_RICH) / director 10
```
- `retention_design`: 이탈 방지·재후크·페이싱이 **구조적으로** 설계됐는가 (제안서 §4.1). anchor 채점(0.2 없음 / 0.6 일부 / 1.0 체계적) — 얕은 director(scene/retention 빈약) 감점("88점 함정" 방어).
- P-007 v1.1.0(8, active) / v1.2.0(9, gated) / **v1.3.0(10 director, gated)** 공존.
- `CriticEvaluation.dimensions` 자유 dict → 10키 additive(스키마 위반 아님). canonical 0–1(ADR-018) 불변.
- ★ commercial 8차원(viral/conversion 등)은 **제외**(NG5) — commercial_viral 영역.

---

## 6. gated wiring 설계 (S3, behavior-preserving)

- `generate.py` + `orchestration/moa_orchestrator.py` + `routers/plans.py`: 현 `rich_output_enabled` boolean 분기 → `effective_output_mode(settings)` 분기.
  - planning 프롬프트 선택: compact→SYSTEM_PROMPT / rich→RICH_SYSTEM_PROMPT / director→DIRECTOR_SYSTEM_PROMPT (+hint 변형).
  - 직렬화: 기존 `envelope_to_response_dict(..., rich_enabled)` → `(..., mode)` 일반화 → `plan.model_dump_for_mode(mode)`.
  - critic: output_mode → DIMENSIONS 집합 선택.
- ★ **compact/rich byte-identical**: mode∈{compact,rich} 경로는 기존과 동일 프롬프트·직렬화·차원 → 회귀 0. director 만 신규 경로.
- meta.prompt_version 분기(compact v1.0.0 / rich v1.1.0 / director v1.2.0).

---

## 7. frontend 설계 (S5, design-review)

- `lib/types.ts`: Plan 에 director 슬롯 optional 미러(hook_system/retention_architecture/scene_breakdown[DirectorScene]).
- `components/PlanCard.tsx`: director 조건부 섹션(값 있을 때만) — rich 섹션 **아래** additive:
  - 후크 시스템(hook_system) / 리텐션 설계(retention_architecture) / 씬 분해(scene_breakdown: 씬별 의도·감정·리텐션·근거 카드).
- ★ compact/rich 렌더 회귀 0(조건부 — director 데이터 없으면 미렌더). 모바일/카드/제작UI 미포함(design.md 7원칙).

---

## 8. cost / eval 설계 (S6)

- **cost**: `cost_control_policy.md` director cost — rich(토큰 3~5배)와 commercial_viral 사이. director = rich + 3슬롯(scene N개) → rich 대비 소폭↑. additive(contract-change). default OFF → 운영 비용 무영향.
- **eval**: director depth 측정(`eval/regression_results/phase-15-*`) — director 경로 연출/리텐션 슬롯 충족 측정(실 LLM, mock 한계는 로드맵②). golden director 케이스(선택, 추가 시 additive). byte-identical 게이트(pytest 508).
- **open issue**: scene_breakdown N씬 상한(토큰 vs 깊이) — 데모 후 실측.

---

## 9. 6-Slice 상세 (구현 순서)

| Slice | 산출물 | 파일 | 검증 |
|---|---|---|---|
| **S1** | output_mode enum + director 스키마 + model_dump_for_mode | config.py / schemas/output.py / output_schema.md(CC) | 모드별 직렬화 test(compact/rich byte-identical + director 포함) + 매핑 + agent-io-check + pytest 508→+ |
| **S2** | P-006 director 프롬프트 v1.2.0 | agents/planning.py / prompt_registry.md(CC) | director 프롬프트 슬롯 지시 + compact/rich 보존 + 버전 test (런타임 미연결) |
| **S3** | gated wiring(output_mode 분기) | generate.py / moa_orchestrator.py / routers/plans.py | 3-mode 분기 test + compact/rich byte-identical 회귀 |
| **S4** | Critic director 차원(retention_design) v1.3.0 | agents/critic.py / prompt_registry.md(CC) | director 차원 + 얕은 director 감점 + compact/rich 회귀 0 |
| **S5** | PlanCard director 조건부 | apps/web/components/PlanCard.tsx / lib/types.ts | tsc + build + design-review + rich 렌더 회귀 0 |
| **S6** | cost + director depth + 라이브 + close | cost_control_policy.md(CC) / eval / retrospective | director depth 측정 + 라이브 데모 + pytest 508 + 키 0 + phase-complete |

- 의존: S2·S3←S1 / S4←S1·S3 / S5←S1 / S6←전체. 충돌 0(충돌 매트릭스 = multi_slice_plan.md).
- 각 Slice sub-agent + P-X1 §SELF-VERIFICATION.

---

## 10. 리스크 / 보정

| 리스크 | 보정 |
|---|---|
| director 슬롯 default 누수 | output_mode default compact + DIRECTOR_FIELDS model_dump 제외 → OFF/compact/rich byte-identical. gated. |
| enum 일반화로 기존 rich_output_enabled 회귀 | effective_output_mode 매핑(backward-compat) + pytest 508 회귀 게이트. rich_output_enabled 보존(삭제 X). |
| scene_breakdown 이 "영상 제작"으로 확대 | 기획 브리프 수준만(의도/감정/근거) — 촬영지시·완성대본 아님(product_boundary, 보정2). |
| director "88점 함정" | retention_design anchor 채점 + 얕은 director 감점 test. |
| 토큰 증가 | director = rich + 3슬롯(상업 10슬롯 미포함) → 증가 제한적. cost additive + default OFF. |
| commercial_viral/PKM 조기 혼입 | NG1/NG2 명시 — director 는 데이터 비의존 슬롯만. |

---

## 11. 결정 사항 / 변경 범위

### 11.1 확정 결정 (제안서 open issue 해소)
- **#1 director 슬롯 경계**: hook_system + retention_architecture + scene_breakdown(5필드). 상업필드 제외.
- **#2 flag→enum**: output_mode enum + rich_output_enabled 흡수(backward-compat).
- director Critic = 기존 9차원 + retention_design 1개(gated). (commercial 8차원 아님.)
- P-006 director=v1.2.0 / P-007 director=v1.3.0 (commercial_viral 은 추후 v1.3.0/v1.4.0 로 재넘버 — 제안서 provisional).

### 11.2 잔여 결정 (진행 중 확정)
- scene_breakdown N씬 상한 (S2/S6 데모 후).
- director depth 측정 방식(실 LLM 표본 vs human) — 로드맵② 연계.

### 11.3 ★ 변경하지 않을 범위 (보장)
- compact default 불변 + compact/rich 경로 byte-identical(회귀 0).
- 기존 7필드 + rich 12슬롯 + 8/9차원 Critic + rich_output_enabled — 전부 보존.
- MOA 4 agent 불변(director = Planner/Critic mode 확장). product_boundary(제작 영구 제외). 키/.env 0.

---

> ★ 요약: director = output_mode 3rd tier(compact<rich<**director**). rich + hook_system/retention_architecture/scene_breakdown(5필드) 를 **additive Optional / gated / OFF byte-identical** 로 추가. LLM-only(데이터 비의존) → 지금 빌드. enum 일반화는 rich_output_enabled 흡수(backward-compat). commercial_viral/PKM-RAG = 후속(로드맵 ②③). Entry 커밋 e70489d · 다음 = S1.
