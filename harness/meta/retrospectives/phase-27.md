# 회고 — Phase 27: 1차 MVP 실사용 마감

> 2026-06-05 | 격리 worktree `phase-27-realuse` | 신규 기능 0 = 활성화 + 마감 + 검증

## 1. 무엇을 했나

GPT 전략 판단(1차 MVP 실사용 마감 → 검증 → 2차 → /GOAL)을 레포 근거(roadmap/mvp_scope)로 객관 검증 = 타당 + 자체 갭분석과 합치 → **2차 기능이 아니라 이미 빌드된 1차 MVP를 실사용 가능하게 마감**.

- **S0**: HIP-006~010 → main 머지(a40eb36) — 홈 진입(B-2 부분)/plan 영속 배선(B-3)/RAG RPC(B-4) 토대.
- **S1 (B-1)**: `APP_PROFILE=realuse` 단일 스위치 — director + PKM 주입·추출 + 브랜딩 시드 + plans_repo 7 flag ON. 코드 default 불변(검증기 no-op) + 명시 env override 존중.
- **S2 (B-2)**: AppShell 지속 네비(홈/새 기획/내 brain) 전 페이지.
- **S3 (B-7)**: 최소 rate limit — generation 신원별 fixed-window→429, gated.
- **S4 (B-3·B-4·M-1)**: plan 영속 검증(기존 테스트) + migration 적용 스크립트(0001~0008) + README.
- **S5 (B-5)**: 첫-사용자 루프 e2e 자동 검증(부팅 director) + 실-런 런북 + human 핸드오프.

결과: hermetic pytest 802→**813**(기존 802 byte-identical) + scenario_simulation 36/36 + audit_naming 0 + frontend build 14/14.

## 2. 잘된 점

- **GPT 판단을 무비판 수용하지 않고 레포로 검증** 후 채택 — "1차 MVP 만들기"가 아니라 "이미 만든 것 실사용 마감"으로 정밀화(코드는 Phase 10에 통합 PASS, 경험·운영층 미완이 진짜 갭).
- **HIP-008 선발견**으로 중복 방지 — B-2/B-3/B-4 코드가 이미 있음을 git 조사로 확인 → Phase 27 범위를 "활성화+마감"으로 축소.
- **단일 스위치(APP_PROFILE) 설계** — flag 8개를 하나로 켜되 default no-op으로 byte-identical 유지(model_validator + model_fields_set override 존중). 실사용 활성과 테스트 결정성 양립.
- **gated + behavior-preserving 일관** — 모든 슬라이스 OFF byte-identical(기존 802 수정 0).

## 3. ★ 핵심 사건 — 동시 작업자 충돌 + worktree 격리 (P-NEW 후보)

- 진입 직후 **같은 작업 디렉터리/브랜치에서 HIP-006/007 자동 작업자가 동시에 활동**(몇 분마다 `git add -A` 커밋 + 히스토리 재작성) 발견 — 내 미커밋 S1 작업이 HIP 커밋에 섞이고 클로버링 위험.
- **대응**: ① 미커밋 산출물 gitignored Temp 백업 ② 사용자에 충돌 보고 + 진행 방식 질의 → "격리 worktree" 선택 ③ main 기준 별도 worktree(`phase-27-realuse`)에서 **내 변경만 수술적 재구성**(백업 config.py에 섞인 HIP-006 `agent_io_log_to_db`는 제외, 깨끗 main에 realuse 만 재적용) ④ 이후 전 작업 worktree에서 진행 → HIP 오염 0.
- **교훈**: 멀티 에이전트가 한 체크아웃을 공유하면 `git add -A`가 서로의 작업을 삼킨다. **격리(worktree/별 브랜치)가 정답** + 미커밋 작업은 즉시 백업. → 신규 패턴 후보 **P-CONCURRENT-ISOLATION-001**.

## 4. 불확실/한계 (U-1~U-5)

- **U-1**: plans_repo 실 영속은 Supabase 실 DB 필요 — 자동은 graceful까지(실 row 검증=실-런).
- **U-2**: rate_limit = in-memory 단일 프로세스(분산은 Redis sliding window 후속).
- **U-3**: director 토큰 비용 실사용 패턴 미상.
- **U-4**: 프론트 시각 e2e = build/typecheck 갈음(headless 한계).
- **U-5**: 격리 worktree → main 머지 시 동시 HIP 작업과 config.py/STATE/REGISTRY 충돌 가능 — 머지 순서로 조율.

## 5. 이월

- **B-5 human 실채점** — kit·런북 준비됨, 사용자 액션(실-런 후).
- **실 라이브 데모**(director 품질·실 영속·PKM 누적·다음-반영) — 사용자 opt-in(비용+Supabase). 자동은 배선까지.
- **AppShell 데스크톱 좌측 사이드바 full** — S2는 하단 탭 최소 구현, 사이드바 후속.
- 배포 Gate B~G(실 staging) — 인프라 user-provided, Phase 28+.

## 6. 다음

1차 MVP 실사용 마감(로컬) 완료 → **다음 = 실-런 검증(사용자 opt-in) → 5~10명 실사용 테스트 → 2차 MVP**. GPT 흐름(검증 → 2차 → /GOAL) 정합.
