# 품질 검증 — human review 기반 (second-opinion + 사용자 채점 시트)

> 2026-06-05 | 실 LLM 출력(compact/rich/director) 직접 읽고 평가 | critic 낙관 편향(전수 approve) 우회 목적
> 케이스: "동네 카페 신메뉴 '흑임자 라떼' 30초 쇼츠 기획" (실 gpt-4o-mini, OUTPUT_MODE 토글)
> 방법: ① 실 출력 생성 ② **회의적 second-opinion** 평가("1인 마케터가 실제로 쓸까?") ③ 사용자 실채점 시트

## 1. 3-tier 실 출력 비교 (구조 지표)
| tier | 총 길이 | flow 비트 | rich 슬롯 | director 슬롯 |
|---|---|---|---|---|
| compact | **509자** | 3 | 0 | 0 |
| rich | **1433자** | 4 | **7** | 0 |
| director | **1972자** | 4 | 7 | **3** |

→ ★ **깊이 격차 실재 + 단조 증가**(Phase 12 "compact 0.231 / rich 1.000" 주장 실 출력에서 검증). compact→rich→director로 구조가 실제로 깊어짐.

## 2. ★ 회의적 second-opinion 평가 (낙관 critic 보정)

### compact — "방향만, 더 일해야"
- name/concept/hook/3비트/pros/risks. 골격은 맞으나 **그대로는 촬영 불가** — 샷·대사·자막 없음. "흑임자 라떼, 당신의 새로운 친구" 류 진부한 후크 후보.
- **would_use 추정: 2/5** (방향 참고용, 실작업 대부분 남음). Phase 12 결론(0.231) 정합.

### rich — "거의 촬영 가능, 일부 진부함 다듬기 필요"
- 비트별 **visual/dialogue/caption** + shots/thumbnail/title/cta/길이변형 → **실제 촬영에 착수 가능한 수준**(진짜 깊이 증가).
- ⚠️ 단 **슬롯 채움 ≠ 일관된 콘텐츠 품질**: title "이 카페의 비밀", references "인스타그램 쇼츠"(실 사례 아닌 카테고리), cta "지금 바로 방문해보세요!"(클리셰) 등 **제너릭 filler 혼재**.
- **would_use 추정: 3.5/5** (구조는 바로 쓸 수 있으나 일부 문구 사람 손질 필요).

### director — "기획 의도까지, 브리프로 충분 / 대본은 아님"
- + hook_system(재후크 @0:20), retention_architecture(이탈 방지 논리), scene_breakdown(씬별 intent/emotion/retention_device/why_this_works) → **기획자가 하는 사고(리텐션·씬 의도)를 담음**.
- ⚠️ why_this_works가 다소 일반론("시각적 요소와 함께 기대감 증대"). 사용자 Phase 15 피드백("director=초안 수준, 대본 쓰기엔 부족") **정확** — 좋은 **브리프**이지 완성 대본 아님(product_boundary 정합).
- **would_use 추정: 4/5**(브리프 목적엔 충분, 깊은 대본기획은 별도).

## 3. ★ 핵심 검증 결론 (정직)
1. **깊이 격차는 실재**(구조): tier가 올라갈수록 실제로 더 깊고 촬영-착수 가능. 빌드(Phase 13/15/20)의 전제 **검증됨**.
2. **그러나 "구조 깊이 ≠ 콘텐츠 품질"**: 슬롯을 채우면 **usability(촬영 가능성)**는 오르나, 진부한 filler(클리셰 CTA, 카테고리성 references, 일반론 why)도 생김. → critic "approve 4.41"은 **콘텐츠 품질을 과대평가**(Phase 23 낙관 편향 재확인).
3. **제품적 진실**: rich/director는 **확실히 더 쓸만한 기획 브리프**(토큰값을 함. compact 대비 would_use ↑). 단 일부 문구는 사람 손질 필요 + "대본 아닌 브리프"(사용자 피드백·product_boundary 정합).

## 4. 권고 (검증 기반)
- **rich default-ON 검토 근거 확보**(Phase 13 이월 결정): would_use 가 compact(2) ≪ rich(3.5)/director(4) → 사용자 경험상 rich+ 가 명백히 우월. **flag default 전환은 cost(3~5배)·filler 손질 인지 하에 진행 가치 있음** → backlog B-1/L-5 연계.
- **filler 개선**(backlog M-5 연계): references=실 사례 강제, CTA 클리셰 회피, why_this_works 맥락 특화 — 프롬프트 보강 후속.
- ★ **자동 critic 점수를 절대 품질로 신뢰 말 것** — 회귀 기준선으로만(Phase 23 정합).

## 5. 사용자 실채점 시트 (★ 최종 human 점수 = 사용자)
> 위 3-tier 실 출력을 보고 0~5(깊이 0~1)로 채점 → second-opinion(§2)과 대조.
```yaml
# compact:  would_use:_  content_quality:_  generic정도(낮을수록좋음):_  depth:_(0~1)
# rich:     would_use:_  content_quality:_  generic정도:_  depth:_
# director: would_use:_  content_quality:_  generic정도:_  depth:_
# Q: rich/director가 compact보다 실제로 쓸만한가? (예/아니오 + 한줄)
# Q: rich를 default ON 할 가치가 있는가? (예/아니오 + 이유)
```

## 6. 상태
- ✅ 실 출력 생성 + second-opinion 품질 검증(낙관 critic 우회) 완료.
- ⬜ 사용자 실채점 — 위 시트(deferred, 사용자 액션). 회수 시 §2 대조로 critic 신뢰도 캘리브레이션.
