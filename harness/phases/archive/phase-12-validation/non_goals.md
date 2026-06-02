# Phase 12 — Non-Goals

| ID | 항목 | 사유 |
|---|---|---|
| **NG1** | **운영 prompt/schema 실제 확장** | ★ Phase 12 = **측정만**. compact→rich 확장(hook 3변형·타임코드·대사·자막·B-roll·썸네일·CTA 등)을 운영 prompt_registry / output_schema 에 반영하는 것은 **Phase 13**. Phase 12 는 운영 코드 0 수정 — S3 의 rich 는 **측정 전용 프롬프트**(운영 미반영) |
| **NG2** | **완성 대본 / 영상 제작·편집 / TTS / BGM** | ★ MVP **영구** non-goal (product_boundary 유지). 확장본(rich)도 "기획 브리프"여야 함 — 깊이를 더하되 "촬영·편집해서 영상이 나오는" 결과물 아님. depth 측정은 기획 깊이(실행가능한 브리프)이지 제작물 아님 |
| **NG3** | **staging 배포 / 운영 환경 적용** | Phase 13+ 배포 골격으로 이관 (사용자 확정: staging S4 제외). Phase 12 는 로컬 측정·분석만 |
| **NG4** | **새 모델 도입** | ★ 깊이 격차 핵심 = "같은 모델(gpt-4o-mini)에서 prompt/schema 만으로 출력 가치가 변한다". 새 모델/flagship 도입은 Phase 12 가설 검증 대상이 아님 (B안 3-provider 는 Phase 11 완료 — eval 에 활용 가능하나 신규 도입 아님) |
| **NG5** | **운영 endpoint / agent 동작 변경** | behavior-preserving — /generate, MOA orchestrator, agents, output schema 0 수정. eval 은 측정 capability(runner 직접 호출, 운영 미경유) |
| **NG6** | **golden_set / eval 의 entry-단계 사전 변경** | ★ golden_set 15→~25 + depth/actionability 차원은 **S1 에서만** contract-change 경유. 본 entry 는 **계획만** — eval/golden_set·rubric 사전 변경 0 |
| **NG7** | **human review 사용자 실 채점 완수** | ★ Phase 12 산출 = human review **kit(표본 + 시트 + 대조 설계)** 준비까지. 사용자가 실제로 앉아서 채점하는 시간 소요분은 **deferred**(Phase 12 acceptance 는 kit 준비, 실 채점은 후속) |
| **NG8** | **확장 우선순위의 실제 구현** | S5 = 우선순위 **제안**(데이터 근거). 어떤 필드를 먼저 추가할지의 실제 구현은 Phase 13~20 |
| **NG9** | **회귀 게이트를 실 LLM 로 전환** | ★ mock-deterministic eval(Phase 9.5/10) = CI 회귀 게이트로 **유지**. Phase 12 의 실 LLM eval 은 **측정 전용**(1회 baseline) — 회귀 게이트를 비용 드는 실 호출로 바꾸지 않음 |
| **NG10** | **실 키 평문 (코드/commit/채팅)** | ★ .env user-provided + .gitignore. 실 LLM 호출은 사용자 승인된 비용으로 실행하되 키 평문 절대 금지 |
| **NG11** | **운영 .py 변경 (backend/fastapi, apps/web)** | ★ Phase 12 = 검증/계획 phase — 문서·eval 데이터만. 운영 코드 0줄 (P-X1 게이트) |

## ★ 핵심 원칙

1. **측정만, 확장 아님**: Phase 12 는 깊이 격차를 **수치로 확정**한다. 격차를 메우는 실제 prompt/schema 확장은 Phase 13 (NG1·NG8).
2. **behavior-preserving**: 운영 endpoint/agent/prompt/schema 0 수정. pytest 471 유지 (NG5·NG11).
3. **기획 브리프 경계 유지**: rich 확장본도 "실행 가능한 기획 브리프"이지 완성 대본·제작물 아님 — product_boundary 영구 준수 (NG2).
4. **mock 게이트 보존 / real 은 측정 전용**: CI 회귀는 mock-deterministic 유지, 실 LLM eval 은 1회 baseline 측정만 (NG9).
5. **contract-first**: golden_set/rubric 변경은 S1 contract-change 경유 — entry 사전 변경 0 (NG6).
6. **kit 까지가 산출**: human review 는 채점 kit 준비까지 — 사용자 실 채점 시간은 deferred (NG7).
7. **키 0**: 실 키 평문 절대 금지 (NG10).

## 회피 패턴
- ❌ "깊이 격차 봤으니 운영 프롬프트도 rich 로 바꾸자" → NG1 (Phase 13)
- ❌ "rich 출력에 대사·샷 다 넣었으니 거의 대본이네, 영상까지" → NG2 (product_boundary)
- ❌ "entry 쓰면서 golden_set 케이스도 몇 개 추가" → NG6 (S1 contract-change 경유)
- ❌ "실 LLM eval 좋으니 CI 게이트도 실 호출로" → NG9 (mock 게이트 유지)
- ❌ "human review 표본 만든 김에 내가 다 채점" → NG7 (kit 까지, 실 채점 deferred)
- ❌ 운영 .py 한 줄 수정 → NG11 (측정·문서만)
