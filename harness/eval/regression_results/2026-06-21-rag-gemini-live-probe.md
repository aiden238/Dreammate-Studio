# RAG Gemini 채택 — 라이브 프로브 (2026-06-21, project-2 잔여 2c-measure 1차)

> 재현: `python scripts/rag_gemini_probe.py` (rootdir harness/, .env = backend/fastapi/.env).
> project-2(2026-06-09~10) Temp/(gitignored) 측정의 **커밋 재작성**(유실 방지). 실 Gemini + Supabase 호출.

## 설정
- `RAG_EMBEDDING_PROVIDER=gemini` (default openai → 측정 시 override), `gemini-embedding-2 @1536`.
- threshold = production **0.7** (및 비교용 0.4). 쿼리=`RETRIEVAL_QUERY` / 문서측=`RETRIEVAL_DOCUMENT`(2c-code 배선).

## 코퍼스 (approved_knowledge)
- **8 rows** (project-2 external_seed, Gemini 임베딩으로 적재됨 — 영속 확인).
- 컬럼: `auth_user_id, brand_id, content, embedding, id, metadata, promoted_at, source_candidate_id`.
  ★ `status`/`is_active` 컬럼 없음 — 이 테이블 자체가 **검색 대상(promoted store)**. RPC `match_approved_knowledge`가 직접 검색.

## 측정 — retrieval.search() (시드 8건 주제 매칭 ko 쿼리 3개)

| 쿼리 | @0.7 hits | top similarity (tag) | @0.4 hits |
|---|---|---|---|
| 무음후크/브이로그 | **5** | 0.889(hook) · 0.749(structure) · 0.733(hook) | 5 |
| 챌린지/CTA | **2** | 0.822(cta) · 0.749(structure) | 5 |
| 리뷰/언박싱 | **2** | 0.760(tone) · 0.721(hook) | 5 |

## 판정
- ✅ **RAG가 production 0.7 threshold에서 라이브 작동.** Gemini 임베딩이 ko 숏폼 쿼리를 정확 랭킹(top 0.72~0.89), **태그가 쿼리 의도와 일치**(무음후크→hook, 챌린지→cta, 리뷰→tone). project-2 3/2/1 재현·검증(잘 매칭된 쿼리로 5/2/2).
- ✅ **임베딩=Gemini / 생성=GPT 분리 채택의 검색측이 실증됨.** OpenAI text-embedding-3-small였다면 같은 코퍼스가 0.7에서 0/3(platform_evolution.md §3.1) — Gemini가 단일 최대 레버임을 라이브로 재확인.

## 정직한 한계 (다음 = "큐레이션·2nd brain")
- **검색 메커니즘만 입증, RAG의 생성 품질 기여는 미측정.** "RAG ON이 plan 품질을 올리나"는 별도 = `golden_set` RAG ON/OFF + cross-provider Claude judge(옵션1 계측기) 측정 대상.
- **코퍼스 빈약(8건, 합성)** — project-2 적대검증 기준 진짜 차별화 ~35–45%. 검색은 되나 **가치는 코퍼스가 다음 블로커**. → 큐레이션(고가치 패턴 수작업 시드) + 2nd-brain(피드백 누적)으로 확대 후 재측정.
- threshold 0.4로 내리면 전 쿼리 5 hits이나 저유사도 노이즈 유입 — 0.7 유지가 정답(Gemini라 0.7에서 충분).
