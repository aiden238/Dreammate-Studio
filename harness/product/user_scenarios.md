# user_scenarios.md — 사용자 시나리오

> 위치: `product/user_scenarios.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `product/target_users.md` (3 페르소나), `apps/web/design.md`
> 참조: `docs/contracts/error_response_contract.md` (실패 시나리오), `ai_system/architecture.md`

---

## 0. 시나리오 작성 원칙

```
1. 각 시나리오는 단계별 사용자 행동 + 시스템 응답 + 예상 시간 + 성공 기준을 포함한다.
2. 시나리오는 페르소나 1 (1인 마케터)를 기본 화자로 한다. 다른 페르소나는 명시.
3. 시간 표기는 사용자 체감 시간 (대기 + 입력 합).
4. 성공 기준은 eval/regression_eval.md 측정 지표와 정합.
5. 모든 시나리오는 4계층 데이터 모델 / Hybrid UX / MOA Lite / RAG Lite 흐름을 따른다.
```

---

## 1. 시나리오 1 — 신규 사용자 첫 영상기획 (Discovery 5단계)

### 페르소나

```
김지영 (페르소나 1, 1인 마케터). 처음 가입.
```

### 시작 컨텍스트

```
- 회원가입 직후 (Supabase Auth + Google OAuth).
- 4계층 데이터 없음 (콜드스타트).
- 만들고 싶은 영상: "신상 향수 인스타 리뷰 영상"
```

### 단계별 흐름

```
[Step 0]  로그인 후 첫 진입 화면
  사용자: "영상기획 시작하기" 버튼 클릭
  시스템: Brand가 없음을 감지 → Discovery Wizard 자동 진입
  시간:   3초

[Step 1]  Brand 등록
  사용자: 입력 "OOO 향수 (1인 브랜드, 친근하고 부드러운 톤)"
  시스템: Brand 카드 생성 + Brand Memory 시드 (자동 추출 톤: friendly_soft)
  시간:   60초

[Step 2]  Domain 선택 (카드 5장)
  시스템: ["뷰티/화장품", "푸드", "패션", "라이프스타일", "직접 입력"]
  사용자: "뷰티/화장품" 선택
  시간:   10초

[Step 3]  Series 등록
  사용자: 입력 "신상 리뷰 시리즈, 주 1회"
  시스템: Series 카드 생성, "신상 리뷰" 컨텍스트 저장
  시간:   30초

[Step 4]  타겟 선택 (페르소나 카드 5장)
  시스템: ["20대 향수 입문자", "30대 시그니처 찾는 사람", "선물용 구매자",
          "본인 보상 소비자", "직접 입력"]
  사용자: "20대 향수 입문자" 선택
  시간:   15초

[Step 5]  톤·메시지 방향 (카드 5장)
  시스템: ["스토리텔링형", "친근 후기형", "비교 분석형",
          "감성 무드형", "직접 입력"]
  사용자: "친근 후기형" 선택
  시간:   15초

[Step 6]  한 줄 방향 승인 카드
  시스템: "20대 향수 입문자에게 친근 후기 톤으로 신상 향수의 매력을
          가볍게 소개하는 인스타 영상"
  사용자: "이대로 진행" 클릭
  시간:   5초

[Step 7]  AI 생성 (4단계 progress stepper)
  시스템: [Intent ✓] → [RAG ✓] → [Plan ✓ (3개)] → [Critic ✓ (점수 0.78/0.72/0.65)]
  시간:   45~60초 대기

[Step 8]  결과 — 영상기획안 3개 비교 카드
  사용자: 첫 번째 카드 (점수 0.78) 선택
  시스템: Video Project 저장 + 피드백 trace 기록
  시간:   30초

[Step 9]  Brand Memory 자동 추출 알림
  시스템: "이번 선택에서 톤 'gentle_review_tone'을 학습했어요"
  사용자: "확인" 또는 "수정"
  시간:   10초
```

### 총 소요 시간

```
첫 진입~결과 선택: 4~5분 (대기 60초 포함)
```

### 성공 기준

```
- Step 7 progress stepper의 모든 단계 ✓.
- Step 8 결과 3개 카드 모두 표시 + Critic 점수 표시.
- Step 9 Brand Memory 자동 추출 정상 동작.
- 사용자 임의 종료 후 다시 들어왔을 때 4계층 데이터 유지.
```

---

## 2. 시나리오 2 — 기존 Series에 새 영상 추가 (Quick Mode)

### 페르소나

```
김지영 (페르소나 1, 1인 마케터). 시나리오 1 1주일 후.
```

### 시작 컨텍스트

```
- Brand: "OOO 향수" (등록됨)
- Domain: "뷰티/화장품"
- Series: "신상 리뷰 시리즈" (1편 작성됨)
- Brand Memory: friendly_soft + gentle_review_tone
- 만들고 싶은 영상: "이번 주 신상 향수 두 번째 리뷰"
```

### 단계별 흐름

```
[Step 0]  로그인 → 홈
  시스템: 기존 Series 카드 노출 + "이 Series에 영상 추가" 버튼
  사용자: "신상 리뷰 시리즈"에 "추가" 클릭
  시간:   5초

[Step 1]  Quick Mode 진입 (자동 분기)
  시스템: Brand/Domain/Series 컨텍스트 발견 → Quick Mode 자동 진입
  화면:   "이번 영상에 대해 짧게 알려주세요" 입력창
  사용자: "이번엔 가을 시그니처 향수, 따뜻한 우디 향" 입력
  시간:   30초

[Step 2]  부족 정보 질문 (1~2개)
  시스템: "이 향수의 셀링 포인트 한 가지만 알려주실래요?"
  사용자: "사무실에서도 부담 없는 가벼움" 입력
  시간:   20초

[Step 3]  한 줄 방향 승인 카드
  시스템: "Brand 톤 (gentle_review_tone)을 그대로 이어서 가을 시그니처
          향수를 사무실 친화 포인트로 소개"
  사용자: "이대로 진행" 클릭
  시간:   5초

[Step 4]  AI 생성 (4단계 progress)
  시스템: Brand Memory 자동 상속 + RAG에서 이전 Series 영상 패턴 검색
  시간:   30~45초 대기

[Step 5]  결과 — 3개 카드
  사용자: 두 번째 카드 (점수 0.81) 선택
  시간:   20초
```

### 총 소요 시간

```
첫 진입~결과 선택: 90초 ~ 2분
```

### 성공 기준

```
- Step 1 Quick Mode 자동 분기 정확 (Discovery 우회).
- Step 4 Brand Memory 자동 상속 (사용자가 톤 재입력 불필요).
- 결과 3개 카드의 톤이 이전 Series와 일관 (eval/brand_consistency_eval.md).
- p95 시간 90초 이내.
```

---

## 3. 시나리오 3 — 영상기획 결과 마음에 안 들 때 (Critic revise + Rewrite)

### 페르소나

```
박서연 (페르소나 2, 브랜드 매니저). Quick Mode 사용 중.
```

### 시작 컨텍스트

```
- Brand: "회사 브랜드 (정중하고 신뢰감 있는 톤)"
- Series: "제품 발표 영상"
- 첫 AI 생성 결과 3개 카드 받음, 그 중 어느 것도 마음에 안 듦.
```

### 단계별 흐름

```
[Step 0]  결과 화면
  사용자: 3개 카드 검토. "광고 표현 좀 강한데..."
  시간:   30초

[Step 1]  카드 옆 "다듬기" 버튼 클릭
  사용자: "톤이 부드러웠으면 좋겠어요" 자유 텍스트 입력
  시간:   20초

[Step 2]  Critic revise 발동
  시스템: Critic Agent가 사용자 피드백 반영 + 광고 단어 강조 차단
  로직:   max_revise_round=2 (무한 루프 차단)
  시간:   25~40초

[Step 3]  Rewrite 결과
  시스템: 같은 카드 새 버전 + diff 표시 ("부드러운 톤으로 다듬어졌어요")
  사용자: 검토 → "이번엔 좋아요" 선택
  시간:   30초

[Step 4]  최종 저장
  시스템: Video Project 저장 + 피드백 trace
          ("user_revision_request: tone_soften, accepted")
  시간:   5초
```

### 분기 — revise 한계 도달

```
사용자가 2회 revise 후에도 만족하지 않으면:

[Step 5-A]  Critic revise_round=2 도달
  시스템: 더 이상 revise 불가 + "직접 다듬어보시겠어요?" 안내
  user_action: manual_edit (error_response_contract §6)
  → 사용자가 텍스트 직접 편집 모드

[Step 5-B]  새 plan 3개 다시 생성
  사용자: "처음부터 다시" 클릭 → Quick Mode 재진입
  시간:   30~45초
```

### 성공 기준

```
- revise 1회: 변경된 결과의 광고 단어 0개 (eval/brand_consistency_eval.md).
- revise 한계 도달 시 명확한 안내 + 다음 액션 제시.
- max_revise_round=2 강제 (E-LLM-010 에러로 보호).
- 피드백 trace 정상 저장 (Brand Memory 갱신 시드).
```

→ `docs/contracts/error_response_contract.md` §4.2 E-LLM-010

---

## 4. 시나리오 4 — 브랜드 정체성 업데이트 (Brand Memory 갱신)

### 페르소나

```
김지영 (페르소나 1). 6개월 사용 후 Brand 톤을 약간 바꾸려 함.
```

### 시작 컨텍스트

```
- Brand Memory 누적: friendly_soft + gentle_review_tone + casual_humor
- 사용자 요청: "이제 좀 더 전문가 톤으로 가고 싶어요"
```

### 단계별 흐름

```
[Step 0]  설정 화면 → Brand Memory 검토
  사용자: 누적 톤 목록 검토. "casual_humor 빼고 싶어요"
  시간:   30초

[Step 1]  Brand Memory 수정 UI
  시스템: 톤별 toggle (활성/비활성) + 새 톤 추가
  사용자: "casual_humor" 비활성 + "professional_warmth" 추가 (수동 입력)
  시간:   60초

[Step 2]  저장 확인
  시스템: "다음 영상부터 새 톤으로 적용해드릴게요"
  사용자: "확인" 클릭
  시간:   3초

[Step 3]  검증 (다음 영상 생성 시)
  사용자: Quick Mode 영상 1편 생성
  시스템: 새 톤 적용 + Critic이 톤 일관성 점수 부여
  성공:   새 톤 카드에 점수 >= 0.70
```

### 성공 기준

```
- Step 1 Brand Memory 수정이 영구 저장 (Supabase brand_memory_entries).
- Step 3 다음 영상에 새 톤 즉시 반영.
- 이전 영상은 영향 없음 (역사 보존).
- 사용자가 다시 원복 가능 (이전 톤 복원 버튼).
```

→ `docs/contracts/db_schema.md` brand_memory_entries

---

## 5. 시나리오 5 — 의도와 다른 입력 (Intent Filter 발동)

### 페르소나

```
이민준 (페르소나 3, 크리에이터). 모바일 사용 중.
```

### 시작 컨텍스트

```
- 새 Series 시작 시도 중.
- 입력: "유튜브 영상 자동 편집 좀 해주세요"
```

### 단계별 흐름

```
[Step 0]  Quick Mode 입력
  사용자: "유튜브 영상 자동 편집 좀 해주세요"
  시간:   5초

[Step 1]  Intent Filter 발동
  시스템: 영상기획 외 의도 감지 → E-SEC-002 발생
  메시지: "영상기획과 거리가 있는 내용 같아요. 다른 방식으로 도와드릴까요?"
  reframe_suggestion: "영상 편집은 본 서비스 범위 밖이지만,
                       영상기획 (어떤 영상을 만들지 결정)은 도와드릴 수 있어요.
                       어떤 영상을 만들고 싶으세요?"
  시간:   2초

[Step 2]  사용자 재입력
  사용자: "아 그럼 이번 주 새 영상 아이디어 좀" 입력
  시간:   10초

[Step 3]  정상 흐름
  시스템: Quick Mode 진행 (Brand/Series 컨텍스트 있음)
  → 시나리오 2와 동일
```

### 분기 — 반복 위반

```
같은 user_id가 1분 안에 5회 Intent Filter 발동:

[Step 1-B]  자동 1시간 차단
  시스템: "잠시 후 다시 시도해주세요" 안내
  운영자 알림: Slack #security (error_response_contract §10)
```

### 성공 기준

```
- Intent Filter 정확도 (영상기획 외 입력 차단율) >= 95%.
- false positive (정상 입력 차단) <= 3% (eval/security_eval.md).
- reframe_suggestion이 사용자 의도와 호환되면 자연스러운 재진입.
- 차단 패턴 자체는 사용자에게 노출 금지 (회피 학습 방지).
```

→ `docs/contracts/error_response_contract.md` §13, `docs/contracts/llm_security_contract.md`

---

## 6. 시나리오 매트릭스

| 시나리오 | 페르소나 | UX 모드 | 예상 시간 | 핵심 검증 |
|---|---|---|---|---|
| 1. 신규 첫 영상 | 1인 마케터 | Discovery 5단계 | 4~5분 | 4계층 데이터 저장 |
| 2. Series 추가 | 1인 마케터 | Quick Mode | 90초~2분 | Brand Memory 상속 |
| 3. 결과 다듬기 | 브랜드 매니저 | Critic revise | 추가 30초 | max_revise=2 강제 |
| 4. Brand 갱신 | 1인 마케터 | 설정 | 2~3분 | Brand Memory 수정 영구 저장 |
| 5. Intent 위반 | 크리에이터 | 분기 차단 | 즉시 | Intent Filter 정확도 |

---

## 7. 실패 시나리오 (간략)

상세는 `docs/contracts/error_response_contract.md` §7 참조.

```
F1. LLM timeout (E-LLM-001)
    → progress stepper [LLM ✗] + retry / wait 액션 제공.

F2. RAG 검색 0건 (E-RAG-003)
    → warning만 표시. "참고 자료 없이 만든 결과예요" 노출.

F3. 일일 사용량 한도 도달 (E-RL-001)
    → "내일 다시 만나요" 안내.

F4. PII 입력 시도 (E-SEC-006)
    → 자동 마스킹 + "개인정보가 포함된 것 같아요" 안내.

F5. 광고 표현 사용자 입력 (E-SEC-003)
    → "다른 표현으로 다시 입력해주세요" 안내.
```

---

## 8. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 5+:  실 사용자 사용 데이터로 시간 수치 갱신 (현재 추정값).
Phase 9+:  Brand Memory 수정 UI 시나리오 (시나리오 4) 상세화 — 설계 확정 시.
Phase 11+: 협업 시나리오 추가 (팀 단위 Brand 공유).
Phase 21+: 다국어 시나리오 추가 (영어/일본어).
```

---

## 9. Open Questions

1. 시나리오 1 (Discovery) 5단계가 너무 길다는 피드백 시 단계 축소 가능성 — 사용자 인터뷰 후 결정.
2. 시나리오 3 (revise) max=2의 적정성 — 데이터 누적 후 조정.
3. 시나리오 4 (Brand Memory 수정)의 UI 위치 — 별도 페이지 vs 모달.
4. 시나리오 5 (Intent Filter) 1시간 차단의 길이 적정성 — 영구 차단 vs 운영자 검토 필요한지.
5. 모바일 시나리오와 데스크탑 시나리오의 차이 — 시간 수치 별도 측정 필요.

---

## 10. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      5 시나리오 (신규 Discovery / Series Quick / Critic revise /
                      Brand 갱신 / Intent 위반) + 5 실패 시나리오.
```
