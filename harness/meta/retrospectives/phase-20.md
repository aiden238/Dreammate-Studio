# Phase 20 회고 — commercial_viral 모드 (output_mode 4th tier)

> 2026-06-04 | 제품 phase (런타임 有, gated/additive) | output_mode 4-tier 완성 (compact<rich<director<commercial_viral)

## 1. 무엇을 했나

PARKED 제안서(2026-06-03_commercial-viral-mode-design.md)의 선행조건(rich 실사용/위저드 실연결/human review + 데이터레이어)이 전부 충족됨을 확인하고, director(Phase 15) 패턴을 그대로 1-tier 위로 확장.

- **S1 schema**: output_mode Literal 4-tier + COMMERCIAL_FIELDS(7) + DirectorScene +2(brand_signal/commercial_signal) + model_dump_for_mode 4-tier. (CC-026)
- **S2 prompt**: COMMERCIAL_SYSTEM_PROMPT(10섹션) + P-006 v1.3.0 + §3.3 제약(보장금지/추측표기/기획경계/일반론금지). (CC-025)
- **S3 wiring**: planning 3개 선택 지점 + max_tokens tier별 상향(commercial 4500). ★ director parallel_3 절단 잠복버그 동반 수정.
- **S4 critic**: DIMENSIONS_COMMERCIAL(17 = director 10 + 상업 7) + P-007 v1.4.0 + 프로그램적 프롬프트. (CC-027)
- **S5 frontend**: PlanCard commercial 슬롯 조건부 렌더 + 보정1/3 disclaimer. types +9.
- **S6**: ★ 라이브 검증 PASS + cost §16(CC-028) + 종료.

## 2. 핵심 성과 / 검증

- ★ **라이브 검증 PASS**(실 LLM, eval/regression_results/2026-06-04_phase-20-commercial-live.md): commercial 7슬롯 전부 채움 + scene 2필드 + **보장 표현 0**(보정1) + market/audience **"추정:" 표기**(보정3) + critic **17/17**(approve, avg 4.41) + compact byte-identical(누수 0).
- behavior-preserving: 전 슬라이스 compact/rich/director **byte-identical**. hermetic pytest 668→**691**(기존 0 수정 + 신규 26) + scenario_sim 36/36 + audit 0.
- gated/additive: default=compact 불변. 4-tier 깊이/비용 오름차순. CC-025~028.

## 3. 학습 / 패턴

- **director 패턴의 1-tier 재사용이 매우 효율적**: effective_output_mode 단일점 + model_dump_for_mode + 프로그램적 critic 프롬프트(.replace 체인) → commercial 추가가 깔끔. tier 확장의 정형(P-OUTPUT-TIER-EXTENSION).
- **sub-agent 코드 검증의 가치**: S1 sub-agent의 model_dump_for_mode nested-exclude 조건 버그(`!= commercial_viral` → compact/rich scene 누수)를 메인 세션 검토에서 적발·수정. P-X1 + 직접 리뷰.
- **라이브 검증이 잡는 것**: 유닛(byte-identical)은 잡지만, "보장 표현 0 / 추정 표기 / 슬롯 실채움"은 실 LLM로만 확증 — 보정1/2/3이 실제로 동작하는지는 라이브에서만 보임(P-LIVE-VERIFY-001).
- **잠복 버그 동반 수정**: S3에서 director가 parallel_3 경로(max_tokens 1500 고정)에서 절단되던 잠복 버그를 commercial 작업 중 발견·수정.

## 4. 정직한 한계 / 이월

- **프론트 시각 e2e**: commercial 렌더는 typecheck/lint + 라이브 백엔드 생성으로 검증, 실 브라우저 시각 렌더는 미확인(이월 — /brain과 동일 환경 한계, S5는 director 패턴 동형이라 위험 낮음).
- **데이터레이어 enrichment 미적용**: market_context/audience_psychology 는 v1 LLM-only(추정 표기). PKM/RAG 실데이터 주입은 후속.
- **golden5/human gate 미수행**: §5.4 게이트(paid 활성 전)는 default OFF라 본 phase 범위 밖. paid 노출 전 별도.
- **비용 정밀 실측 미수행**: §16은 추정. 운영 누적 후 정밀 단가.

## 5. 산출물
- backend: config(Literal 4-tier) + schemas/output(COMMERCIAL_FIELDS/SCENE_COMMERCIAL_FIELDS/model_dump_for_mode) + planning(COMMERCIAL_SYSTEM_PROMPT/helper/version/wiring) + critic(DIMENSIONS_COMMERCIAL/프롬프트/version)
- frontend: PlanCard commercial 섹션 + types +9
- contract: CC-025(prompt P-006 v1.3.0) + CC-026(output_schema §8.1 v1.4.0) + CC-027(prompt P-007 v1.4.0) + CC-028(cost §16)
- tests +26(668→691): commercial schema/prompt/wiring/critic
- 라이브 리포트 + 회고/closing

## 6. 다음
- 이월: 프론트 commercial 시각 e2e / 데이터레이어 enrichment(market/audience 실데이터) / golden5+human gate(paid 전) / 비용 실측.
- 로드맵: (다) /brain 4계층 깊이+출처 엣지 / 배포 Gate B~G. ★ output_mode 4-tier 완성 — 깊이 스펙트럼(골격→제작착수→연출→전략) 전부 gated.
