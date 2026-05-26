# project_memory_policy.md — 프로젝트 메모리 정책

> 위치: `ai_system/memory/project_memory_policy.md`
> 상태: S4-3 deep
> 참조: `docs/contracts/db_schema.md` (video_projects), `user_memory_policy.md`
> 참조: `ai_system/memory/candidate_knowledge_policy.md`

---

## 1. 정의

**프로젝트 메모리(Project Memory)**는 4계층 컨텍스트의 가장 깊은 단위인 `video_projects`에 묶이는 메모리다. 한 영상 프로젝트의 라이프사이클 동안 생성/수정된 모든 의도/방향/결과/피드백을 추적한다.

User Memory(Brand 단위 누적 학습) vs Project Memory(video 단위 컨텍스트)는 명확히 다르다:

| 항목 | User Memory | Project Memory |
|---|---|---|
| 단위 | Brand | Video Project |
| 수명 | 사용자 활성 기간 | 프로젝트 lifecycle |
| 용도 | 다음 세션 학습 신호 | 현재 세션 컨텍스트 유지 |
| 저장 위치 | brand_memory_entries | video_projects + 관련 테이블 |
| 학습 자산 여부 | yes (장기) | no (단기 컨텍스트) |

---

## 2. 저장 내용

```
video_projects 컬럼:
  - video_id (uuid)
  - user_id, brand_id, domain_id, series_id
  - one_line_direction (P-005/P-005q 결과)
  - mode ('discovery' | 'quick')
  - status ('draft' | 'selected' | 'final' | 'archived')
  - created_at, updated_at

연결 테이블:
  - discovery_choices: 카드 선택 누적
  - plan_options: 3개 plan 후보 + 사용자 선택
  - quality_scores: Critic 결과
  - revision_requests: Rewriter 결과
  - feedback_events: 사용자 피드백
```

---

## 3. 재방문 시 활용

```
사용자가 동일 video_project 재진입 시:
  1. status='draft' → 마지막 카드 선택 시점부터 재개
  2. status='selected' → plan 결과 + 사용자 선택 표시
  3. status='final' → 결과 + "새로 만들기" / "복제하기" 옵션

재방문 시 컨텍스트 복원:
  - 4계층 컨텍스트 자동 주입
  - 이전 카드 선택 표시 (변경 가능)
  - Brand Memory 최신화 후 주입
```

---

## 4. candidate_knowledge와의 차이

```
Project Memory:
  - 개별 video 결과 (단기 컨텍스트)
  - global 학습 자산 아님
  - 다른 사용자에게 노출 안 됨

candidate_knowledge:
  - 학습 자산 후보 (장기, 잠재적 global)
  - 5단계 승격 파이프라인 거침 (rag-update Skill)
  - approved 시 다른 사용자에게도 활용 (anonymized)
```

Project Memory의 일부 패턴(좋은 hook, 효과적 outline)이 candidate_knowledge로 승급될 수 있으나, 항상 anonymization + quality filter 통과 후.

---

## 5. 보존 기간

```
status='draft' / 'selected':
  - 활성 기간 무제한 (사용자가 작업 중)
  - 90일 이상 미수정 → status='archived' 자동 전환

status='final':
  - 활성 무제한
  - 사용자 명시 삭제 시 30일 grace → 물리 삭제

status='archived':
  - 365일 후 자동 hash + 익명화

연결 테이블(plan_options, quality_scores 등):
  - video_projects와 동일 lifecycle
  - CASCADE DELETE (FK)
```

→ data_retention_policy placeholder가 Phase 7+에서 정량화.

---

## 6. 4계층 컨텍스트 연결

```
User → Brand → Domain → Series → Video Project

상위 계층 변경 영향:
  - Brand 삭제 시: 하위 모든 Video Project archived
  - Domain 변경 시: 하위 Video Project warning (재검토 권장)
  - Series 변경 시: 하위 Video Project 카드 재선택 안내
```

---

## 7. 의존성

- `docs/contracts/db_schema.md` (video_projects + 연결 테이블)
- `ai_system/memory/user_memory_policy.md` (User Memory와 비교)
- `ai_system/memory/candidate_knowledge_policy.md` (학습 자산 분리)
- `apps/web/design.md` (재방문 UX)

---

## 8. 확장 가능성

- Phase 11+: Project 간 cross-reference (같은 series에서 video A 결과 → video B 참고).
- Phase 11+: 협업 (team 단위 프로젝트 공유).
- Phase 21+: Project 자동 분류/태깅.

---

## 9. Open Questions

1. status='draft' 90일 미수정 archive 임계 — 사용자 사용 패턴 누적 후 재조정.
2. 재방문 시 Brand Memory 변경 사항 자동 적용 vs 사용자 확인(현재 자동 적용).
3. cross-reference 도입 시점(Phase 11+) — 사용자 요청 누적 후 검토.
4. Project 자동 archive 시 사용자 알림 채널(현재 무음).
5. 협업 도입 시 권한 모델(viewer/editor/owner) 정의 필요.
