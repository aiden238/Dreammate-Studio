# Proposal: 브랜딩 세션 — Akinator식 주제 발굴 (LLM 동적 스무고개)

> 날짜: 2026-06-04 | 유형: **설계 제안 (proposal-only)** — 코드/contract/endpoint/schema 0 변경. 전부 "제안".
> 대상 phase: **Phase 18 (provisional — Phase 17 마무리 후 entry)**
> 사용자 결정(2026-06-04): 질문엔진=**LLM 동적** / 답변=**카드+자유입력 혼합** / 결과=**후보 주제 3개 × 브랜딩 방향 + PKM 연결**
> 근거: 사용자 요청("내가 원하는 주제를 정해주는 브랜딩 세션, 아키네이터 X고개") + 배포 전 로드맵의 "아키네이터+프롬프트 UX"
> 절차: 실 착수 시 phase-start + ai-architecture-review + prompt-version-review + agent-io-check + (스키마 닿으면) contract-change

---

## 0. 상태 / 목적 / 한 줄

- **상태**: 설계 제안. Phase 17(계정별 PKM) active — 본 빌드는 Phase 17 phase-complete 후.
- **한 줄**: 주제를 모르는 사용자를 **LLM 동적 스무고개**로 좁혀, **후보 주제 3개(+각 브랜딩 방향)** 를 제안하고, 택1 → 기존 planning + brand_memory(PKM) 시드로 연결한다.
- **위치**: 기존 진입 **Quick**(의도 직접 입력) · **Discovery**(카드 위저드)에 더해 **세 번째 진입 = "주제 추천받기 / 모르겠어요"**.

## 1. UX 흐름

```
[진입] "주제를 모르겠어요 / 추천받기"
   ↓
[스무고개 루프] (LLM 동적, 적응형)
   Q1: 카드 2~4개 + (선택)자유입력  → 답변
   Q2: 직전 답변 반영한 다음 질문    → 답변
   …  (확신도 충분 OR N고개 상한 도달 시 종료)
   ↓
[제안] 후보 주제 3개 — 각각:
   · 주제 한 줄  · 톤  · 타깃  · 포맷(예: 정보형 30초 쇼츠)  · 왜 당신에게 맞는지
   ↓
[택1] → 기존 planning(3안 생성) 으로 initial_input/방향 전달
        + (gated) 선택한 브랜딩 방향을 brand_memory 후보로 적재(PKM source)
```

## 2. 질문 엔진 (LLM 동적) — 핵심 설계

- **적응형 next-question**: agent 가 (지금까지 Q&A 상태)를 받아 **다음 질문 1개 + 카드 옵션 2~4개**를 생성. 직전 답변에 따라 분기(아키네이터 핵심).
- **종료 판단**: agent 가 "주제 공간이 충분히 좁혀졌다" 판단 시 종료, 또는 **N고개 상한**(예: 기본 6~8, 최대 12)에서 강제 종료. (X고개 = 적응형 — 정통 20이 아니라 "충분할 때까지, 상한 내".)
- **상태**: Q&A 히스토리(질문/선택/자유입력)를 세션에 누적. 매 호출 전체 상태를 프롬프트에 주입(stateless agent + client/DB 상태 보관).
- **두 모드 (1 agent 또는 2 프롬프트)**:
  - mode=`ask` → 다음 질문 + 옵션(또는 종료 신호).
  - mode=`finalize` → 후보 주제 3개 + 브랜딩 방향 합성.

## 3. 답변 형식 (카드 + 자유입력 혼합)

- 각 질문: **카드 2~4개**(기본 — Discovery 카드 UX 일관) + **"기타/직접 입력" 자유 텍스트**(특수 의도 보완).
- 자유입력은 다음 질문 생성/최종 합성에 그대로 반영(LLM 동적이라 자연 처리).

## 4. 결과 (후보 3 × 브랜딩 방향 + PKM 연결)

```json
{
  "candidates": [
    {
      "topic": "동네 카페 원두 비하인드",
      "tone": "담백하고 솔직한 동네 가게 톤",
      "target": "동네 카페를 좋아하는 커피 애호가",
      "format": "정보형 30초 쇼츠",
      "why_fit": "당신의 '진정성/일상' 선호 답변과 맞음"
    }, { … }, { … }
  ]
}
```
- 택1 → `topic`(+방향)을 planning 의 `initial_input`/approved_direction 으로 전달(기존 흐름 재사용).
- ★ **PKM 연결(gated)**: 선택한 `tone`/`target`/`format` 을 **brand_memory 후보로 적재**(Phase 17 brand_memory_entries + governance ≥0.9/proposal). → 이후 생성에서 Phase 17 **brand_memory 주입**이 이 방향을 구속 반영. **발굴(P18) → 축적(brand_memory) → 주입(P17)** 루프 완성.

## 5. 아키텍처 (제안)

| 요소 | 제안 |
|---|---|
| **신규 agent** | `topic_discovery`(P-AUX-?, LLM) — ask/finalize 2모드. prompt_registry 등록(prompt-version-review). |
| **endpoint** | `POST /plans/{id}/branding/next` — body=답변 → 다음 질문 or 종료 / `POST /plans/{id}/branding/finalize` → 후보 3. (또는 기존 generic wizard endpoint 확장 — agent-io-check) |
| **frontend** | 신규 `/new/branding`(또는 `/new/discover-topic`) — 질문 카드 + 자유입력 + 진행바, 마지막 후보 3 카드 → 택1 → `/plan/[id]` |
| **상태** | plan_entry.wizard_data.branding[] 누적(기존 wizard_data 재사용) 또는 신규 세션 store |
| **planning 연결** | 택1 결과 → initial_input/approved_direction (기존 generateMultiPlan 흐름 무변경) |

## 6. 기존 통합 / 비충돌

- Quick/Discovery **무변경** — 세 번째 진입 additive.
- planning/critic/output **무변경** — 브랜딩 세션은 입력(주제·방향) 생성까지만, 그 뒤는 기존 3안 생성.
- Phase 17 brand_memory/PKM **재사용** — 브랜딩 방향을 brand_memory source 로 추가(자동 승격 X, governance 계승).
- gated/additive: 신규 진입·endpoint·agent·frontend page 추가만. 기존 경로 byte-identical.

## 7. 비목표 (NON-GOALS)

```
✗ Quick/Discovery 대체 — 보완(세 번째 진입)일 뿐.
✗ 정통 예/아니오 20고개 고정 — 적응형 LLM(상한 내), 카드+자유입력.
✗ brand_memory 자동 승격 — 브랜딩 방향도 후보/제안까지(ADR-031 NG12 계승, 운영자/사용자 확정 후).
✗ 영상 제작 — product_boundary 계승.
✗ output_schema/planning 변경 — 입력 생성까지만.
```

## 8. 슬라이스 (provisional)

```
[GATE] Phase 17 phase-complete 후 entry.
S1  topic_discovery agent(ask/finalize) + prompt_registry 등록 + 단위 test(mock)
S2  branding endpoint(next/finalize) + 상태 누적 (agent-io-check)
S3  frontend /new/branding (질문 카드+자유입력+진행바 → 후보 3 → 택1)
S4  planning 연결(택1 → initial_input) + ★ brand_memory source 연결(gated, Phase 17 재사용)
S5  라이브 e2e(스무고개→주제→생성, PKM 반영) + phase-complete
```

## 9. 리스크와 방어

| 리스크 | 방어 |
|---|---|
| LLM 질문 루프 비용/지연 | N고개 상한 + 카드 옵션(짧은 응답) + workhorse 모델(gpt-4o-mini) |
| 질문이 겉돌아 안 좁혀짐 | finalize 종료 판단 + 상한 강제 + "충분 신호" 프롬프트 규칙 |
| 비결정성(같은 답→다른 질문) | temperature 낮춤 + 상태 전체 주입. 측정은 golden 시나리오 |
| 자유입력 인젝션/오프도메인 | 기존 Intent(P-001) + llm_security 차단 재사용 |
| scope creep(브랜딩 전체로 확대) | 본 phase = 주제 발굴 + 방향 제안까지. 브랜드 관리 UI 는 별도 |

## 10. 다음
```
1. 본 제안 검토(사용자) — UX/슬라이스 확정.
2. Phase 17 phase-complete → Phase 18 entry(phase-start 4점검).
3. S1~S5 진행. brand_memory 연결로 Phase 17 PKM 과 루프 결합.
```
