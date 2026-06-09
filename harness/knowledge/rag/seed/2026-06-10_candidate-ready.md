# RAG 콜드스타트 — candidate-ready 세트 (rag-update Step 1~2 준비)

> 위치: `knowledge/rag/seed/2026-06-10_candidate-ready.md`
> 출처: `2026-06-10_coldstart-seed-draft.md`(40 draft) → 적대검증 고신호 + 필수수정 3건 반영 → **8건 선별**
> source_kind: **external_seed** → rag-update Step 4 승인은 **사용자 명시 필수**(자동승격 금지). 본 파일은 Step 1~2 준비까지.
> ★ 태그는 metadata일 뿐(검색키 아님 — approved_knowledge는 시맨틱 임베딩 cosine 0.7 검색). 전제오류 정정 반영.

---

## 필수 수정 반영 (적대검증 3건)
- ✅ 차단단어 직접인용 제거(재테크): `quality_filter §3.1` 사전매칭 회피 — 단정 수익/원금 표현을 *기술*하되 차단어 미포함.
- ✅ 법적 단정 약화: "자본시장법 위반" → "플랫폼 금융광고 정책 위반 소지".
- ✅ 미검증 정량수치에 `unverified_quant` 플래그(평가자가 specificity를 근거로 오인 방지).

## candidate 세트 (status=pending, brand_id=null=global, language=ko-KR)

| # | tag | platform / type | content (정제) | flag |
|---|---|---|---|---|
| 1 | hook | instagram / vlog_daily | Reels 브이로그는 무음 자동재생 전제로 후크를 설계한다. 말하는 톡헤드보다 무음 B롤 위 자막 한 줄이 안정적. 첫 1초 좌상단(프로필·시간 UI에 안 가리는 안전영역)에 맥락 자막("평일 아침 7시, 1인가구 루틴")을 박는다. | — |
| 2 | structure | instagram / vlog_daily | 일상 브이로그는 시간순 오프닝(현관문·기상)이 이탈 안티패턴이다. 후반의 가장 그림 좋은 장면(완성된 저녁상·정리된 방·노을)을 콜드오픈으로 앞에 붙이고 "이게 되기까지 N시간" 자막을 깐다. | — |
| 3 | hook | instagram / vlog_daily | 브이로그 기획서에는 '부러워할 한 가지(열망)'와 '안심할 한 가지(현실)'를 페어로 넣는다. 너무 완벽하면 거리감, 너무 구질하면 비호감 — 감성 컷 + "근데 설거지는 이만큼" 식 현실 페어링이 공감과 저장을 동시에 만든다. | — |
| 4 | structure | tiktok / challenge | 챌린지는 핵심 동작 1사이클을 짧게(약 7초 내외) 한 번 통으로 보여준다. 따라하려는 사람이 동작을 통째로 기억하는 인지 한계. 긴 영상도 핵심 사이클 1회 통컷 후 변주를 붙인다. | `unverified_quant` |
| 5 | cta | tiktok / challenge | 챌린지 CTA(지정 해시태그·따라찍기 동선·인증 방식)는 엔딩이 아니라 핵심 동작 직후(영상 중반)에 노출한다. 끝까지 보는 비율이 낮은 매체라 엔딩 CTA는 도달하지 못한다. | `unverified_quant` |
| 6 | hook | youtube_shorts / review_unboxing | 언박싱은 제품 전체샷/미개봉 정물로 시작하지 않는다(피드에서 광고로 오인돼 스킵). 첫 1~2초에 '이미 뜯는 손동작'을 보여주고 가격·판매량 같은 순수 수치 자막을 곁들인다(과장 형용사 제외). | — |
| 7 | tone | youtube_shorts / review_unboxing | 리뷰 숏폼은 아쉬운 점 1개를 반드시 포함한다(치명적 결함 아닌 수준 — 예: 색상 옵션 적음). 단점 0개는 협찬 의심을 부르고, 가벼운 단점은 진정성 신호로 체류·댓글을 만든다. | — |
| 8 | tone | tiktok / finance_info | 재테크/금융 콘텐츠는 단정적 수익·원금 관련 표현을 피하고 정보 제공 톤을 유지한다(권유성 단정은 플랫폼 금융광고 정책 위반 소지). 사실 설명은 명확히, 결과 약속은 배제. | `policy_sensitive` |

## Step 2 자동필터 자가점검 (rag-update §Step 2)
- PII: 없음(일반 패턴 지식). ✅
- off_topic: 전부 영상기획 관련. ✅
- length: 각 50~5000자 범위. ✅
- **ad_language**: 정책 사전의 과장·약속류 차단어 **미포함**(grep 검증 — 단, 본 메타 문서가 차단어를 *나열*하면 naive 사전매칭이 트립되므로 content 행만 검사 대상). ✅
- injection: 없음. ✅
- language: ko-KR. ✅

## 결단 (A9 — 사용자)
external_seed라 Step 4 승인이 사용자 몫. 선택지:
1. **소량 투입 + 측정**: 위 8건을 candidate→evaluated→(승인)→promoted → `eval/golden_set` 회귀로 RAG ON/OFF 품질 비교(Step 5). 5% 하락 시 비활성화. → RAG 가치 실측.
2. **보류(use_rag off)**: 8건으론 빈약 판단 시 RAG 보류, brand_memory(개인화)에 집중. 시드는 staging 보존.

> 권장: **1) 소량 투입 + 측정** — 이제 측정 접지선(A8)이 있으니 "RAG가 실제로 품질을 올리나"를 처음으로 *측정*할 수 있다. 빈약하면 그때 보류해도 늦지 않다.
