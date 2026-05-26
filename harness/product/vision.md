# vision.md — 제품 비전

> 위치: `product/vision.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `PROJECT_STATE.md` (25 확정 결정), `product/positioning.md`, `product/mvp_scope.md`
> 참조: `docs/contracts/product_boundary.md`, `docs/contracts/mvp_non_goals.md`

---

## 0. 한 줄 비전

> **누구나 영상기획을 잘 할 수 있게.**

영상 제작 도구는 이미 충분히 많다. 모자란 것은 "무엇을, 누구를 위해, 어떻게 말할지"를 결정하는 **기획의 품질**이다.

---

## 1. 3–5년 비전 (2030년 목표)

```
2026 (지금): 영상기획 AI 에이전트 MVP 출시. 1인 마케터·소규모 브랜드·콘텐츠 크리에이터 1만 명 사용.
2027–2028 : Brand Memory + 학습형 RAG 누적. 사용자별 맞춤 기획 품질이 사람 수준에 근접.
2029–2030 : 영상기획 분야 한국어 1위 AI 도구. 글로벌 진출 (영어/일본어). Custom RAG.
```

장기적으로 우리는 다음 두 가지를 동시에 추구한다.

```
1. "기획을 잘 하는 사람"의 사고 과정을 학습형 RAG로 누적해 누구나 접근 가능하게 만든다.
2. 영상기획이 영상 제작 비용보다 더 큰 가치를 만든다는 인식을 시장에 확립한다.
```

---

## 2. 우리가 푸는 문제

영상기획은 진입 장벽이 높다.

```
- 시간 비용: 한 영상 기획에 평균 2~4시간 (사람마다 편차 크다).
- 인지 부하: 목적/타겟/메시지/후킹/구성/CTA를 동시에 결정해야 한다.
- 학습 곡선: 좋은 기획 패턴을 익히려면 수백 편의 영상을 분석해야 한다.
- 일관성: Brand별 톤·정체성을 유지하기 어렵다 (특히 1인 운영자).
- 검증 부재: 기획 직후 품질을 객관적으로 평가할 방법이 없다.
```

기존 도구의 한계.

```
- ChatGPT/Claude: 범용 LLM이라 영상 도메인 지식이 얕다. 광고적 표현 자주 생성.
- 영상 편집 AI (CapCut, Runway 등): 제작 자동화에 집중. 기획 단계 없음.
- 전통 기획 컨설팅: 비싸다 (편당 50만원~), 느리다 (1~2주).
```

---

## 3. 우리의 접근

```
영상기획 AI 에이전트 (영상 제작 아님)
  → 사용자가 영상을 "만들기 전"에 필요한 모든 기획 판단을 도와준다.
  → 결과물은 영상이 아니라 "기획안"이다.
```

핵심 흐름.

```
사용자 입력 → Intent 분석 (Discovery 또는 Quick 자동 분기)
            → 부족 정보 질문 → 한 줄 방향 승인
            → LLM Wiki/RAG 검색 → 기획안 3개 생성
            → Critic Agent 평가 (revise 최대 2회)
            → 사용자 선택 + 피드백 저장 (Brand Memory 자동 추출)
```

→ `CLAUDE.md` §"핵심 흐름"과 정합

---

## 4. 차별점 (4개)

### 4.1 Hybrid UX (Discovery + Quick)

```
- 신규/콜드스타트: Discovery Wizard 5단계 카드 (4추천 + 1직접입력)
- 기존 Series 재사용: Quick Mode (짧은 프롬프트 + 1~2 질문)
- 자동 분기: Brand/Domain/Series 컨텍스트 유무로 판단
```

→ ChatGPT 단일 입력창 vs 우리 Discovery 구조. 신규 사용자 진입 장벽이 절반 이하.

### 4.2 4계층 데이터 모델

```
User → Brand → Domain → Series → Video Project
```

```
- Brand: 정체성 (톤, 가치, 톤매너)
- Domain: 산업/카테고리 (뷰티, 푸드, 교육 등)
- Series: 콘텐츠 묶음 (예: "주 1회 신상품 소개")
- Video Project: 개별 영상기획안
```

→ 단발성 LLM 대화에서는 불가능한 일관성. Brand Memory 자동 추출과 결합.

### 4.3 MOA Lite (Mixture of Agents, 가벼운 버전)

```
Intent → Planning → Critic[revise max 2] → Rewriter
```

```
- 단일 LLM 호출이 아닌 4개 agent의 분업.
- Critic이 기획안을 평가하고 최대 2회 재작성 요청 (무한 루프 차단).
- Full MOA의 비용 폭증 없이 품질 확보.
```

→ `ai_system/architecture.md`, `ai_system/orchestration/moa_policy.md` 참조

### 4.4 RAG Lite + 학습형 5단계 승격

```
pending → filtered → evaluated → approved → promoted
```

```
- 사용자 피드백, 외부 시드 데이터, LLM Wiki 항목이 모두 5단계 검증 후 RAG에 진입.
- 광고 표현·PII·중복은 자동 필터.
- "사용자가 쓸수록 시스템이 똑똑해진다."
```

→ `knowledge/rag/promotion_rule.md`, `docs/contracts/rag_data_contract.md` 참조

---

## 5. 측정 지표 (3–5개)

```
1. 영상기획 성공률 (Critic 점수 >= 0.75 비율)
   - 목표: MVP 6개월 시점 80%, 12개월 시점 90%.

2. 반복 사용률 (DAU/MAU)
   - 목표: MVP 12개월 시점 0.25 이상.

3. 영상기획 1건당 평균 소요 시간 (사용자 체감)
   - 목표: Discovery 5분 / Quick 90초 이내.

4. Brand Memory 활용률 (Quick Mode에서 Brand 컨텍스트 참조 비율)
   - 목표: MVP 12개월 시점 70% 이상.

5. 사용자 NPS (Net Promoter Score)
   - 목표: MVP 12개월 시점 +30 이상.
```

→ `eval/regression_eval.md`, `eval/golden_set.md`와 연동되어 객관 측정

---

## 6. 비전과의 정합 체크

다음 결정은 본 비전에서 직접 도출된다 (PROJECT_STATE.md 25 결정 중).

```
[1] Discovery + Quick Hybrid → §4.1 차별점
[6] 4계층 데이터 모델       → §4.2 차별점
[8] Brand Memory 자동 추출   → §4.2 + §5 측정 지표 4
[5] Critic revise 최대 2회   → §4.3 차별점
[18] candidate_knowledge 5단계 → §4.4 차별점
```

---

## 7. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 11+: 비전 갱신 (사용자 실 데이터 기반 측정 지표 조정)
Phase 21+: 영어/일본어 확장 시 글로벌 비전 추가
연 1회   : 본 문서 정합성 재검토 (meta-retrospective Skill 연동)
```

---

## 8. Open Questions

1. "기획을 잘 하는 사람"의 사고 과정을 어떻게 객관적 패턴으로 누적할지 — knowledge/llm_wiki/ 확장 전략 필요.
2. 측정 지표 5번 NPS는 정량 수집이 어렵다 — 대체 지표 검토.
3. 글로벌 진출 시점 (Phase 21+ 후보) 트리거 기준 — 한국 사용자 5만 도달 vs 시간 기반.
4. "영상기획 분야 1위" 정의 — 사용자 수 / 매출 / 인지도 중 어느 기준.
5. Custom RAG로의 전환 트리거 — pgvector 한계가 도달했을 때 vs 비용 기준 도달.

---

## 9. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      한 줄 비전, 3-5년 목표, 문제 정의, 접근법, 4 차별점,
                      5 측정 지표, 25 결정과의 정합.
```
