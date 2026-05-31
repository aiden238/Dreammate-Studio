# Phase M3 — Non-Goals

| ID | 항목 | 사유 |
|---|---|---|
| **NG1** | FastAPI/Next.js/Supabase 변경 | dry-run — 런타임 무관 (A9) |
| **NG2** | machinery(meta_factory 개선본) 변경 | M3 는 개선본을 **사용/검증**만 — 새 GAP 은 백로그 기록, 반영은 별도(M2 식) |
| **NG3** | 생성 재무 harness active 전환 / 2nd 프로젝트 시작 | proposal-first (factory_contract 규칙 7) |
| **NG4** | 기존 하네스(L2) / product contract / Skill 본문 변경 | dry-run 읽기만 |
| **NG5** | M1·M2 TEST 산출물(podcast) 변경 | 보존 — finance/ 별도 |
| **NG6** | 실 LLM 대량 호출 / 비용 평가 | dry-run — 추론·문서 설계. 검증5 는 절차 적용성 (pending-by-design) |
| **NG7** | 실제 금융 자문/투자 권유 로직 설계 | ★ 도메인 forbidden_scope 자체 (정보·기획 도구 한정) — 하네스 설계만, 금융 행위 0 |
| **NG8** | 새 GAP 을 M3 안에서 즉시 machinery 반영 | 검출·기록까지. 반영은 별도 (분기 결정) |
| **NG9** | 자동 generator / 영상·금융 실행 코드 | M0~M2 NG 계승 |

## ★ 핵심 원칙
1. **dry-run only**: 쓰기는 outputs/TEST/finance + validation 리포트만. machinery/런타임/기존 하네스 0.
2. **개선본 사용·검증**: M2 G1~G8 을 이질 도메인에서 실사용해보고 유효성 점검 + 새 GAP 검출 (반영 X).
3. **분기**: 새 GAP/수정 없음 → Phase 10 직행 / 있음 → 백로그 + 후속 결정.
4. **금융 안전**: 도메인 자체가 투자권유/원금보장/특정상품추천 금지 — forbidden_scope 로 명시 (G5/non_goals 매핑 테스트).

## 회피 패턴
- ❌ "이질 도메인이니 machinery 도 손보자" → NG2/NG8 (검출·기록까지)
- ❌ "재무니까 실제 투자 배분 알고리즘" → NG7 (하네스 설계만)
- ❌ "dry-run 김에 podcast 산출물도 정리" → NG5 (보존)
- ❌ runtime/machinery 1줄 변경 → NG1/NG2
