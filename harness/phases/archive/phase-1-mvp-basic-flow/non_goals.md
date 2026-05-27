# Phase 1 — Non-Goals

> 이 파일은 Phase 1에서 **명시적으로 하지 않을 것**을 정의한다.  
> scope creep 방지용. "조금만"이라도 여기 항목을 건드리면 Phase 경계 위반.

---

## Phase 1에서 하지 않을 것

### UI / UX
- [ ] Discovery Wizard 5단계 카드 흐름 → Phase 3
- [ ] Quick Mode 카드 UI → Phase 3
- [ ] Direction Approval 카드 UI → Phase 3
- [ ] 기획안 3개 비교 카드 → Phase 4+
- [ ] 브랜드 컬러 / 폰트 시스템 → Phase 3
- [ ] 다국어 지원 (i18n) → Phase 11+
- [ ] 접근성 AA 완전 준수 → Phase 11+
- [ ] 애니메이션 / 트랜지션 → Phase 3

### AI 기능
- [ ] Critic revise 2회 루프 → Phase 4+
- [ ] 기획안 3개 동시 생성 → Phase 4+
- [ ] Brand Memory 자동 추출 → Phase 4+
- [ ] MOA 전체 (4 Agent 완전 파이프라인) → Phase 8
- [ ] RAG 5단계 승격 파이프라인 → Phase 7
- [ ] Custom RAG (Graph / 파인튜닝) → Phase 21+
- [ ] 광고 표현 차단 실사용 → Phase 4+

### 인프라 / 보안
- [ ] 로그인 / 회원가입 (Auth) → Phase 5
- [ ] 팀 / 멀티 사용자 → Phase 11+
- [ ] Rate Limit 실서버 적용 → Phase 10
- [ ] PII 마스킹 자동화 → Phase 6+
- [ ] CI/CD 파이프라인 → Phase 10
- [ ] 배포 (Vercel / AWS) → Phase 10
- [ ] Docker 프로덕션 이미지 → Phase 10

### 데이터
- [ ] Brand / Domain / Series 테이블 → Phase 5+
- [ ] 피드백 저장 (choice_logs) → Phase 9
- [ ] 데이터 보존 정책 적용 → Phase 9+
- [ ] 사용자 데이터 내보내기 → Phase 11+

### 제품 (영구 제외 — MVP 이후도 해당)
- [ ] 자동 영상 생성 / 편집
- [ ] TTS 생성
- [ ] BGM 삽입
- [ ] 자막 자동 합성
- [ ] YouTube / Instagram 자동 업로드
- [ ] 결제 기능
- [ ] Expo React Native 앱 (Phase 21+)
- [ ] Java / Spring Boot 백엔드 분리 (Phase 21+)

---

## 경계 위반 판단 기준

요청받은 기능이 위 목록에 있으면:

1. **즉시 거절** — "Phase 1 non-goals에 해당합니다"
2. **후속 Phase 이관** — PHASE_REGISTRY.md의 해당 Phase 언급
3. **예외 검토** — 사용자가 반드시 필요하다면 `meta/proposals/`에 제안 작성 후 결정

---

## 변경 절차

non_goals 변경 (항목 제거 = Phase 1 scope 확장) 시:

1. `docs/contract_changes/` 또는 `meta/proposals/`에 제안 작성
2. `contract-change` Skill 절차 실행
3. `multi-llm-validation` 필수 (scope 변경은 큰 결정)
4. 사용자 최종 승인
