# skill_draft.md — podcast eval 절차 Skill scaffold (★ 재사용 권장 예시)

> 위치: `harness/meta_factory/outputs/TEST/podcast/scaffolds/skill_draft.md`
> 기반: `meta_factory/templates/skill_template.md`
> 상태: Phase M1 S1 dry-run scaffold (active 아님 — Skill 추가는 contract-change 절차 경유)
> ★ 핵심 결론: 팟캐스트 도메인은 **신규 Skill 0 권장**. 본 draft 는 "신규 Skill 을 만들면 어떤 충돌이 나는가"를
>   보여주기 위한 예시(podcast-eval-run) + 재사용 권고를 함께 담는다.

---

## A. 만약 신규 Skill 을 만든다면 (충돌 시연 — ❌ 채택 안 함)

```markdown
---
name: podcast-eval-run
description: |
  팟캐스트 기획안 품질 평가(eval)를 실행할 때 사용한다. golden_set 회귀, 후킹 강도 평가,
  대화 흐름 평가를 어떤 순서로 돌릴지 강제한다.
  키워드: "eval 실행", "golden_set", "regression", "품질 평가".   # ❌ eval-run 과 100% 충돌
applies_to: [agents]
phase: [phase-P3]
version: v1.0.0
---
```

→ ❌ **키워드 "eval 실행" / "golden_set" / "regression" 이 기존 `eval-run` Skill 과 완전 중복**
   = factory_contract 규칙 4 위반 (INDEX "같은 description 키워드 둘 이상 = 충돌"). **채택 불가.**

---

## B. 권장 — 기존 eval-run 재사용 (신규 Skill 0)

- 팟캐스트 평가는 **기존 `eval-run` Skill 절차(§3~§6)를 그대로 재사용**한다.
- 도메인 차이(후킹→opening_hook_strength, 대화흐름→conversation_flow, +question_quality/guest_fit)는
  **Skill 절차가 아니라 데이터**(`eval/podcast_planning_eval.md` 채점 차원 + `eval/golden_set.md` 케이스 PE-001~)로 표현한다.
- 근거: skill_template §작성가이드 3 "Skill 본문은 절차만 — 데이터/명세는 docs/contracts/, eval/, knowledge/ 에".

```
재사용 매핑 (신규 0):
  평가 실행            → eval-run        (기존)
  golden_set 확장      → eval-design     (기존)
  contract/Skill 변경  → contract-change (기존)
  agent IO drift 검사  → agent-io-check  (기존)
  하네스 감사          → harness-audit   (기존)
  회고/개선            → meta-retrospective (기존)
```

---

## 작성 가이드 점검 (skill_template §작성가이드)

1. ✅ description 키워드 scoped — A 가 충돌함을 보여 B(재사용)로 결론. 신규 0 → 충돌 0.
2. (재사용 시) `사용하지 않는 경우` 섹션은 기존 eval-run 에 이미 존재.
3. ✅ Skill 본문 = 절차만, 도메인 데이터는 eval/ 로.
4. applies_to — eval 실행은 [agents].
5. 우선순위 표 — 신규 0 이므로 INDEX 우선순위 변경 없음.
6. version semver — 해당 없음(신규 0).
7. ★ 만약 정말 신규가 필요하면 outputs/ 에 먼저 + contract-change 경유 + 사용자 승인.

## ★ GAP 관찰 (G2)

generation_workflow 단계 4 "skill 후보 생성"은 신규 생성을 전제하나, 본 도메인은 **재사용이 우월**.
machinery 에 "신규 Skill vs 기존 재사용 결정 트리"가 없음 → S2 with-without_skill_eval 의 핵심 검증 포인트.
(신규 Skill 추가의 효용 ≤ 기존 재사용 → 신규 0 이 옳다는 가설을 S2 가 검증)
