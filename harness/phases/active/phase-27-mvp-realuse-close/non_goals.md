# Phase 27 — non_goals (명시적 제외)

## 신규 기능 0 — GPT "하지 말 것" 목록 동의

- 니즈 서치 / 트렌드 분석 / 외부 데이터 연동
- 공유·커뮤니티 / 팀 협업
- SNS 콘텐츠 자동 완성(완성본 자동 게시)
- 다중 AI 에이전트 확장
- 2차 MVP 기능 일체

→ 1차 MVP 핵심 루프 실사용 검증 전에는 확장 보류(범위 분산 = "잡다한 AI 워크스페이스"화 위험).

## 운영·배포 (이번 범위 제외 — 사용자 인프라/액션 의존)

- 실제 staging 배포 (Gate B~G) — 로컬 마감까지만. 배포는 Supabase 프로젝트/호스팅/키 준비 후 별도.
- Supabase 실 DB에 migration 0001~0008 **실행** — 운영자/사용자 인프라. Phase 27은 **적용 스크립트/절차 제공**까지.
- human 실채점 **실행** — 사용자 액션. Phase 27은 **kit 핸드오프**까지(이미 준비됨).

## 기술 제약

- 코드 default flag **flip 금지** — 기존 pytest 802 byte-identical 유지. 활성은 **env 프로파일**로만.
- 프론트 시각 e2e(react-flow 그래프 등) — headless ResizeObserver 한계(4회+ 이월). DOM/유닛/API로 대체 검증.
- commercial 데이터레이어 enrichment(B-6) — 후속.
- SSE async worker(M-6) — 후속(로컬 동기로 충분).
