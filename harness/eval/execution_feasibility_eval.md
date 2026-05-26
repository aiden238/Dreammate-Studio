# execution_feasibility_eval.md — 제작 실행 가능성 평가

> 위치: `eval/execution_feasibility_eval.md`
> 상태: Phase 0–1 진입용 베이스라인
> 참조: `eval/video_planning_eval.md` §2.6 feasibility
> 참조: `docs/contracts/output_schema.md` §17 final_outputs.shooting_notes
> 참조: `apps/web/design.md` §22 GenerationProgressStepper

---

## 1. 목적

기획안이 아무리 좋아도 1인 제작자가 만들 수 없으면 무용지물이다. 본 문서는 plan을 "실제로 만들 수 있는가"의 관점으로 5 차원 평가한다. Mass 사용자(대학생 / 스타트업 / 1인 크리에이터)가 1~2일 안에 촬영·편집 완료할 수 있는 수준을 기준으로 한다. P-007의 `feasibility` 차원이 본 문서를 참고로 채점된다.

---

## 2. 평가 차원 (5 개)

### 2.1 budget_fit — 예산 적합

```
정의: 1인 제작자의 일반 예산(0~30만원) 안에서 가능한가.
측정: 유료 출연자 / 장소 대관 / 장비 렌탈 / 외주 편집 등 비용 항목 개수.
0점: 50만원 이상 필수 (광고/스튜디오)
3점: 10~30만원
5점: 0~10만원 (스마트폰 + 자연광 + 본인 출연)
```

### 2.2 shooting_complexity — 촬영 난이도

```
정의: 촬영 장면 수 / 카메라 이동 / 특수 효과 요구.
측정: shooting_notes의 camera + location + acting 합산 난이도.
0점: 다중 카메라 + 드론 + 야간 + 다중 장소
3점: 1 카메라 + 2~3 장소 + 일반 자연광
5점: 1 카메라 + 1 장소 + 핸드헬드 또는 삼각대
```

### 2.3 edit_time — 편집 시간

```
정의: 일반적인 편집 도구(CapCut, Premiere)로 몇 시간 안에 완성 가능한가.
측정: cut 수 / 자막 양 / 효과음 / 색 보정 요구.
0점: 8시간 이상 (전문 편집 수준)
3점: 3~6시간 (저녁 시간 1회)
5점: 1~2시간 (저녁 시간 절반)
포맷별 baseline:
  shorts_30s   ≤ 2시간
  shorts_60s   ≤ 3시간
  reels_60s    ≤ 3시간
  youtube_3m   ≤ 5시간
  youtube_8m   ≤ 8시간
초과 시 점수 감점.
```

### 2.4 cast_requirement — 출연자 요구사항

```
정의: 출연자가 몇 명 필요하고 섭외 난이도가 어떤가.
측정: 출연자 수 + 일정 조율 필요 + 외부 전문가 섭외 필요.
0점: 3명 이상 + 외부 전문가 (셀럽/전문가)
3점: 2명 (본인 + 친구 1명)
5점: 1명 (본인 단독) 또는 보이스오버 가능
```

### 2.5 risk_level — 제작 리스크

```
정의: 촬영 중 사고 / 법적 이슈 / 권리 침해 가능성.
측정:
  - 야외 위험 장소 (도로/높은 곳 등) 여부
  - 음악 / 영상 / 사진 저작권 (BGM 무단 사용 등)
  - 초상권 (행인 등장 후 모자이크 필요 여부)
  - 광고적 표현으로 인한 소비자 보호법 이슈
0점: 다중 위험
3점: 1~2개 관리 필요
5점: 위험 없음 (본인 자료/공유 가능 BGM)
```

---

## 3. 입력 / 출력 형식

### 3.1 입력

```yaml
plan: { P-006 plan 1개 }
shooting_notes: [
  { type: "camera | location | prop | acting | editing", note: "string" }
]
format: shorts_30s | ... | other
length_sec: 30
context:
  user_profile: "student | freelance | smb_owner | ..."   # Phase 2+
  budget_cap_krw: 100000                                  # Phase 2+
```

### 3.2 출력

```yaml
scores:
  budget_fit: 0~5
  shooting_complexity: 0~5
  edit_time: 0~5
  cast_requirement: 0~5
  risk_level: 0~5
feasibility_avg: 0~5
estimated_total_hours: 0~12
warnings:
  - "music_copyright_risk"
  - "outdoor_safety_check"
reasons: { 차원별 1줄 }
```

---

## 4. 자동 평가 vs 수동 평가

| 차원 | 자동 | 수동 |
|---|---|---|
| budget_fit | LLM | 운영자 1차 |
| shooting_complexity | LLM | 운영자 보조 |
| edit_time | LLM + 룰 (포맷 baseline) | 운영자 보조 |
| cast_requirement | LLM | 운영자 보조 |
| risk_level | LLM + 룰 (저작권 키워드) | 운영자 주도 |

risk_level은 운영자 검토 비중이 큼 (법적 이슈 사전 차단).

---

## 5. 임계값

```
feasibility_avg ≥ 4.0   passing
3.0~3.9                 warning (suggestions 필수)
< 3.0                   failing (revise 후보)

특수 게이트:
- risk_level = 0: 자동 reject (Critic verdict=reject 권고)
- music_copyright_risk warning: 사용자 확인 필수 (UI 노출)
- budget_fit = 0: revise 권고 + 운영자 검토 큐
- estimated_total_hours > 12: revise 권고 (1인 제작자 1일 한계)
```

---

## 6. 관련 contract / Skill 연결

```
contract:
  - output_schema.md §17 (final_outputs.shooting_notes)
  - output_schema.md §8 (plans[*].flow.duration_sec)

Skill:
  - eval-design (차원 갱신)
  - design-review (사용자 노출 UI에 risk warning 명시)
  - meta-retrospective (실패 케이스: 사용자 "못 만들겠다" 피드백 누적)

연관 골든 셋: GS-005, GS-008 (포맷별 edit_time baseline).
```

---

## 7. Open Questions

1. user_profile 도입 시 (학생/프리랜서/소상공인) 가중치 분기 — Phase 2+.
2. budget_cap_krw 사용자 입력 — 첫 세션에서 묻는 것 vs 차차 학습.
3. risk_level의 LLM 채점 신뢰성 — 법적 이슈는 운영자 100% 검토 권장.
4. edit_time baseline의 사용자 숙련도 차이 — 초보 vs 중급 vs 고급 분기 필요한지.
5. AI 생성 BGM/이미지 사용 시 저작권 규정 — Phase 2+ 별도 contract.
