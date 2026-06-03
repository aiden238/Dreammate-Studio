# Phase 18 회고 — 브랜딩 세션 (Akinator 주제발굴)

> 2026-06-04 | 제품 phase (런타임 有, gated/additive) | Phase 17 PKM 루프 위에 "발굴" 진입 추가

## 1. 무엇을 했나

주제 모르는 사용자를 **LLM 동적 스무고개**로 좁혀 **후보 주제 3개 × 브랜딩 방향**을 제안하고, 택1 → planning + brand_memory(PKM) 시드로 연결. Quick/Discovery에 더한 **3번째 진입**.

- **S1**: `topic_discovery` agent(P-AUX-3) — ask(다음 질문+카드 2~4, MAX_QUESTIONS=8 cap) / finalize(후보 3×{topic,tone,target,format,why_fit}).
- **S2**: branding endpoint(`/branding/next`·`/finalize`) + Q&A 상태(`_plan_store.wizard_data.branding`).
- **S3**: frontend `/new/branding`(질문 카드+자유입력+진행바 → 후보 3 → 택1) + `/new` 진입 카드. StrictMode 가드(startedRef).
- **S4**: `/branding/select` — 택1 방향 → brand_memory 시드(gated/authed/graceful, conf 0.9) + initial_input 연결.

## 2. 핵심 성과 / 검증

- ★ **라이브 e2e(브라우저 드라이브, B)**: `/new/branding` → 8 적응형 질문(정보→전통문화→음식→한국→김치→조리법) → 후보 3개 × 브랜딩 방향 → 택1 → 생성 성공(plan_id, 3안, approve). S1+S2+S3 통합 실동작 확인.
- ★ **발굴→축적→주입 루프 닫힘**: 택1 방향이 brand_memory 시드(S4) → Phase 17 brand_memory 주입이 이후 생성에 반영.
- behavior-preserving: 신규 진입/agent/endpoint/page **additive**, 기존 Quick/Discovery/planning byte-identical. pytest **608→641** + scenario_sim 36/36 + audit 0.

## 3. 학습 / 패턴

- **P-STRICTMODE-ONESHOT-001 재적용**: 새 페이지 mount 부트스트랩에 startedRef 가드(cancelled 플래그 미사용) — Phase 14 학습 그대로.
- **stale 백엔드 함정**: 가 단계에서 기동한 백엔드가 S1/S2 코드 전이라 branding endpoint 404 → 재기동으로 해소(라이브 검증 시 코드-서버 버전 일치 필요).
- **adaptive Akinator 품질**: LLM 동적이 실제로 좁혀짐(정보→...→김치 조리법). cap 8 + finalize 종료 정상.

## 4. 정직한 한계 / 이월

- **결과 view auth-gate**: 익명으로 스무고개·생성은 되나 `/plan/[id]`는 로그인 필요(기존 동작, Quick/Discovery 동일). 익명 브랜딩 사용자는 결과를 보려면 로그인 — 의도/완화는 별도 UX 결정.
- **authed seed 라이브**: brand_memory 시드(S4)의 실 Supabase 라이브 e2e는 로그인 필요 → 유닛(641)+B 플로우로 검증, 실계정 authed e2e는 이월.
- LLM 질문 루프 비용/지연: cap 8 + 카드 응답으로 완화(실측은 운영 단계).

## 5. 산출물
- agent `topic_discovery.py`(P-AUX-3) + prompt_registry / endpoints `next/finalize/select` + schemas / frontend `/new/branding` + 진입 카드 + api/types / config 2 flag(extract 아님 — seed) / tests +41(S1 12 + S2 11 + S3 build + S4 9 + 등)
- contract: CC-023(api_contract 브랜딩 endpoint) + page_map/component_map docs-sync
- 회고/closing.

## 6. 다음
- **Phase 19~20(provisional) 2nd brain 시각화** — 마이페이지 PKM(개인+브랜드) 도식화. 이제 brand_memory 시드 source(브랜딩 세션)까지 있어 데이터 풍부.
- 이월: 결과 view auth UX / authed seed 라이브 e2e / commercial_viral / 배포 게이트.
