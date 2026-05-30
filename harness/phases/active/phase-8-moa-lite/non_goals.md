# Phase 8 — Non-Goals

## 명시적 제외 (NG1~NG15)

| ID | 항목 | 이관 | 사유 |
|---|---|---|---|
| **NG1** | 비동기 큐 / background task 도입 | Phase 11+ | moa_policy §4 — 동기 처리 유지 (Phase 0~10), async는 트래픽 증가 후 |
| **NG2** | Brand Memory extractor (P-AUX-2) 실 구현 | Phase 9+ | 사용자 결정 5 계승 |
| **NG3** | prompt A/B 실행 (50:50 라우팅) | Phase 11+ | semver 정식화만, A/B 실행은 100세션 누적 후 |
| **NG4** | 새 agent 추가 (5번째 agent) | Phase 11+ | moa_policy §6 — Phase 0~10 새 agent 보류 |
| **NG5** | **Critic canonical 재정의** (Phase 6 ADR-018 변경) | — | 사용자 결정: conservative adapter (Phase 6 불변) |
| **NG6** | Critic fallback 4 완전 제거 | Phase 9+ eval | Phase 6 deprecated 유지 |
| **NG7** | eval-run Skill 정식화 + golden_set 회귀 자동화 | Phase 9+ | prompt 회귀 평가는 Phase 9+ |
| **NG8** | Custom RAG / Graph RAG / Re-ranking | Phase 21+ | ADR-024 §확대 지점 |
| **NG9** | **PlanCard.tsx 수정** ★ | Phase 9+ | backend-only phase |
| **NG10** | **component_map.md 수정** ★ | Phase 9+ | |
| **NG11** | Phase 1 endpoint `/api/v1/generate` 제거 | Phase 8+ 교차검토 후 | 사용자 결정 5-a — 마이그 완료 후 (본 phase 아님) |
| **NG12** | multi-provider client factory (Z-X2) | Phase 21+ | prompt semver는 정식화하되 provider 교체는 미구현 |
| **NG13** | SSE 실시간 양방향 / WebSocket | Phase 21+ | 단방향 progress만 (ADR-022) |
| **NG14** | 결과 저장 + 피드백 UI | Phase 9 | |
| **NG15** | 영상 자동 편집 / TTS / BGM / 자동 업로드 | **MVP 영구 제외** | |

## 핵심 제약: Behavior-Preserving (★ Phase 8 정신)

- orchestrator 추출은 **동작 보존 리팩터** — Envelope 출력 byte-identical
- 기존 pytest 223개 **수정 없이** 그대로 PASS (테스트가 동작 불변의 증거)
- god-function의 graceful 처리 / 에러 코드 / validation.checks 순서 모두 보존
- "리팩터 김에 로직 개선"은 scope creep → 금지

## 단어 수준 금지 (신규 파일)

- `background task`, `Celery`, `큐`, `asyncio.create_task` (NG1 — 단 orchestrator 내부 asyncio.gather는 기존 패턴 유지 허용)
- `Brand Memory 추출`, `memory_extractor` (NG2 — 단 P-AUX-2 registry 항목 참조는 허용)
- `WebSocket` (NG13)
- `Anthropic`, `Claude API`, `claude-3` (NG12)
- `Spring`, `Expo`, `자동 편집`, `TTS`, `BGM` (NG15)

## 회피 패턴

- ❌ "orchestrator 추출 김에 Intent 로직 개선" → behavior-preserving 위반
- ❌ "SSE 김에 background task로 비동기화" → NG1
- ❌ "prompt 정식화 김에 Critic canonical 0–1 재작성" → NG5 (사용자 결정)
- ❌ "MOA 김에 5번째 agent" → NG4
