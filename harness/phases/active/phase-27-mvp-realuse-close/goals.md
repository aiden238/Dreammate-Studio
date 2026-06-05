# Phase 27 — 1차 MVP 실사용 마감 (goals)

## 한 줄 정의

이미 빌드된 1차 MVP(Phase 1~26 + HIP-006~010)를 **실사용 가능하게 마감**한다 — 핵심 루프를 ON으로 켜고(실사용 프로파일), 발견 가능하게(AppShell 네비), 안전하게(rate_limit), 영속·운영 반영을 검증하여 **"처음 온 사용자가 도움 없이 기획안 1개 생성 → 저장 → 내 brain 축적 → 다음 기획에 반영"**을 로컬에서 끊김 없이 입증한다.

## 배경 (왜 지금)

- GPT 전략 판단 + 자체 갭분석(PROJECT_STATE §실사용 준비도 / meta/backlog.md) 합치: **코드 완성도 高(Phase 0~26, pytest 802) / 실사용·운영 준비 中 / 품질 검증 弱**.
- 가장 큰 갭 = "만들었지만 안 보이고, 안 켜져 있다": 핵심 기능 전부 flag default OFF + AppShell 네비 미구현 + plan 영속 OFF + rate_limit 0.
- HIP-008(main 머지 a40eb36)이 토대를 깔아둠: 홈 진입 카드(B-2 부분) · plan 영속 배선(B-3, gated) · match_approved_knowledge RPC(B-4 SQL). → Phase 27 = **신규 빌드가 아니라 활성화 + 마감 + 검증**.

## 통과 기준(요지)

처음 온 사용자가 도움 없이 → 기획안 1개(director) 생성 → 저장 → 내 brain 축적 → 다음 기획에 반영 이 **끊김 없이** 로컬에서 동작. (상세 = acceptance.md)

## 명시적 결정 (사용자)

- 진행 범위: **로컬 마감까지** (실 staging 배포는 인프라 준비 후 별도).
- 기본 output tier: **director** (실사용 프로파일에서 첫 기획안 = 연출/리텐션 브리프).
- flag 활성 = **운영 env 프로파일**(APP_PROFILE=realuse)로 ON. 글로벌 코드 default는 OFF 유지(기존 pytest 802 byte-identical).
- ★ 동시 HIP-006/007 작업자와 충돌 회피 위해 **격리 worktree(`phase-27-realuse`)**에서 진행(사용자 결정 2026-06-05).
