# ADR-036: Meta-Factory 첫 Sample Test (팟캐스트 도메인 dry-run)

> 상태: Accepted
> 결정일: 2026-05-31
> Phase: M1 (Meta-Factory Sample Test, ★ meta-phase)
> 관련: ADR-035 (L3 Meta-Factory 도입) / CC-006 (harness-factory #21) / validation_workflow.md / eval-run SKILL
> ★ 런타임 변경 0 (A9) + dry-run 산출물 `meta_factory/outputs/TEST/` 격리 (MG1)

---

## Context

Phase M0(ADR-035)로 L3 Meta-Factory machinery(generation_workflow 11단계 + validation_workflow 6검증 + schema/templates/blueprint + harness-factory Skill)를 만들었으나 **"문서·skeleton만" 상태**였다. GPT M0 검토에서 validation 8.5/10이지만 *실작동 증명 부재*가 약점으로 지적됨. machinery가 실제로 ① 새 도메인 harness blueprint를 생성하고 ② 그 blueprint를 검증할 수 있는지를 1회 dry-run으로 확인할 필요.

GPT 검토 보완 3건: ① with/without 비교 수치화, ② 판정 PASS/FAIL/PENDING/GAP 4상태, ③ outputs 외 변경 0 강제 + phase 기록 별도 doc-sync 분리. 사용자 지침: 테스트 산출물은 별도 **TEST 폴더**에 격리.

## Decision

**Phase M1 — Meta-Factory Sample Test (meta-phase)** 로 분리하여, 인접 도메인 **「팟캐스트 에피소드 기획 AI」** 1개에 machinery를 **1회 dry-run** 적용한다. 목적은 "성공"이 아니라 **machinery 실작동 입증 + GAP 발견**.

1. **테스트 도메인 = 팟캐스트(인접)** — Dreammate(영상기획)와 공통(브랜드/타깃/톤/후킹/시리즈) + 차이(오디오 segment/오프닝 멘트/게스트). 완전 이질 도메인은 실패 원인 분석 곤란 → 인접부터.
2. **2 Slice dry-run + 별도 doc-sync** — S1 generation / S2 validation은 sub-agent(outputs/TEST/만), phase 등록·회고·archive는 main 세션 별도 commit.
3. **격리 = `meta_factory/outputs/TEST/`** — 실 산출 영역(generated_harnesses/improvement_reports)과 분리. MG1 게이트 = dry-run 변경이 TEST/ 외부 0줄.
4. **with/without 6지표 수치화** + **4상태 판정** + **GAP을 improvement_reports로** (proposal-only, machinery 0줄 변경).

## Result

- **6검증 PASS 5 / PENDING 1** (검증5 eval-run = 실측 미수행, 정상). blueprint validation 3필드 = pass/pass/pass.
- **with/without 6지표**: WITH(누락 0 / forbidden 1 / cross-ref 누락 0 / eval gate 1) ≫ WITHOUT(누락 6 / forbidden 0 / cross-ref 누락 4 / eval gate 0).
- **5 gaps 전부 재현** (재현 5/부분 0/비재현 0) — 부족점 4·5는 S2 절차로 부분 완화.
- **GAP 8개** (G1~G8, 핵심 G2/G3/G5) = 다음 machinery 개선 백로그.
- **machinery 작동 입증**: 검증2가 podcast-eval-run 신규 Skill의 eval-run 키워드 4중첩을 검출하여 채택 사전 차단.
- ★ runtime 0 (A9) + outputs/TEST/ 외 0 (MG1) + P-X1 52연속.

## Consequences

### 긍정
- machinery가 "검증 가능하다"는 것을 1회 입증 — M0의 payoff를 처음 실증.
- 8 GAP 백로그 확보 — L3 다음 개선의 실측 근거 (특히 G2 skill 재사용 결정트리 / G3 conditional 슬롯 / G5 제3자 PII).
- TEST 폴더 격리 + dry-run/doc-sync 분리 패턴 확립 (P-META-FACTORY-002 후보).

### 제약 / 한계
- **소표본**(1 도메인 1회) — 정량 우열 단정 불가, 방향성만.
- **검증5 실측 부재** — 품질·일관성(검증4)은 PENDING. 다음: 실 eval-run 표본 1회.
- **with/without 오염 잔존** — 단일 sub-agent가 양 팔 작성 (without 먼저 작성으로 완화, 한계 명시).
- generated 팟캐스트 harness는 6검증 통과(PASS 5)에도 **active 아님** (factory_contract 규칙 7) — 사용자 승인 전 proposal 상태.

## Non-Goals (재확인)
- 팟캐스트 harness를 active로 전환 / 2nd 실제 프로젝트 시작 (NG2).
- machinery 문서 변경 (NG4 — 본 phase는 사용만, 보완은 별도 contract-change).
- 자동 generator 코드 (NG5 — M0 NG11 계승).
- 실 LLM 대량 호출/비용 평가 (NG7 — dry-run).

## 다음 ADR 후보
- (M2?) 8 GAP 중 핵심 3개(G2/G3/G5) machinery 보완 — contract-change 경유.
- 검증5 실측 eval-run 표본 결과 (eval-run §3~§6).
