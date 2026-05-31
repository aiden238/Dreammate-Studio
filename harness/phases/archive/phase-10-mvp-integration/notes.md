# Phase 10 — Notes

## 진입 맥락
- Meta-Factory detour(M0~M3) 종료 — self-improvement loop 완주 + 도메인 범용성(인접·이질) 입증. **제품 로드맵 복귀**.
- 사용자 결정: 범위 **C(풀)** + eval 실행 **mock-deterministic 유지**.

## ★ scope C + mock 화해 (핵심)
```
범위 C = 핵심 통합 + P-AUX-2 agent + 실 LLM eval mode + RAG rubric + golden_set 확대 + 배포 게이트
eval mode = 실 LLM mode capability(경로 wire + 문서)만 구축, default 실행은 mock-deterministic
→ "활성"(C)은 모드 capability, "mock 유지"는 default 실행. ADR-033 정합. 실 LLM run = opt-in(키).
```

## ★ 성격 전환: meta-phase → 제품 phase
- 런타임 변경 有 — **A9(런타임 0) 미적용**.
- 게이트: behavior-preserving(기존 endpoint/test 불변 + 신규 추가) + pytest 339→확대(기존 수정 0) + eval 회귀 + P-X1.
- meta_factory 무관 (detour 종료). M3 새 GAP 3은 백로그.

## 6 scope 항목 → Slice
| 항목 | Slice |
|---|---|
| MVP end-to-end 통합 + 누적 baseline 회귀 | S1 |
| P-AUX-2 brand_memory_extractor agent 실구현 | S2 |
| 실 LLM eval mode 정식화 (capability, default mock) | S3 |
| RAG eval_rubric golden_set 정식화 + golden_set 11→확대 | S3 |
| 배포 테스트 게이트 A~G 준비 | S4 |

## ★ 안전 게이트
```
behavior-preserving : 기존 endpoint/test 0 수정 (신규 추가만)
eval default mock    : 실 LLM = capability only, default off, 키 커밋 금지 (.env user-provided)
PlanCard/component_map : 35/45연속 0줄 유지 (page 레벨 통합)
MVP 경계             : 영상 제작 영구 미포함
P-X1                 : sub-agent forbidden 검사 연속
```

## 보안 메모 (★ 사용자 지침 계승)
- 실제 자격증명/API 키(OPENAI/ANTHROPIC/SUPABASE)는 .env 로 사용자 제공 — **파일/commit 에 절대 포함 금지**. sub-agent 도 placeholder 만.
- brand memory 추출은 PII 마스킹(Phase 9 security-review 계승) 필수.

## 결정 대기 / 옵션
- 본 entry 는 실행 전 계획(기획). 사용자 "진행" 시 entry commit(이미 완료 시) → S1~S4 순차 + close.
- M3 새 GAP 3(G9/G10/G11) = 백로그 — Phase 10 후 또는 차기 meta-phase (blocking 0, Phase 10 무관).

## 다음 (Phase 10 이후)
- 배포 게이트 A~G 통과 → 알파/베타 진입.
- Phase 11+: 4계층 full linkage / SSE async worker / prompt A/B / 자동 promotion / 실 LLM eval default 전환 / M3 GAP 반영.
