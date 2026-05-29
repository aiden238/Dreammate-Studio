# Phase 7 — Dependencies

## 이전 Phase 의존성

| Phase | 상태 | 의존 항목 |
|---|---|---|
| Phase 0~3 | ✅ done | 기본 |
| Phase 1 | ✅ done | `agents/rag.py` (baseline, RAG Lite 통합 대상) + `knowledge/rag/*` 정책 + `knowledge/llm_wiki/*` |
| Phase 4 | ✅ done | /plans/{plan_id}/generate baseline |
| Phase 4.5 | ✅ done | Rewriter + revise loop |
| Phase 5 | ✅ done | **Supabase + pgvector 환경** (pgvector extension 활용) + plans_repo + RLS 정책 |
| Phase 6 | ✅ done | canonical schema baseline |
| Phase 5.5 | ✅ done | **ADR-024 (Phase 7 RAG scope evolution)** — 5단계 + 확대 지점 + Brand Memory Phase 9+ |

**모두 done** — 강제 진행 사유 없음.

## Contract 참조 + 수정

| Contract | 사용 |
|---|---|
| `docs/contracts/rag_data_contract.md` | **수정 대상** (Slice 2 contract-change) — 5단계 stage enum 정식 등록 |
| `docs/contracts/api_contract.md` | **수정 선택** (선택, RAG endpoint 추가 시) |
| `docs/contracts/output_schema.md` | **참조만** (Phase 6 canonical 그대로) |
| `docs/contracts/agent_io_contract.md` | **참조만** (agents/rag.py 변경 시 v1.0.0 → v1.1.0 검토) |
| `docs/contracts/llm_security_contract.md` | **참조만** (PII + 인젝션 baseline) |
| `docs/contracts/mvp_non_goals.md` | 참조 |

## Skill 의존성

| Skill | 호출 시점 | 필수 |
|---|---|---|
| `phase-start` v1.3.0 | entry | 필수 |
| `multi-llm-validation` | Slice 1 (formal self V형식) | 필수 |
| **`rag-design`** | **Slice 1 ★ 첫 정식 트리거** (RAG architecture) | **필수** |
| **`rag-update`** | **Slice 4 ★ 첫 정식 트리거** (5단계 승격 절차) | **필수** |
| `contract-change` | Slice 2 (rag_data_contract.md) | 필수 |
| `qa-check` v1.2.0 | Slice 1 + 5 | 필수 |
| `harness-audit` | Slice 1 + 5 | 필수 |
| `design-review` | Slice 5 | 필수 (frontend 변경 0 회귀 검증) |
| `agent-io-check` | Slice 5 (agents/rag.py 변경 후) | 필수 |
| `meta-retrospective` | Slice 5 | 필수 |
| `phase-complete` v1.2.0 | Slice 5 (P-X2 다섯 번째 자동 게이트) | 필수 |

## 환경 / 외부

- **Supabase pgvector extension** (Phase 5 baseline) 활용
- **OpenAI embedding API** (`text-embedding-3-small` 권장 — Phase 21+ Custom 대체 NG2)
- **PostgreSQL JSONB + GIN 인덱스 미적용** (Phase 9+ 도입 검토 NG, V5 self-strengthen)
- pytest: 172/172 → 195~210/195~210 (+25~40 신규)
- next build / tsc / lint: 회귀 0 유지 (frontend 변경 0)
