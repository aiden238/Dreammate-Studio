# phase_draft.md — phase entry 8 files scaffold (팟캐스트)

> 위치: `harness/meta_factory/outputs/TEST/podcast/scaffolds/phase_draft.md`
> 기반: `meta_factory/templates/phase_template.md`
> 상태: Phase M1 S1 dry-run scaffold (active 아님 — active phase 등록은 사용자 승인 후)
> 대상 예시: `phase-P1-mvp-planning` (entry 8 files 채움 예시)

---

## entry 8 files (phase_template placeholder → 팟캐스트)

### goals.md
```markdown
# phase-P1-mvp-planning — Goals
- intent + planning(3-plan) + critic + rewriter MVP 동작
- golden_set PE-001~PE-005 정의 (솔로/인터뷰/패널/시리즈오프닝/단발)
- output_schema EpisodePlan(angle+segment_flow[]+opening_hook) 확정
```

### scope.md
```markdown
# phase-P1-mvp-planning — Scope
## 포함 (In-Scope)
| 파일/영역 | 작업 |
|---|---|
| ai agent: intent/planning/critic/rewriter | 신규(설계→구현, 별도 승인 후) |
| eval/golden_set.md PE-001~005 | 신규 |
| docs/contracts/output_schema.md EpisodePlan | 신규 |
## ★ 절대 수정 금지 (forbidden)
- guest_brief/question/shownotes agent (phase-P2)
- 오디오 녹음/편집/TTS (forbidden_scope 영구)
- meta_factory/** 외 런타임 (dry-run 단계)
```

### non_goals.md          # ★ 필수 — forbidden_scope 매핑
```markdown
# phase-P1-mvp-planning — Non-Goals
| ID | 항목 | 사유 |
|---|---|---|
| NG1 | 게스트 브리프/질문/쇼노트 | phase-P2 (범위 분리) |
| NG2 | TTS/오디오 생성 | forbidden_scope 영구 제외 |
| NG3 | 자동 promotion (사람 검토 없이) | forbidden_scope (규칙 8) |
| NG4 | Show Memory 자동 추출 | forbidden_scope (phase-P4 후속) |
```

### dependencies.md
```markdown
# phase-P1-mvp-planning — Dependencies
- 선행 phase: phase-P0-foundation (db_schema/output_schema 초안)
- 외부 의존: LLM API (placeholder 키 — 실 키 미커밋)
```

### acceptance.md         # ★ 필수
```markdown
# phase-P1-mvp-planning — Acceptance
| ID | 기준 | 검증 방법 |
|---|---|---|
| A1 | golden_set PE-001~005 회귀 PASS | eval-run (mock-deterministic) |
| A2 | schema 준수 100% | eval-run §4 1차 게이트 |
| A3 | revise max 2 차단 | test (rewriter critic_max_revise) |
| A4 | agent IO ↔ agent_io_contract 0 drift | agent-io-check |
```

### assumptions.md
```markdown
# phase-P1-mvp-planning — Assumptions
- 게스트 모드는 P2 로 분리 가능하다 (4-check: scope 명확/의존 없음/위험 낮음/되돌림 가능 — 통과)
- format(interview/solo/panel)은 planning agent 파라미터로 충분 (expert_pool 미채택 — GAP G1)
```

### multi_slice_plan.md
```markdown
# phase-P1-mvp-planning — Multi-Slice Plan
## Wave 구조
- Slice 1 [output_schema + db_schema EpisodePlan] → Slice 2 [intent+planning] → Slice 3 [critic+rewriter+golden_set] → Slice 4 [close]
## 충돌 매트릭스
| Slice | contracts/ | ai agent | eval/ |
|---|---|---|---|
| S1 | ✏ | — | — |
| S2 | — | ✏ | — |
| S3 | — | ✏ | ✏ |
```

### notes.md
```markdown
# phase-P1-mvp-planning — Notes
## Entry (dry-run)
- 본 phase 는 blueprint 상의 설계 — 실 진입은 사용자 승인 후
## rollback/retrospective 경로
- rollback: 각 Slice commit 단위 revert (P-X1 SELF-VERIFICATION)
- retrospective: phase 종료 시 meta-retrospective (closing_notes 경로)
```

---

## 작성 가이드 점검 (phase_template §작성가이드)

1. ✅ non_goals.md 필수 — forbidden_scope 4항목 → NG1~NG4 매핑.
2. ✅ acceptance.md — eval-run 임계값 연결(A1/A2).
3. ✅ scope.md forbidden 영역 — sub-agent 침범 금지 명시 (P-X1 정신).
4. ✅ multi_slice_plan 충돌 매트릭스 — 폴더 충돌 0.
5. ✅ assumptions 4-check.
6. ✅ rollback·retrospective 경로 (notes/acceptance).
7. ★ outputs/ 에 먼저, active phase 등록은 승인 후.

## ★ GAP 관찰

phase_template 은 8 files 형식이 견고 — 팟캐스트에 거의 그대로 적용됨(GAP 적음).
유일한 마찰: G1(expert_pool 미채택 근거)을 assumptions 에 담아야 했음 — pattern 선택 근거의 phase 전파 경로가 암묵적.
