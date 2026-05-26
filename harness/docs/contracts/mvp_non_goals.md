# mvp_non_goals.md

> ⚠️ **PLACEHOLDER (부분 채움)** — 본 contract는 MVP 제외 목록 본문은 이미 운영 중이며,
> 정식 contract 형식(Phase별 재검토 절차, 변경 procedural)은 추후 갱신.

## Status

```yaml
status: placeholder_partial
fill_in_phase: 5+
priority: high
estimated_final_lines: 150
last_updated: 2026-05-26
```

## Why Placeholder?

핵심 제외 목록(아래 §본문)은 이미 결정되어 운영 중. 정식 contract 형태로 갱신하는 시점은 Phase 5+ MVP 출시 직전 또는 첫 외부 사용자 onboarding 설계 시점. 그 전까지는 본 마크다운이 유일한 출처(source of truth).

---

## MVP에서 하지 않을 것

- 자동 영상 생성
- 자동 영상 편집
- TTS 생성
- BGM 삽입
- 자막 자동 합성
- 이미지/영상 소스 생성
- 컷 편집 자동화
- 쇼츠 자동 조립
- 유튜브/인스타 자동 업로드
- 결제
- 팀 기능
- Expo React Native 앱
- Java/Spring Boot 백엔드 분리
- Full MOA
- Graph RAG
- 대규모 파인튜닝

## 예외 처리

MVP 범위 밖 기능이 필요하다고 판단되면 직접 구현하지 않고 `docs/contract_changes/` 또는 `meta/proposals/`에 제안한다.

---

## Scope (Future Fill-In)

본 contract가 추가로 다룰 범위 (Phase 5+):

- 제외 항목별 "왜 제외했는지" 사유 명시
- 각 항목의 Phase 재검토 시점 (Phase 11+, Phase 21+)
- 제외 항목이 사용자 요청으로 자주 들어오는 패턴 (운영자 통계)
- 제외 → 포함 전환 절차 (contract-change Skill + multi-llm-validation 필수)
- 영구 제외 항목 (영상 자동 편집, TTS 등 영상 제작 기능 일체) 명시
- 일시 제외 항목 (Phase X+ 진입 시 재검토 후보) 명시
- 외부 사용자가 제외 항목을 요청했을 때의 응답 가이드

## Known Dependencies (when filled in)

내부 의존:
- `product/mvp_scope.md`
- `product/vision.md`, `product/positioning.md`
- `docs/contracts/product_boundary.md` (placeholder)
- `PHASE_REGISTRY.md`
- `PROJECT_STATE.md` (제품 정의 결정)

## Fill-In Trigger

다음 조건 충족 시 본 contract 작성 착수:
- Phase 5+ 진입 (MVP 출시 직전)
- 또는 매 Phase 시작 시 재검토 (phase-review Skill)
- 또는 제외 항목 변경 제안 발생 시
- 또는 mvp_scope.md 변경 시 동시 갱신

## Related Skill / Phase

- Skill: `phase-review`, `qa-check` (제품 범위 카테고리)
- Phase: 매 Phase 시작 시 재검토 / 정식 갱신은 5+
- 책임자: AI(초안) + 사용자(최종 결정자, 영구 제외 결정은 사용자만)
