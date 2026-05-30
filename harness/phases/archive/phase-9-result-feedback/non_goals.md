# Phase 9 — Non-Goals

## 명시적 제외 (NG1~NG14)

| ID | 항목 | 이관 | 사유 |
|---|---|---|---|
| **NG1** | **P-AUX-2 brand_memory_extractor agent 실 구현 + 자동 추출** | Phase 10+ | 사용자 결정 5 — Phase 9는 schema + ADR + 적재 경로 **준비만** |
| **NG2** | 4계층 full linkage (plan_options 테이블 / video_projects ↔ plans FK 강제) | Phase 11+ | 실 구현은 `plans` 테이블 + plan_candidates JSONB. idealized plan_options는 db_schema.md 미래 |
| **NG3** | Critic deprecated 0–5 fallback **완전 제거** | Phase 9.5+ eval-run | normalize wiring은 canonical 추가만, 0–5 병행 유지 (회귀 0) |
| **NG4** | eval-run Skill 정식화 + golden_set 회귀 자동화 | Phase 9.5+ | |
| **NG5** | async / background task / 큐 | Phase 11+ | moa_policy §4 sync |
| **NG6** | **PlanCard.tsx 수정** ★ | Phase 11+ | wrapper 정신 (피드백 UI는 page.tsx inline) |
| **NG7** | **component_map.md 수정** ★ | Phase 11+ | 신규 component 등록 X (page.tsx inline UI) |
| **NG8** | Phase 1 endpoint `/api/v1/generate` 제거 | Phase 8+ 교차검토 후 | 사용자 결정 5-a |
| **NG9** | multi-provider client factory (Z-X2) | Phase 21+ | |
| **NG10** | Discovery 카드 클릭 로그(discovery_choices) **수집 endpoint 본격** | Phase 10+ | Phase 9는 테이블 schema만 (선택), 수집은 Discovery wizard 본격 시 |
| **NG11** | scripts / storyboards / final_outputs 산출물 테이블 | Phase 10+ | 결과 저장은 plan 선택/피드백 범위 |
| **NG12** | RAG candidate 자동 promotion (피드백 → approved_knowledge 자동 승격) | Phase 11+ | 적재(pending)까지만, 승격은 rag-update 두 번째 |
| **NG13** | prompt A/B 실행 | Phase 11+ | |
| **NG14** | 영상 자동 편집 / TTS / BGM / 자동 업로드 | **MVP 영구 제외** | |

## 핵심 제약: normalize wiring은 의도된 critic_evaluation delta만 (★)

- normalize_to_canonical wiring은 critic_evaluation에 canonical(overall_score 0–1 + dimensions) **추가** (deprecated 0–5 병행 유지)
- 이로 인해 critic_evaluation 구조가 바뀌는 baseline test가 있으면 = **의도된 delta** (Phase 8 Slice 4 version bump 선례) → 해당 assertion만 최소 갱신
- 단, **schemas/output.py CriticEvaluation 모델은 불변** (Phase 6 canonical — 이미 Optional canonical 필드 보유)
- "wiring 김에 0–5 제거" = NG3 위반

## 단어 수준 금지 (신규 파일)

- `brand_memory_extractor` 실행 / `자동 추출 활성` (NG1 — agent 미구현, ADR 설계 참조는 허용)
- `plan_options` 테이블 신규 (NG2 — db_schema 참조는 허용)
- `background task`, `Celery`, `큐`, `WebSocket` (NG5)
- `Anthropic`, `Claude API`, `claude-3`, `Spring`, `Expo` (NG9)
- `자동 편집`, `TTS`, `BGM` (NG14)

## 회피 패턴
- ❌ "피드백 김에 P-AUX-2 자동 추출도" → NG1
- ❌ "선택 저장 김에 plan_options 4계층도" → NG2
- ❌ "normalize wiring 김에 0–5 제거" → NG3
- ❌ "피드백 UI 김에 PlanCard에 버튼 추가" → NG6 (page.tsx wrapper)
