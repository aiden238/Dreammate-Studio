# Phase 18 — Dependencies

## 선행 (충족)
| 의존 | 상태 | 제공 |
|---|---|---|
| Phase 17 (계정별 PKM) | ✅ done | brand_memory/PkmRepo/BrandRepo + 주입 경로 — 발굴 결과를 시드/주입할 대상 |
| Phase 4/8 (planning/orchestrator) | ✅ done | 택1 결과 → generateMultiPlan 기존 흐름 |
| Phase 5 (Auth) | ✅ done | auth_user_id(세션 사용자) — brand_memory 시드 격리 |
| Phase 1 Intent(P-001) | ✅ done | 자유입력 오프도메인/인젝션 차단 재사용 |

## 재사용 자산
```
plans/start + wizard endpoint(상태 누적) / generateMultiPlan(택1→생성)
BrandMemoryRepo.add_entry (브랜딩 방향 시드, Phase 17)
LLM gateway/workhorse(gpt-4o-mini) — 동적 질문 생성
prompt_registry semver (P-신규 topic_discovery 등록)
```

## 불확실 / 외부
- U1: N고개 상한 적정값(6~12) — S5 실측 후 조정.
- U2: 질문 루프 비용/지연 — 카드 응답 + workhorse 로 완화, S5 측정.
- U3: 세션 상태 보관 = wizard_data 재사용 vs 신규 store — S2 진입 시 확정.
