# Phase M2 — Non-Goals

## 명시적 제외 (NG1~NG12)

| ID | 항목 | 사유 |
|---|---|---|
| **NG1** | FastAPI/Next.js/Supabase runtime 변경 | meta machinery 개선 — 런타임 무관 (A9) |
| **NG2** | 기존 product contracts 변경 (api/output_schema/agent_io/db_schema/rag/llm_security) | M2 는 meta_factory machinery 만 — product contract 는 별도 contract-change |
| **NG3** | 기존 Skill 본문 변경 (harness-factory 포함) | machinery **문서**만 변경. Skill 절차 변경은 별도 contract-change |
| **NG4** | AGENTS.md / CLAUDE.md 라우터 변경 | machinery 개선은 라우터 무관 |
| **NG5** | `meta_factory/{README, factory_contract, validation_workflow}.md` 변경 | 8 GAP 이 가리키는 파일만 (G1~G8 명시 대상). validation_workflow 는 검증 절차 — GAP 없음 |
| **NG6** | 자동 generator 코드 작성 | M0 NG11 + M1 NG5 계승 — skeleton·문서 개선까지만 |
| **NG7** | 2nd 하네스 실 생성 / generated harness active 전환 | M1 NG2 계승 — proposal-first (factory_contract 규칙 7) |
| **NG8** | 새 GAP 발굴 / 새 도메인 dry-run | M2 는 M1 발견 8 GAP 반영 + 재검증만. 추가 도메인은 별도 phase |
| **NG9** | machinery 의 **파괴적 변경** (기존 필드/절차 삭제·재명명) | ★ **추가만** (additive) — 기존 M1 blueprint backward-compat 보장 (A5/GE) |
| **NG10** | blueprints/dreammate_current_harness_blueprint.md (M0 실측) 변경 | 실측 기록 — 변경 X (참조만) |
| **NG11** | golden_set / eval contract 변경 | 읽기만 — 재검증 5(eval-run)는 절차 적용성만 |
| **NG12** | 영상/오디오 자동 편집·TTS·async·A/B | MVP/Phase 11+ |

## ★ 핵심 원칙 (3)

1. **additive-only**: 8 GAP 반영은 **추가**만 (새 슬롯/필드/결정트리/enum 값). 기존 machinery 필드·절차 삭제·재명명 0 → M1 blueprint 가 개선 machinery 하에서도 그대로 유효 (NG9 = backward-compat 게이트).
2. **contract-change (CC-007)**: machinery = L3 contract. 8 변경은 contract-change Skill 절차 — proposal(M1 §D) → 검토 → 승인 → 반영 → CC-007 로그.
3. **재검증으로 입증**: "반영했다"로 끝내지 않고 M1 TEST 팟캐스트에 재적용하여 before/after 로 GAP 해소를 보인다 (사용자 결정 re-validate).

## 회피 패턴
- ❌ "machinery 고치는 김에 validation_workflow/factory_contract 도" → NG5 (GAP 없는 파일)
- ❌ "기존 필드 정리도 같이" → NG9 (additive-only, backward-compat 깨짐)
- ❌ "product contract 도 정합 맞추자" → NG2 (별도 contract-change)
- ❌ "재검증 김에 새 도메인도" → NG8 (M1 8 GAP 반영 + 재검증만)
- ❌ runtime 1줄 변경 → NG1 (A9 위반)
