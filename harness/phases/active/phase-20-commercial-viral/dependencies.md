# Phase 20 — Dependencies

## 선행 (제안서 §0.2 선행조건 — 전부 충족)
| 의존 | 상태 | 제공 |
|---|---|---|
| Phase 13 (rich 출력) | ✅ done | PLAN_RICH_FIELDS/BEAT_RICH_FIELDS + model_dump_compact — additive 슬롯 패턴 |
| Phase 14 (위저드 실연결) | ✅ done | (선행조건 b) /new/* → backend end-to-end |
| Phase 15 (director tier) | ✅ done | **★ 직접 계승** — output_mode enum + DIRECTOR_FIELDS + model_dump_for_mode + DirectorScene + DIMENSIONS_RICH gated. commercial_viral = 동일 패턴 1-tier 위 |
| Phase 12 S4 (human review) | ✅ done | (선행조건 c) depth + 품질 5차원 kit |
| Phase 16/17 (PKM/RAG 데이터레이어) | ✅ done | (제안서 §7.2 의존) brand_memory/pkm_entries — market/audience enrichment 재사용 가능(v1 옵션) |

## 재사용 자산 (★ director 패턴 그대로 1-tier 확장)
```
config.effective_output_mode()  — 단일 종합점. Literal 에 commercial_viral 추가 시 자연 반환.
schemas/output.py:
  PLAN_RICH_FIELDS(9)/BEAT_RICH_FIELDS(3)/DIRECTOR_FIELDS(3) + DirectorScene(5)
  model_dump_for_mode(output_mode) — compact:RICH∪DIRECTOR 제외 / rich:DIRECTOR / director:없음
  → commercial 추가: +COMMERCIAL_FIELDS(10)+CommercialScene(7), 각 tier 에 COMMERCIAL 제외 추가
  envelope_to_response_dict(output_mode) — 이미 mode-aware
agents/planning.py: RICH_SYSTEM_PROMPT/DIRECTOR_SYSTEM_PROMPT + *_PROMPT_VERSION (gated 공존)
agents/critic.py: DIMENSIONS / DIMENSIONS_RICH(gated) — dimensions 자유 dict(additive)
cost_control_policy §13/§14 — rich/다중-provider cost 패턴
```

## 불확실 / 외부
- U1 director↔commercial 슬롯 경계(어느 필드가 director 까지) — 제안서 §2.1 은 director 가 commercial 일부(hook_system 등) 보유 가능성 언급. ★ 현 코드 director=DIRECTOR_FIELDS(3 전용 슬롯)로 이미 구현 → commercial 은 별도 COMMERCIAL_FIELDS(10)로 깔끔 분리(겹침 0)로 단순화. S1 에서 확정.
- U2 market/audience 의 LLM 추측 표기 UX — v1 프롬프트 내 마커(§3.3), 정식 데이터 enrichment 후속.
- U3 scene_breakdown N씬 상한 — 토큰/비용 vs 깊이, S6 실측.
- U4 critic 17차원 비용/지연 — S4/S6 측정.
