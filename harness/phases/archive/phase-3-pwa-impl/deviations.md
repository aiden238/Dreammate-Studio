# Phase 3 — Deviation Log

> 조정 4번 (component_map.md read-only 절대 보장) 운영을 위한 누적 로그.
> spec ↔ 코드 drift 발견 시 component_map.md 직접 수정 X, 본 파일에 기록만.

---

## 운영 정책

1. Sub-agent 또는 main session이 Phase 2 spec (component_map / page_map / design_handoff 등) 과 실 코드 사이 drift 발견 시:
   - **절대 spec 파일 수정 X**
   - 본 파일에 entry 추가
2. drift가 의도된 단순화 (조정 사항)면 → "intentional simplification"으로 분류
3. drift가 실 차이면 → `meta/proposals/2026-05-28_*.md` 제안서 작성 후 Phase 4 진입 시 처리
4. Slice 6 retrospective에서 deviation 총합 보고

---

## Entry 형식

```yaml
- id: DEV-{NN}
  date: YYYY-MM-DD
  slice: N
  finding: "1~2줄 요약"
  spec_file: "apps/web/component_map.md §X"
  code_file: "apps/web/components/Y.tsx"
  drift_type: intentional_simplification | real_difference | spec_ambiguity
  resolution: "본 파일 기록 only" | "meta/proposals/ 제안 등록"
  follow_up_phase: 4 | 11+ | none
```

---

## 인덱스

(현재 0건 — Phase 3 진행 중 누적 시작)

---

## 변경 이력

- 2026-05-28: Phase 3 진입 시 최초 작성 (조정 4번 운영용)
