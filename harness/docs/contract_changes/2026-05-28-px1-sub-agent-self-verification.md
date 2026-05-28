# Contract Change Log — P-X1 Sub-Agent Self-Verification

> ID: CCL-001 (Phase 3 pre-entry, 2026-05-28)
> Type: Skill 변경 (Skill도 contract처럼 취급, contract-change §"적용 범위")
> Status: applied
> Trigger: Phase 2 retrospective P-X1 (meta/proposals/2026-05-27_*)
> Source pattern: P-AGENT-SCOPE-001 (meta/patterns.md)

---

## 1. 변경 대상

- `.claude/skills/phase-start/SKILL.md` v1.2.0 → **v1.3.0**

## 2. 변경 내용

§6.3 Surgical Scope 하위에 신규 sub-section "Sub-agent 자기 검증 절차" 추가.

### Before (v1.2.0)
§6.3 끝부분: "범위 밖 파일을 건드릴 필요가 생기면 → scope creep 신호, 즉시 사용자에게 알림."

### After (v1.3.0)
위 줄 다음에 다음 sub-section 추가:

```markdown
##### Sub-agent 자기 검증 절차 (v1.3.0 추가, P-X1)

배경: P-AGENT-SCOPE-001 패턴 — Phase 2 Wave 3 Slice 3 sub-agent가 forbidden 영역 침범.

모든 sub-agent prompt에 다음 section 포함 의무화:
1. git status — staged 파일 목록
2. git diff --stat HEAD — 본인 수정 파일 목록
3. 본인 프롬프트의 editable / forbidden 목록과 비교
4. 의도하지 않은 forbidden 파일 변경 시 즉시 revert + 보고

Main session 후속 검증 (sub-agent 완료 후):
- git log -1 --stat 또는 git diff HEAD~1 HEAD --stat
- forbidden 영역 변경 발견 시 즉시 알림 + revert 결정
```

## 3. 영향 받는 영역

- [x] Skill 절차 (phase-start)
- [x] Sub-agent prompt template (Phase 3 Wave 1~5)
- [ ] API 응답 형식
- [ ] DB 스키마
- [ ] Agent IO
- [ ] Output Schema
- [ ] 프론트 컴포넌트
- [ ] Prompt
- [ ] RAG 파이프라인
- [ ] 평가 / golden_set
- [ ] 보안 / 권한

## 4. 영향 받는 파일

```
.claude/skills/phase-start/SKILL.md (이 변경의 본문)
meta/proposals/2026-05-27_phase-2-retrospective-proposals.md (P-X1 status: applied)
meta/patterns.md (P-AGENT-SCOPE-001 status 갱신 가능, optional)
PROJECT_STATE.md (last_contract_change 갱신)

운영 영향 (자동 반영):
- Phase 3 모든 Wave (Slice 1~6) sub-agent prompt가 §SELF-VERIFICATION section 포함
- Main session이 sub-agent 완료 후 git diff --stat 검증 단계 추가
```

## 5. Rollback 방안

`git revert <commit-hash>` 또는 phase-start SKILL.md를 v1.2.0 상태로 되돌림.
영향: Phase 3 sub-agent prompt에서 §SELF-VERIFICATION section만 제거하면 됨.

## 6. 마이그레이션 필요 여부

- [ ] DB 마이그레이션
- [ ] 기존 데이터 변환
- [ ] 사용자 통지 — N/A (내부 절차)
- [ ] 외부 API 클라이언트 통지

운영 마이그레이션: Phase 3 sub-agent 발사 직전 prompt template 갱신 (main session 책임).

## 7. 결정

- **결정**: 승인 + applied (2026-05-28)
- **결정자**: 사용자 ("P-X1은 선적용" 명시)
- **결정 출처**: meta/proposals/2026-05-27_phase-2-retrospective-proposals.md §P-X1 accepted
- **메모**: Phase 3 진입 전 pre-step으로 선적용. 동일 commit에 phase-start SKILL.md + PROJECT_STATE + 본 changelog + proposal status 갱신 묶음.

## 8. 후속 액션

- [x] phase-start SKILL.md v1.3.0 갱신 완료
- [ ] meta/proposals/2026-05-27_*.md §P-X1 status: applied 표시 (다음 단계)
- [ ] PROJECT_STATE.md: last_contract_change=2026-05-28, last_skill_version_changed=phase-start@v1.3.0
- [ ] Phase 3 Wave 1~5 sub-agent prompt template에 §SELF-VERIFICATION 의무 적용

## 9. 변경 이력

- 2026-05-28: P-X1 적용 commit (Phase 3 진입 직전 pre-step)
