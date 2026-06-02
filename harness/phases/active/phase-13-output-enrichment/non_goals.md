# Phase 13 — Non-Goals

| ID | 항목 | 사유 |
|---|---|---|
| **NG1** | **완성 대본 / 영상 제작·편집 / TTS / BGM** | ★ MVP **영구** non-goal (product_boundary 유지). 확장본(rich)도 **"기획 브리프"**(촬영·편집 가이드)여야 함 — 후크 변형·타임코드·대사 가이드·샷 제안·썸네일 방향까지지만, "촬영·편집해서 영상이 나오는" 결과물 아님. 깊이를 더하되 경계를 넘지 않는다 |
| **NG2** | **모델 tier 상향 (opus/gpt-5.5 등)** | ★ Phase 12 가 입증 — 깊이 격차는 **같은 모델(gpt-4o-mini)에서 prompt/schema 만으로** 메워짐. 모델 tier 상향은 **2차 레버** — prompt/schema 확장 후 효과 재측정(S6) 뒤에 별도 검토. Phase 13 = 1차 레버(prompt+schema)만 |
| **NG3** | **flag default ON 즉시 전환** | ★ `rich_output_enabled` default **False** 유지 — 검증(S6 depth 재측정 + 라이브 데모) 통과 후 ON 전환은 **별도 결정**(Phase 13 acceptance 아님). 첫 출력 변경이므로 gated 로 안전하게 |
| **NG4** | **staging 배포 / 운영 환경 적용** | Phase 14+ 배포 골격으로 이관(Phase 12 staging S4 제외 계승). Phase 13 = 로컬 구현 + flag ON 라이브 데모(키 user-provided)까지 |
| **NG5** | **스키마 breaking change / 기존 필드 삭제·재명명** | ★ rich 슬롯 **전부 Optional default None/[]** (additive). 기존 7필드(name/concept/hook/flow/pros/risks/approach_label)·기존 소비자(PlanCard·orchestrator·Critic) **회귀 0**. 기존 compact 프롬프트도 삭제 X(flag OFF 경로 보존) |
| **NG6** | **flag OFF 경로 동작 변경** | ★ behavior-preserving — `rich_output_enabled=False` 면 기존 compact 출력 **byte-identical**(Envelope 불변). OFF 가 default → 검증 전까지 기존 사용자 영향 0 |
| **NG7** | **rich 데이터 없을 때 frontend 변경** | ★ PlanCard rich 렌더는 **conditional** — rich 필드 있을 때만 표시. 기존 compact 렌더 회귀 0(PlanCard 35연속·component_map 45연속 baseline 보호) |
| **NG8** | **golden_set / eval rubric 변경** | ★ depth_actionability rubric(CC-011)·golden_set 25 는 Phase 12 산출 — **그대로 재측정**(S6). Phase 13 은 rubric 변경 X, 측정만 |
| **NG9** | **B안 다중-provider UX 노출 / cross_validation 응답 노출** | output_schema 에 consensus/divergence UX 노출은 별도(Phase 14+). Phase 13 = depth 슬롯만. (B-RES-1 cost 재조정은 S6 흡수 — 그건 cost 정책, UX 아님) |
| **NG10** | **실 키 평문 (코드/commit/채팅)** | ★ .env user-provided + .gitignore. flag ON 라이브 데모는 사용자 승인 비용, 키 평문 절대 금지 |
| **NG11** | **본 entry 단계 운영 .py/contract 변경** | ★ 본 작업(종료+entry) = 문서/계획만. output_schema/prompt/config/critic/frontend 실제 변경은 **S1+ 에서** (P-X1 게이트 — entry 운영 .py 0) |

## ★ 핵심 원칙

1. **gated 롤아웃 (첫 출력 변경)**: `rich_output_enabled` default False → 검증 후 ON. OFF 면 compact byte-identical (NG3·NG6).
2. **additive 스키마**: rich 슬롯 전부 Optional → 기존 필드·소비자 회귀 0. 기존 compact 프롬프트 보존 (NG5).
3. **기획 브리프 경계 유지**: 확장본도 "실행 가능한 기획 브리프"이지 완성 대본·제작물 아님 — product_boundary 영구 준수 (NG1).
4. **1차 레버만**: prompt + schema 확장. 모델 tier 상향은 2차 레버(재측정 후) (NG2).
5. **conditional frontend**: rich 데이터 있을 때만 렌더, 기존 compact 렌더 회귀 0 (NG7).
6. **rubric 불변·측정만**: depth_actionability(CC-011)·golden_set 25 그대로 재측정 (NG8).
7. **키 0**: 실 키 평문 절대 금지 (NG10).

## 회피 패턴
- ❌ "rich 좋으니 default ON 으로 바로 전환" → NG3 (검증 후 별도 결정)
- ❌ "rich 에 대사·샷 다 넣었으니 거의 대본, 영상까지" → NG1 (product_boundary)
- ❌ "기존 Plan 필드 정리하면서 rich 로 교체" → NG5 (additive Optional, 기존 보존)
- ❌ "gpt-4o-mini 한계니 opus 로" → NG2 (1차 레버 = prompt/schema, tier 는 재측정 후)
- ❌ "flag OFF 경로도 살짝 바꿔서 통일" → NG6 (OFF byte-identical)
- ❌ "entry 쓰면서 output_schema 슬롯도 몇 개 추가" → NG11 (S1 contract-change 경유)
