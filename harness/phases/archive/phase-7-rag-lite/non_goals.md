# Phase 7 — Non-Goals

## 명시적 제외 (NG1~NG15)

| ID | 항목 | 이관 |
|---|---|---|
| **NG1** | Brand Memory 자동 추출 | **Phase 9+** (사용자 결정 5 계승) |
| **NG2** | Custom RAG (자체 embedding model) | Phase 21+ (ADR-024 §B) |
| **NG3** | Graph RAG (관계 graph 기반 retrieval) | Phase 21+ (ADR-024 §C) |
| **NG4** | Multi-modal RAG (이미지 + 영상 embedding) | Phase 8+/21+ (ADR-024 §E, 제한) |
| **NG5** | Re-ranking model (cross-encoder) | Phase 9+ (ADR-024 §F) |
| **NG6** | Hybrid retrieval (BM25 + vector) | Phase 7+ 별도 결정 (ADR-024 §D) |
| **NG7** | 사용자 데이터 자동 promotion (실 피드백 기반) | Phase 11+ (ADR-024 §A) |
| **NG8** | eval-run Skill 정식화 + golden_set 자동 평가 | Phase 9+ |
| **NG9** | prompt_registry 본문 정식화 (P-001~P-008) | Phase 8+ |
| **NG10** | MOA Lite 본격 (Intent / Planner / Critic / Rewriter 완전 분리) | Phase 8 |
| **NG11** | **PlanCard.tsx 수정** ★ | Phase 8+ (19연속 0줄 유지) |
| **NG12** | **component_map.md 수정** ★ | Phase 8+ (29연속) |
| **NG13** | Phase 1 endpoint `/api/v1/generate` 제거 | Phase 8+ |
| **NG14** | multi-provider client factory (Z-X2) | Phase 21+ |
| **NG15** | 영상 자동 편집 / TTS / BGM / 자동 업로드 | **MVP 영구 제외** |

## 단어 수준 금지 (신규 파일)

- `Brand Memory 추출`, `자동 추출 활성` (NG1)
- `Custom RAG`, `자체 embedding` (NG2)
- `Graph RAG`, `관계 graph` (NG3 — 단 LLM Wiki/RAG 분리 본문 참조는 허용)
- `Multi-modal`, `이미지 embedding`, `영상 embedding` (NG4)
- `Re-ranking`, `cross-encoder` (NG5)
- `Hybrid retrieval`, `BM25` (NG6)
- `자동 promotion`, `사용자 피드백 promotion` (NG7)
- `prompt_registry 본문` (NG9 — 단 ADR 참조 허용)
- `MOA Lite 본격` (NG10)
- `Anthropic`, `Claude API`, `claude-3` (NG14)
- `Spring`, `Boot`, `Expo`, `React Native` (NG14)
- `자동 편집`, `TTS`, `BGM`, `자동 업로드` (NG15)

## 회피 패턴

- ❌ "RAG 김에 Brand Memory도" → NG1
- ❌ "embedding 김에 multi-modal도" → NG4
- ❌ "retrieval 김에 re-ranking도" → NG5
- ❌ "promotion 김에 자동도" → NG7
- ❌ "agents/rag.py 수정 김에 MOA 분리도" → NG10
- ❌ "PlanCard에 RAG 결과 표시 한 줄" → NG11

## 사용자 결정 6-a 계승

PlanCard.tsx 무수정 + wrapper 정신. Phase 7은 backend 작업 중심 → frontend 변경 0 자동 보장. RAG 결과 노출은 backend Body에 추가 필드 (Optional)로만, frontend 표시는 Phase 8+ 또는 별도 결정.
