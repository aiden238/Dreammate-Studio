# ux_eval.md — UX / UI 평가

> 위치: `eval/ux_eval.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `apps/web/design.md` §22 GenerationProgressStepper
> 참조: `docs/contracts/frontend_design_contract.md` §1 설계 원칙
> 참조: `docs/contracts/error_response_contract.md` §7 4단계 stepper 에러 처리
> 참조: `eval/accessibility_checklist.md` (a11y 별도)

---

## 1. 목적

영상기획 AI 에이전트의 UX 품질을 측정한다. 본 문서는 디자인 토큰 검증이 아니라 **실제 사용자의 인지·정서·행동 흐름**에 대한 평가다. 카드 5장 명확성 / 30~60s 진행 노출 / 부분 결과 가시성 / 에러 메시지 톤 / 모바일 적합성을 중심으로 한다.

---

## 2. 평가 차원 (6 개)

### 2.1 progress_visibility — 진행 가시성

```
정의: 30~60초 LLM 생성 동안 사용자가 멍하지 않는가.
측정: GenerationProgressStepper 4단계(Intent/RAG/Plan/Critic) 노출 + 단계별 진행 표시.
0점: 스피너 1개만, 단계 정보 없음
3점: 단계 진행 표시 있으나 정보 부족
5점: 4단계 stepper + 각 단계별 부분 결과 / 예상 시간
참고: design.md §22 정합 + frontend_design_contract §5.
```

### 2.2 partial_result_visibility — 부분 결과 노출

```
정의: 일부 단계가 완료되면 결과를 즉시 보여주는가.
측정:
  - RAG 완료 → 참고 자료 사용 여부 즉시 노출
  - Planning 일부 완료(3개 중 1~2개) → 완료된 plan 즉시 노출
  - Critic 일부 실패 → 성공한 plan만이라도 점수 노출 (error_response §7.4)
0점: 모든 단계 완료까지 흰 화면
3점: Planning 완료 시점부터 노출
5점: 각 단계 완료마다 즉시 부분 결과 (스트리밍)
```

### 2.3 card_clarity — 카드 5장 명확성

```
정의: AI 추천 4 + 직접 입력 1 = 5장 구조가 명확한가.
측정:
  - 카드 4장의 의미 중첩 < 30% (사용자 입장 확인)
  - 카드별 name/description/pros/cautions 모두 보임
  - 직접 입력 카드가 5번째에 명확히 구분
  - 거절 / 재생성 / 직접 입력 버튼 위치
0점: 4장이 비슷해서 선택 못 함
3점: 차이는 있으나 cautions 가시성 부족
5점: 4장 + 1 slot 모두 명확 + 거절/직접입력 버튼 명확
참고: output_schema §13 카드 5장 정책.
```

### 2.4 error_tone — 에러 메시지 톤

```
정의: 에러 메시지가 친근체 + 다음 행동 안내인가.
측정 (error_response_contract §5.1):
  - 한국어 친근체 (~예요, ~해주세요)
  - 50자 이내
  - 광고적 표현 0개
  - 영어 기술 용어 0개
  - 다음 행동 명시 (user_action 매핑)
0점: "오류가 발생했습니다" 또는 영어 메시지
3점: 한국어이나 다음 행동 부족
5점: 친근체 + 다음 행동 + 부분 결과 안내 포함 (예: "일부 결과는 확인하실 수 있어요")
```

### 2.5 mobile_fitness — 모바일 적합성

```
정의: 360px 너비에서 한 손 조작 가능한가.
측정 (frontend_design_contract §1):
  - 카드 1열 노출 (360px) / 2열 노출 (768px+)
  - CTA 버튼 thumb zone (하단 1/3)
  - 입력 폼 가독성 (font-body 15~16px)
  - 스크롤 깊이 (한 화면에서 1~2 스크롤 안에 결정)
0점: 데스크톱 가정 (가로 스크롤 발생)
3점: 작동하나 thumb zone 미고려
5점: 360px 최적 + thumb zone + 큰 터치 타겟 (≥ 44×44px)
```

### 2.6 cognitive_load — 인지 부하

```
정의: 사용자가 한 화면에서 의사결정 항목이 적절한가.
측정:
  - 한 화면 의사결정 ≤ 3개 (1순위 CTA, 2순위 CTA, 직접 입력)
  - placeholder 텍스트 명확
  - help text 노출 위치 적절 (호버 vs 인라인)
0점: 5개 이상 선택지 한 화면
3점: 3~4개
5점: 1~2개 핵심 + 부가 옵션 접힌 상태
```

---

## 3. 입력 / 출력 형식

### 3.1 입력 (UX 평가 단위)

```yaml
ux_target:
  - "page"                       # page_map.md의 10 페이지 중 하나
  - "component"                  # component_map.md의 컴포넌트
  - "flow"                       # Discovery 전체 / Quick 전체 / 에러 회복
page_or_component: "string"
viewport:
  - { width: 360, label: "mobile" }
  - { width: 768, label: "tablet" }
  - { width: 1280, label: "desktop" }
user_persona: "first_time | returning | power"
context: "first_session | revision_loop | error_recovery"
```

### 3.2 출력

```yaml
scores:
  progress_visibility: 0~5
  partial_result_visibility: 0~5
  card_clarity: 0~5
  error_tone: 0~5
  mobile_fitness: 0~5
  cognitive_load: 0~5
ux_avg: 0~5
issues:
  - { dim: "mobile_fitness", severity: "high", desc: "..." }
suggestions:
  - "..."
reasoned_by: "operator | usability_test | a11y_audit | heuristic_eval"
```

---

## 4. 자동 평가 vs 수동 평가

| 차원 | 자동 (axe/Lighthouse) | 수동 (운영자/QA) |
|---|---|---|
| progress_visibility | Lighthouse (FCP/LCP) + 디자인 토큰 검사 | 운영자 1차 |
| partial_result_visibility | 코드 검사 (SSE/Streaming) | 운영자 보조 |
| card_clarity | 사용성 테스트 (5명) | 운영자 주도 |
| error_tone | 룰 (한국어 + 50자 + 영어 단어 검사) | 운영자 보조 |
| mobile_fitness | Lighthouse + Playwright viewport | 운영자 보조 |
| cognitive_load | 사용성 테스트 | 운영자 주도 |

---

## 5. 임계값

```
ux_avg ≥ 4.0      passing
3.0~3.9           warning (개선 권고)
< 3.0             failing (디자인 재검토)

특수 게이트:
- error_tone < 3: 즉시 카피 수정 (영어 메시지 / 광고 표현 노출 차단)
- mobile_fitness < 3: 모바일 사용자 차단 (대안: 데스크톱 권장 배너)
- partial_result_visibility = 0: 사용자 이탈 위험 큼 → P0 개선
```

---

## 6. 관련 contract / Skill 연결

```
contract:
  - frontend_design_contract.md §1, §5 (a11y), §10 (4단계 stepper)
  - error_response_contract.md §5 (user_message), §6 (user_action), §7 (stepper 에러)
  - api_contract.md §13 (SSE progress stepper)

Skill:
  - design-review (디자인 리뷰 시 본 문서 체크)
  - eval-design (차원 갱신)
  - meta-retrospective (사용자 피드백 누적 회고)

연관 골든 셋: GS-005 (revise 흐름 UX), GS-006 (forced_approve 안내), GS-007 (RAG 사용 표시).
```

---

## 7. Open Questions

1. 사용성 테스트 인원 — 5명 nielsen heuristic vs 더 큰 표본.
2. card_clarity 4장 의미 중첩 30%의 사용자 인식 측정 — 정량(클릭 분포) vs 정성(인터뷰).
3. partial_result_visibility의 SSE vs polling 선택 — tech_stack에서 SSE 채택, 모바일 안정성 검증.
4. error_tone 룰 자동화에서 영어 단어 false positive — 고유명사 예외 사전 필요.
5. cognitive_load의 한 화면 의사결정 수 — 3개 baseline의 사용자 데이터 검증.
6. dark mode 도입 시점 (Phase 2+) — 운영자 부담 vs 사용자 요구.
