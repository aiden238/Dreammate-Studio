# Phase 27 — scope

## 포함 (5 슬라이스, 신규 기능 0)

- **S0 (선행, 완료)**: HIP-006~010 → main 머지 (a40eb36, pytest 802 green/gated).
- **S1 실사용 프로파일 (B-1)**: 핵심 루프를 ON으로 켜는 env 프로파일(APP_PROFILE=realuse) 정의 + 문서. output_mode=director + PKM 주입·추출(brand/personal) + 브랜딩 시드 + plans_repo. 코드 default는 OFF 유지.
- **S2 AppShell 네비 (B-2 잔여)**: 홈/새 기획/내 brain 상시 이동 네비. (홈 진입 카드는 HIP-008 S4 완료 — 네비 shell만 남음.)
- **S3 rate_limit 최소 (B-7)**: free-tier quota(요청 수 상한 → 429), gated default OFF, OFF byte-identical.
- **S4 plan 영속 ON 검증 + migration 운영 반영 준비 (B-3·B-4·M-1)**: 프로파일 ON에서 plan 영속 실동작 확인(또는 Supabase 의존 명시) + 0001~0008 적용 스크립트/절차.
- **S5 첫-사용자 루프 로컬 e2e + close (B-5)**: 프로파일 ON에서 홈→director 기획안→저장→/brain 축적→다음 반영 입증 + human 채점 kit 핸드오프 + 회고/머지.

## 예상 파일 변경 목록 (editable)

```
backend/fastapi/config.py                 # S1 프로파일 검증기 (default 불변)
backend/fastapi/middleware/ (신규)         # S3 rate_limit
backend/fastapi/main.py                    # S3 미들웨어 배선 (gated)
backend/fastapi/tests/                     # S1/S3 신규 test
apps/web/components/AppShell* (신규)        # S2
apps/web/app/layout.tsx                    # S2 shell 배선
backend/fastapi/.env.example               # S1 실사용 프로파일 키 문서화
backend/fastapi/.env.realuse.example       # S1 전용 프로파일 파일
scripts/ (신규 apply_migrations / realuse)  # S1/S4
phases/active/phase-27-mvp-realuse-close/  # 진행 메모/회고
PROJECT_STATE.md, PHASE_REGISTRY.md, meta/backlog.md  # 상태/이월 (상시 갱신)
docs/ (contract-change 경유만)              # 필요 시 api/env contract
```

## read-only (수정 시 contract-change)

```
docs/contracts/*            # api_contract, env_contract, rate_limit_policy 등
ai_system/prompts/*         # 프롬프트
backend/fastapi/db/migrations/*  # 기존 migration (참조만, 신규 작성은 별건)
```

## forbidden

```
phases/archive/*            # 과거 phase
HIP-006/007 동시 작업 파일   # critic.py·agents/planning.py·observability/agent_io_log.py·meta/improvement_* (다른 작업자 영역)
신규 제품 기능 (commercial 데이터레이어, 니즈서치, 공유/협업, SNS 자동생성, 트렌드, 외부데이터, 다중에이전트)
2차 MVP 기능
```

범위 밖 파일을 건드릴 필요가 생기면 → scope creep 신호, 즉시 사용자에게 알림.
★ 격리 worktree(`phase-27-realuse`)에서 작업 — main 체크아웃의 HIP-006/007 작업자와 분리.
