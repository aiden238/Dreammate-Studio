# CC-007: Meta-Factory machinery 8 GAP 반영 (Phase M2)

> 유형: contract-change (L3 machinery 문서 — Skill 본문 아님)
> 날짜: 2026-05-31
> Phase: M2 (Meta-Factory GAP Remediation)
> proposal: `meta/proposals/2026-05-31_phase-M2-gap-remediation.md` (원천 = M1 `outputs/TEST/sample_test_podcast_validation.md §D`)
> ADR: ADR-037
> ★ additive-only — 기존 필드·절차 삭제·재명명 0 (backward-compat). 런타임 0 (A9).

---

## 절차 (contract-change Skill)

1. **제안**: M1 dry-run 이 8 GAP 발견 → `outputs/TEST/sample_test_podcast_validation.md §D` (각 1줄 보완안).
2. **검토**: `meta/proposals/2026-05-31_phase-M2-gap-remediation.md` (8 변경 표 + additive 근거).
3. **승인**: 사용자 결정 "전체 8개 (G1~G8)" + "M1 TEST 재적용 검증".
4. **반영**: S1 (G1/G2/G5/G6) + S2 (G3/G4/G7/G8) machinery additive 편집.
5. **검증**: S3 재검증 — M1 TEST 재적용 before/after (백로그 8→0).
6. **로그**: 본 CC-007.

## 변경 내역 (8 — 전부 additive)

| GAP | 파일 | 변경 (추가) | commit |
|---|---|---|---|
| G2 ★ | `generation_workflow.md` | §4.1 신규 Skill vs 재사용 결정트리 (키워드 충돌 검사 → 충돌 시 재사용 강제 + YAGNI) | 131ee06 |
| G1 | `architecture_patterns.md` | §2.1 expert_pool vs 단일 agent 결정 기준 (4축 + 비용 임계) | 131ee06 |
| G5 ★ | `domain_brief_schema.md` | §1.1 risk_level 제3자(비사용자) PII 상향 트리거 | 131ee06 |
| G6 | `domain_brief_schema.md` | §1.2 data_model 선택 필드 (hierarchy/entities/pii) | 131ee06 |
| G3 ★ | `templates/agent_template.md` | conditional_execution 슬롯 (condition: mode==guest) | 2058661 |
| G3 ★ | `templates/contract_template.md` | §3 cross-ref "조건부 산출(conditional output)" 열 | 2058661 |
| G4 | `templates/eval_template.md` | §B 채점 차원 applies_when (미해당 시 평균 제외) | 2058661 |
| G7 | `templates/project_state_template.md` | harness_status enum (active/dry-run-blueprint/proposal) | 2058661 |
| G8 | `harness_blueprint_schema.md` | §1.1 validation enum pending-by-design + 차원별 sub-status | 2058661 |

(G3 = agent + contract 2파일이므로 변경 항목 9, GAP 8.)

## cross-ref 정합

- **G8 ↔ validation_workflow.md §4 판정 종합**: 기존 `pass|fail|pending` 의미 보존, `pending-by-design` 은 "dry-run 범위상 정상"으로만 추가 구별 (active 게이트 규칙 7 불변).
- **G3 agent ↔ contract**: agent_template `conditional_execution` ↔ contract_template "조건부 산출" 열 — 양축 정합 (조건부 agent 의 출력이 조건부 산출로 매핑).
- **G6 ↔ G5**: domain_brief_schema `data_model.pii` (제3자 표시) ↔ risk_level 상향 트리거 — data_model 의 제3자 PII 표시가 risk 격상 입력.
- **G5/G6 ↔ generation_workflow 단계1~2**: data_model 수집이 domain_brief 단계와 정합.

## backward-compat (★ additive 검증)

- 8 변경 전부 **추가형** (새 섹션/필드/슬롯/enum 값/표 열). 기존 필드·절차·enum 값 삭제·재명명 **0**.
- 미기재 시 기본값: conditional_execution 생략=항상 실행 / applies_when 없음=무조건 채점 / harness_status 생략=active / validation 기존 pass·fail·pending 그대로.
- → **M1 podcast blueprint(구 machinery 산출)가 개선 machinery 하에서도 valid** (S3 재검증 §D 입증). validation_workflow 6검증 절차 자체 변경 0.

## 영향 범위
- 변경: meta_factory machinery 8 항목(7 파일) + 재검증 산출물(outputs/TEST/).
- 비변경: product runtime(A9 0줄) / product contracts / Skill 본문 / 라우터 / pytest 339(무관).
- improvement backlog: 8 → 0.

## 후속
- 차기 도메인 dry-run / 2nd 하네스 생성 시 개선 슬롯 활용.
- 검증5 실 eval-run 표본(PENDING-BY-DESIGN)은 별도 (eval-run §3~§6).
