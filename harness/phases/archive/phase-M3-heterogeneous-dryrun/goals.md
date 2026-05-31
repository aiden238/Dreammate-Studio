# Phase M3 — Goals (Heterogeneous Domain Dry-run, Generality 2nd Check)

> Phase: phase-M3-heterogeneous-dryrun
> 유형: **meta-phase dry-run** (M1 과 동형 — machinery 0 변경, 개선본 읽기만. 산출물 outputs/TEST/ 격리)
> 진입일: 2026-05-31
> 예상 시간: 2.5~3.5h (S1 generation + S2 validation + assess, sub-agent)
> ★ 런타임 0 (A9) + dry-run 변경 outputs/TEST/ 외 0줄 (MG1)
> 결정 근거: 사용자 "이질 도메인 dry-run — 개선 machinery 범용성 2차 검증후 ... 없으면 바로 Phase 10 기획"

## 한 줄 정의

M2 로 개선된 meta_factory machinery(G1~G8 반영본)를, M1(인접 도메인 팟캐스트)과 달리 **이질 도메인**「개인 재무 플래닝 AI」에 **1회 dry-run** 적용하여 ① machinery 가 이질 분야에서도 일관된 harness blueprint 를 생성하는가(범용성) ② **M2 개선 8요소(G1~G8)가 이질 도메인에서 실사용·유효한가** ③ 새 GAP(범용성 한계)이 있는가를 검증한다.

## 테스트 도메인 — 개인 재무 플래닝 AI (★ 이질)

```
정의   : 개인 재무 목표(저축/부채상환/투자배분/은퇴) → 예산·저축·투자배분 플랜 3안 생성 + 리스크/적합성 검토
★ 아님 : 투자 자문/권유, 원금 보장, 특정 상품 추천, 세무·법률 자문 (정보·기획 도구)
이질성 : 미디어(영상/팟캐스트) → 금융(수치·규제). 창의적 hook 대신 리스크/적합성, 규제 forbidden_scope 강함
공통   : planning-shaped (플랜 3안 + Critic/검토) → M1 팟캐스트와 공정 비교 가능
```

## M1 → M3 비교축

| | M1 (팟캐스트) | M3 (재무) |
|---|---|---|
| 도메인 거리 | 인접 (미디어) | **이질 (금융)** |
| machinery | M0 원본 | **M2 개선본 (G1~G8)** |
| 목적 | 실작동 + GAP 발견 | **범용성 2차 + M2 개선 유효성 + 새 GAP** |

## 핵심 목표 (G1~G6)

| ID | 목표 | 검증 |
|---|---|---|
| **GA** | 재무 domain_brief (data_model G6 + 제3자 PII risk G5 활용) + harness_blueprint + scaffold 생성 | A1·A2 |
| **GB** | M2 개선 8요소(G1~G8) 이질 도메인 **실사용 점검** — 각 사용/유효/부적합 판정 | A3 (★ 핵심) |
| **GC** | validation_workflow 6검증 (PASS/FAIL/PENDING/PENDING-BY-DESIGN/GAP) | A4 |
| **GD** | 범용성 판정 — 미디어 편향(창의 hook/3-variant 강요) 유무 + 이질 도메인 적합도 | A5 |
| **GE** | **새 GAP 검출** (범용성 한계 — 있으면 백로그, 없으면 0) | A6 |
| **GF** | 종합 — 추가 검증/반영/수정 필요 여부 결정 (→ 있으면 후속, 없으면 Phase 10 직행) | A7 (★ 분기) |

## 메타 목표 (MG1~MG3)

| ID | 목표 |
|---|---|
| **MG1** | dry-run 변경 outputs/TEST/ 외 0줄 (machinery 개선본 읽기만 — 변경 0) |
| **MG2** | A9 — FastAPI/Next.js/Supabase 0줄 |
| **MG3** | P-X1 §SELF-VERIFICATION **57연속** (M2 55 + M3 S1·S2 2) |

## ★ 분기 (사용자 지침)
- **새 GAP/반영/수정 요소 없음** → 바로 Phase 10 (MVP 통합) 기획.
- **있음** → 백로그 기록 + 후속 결정 (M2 식 반영 or Phase 10 후 처리).

## 사용자 가치 (Why)
- **범용성 실증**: M2 개선이 인접(팟캐스트)뿐 아니라 이질(금융)에서도 작동하면 Meta-Factory 의 도메인 범용성 입증 — 2nd 하네스 생성 신뢰도 ↑.
- **편향 점검**: machinery 가 Dreammate(미디어 생성) 편향인지 이질 도메인이 드러냄.
- **Phase 10 진입 판단**: meta-tooling 이 충분히 안정됐는지 최종 확인 후 제품 로드맵 복귀.
