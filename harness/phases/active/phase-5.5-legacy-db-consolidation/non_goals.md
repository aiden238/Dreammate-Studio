# Phase 5.5 — Non-Goals

## 명시적 제외 (NG1~NG10)

| ID | 항목 | 이관 |
|---|---|---|
| **NG1** | Phase 7 RAG 본격 구현 (candidate_knowledge 5단계 코드, pgvector retrieval, promotion logic) | Phase 7 |
| **NG2** | Brand Memory 자동 추출 (확정 결정 [8]) | **Phase 9+** (사용자 결정 5 확정) |
| **NG3** | prompt_registry 본문 작성 (P-007 / P-008 prompt body 정식화) | Phase 7+ 또는 Phase 8+ |
| **NG4** | multi-provider client factory (Z-X2) | Phase 21+ |
| **NG5** | Spring / Expo 확장 | Phase 21+ |
| **NG6** | Phase 1 endpoint `/api/v1/generate` 제거 | Phase 8+ |
| **NG7** | **PlanCard.tsx 수정** ★ | Phase 7+ (18연속 0줄 유지) |
| **NG8** | **component_map.md 수정** ★ | Phase 7+ (28연속 0줄) |
| **NG9** | Critic fallback 4 완전 제거 (deprecated → 실 제거) | Phase 9+ eval-run 정식화 후 |
| **NG10** | 영상 자동 편집 / TTS / BGM / 자동 업로드 | **MVP 영구 제외** |

## 단어 수준 금지 (신규 파일)

- `Anthropic`, `Claude API`, `claude-3` (NG4)
- `Spring`, `Boot`, `Expo`, `React Native` (NG5)
- `자동 편집`, `TTS`, `BGM`, `자동 업로드` (NG10)
- `Brand Memory 추출`, `자동 추출 활성` (NG2 — 단 confirmation 명시는 허용)
- `prompt_registry 본문 작성` (NG3 — semver 참조는 허용)

## 회피 패턴

- ❌ "legacy 통합 김에 Phase 7 RAG 일부도" → NG1
- ❌ "validation 강화 김에 Brand Memory 명세도" → NG2
- ❌ "Phase 7 scope 진화 문서 김에 prompt_registry도" → NG3
- ❌ "PlanCard 4-layer 정합 한 줄만" → NG7

## 사용자 결정 6-a 계승

PlanCard.tsx 무수정 + wrapper 정신 — Phase 5.5는 코드 변경 최소 (legacy DB 통합 외)이므로 자동 보장.
