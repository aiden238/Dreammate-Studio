# Phase 31 S2·S3 — director v1.2.1 회귀 + RAG ON/OFF 품질 (bounded 라이브 측정)

> 재현: `scripts/phase31_director_ab.py`(S2) · `scripts/phase31_rag_onoff.py`(S3). 실 OpenAI 생성 + cross-provider Claude judge(claude-sonnet, 10차원). project-2 교훈 따라 커밋 재현 스크립트.

## S2 — P-006 director v1.2.0 vs v1.2.1 (특이성+정직가드 회귀)

생성 gpt-4o-mini, 채점 Claude. overall = director 10차원 평균(/5).

| 케이스 | v1.2.0 | v1.2.1 | Δ |
|---|---|---|---|
| shallow(맛집) | 2.6 | 2.8 | **+0.2** |
| normal(창업동아리) | 2.8 | 2.9¹ | ≈+0.1 |

¹ 동일-seed 아님(절단 flakiness로 run 교차 집계). 정직라벨 휴리스틱=0(두 케이스 모두 invented 고유명 없음 → 가드는 latent, 단정 시에만 발동).

- **판정**: **비퇴행 + 소폭 표면 개선**. 메인 B0/B1(+0.33)·CODEX(+0.12) 독립 3종과 방향 정합(특이성=표면 레버). approve 상향은 없음(상한 미돌파, 예상대로 — 개념층 차별화는 프롬프트로 안 됨). → **v1.2.1 활성 OK**(realuse director).

## S3 — golden_set RAG ON/OFF 품질 (RAG grounding 기여)

검색 = RAG_EMBEDDING_PROVIDER=gemini, retrieval.search @0.7(approved_knowledge 8건, 6ba1aaf 라이브분). ON=검색 청크를 생성 프롬프트에 주입, OFF=미주입(동일 입력).

| 쿼리 | 청크 | OFF | ON | Δ |
|---|---|---|---|---|
| 리뷰(언박싱) | 2 | 2.6 | 3.5 | **+0.9** |
| 브이로그 | 3 | (절단)² | 2.6 | — |

² OFF 생성이 JSON 절단으로 채점 불가.

- **판정**: **RAG grounding이 품질을 측정 가능하게 올림(+0.9, 리뷰)** — 관련 청크가 retrieval될 때. 프롬프트 특이성(S2 +0.2)보다 **큰 레버**. → "진짜 차별화 = RAG/PKM grounding 필요"(B0/B1 결론)를 **생성측에서 첫 실증**. use_rag ON(Gemini 코퍼스) 유지 근거 확보.

## 한계 (정직)

- **JSON robustness flakiness**: gpt-4o-mini가 큰 한국어 director 스키마(rich 12 + director 3슬롯)에서 간헐적 malformed/절단 JSON 생성 — max_tokens=8000에도 ~1k 토큰에서 unterminated. **연구가 사전 경고한 confound**(2026-06-21-improved-output-ab.md §6 "5/10 절단"). 전체 생성의 ~절반 실패 → 클린 데이터 포인트 부족.
- **bounded N**(케이스 2 + 2), judge 단일·temp 0.1 단일 실행(분산 미추정). **방향성 측정이지 정식 통계 아님.** 정식화 시 = JSON 파서 robustness(펜스/절단 복구) + N↑ + 다중 human 재평가.
- S2 honesty 가드 효과(추정/예시: 라벨)는 본 케이스들에서 미발동(invented 고유명 부재) → 가드 작동은 별도 케이스 필요.

## 결론

- **S2 v1.2.1 = 비퇴행 확인 → 활성 유지.** (acceptance A4/A5 directional 충족, JSON robustness는 후속.)
- **S3 = RAG ON이 품질 기여(+0.9) → use_rag ON 유지 + 코퍼스 확대(큐레이션·2nd-brain)가 다음 최대 레버.** (acceptance A6 충족 — 개선 판정.)
- 후속: gpt-4o-mini JSON robustness(파서 보강) → 클린 N↑ 재측정.
