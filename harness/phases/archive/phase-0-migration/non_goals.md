# Phase 0. Non-Goals

이 Phase에서는 **하네스 정비만** 수행한다. 다음은 명시적 제외:

## 코드 / 구현 제외

- ❌ 영상기획 에이전트 본체 코드 작성 (Phase 1+에서)
- ❌ Next.js / FastAPI 실제 코드 작업 (Phase 3+에서)
- ❌ DB 마이그레이션 SQL 작성 (Phase 5에서)
- ❌ LLM API 호출 코드 (Phase 6+에서)
- ❌ RAG 벡터 임베딩 작업 (Phase 7에서)

## 도구 / 별도 작업 제외

- ❌ `tools/agent-html/` Claude Code 빌드 (Phase 0 완료 후 별도 세션)
- ❌ 캡스톤 (SSAK-LOG) 관련 작업
- ❌ Mobile (Expo) / Spring Boot 관련 작업 (Phase 21+)
- ❌ 결제 / Auth / Admin Dashboard (각 Phase)

## 본 Phase 내 자제

- ❌ Sprint 자동 진입 (각 Sprint 종료 후 사용자 승인 필요)
- ❌ contract 본문 직접 편집 (contract-change Skill 절차 필요. S1 교체와 S3 깊은 작성은 예외)
- ❌ HARNESS_ROOT 변경 (S0에서 확정. Dreammate_Studio/harness/)
- ❌ Skill 폴더 구조 재변경 (v1.2.0에서 .claude/skills/ 단일 확정)
- ❌ MVP 제외 항목 (Mobile / Spring / billing 등) 폴더에 새 파일 작성
- ❌ skip hooks (`--no-verify`) 사용
- ❌ `git reset --hard` / `force push` (사용자 명시 허가 없이)

## MVP 영구 제외 (Phase 1+ 도 동일)

- ❌ 영상 자동 편집 / 자동 업로드
- ❌ TTS / BGM 생성
- ❌ 팀 협업 / 권한 관리
- ❌ Admin Dashboard
- ❌ 결제 / Billing
- ❌ 고급 성과 분석 / 실시간 SNS 크롤링
