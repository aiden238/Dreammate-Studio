# Phase 5 — Non-Goals

## 명시적 제외 (NG1~NG15)

| ID | 항목 | 이관 |
|---|---|---|
| **NG1** | Brand Memory 자동 추출 (확정 결정 [8]) | Phase 6+ (DB baseline 활용) |
| **NG2** | RAG Lite 본격 구현 (Phase 7) | Phase 7 |
| **NG3** | MOA Lite 본격 (Phase 8 — Intent / Planner / Critic / Rewriter 완전 분리) | Phase 8 |
| **NG4** | 결과 저장 + 피드백 UI (Phase 9) | Phase 9 |
| **NG5** | 결제 / 구독 / Team 기능 | Phase 21+ |
| **NG6** | multi-provider client factory (Z-X2) | Phase 21+ |
| **NG7** | Phase 1 endpoint `/api/v1/generate` 제거 | Phase 8+ |
| **NG8** | **PlanCard.tsx 수정** ★ | Phase 7+ (13연속 0줄 baseline 유지) |
| **NG9** | **component_map.md 수정** ★ | Phase 7+ (23연속 0줄) |
| **NG10** | prompt_registry 본문 정식화 (P-007 / P-008) | Phase 7+ |
| **NG11** | Critic fallback 4 완전 제거 | Phase 9+ eval-run 정식화 후 |
| **NG12** | Spring Boot / Expo 확장 | Phase 21+ |
| **NG13** | Custom RAG / Graph RAG | Phase 21+ |
| **NG14** | 영상 자동 편집 / TTS / BGM / 자동 업로드 | **MVP 영구 제외** |
| **NG15** | Critic revise effect 자동 eval (golden_set FC-001~005) | Phase 9+ eval-run |

## 단어 수준 금지

신규 파일에 다음 단어 등장 금지:
- `prompt_registry` (NG10)
- `Anthropic`, `Claude API`, `claude-3` (NG6, multi-provider)
- `Spring`, `Boot` (NG12)
- `Expo`, `React Native` (NG12)
- `Brand Memory` (NG1, 단 DB column 정의 시 `brand_memory` 컬럼 자체는 허용 — Phase 6+ 활용 baseline)
- `자동 편집`, `TTS`, `BGM`, `자동 업로드` (NG14)

## 회피 패턴

- ❌ "DB 김에 Brand Memory도" → NG1
- ❌ "Auth 김에 결제도" → NG5
- ❌ "RLS 김에 RAG도" → NG2
- ❌ "PlanCard 수정 김에 4-layer도" → NG8

## 사용자 결정 6-a 계승

PlanCard.tsx 무수정 정신 + wrapper UI 패턴 유지. AuthGuard / SSE Progress UI는 wrapper 또는 별도 컴포넌트로 추가, PlanCard 내부 수정 X.
