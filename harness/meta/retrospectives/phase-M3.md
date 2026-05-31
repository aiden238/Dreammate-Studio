# Phase M3 회고 — 이질 도메인 dry-run (범용성 2차 검증, ★ meta-phase)

> 종료일: 2026-05-31
> 유형: meta-phase dry-run (M1 동형 — machinery 0 변경, 개선본 읽기만)
> 결과: ✅ A1~A7 + MG1~MG3 PASS / 범용 강함 / M2 개선 유효 7·부분 1 / 새 GAP 3(전부 minor·nice-to-have) / ★ 분기 = **Phase 10 직행 가능**
> 트리거: phase-complete v1.2.0 §7 회고

---

## 1. 무엇을 했나

M2 개선 machinery(G1~G8)를 **이질 도메인「개인 재무 플래닝 AI」**에 1회 dry-run 적용 — 범용성 2차 검증.

- **S1 (dbd4f7e)**: 재무 harness 생성 — without baseline + domain_brief(data_model G6 + 제3자 PII G5 + 규제 forbidden) + blueprint(G1 expert/단일 결정) + 6 scaffold(G3 conditional / G4 applies_when / G7 harness_status). finance/ 9파일 1179줄.
- **S2 (3ad817e)**: 6검증 + M2 G1~G8 유효성 점검 + 범용성 판정 + 새 GAP + 분기 권고. validation 리포트 +352.

## 2. 핵심 결과

### 범용성 = 강함 (미디어 편향 0)
machinery 가 창의 hook/3-variant(창의 다양성)/썸네일/brand 를 재무에 **강요하지 않음**. 계승 형태(3안/supervisor/producer_reviewer/pipeline)는 도메인 무관 패턴 카탈로그의 재사용이고, blueprint 는 재무 고유 축(리스크/적합성/규제 forbidden/수치 합=100%)으로 적극 재정의됨 — hook_strength→actionability, brand_consistency→risk_appetite_fit, advisory_boundary 하드 게이트.

### M2 개선 8요소 유효성: 유효 7 / 부분 1 / 부적합 0
- **G5 가 M1(expressible)을 넘어 실 등급 상향(medium→high)으로 귀결** — 제3자 PII 2종(부양가족/수익자) + 금융 민감정보 결합 → high → human_review + security_review 강제.
- **G3·G4 가 enum mode(mode==guest)를 넘어 불리언 데이터 조건(has_debt/has_dependents)** 까지 표현 — 예상보다 범용적.
- **G2 결정트리**가 재무 신규 Skill 후보 4개를 **사전 차단**(M1 의 사후거부 1개 → M3 사전차단 4개).
- **G3 만 "부분"**: 표현은 유효하나 agent_template 예시가 enum mode 에 치우쳐 불리언 데이터조건을 명문 안내 안 함 → 문서화 GAP(NEW-G11), machinery 결함 아님.

### 6검증 PASS 4 / PENDING-BY-DESIGN 2 (fail 0)
- 검증3(contract): G3 조건부 산출 축이 **생성 시점부터 적용** → M1 의 GAP-flag 자체가 발생 안 함 (M2 개선 효과 실증).
- 검증5(eval-run): PENDING-BY-DESIGN (G8, 실측 별도).

## 3. 새 GAP (백로그 — blocking 0, Phase 10 막지 않음)

| GAP | 내용 | 심각도 | 비고 |
|---|---|---|---|
| **NEW-G9** | forbidden_scope 가 regulatory_forbidden(법적·영구) vs deferred_scope(MVP 후순위) 미구분 | **minor** | advisory_boundary 하드 게이트로 이미 실질 차단 — 표현 정밀도 개선 |
| **NEW-G10** | risk_level 단일 enum 이 data_risk vs regulatory_risk 미분해 | **nice-to-have** | G9 와 부분 중복 (규제위험 이미 forbidden_scope 축 표현) |
| **NEW-G11** | conditional_execution template 예시가 enum mode 치우침 (불리언 데이터조건 문서화 부재) | **nice-to-have** | 표현은 작동, 문서 명료화만 |

→ blocking 0. 3개 모두 백로그(`meta_factory/outputs/improvement_reports/` 또는 차기 meta-phase). Phase 10 진입을 막지 않음.

## 4. 잘된 것
1. **이질 도메인이 범용성을 입증** — 인접(M1 팟캐스트)뿐 아니라 이질(M2 개선본 + 재무)에서도 작동 → Meta-Factory 도메인 범용성 2차 검증 PASS.
2. **M2 개선이 예상보다 범용적** — G3/G4 가 enum 넘어 불리언 데이터조건, G5 가 실 등급 상향으로 귀결.
3. **보수적 분기 판정** — 새 GAP 을 minor/nice-to-have 로 정직 분류, blocking 아님을 근거와 함께 → Phase 10 직행 권고.
4. **TEST 격리(MG1) + machinery 보존** — dry-run 이 machinery/podcast/런타임 0줄. P-X1 57연속.

## 5. 한계
1. **실 LLM 의미 품질 미측정** — "범용 강함"은 표현·설계 차원 (검증5 pending-by-design). 실 품질 우열 아님.
2. **소표본** — 이질 도메인 1개(재무). 다른 이질 도메인(분류/추출 등 비-planning)은 미검증 — 추가 일반화는 차후.
3. **새 GAP 3개 백로그** — 즉시 반영 안 함(NG8). Phase 10 후 또는 차기 meta-phase.

## 6. 패턴
- **P-META-FACTORY-002 update** — 범용성 2차 검증(이질 도메인)까지 입증. "도입(M0) → 검증(M1) → 반영(M2) → 범용성 2차(M3)" loop 확장.
- **P-X1-EFFECT-001 update (57연속)**.
- **P-ADDITIVE-COMPAT-001** — M2 개선이 M3 에서 backward-compat 깨짐 0 (개선본으로 새 도메인 생성 정상).

## 7. 다음 단계 (분기 = Phase 10 직행)
- ★ **Phase 10 (MVP 통합 테스트) 기획** — meta-phase detour(M0~M3) 종료, 제품 로드맵 복귀.
- 새 GAP 3개(G9/G10/G11)는 백로그 — Phase 10 후 또는 차기 meta-phase 에서 minor 반영 검토.
- 이질 비-planning 도메인 일반화는 차후 (필요 시).

## 8. 메타 정합
- 제품 로드맵 0줄 진전(detour) — next_phase_status 불변, 단 M3 통과로 Phase 10 진입 근거 확보.
- runtime 0 (A9) + outputs/TEST/ 외 0 (MG1) + machinery 0 (개선본 읽기만).
- ★ Meta-Factory 범용성 2차 검증 완료 → meta-tooling 안정성 확인, 제품 복귀 적기.
