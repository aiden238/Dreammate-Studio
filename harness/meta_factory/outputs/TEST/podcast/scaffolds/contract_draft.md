# contract_draft.md — output_schema contract scaffold (팟캐스트)

> 위치: `harness/meta_factory/outputs/TEST/podcast/scaffolds/contract_draft.md`
> 기반: `meta_factory/templates/contract_template.md`
> 상태: Phase M1 S1 dry-run scaffold (active 아님 — contract 변경은 contract-change 절차 경유, 규칙 5)
> 대상 예시: `output_schema.md` 의 EpisodePlan 본문 (1개)

---

## 채운 scaffold (contract_template placeholder → 팟캐스트)

```markdown
# output_schema.md — 팟캐스트 에피소드 기획 출력 본문 스키마

> 위치: `docs/contracts/output_schema.md`
> 상태: Phase P0 진입용 (초안)
> 참조: agent_io_contract.md, db_schema.md     # ★ cross-ref

---

## 0. 이 문서의 위치

7 agent 가 산출하는 본문(EpisodePlan / GuestBrief / QuestionList / Shownotes / Critic)의 JSON 스키마를 정의한다.

이 문서가 정의하는 대상:
- EpisodePlan (angle / segment_flow[] / opening_hook), GuestBrief, QuestionList, Shownotes, Critic 본문

이 문서가 정의하지 않는 대상:
- agent 실행 정책(timeout/retry/graceful) → `agent_io_contract.md`
- 테이블/컬럼/마이그레이션 → `db_schema.md`
- 오디오 파일 포맷 → (정의 안 함 — forbidden_scope, 기획 AI 는 오디오 미산출)

---

## 1. 필드 정의 (EpisodePlan 발췌)

| 필드 | 타입 | 필수 | 설명 |
|---|---|---|---|
| angle | string | ✅ | 에피소드 주제 앵글 (1~2문장) |
| segment_flow | array<Segment> | ✅ | 오디오 대화 흐름 (오프닝→본론 segment→클로징) |
| opening_hook | string | ✅ | 오프닝 후킹 멘트/질문 (썸네일 대응) |
| target_length_min | int | — | 목표 길이(분) — recording_feasibility 입력 |
| format | enum | ✅ | interview \| solo \| panel |

---

## 2. JSONB schema (Segment)

\`\`\`json
{
  "segment_title": "string — 예: 게스트 소개",
  "purpose": "string — 이 segment 의 역할",
  "talking_points": ["string"],
  "est_minutes": "int"
}
\`\`\`

---

## 3. Cross-reference                # ★ 정합 축

| 이 contract 의 필드 | 정합 대상 | 정합 규칙 |
|---|---|---|
| EpisodePlan(JSONB) | db_schema episodes.plan_json | 1:1 매핑 |
| Critic.overall_score | agent_io_contract critic 출력 | canonical 1개 (deprecated fallback 제거 정책 계승) |
| format enum | db_schema episodes.format CHECK | enum 동일 |

---

## 4. 변경 이력
- v0.1.0 (dry-run): 초안 — EpisodePlan/GuestBrief/QuestionList/Shownotes/Critic 본문 (active 아님)
```

---

## 작성 가이드 점검 (contract_template §작성가이드)

1. ✅ cross-reference 필수 — output_schema ↔ db_schema(plan_json) / ↔ agent_io_contract(critic) 3축.
2. ✅ "정의하지 않는 대상" 명시 — 실행 정책/테이블/오디오 포맷 경계 분리.
3. ✅ canonical + deprecated — Critic.overall_score canonical 1개 (Dreammate P-CRITIC-CANONICAL-001 정신 계승).
4. ✅ JSONB schema 키/타입/예시 — Segment.
5. ✅ 변경 이력 semver — 변경 시 contract-change 경유.
6. ★ outputs/ 에 먼저 + active 반영은 사용자 승인 + contract-change 후.

## ★ GAP 관찰 (G3 보강)

agent_io_contract 형식이 4 agent(MOA) 전제 → 7 agent + 조건부 실행(guest_brief/question/shownotes 는 게스트/모드 의존)을
contract 형식이 직접 표현하지 못함. contract_template 의 cross-ref 표는 "조건부 산출" 축이 없음 → S2 contract_consistency 관찰점.
