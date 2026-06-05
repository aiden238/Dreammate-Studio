# Phase 27 — acceptance

> 통과 기준 = "처음 온 사용자가 도움 없이 → director 기획안 1개 생성 → 저장 → 내 brain 축적 → 다음 기획에 반영"이 로컬에서 끊김 없이.

- [x] **A1 (S1) 실사용 프로파일**: env 프로파일(APP_PROFILE=realuse) 정의 + 문서화. 그 프로파일로 서버 기동 시 effective output_mode=director + PKM 주입·추출 ON + 브랜딩 시드 ON + plans_repo ON. **코드 default OFF 유지 → 기존 hermetic pytest byte-identical**. (자동: test_realuse_profile.py 6케이스 + OFF no-op)
- [ ] **A2 (S2) AppShell 네비**: 모든 주요 페이지(홈/플랜/brain/위저드)에서 홈·새 기획·내 brain 이동 가능. typecheck + lint pass, 모바일 360px 한 손 조작, design.md 준수(제작 UI 미포함). (수동 DOM + typecheck)
- [ ] **A3 (S3) rate_limit 최소**: free-tier 요청 상한 초과 시 429 + 명확한 메시지. gated default OFF → OFF byte-identical. 신규 test(상한 내 통과 / 초과 차단 / OFF no-op). (자동)
- [ ] **A4 (S4) plan 영속 + 운영 반영 준비**: 프로파일 ON에서 생성 plan이 PlansRepo 경로로 영속 시도(graceful) + 재조회 동작 — 또는 Supabase 실DB 의존을 명시. migration 0001~0008 적용 스크립트/절차 존재(실행은 ops). (자동 + 문서)
- [ ] **A5 (S5) 첫-사용자 루프 로컬 e2e**: 프로파일 ON에서 홈→director 기획안 생성→저장→/me/pkm-graph(또는 /brain) 축적 확인→같은 사용자 다음 생성에 반영. PASS 리포트. human 채점 kit 핸드오프(사용자 액션). (수동 e2e + API)
- [ ] **A6 게이트**: hermetic pytest green(802 + 신규) + scenario_simulation 36/36 + audit_naming 0 + frontend typecheck/lint. (자동)

## 검증 방법 매핑

| 기준 | 방법 | 자동/수동 |
|---|---|---|
| A1 | test_realuse_profile.py (default OFF / realuse ON / override / env) | 자동 ✅ |
| A2 | typecheck/lint + 브라우저 DOM 네비 확인 | 반자동 |
| A3 | rate_limit 신규 test (통과/차단/OFF no-op) | 자동 |
| A4 | 영속 test(graceful) + apply 스크립트 dry-run | 자동+문서 |
| A5 | 로컬 서버 e2e(API + DOM) 리포트 | 수동 |
| A6 | pytest + scenario_simulation.ps1 + audit_naming.ps1 + npm typecheck/lint | 자동 |
