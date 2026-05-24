# Handoff Package: 영상기획 AI 에이전트 하네스 → Claude Code (Sprint S0)

> **세션 종료일**: 2026-01-XX (Claude 채팅 세션)
> **다음 세션 예정**: Claude Code (Cursor / VS Code)
> **목적**: 이 패키지 한 파일만 첨부하면 Claude Code가 Sprint S0를 정확히 실행할 수 있다.

---

## 1. 30초 요약 (가장 먼저 읽기)

```
프로젝트: 영상기획(≠제작) AI 에이전트. Discovery Wizard + Quick Mode 하이브리드.
지금 상태: GPT가 만든 155파일 골격 + 우리가 만든 깊은 콘텐츠 18파일이 따로 있음.
다음 작업: 둘을 병합 (Sprint S0~S5). 너(Claude Code)는 S0부터 시작.
첫 30분 할 일: HARNESS_ROOT 결정 → 폴더 생성 → 14개 누락 폴더 추가 
              → PROJECT_STATE/PHASE_REGISTRY 갱신 → sanity 스크립트 작성 → S0 commit.
참조 문서: migration_procedure.md (1337줄). 이걸 통째로 읽고 S0 섹션 따른다.
```

---

## 2. 프로젝트 핵심 컨텍스트

### 2-1. 무엇을 만드는가

```
- 사용자가 영상을 "기획"할 때 도와주는 AI 에이전트 (영상 제작 아님)
- 4계층 데이터 모델: User → Brand → Domain → Series → Video Project
- 두 가지 진입 모드:
  · Discovery: 신규 사용자 / 새 Brand·Domain·Series 만들 때 7단계 카드 wizard
  · Quick: 기존 Series에 영상 추가 시 짧은 프롬프트 + 한 줄 방향 승인
- MOA Lite 파이프라인: Intent → Planner → Critic → Rewriter (Critic revise 최대 2회)
- 한 번 호출당 3개 plan 후보 생성 → 사용자가 1개 선택
```

### 2-2. 기술 스택 (확정)

```
Frontend  : Next.js 14 (App Router) + TypeScript + Tailwind + shadcn/ui
Backend   : FastAPI (Python) — MVP
Mobile    : Phase 21+ Expo (지금은 placeholder)
Spring    : Phase 21+ (지금은 placeholder)
DB        : Supabase (PostgreSQL + pgvector)
LLM       : gpt-4o-mini 기본, gpt-4o 일부 (Critic 등)
배포      : Vercel (FE) + Render (BE)
```

### 2-3. MVP 제외 항목 (절대 안 함)

```
❌ 영상 자동 편집 / 자동 업로드
❌ TTS / BGM 생성
❌ 결제 / billing
❌ 팀 협업
❌ Mobile native (Expo) — Phase 21+
❌ Spring Boot — Phase 21+
❌ Admin Dashboard
```

---

## 3. 확정된 결정 (누적 25+개)

이 결정들은 Claude Code가 작업 도중 흔들면 안 됨.

### 3-1. 설계 결정

```
1.  Discovery + Quick 하이브리드 UX (1.6x 비용 수용)
2.  Mode 자동 분기: 신규 사용자/Brand → Discovery, 기존 Series → Quick
3.  Discovery 단계당 카드 5장 (4장은 추천, 1장은 "직접 입력")
4.  3개 plan 후보 생성 (P-006 plan_candidates)
5.  Critic revise 최대 2회 (무한 루프 차단)
6.  4계층 데이터 모델 (Brand/Domain/Series/VideoProject)
7.  Intent Filter (영상기획 외 입력 차단)
8.  Brand Memory 자동 추출 + 사용자 검토 가능
9.  광고적 표현 ("최고의", "혁신적인") 차단 단어 검사
10. 30–60초 생성 대기 시 4단계 progress stepper + 부분 결과 즉시 노출
```

### 3-2. 하네스/시스템 결정

```
11. 14 Skill (이전 세션) → 20 Skill (이번 세션, GPT 흡수 후)
12. Skill 폴더: .agents/.claude 분리 (이전 단일 결정 변경)
13. 22 Phase 등록 (1~10 MVP, 11~20 안정화, 21~30 확장)
14. Phase 0 = 마이그레이션 자체 (지금 active)
15. context-compact가 모든 Skill 위 최우선
16. multi-llm-validation 워크플로 (Claude/GPT-5/Gemini Pro 교대)
17. agent.html은 토큰 최적화 압축 레이어 (안정화 후 빌드)
18. RAG: candidate_knowledge 5단계 승격 (pending→filtered→evaluated→approved→promoted)
19. PII 마스킹 + 프롬프트 인젝션 차단 (Step 1, Step 2 자동 검사)
20. prompt 변경은 semver + golden_set 회귀 + A/B (major 시 10%→50%→100%)
```

### 3-3. 운영 결정

```
21. agent_html_spec v1.1.0 갱신 필요 (Sprint S2 후, .agents/.claude 결정 반영)
22. placeholder marker 표준 형식 (16개 stub 일관 적용)
23. Sprint별 git commit + sanity script (시작/종료)
24. PROJECT_STATE.migration_progress 필드로 부분 완료 감지
25. Codex / Copilot Code 교대 작업 (multi-llm-validation Skill 활용)
```

---

## 4. 산출물 인벤토리

모든 파일은 `/mnt/user-data/outputs/`에 있음. Claude Code 세션 시작 시 이 폴더 전체를 받음.

### 4-1. 핵심 콘텐츠 (이식 대상)

| 파일 | 줄 수 | 최종 위치 (HARNESS_ROOT 기준) |
|---|---|---|
| `design.md` | 688 | `apps/web/design.md` (GPT 163줄 교체) |
| `db_schema.md` | 580 | `docs/contracts/db_schema.md` (GPT 80줄 교체) |
| `prompt_registry.md` | 628 | `ai_system/prompts/prompt_registry.md` (GPT 8줄 교체) |
| `agent_html_spec.md` | 789 | `tools/agent_html_spec.md` (신규, Sprint S2 후 v1.1.0 갱신) |

### 4-2. Skills (14개, .agents/.claude로 분리 이식)

```
skills/
├── INDEX.md                          (115줄, 라우팅)
├── bug-triage/SKILL.md               (195) → .agents/skills/
├── contract-change/SKILL.md          (223) → .agents/skills/ + .claude/skills/  (양쪽)
├── context-compact/SKILL.md          (270) → .claude/skills/ (claude only)
├── cost-review/SKILL.md              (273) → .agents/skills/
├── design-review/SKILL.md            (224) → .claude/skills/
├── eval-run/SKILL.md                 (233) → .agents/skills/
├── meta-retrospective/SKILL.md       (246) → .claude/skills/ (claude only)
├── multi-llm-validation/SKILL.md     (252) → .claude/skills/
├── phase-complete/SKILL.md           (221) → .agents/skills/ + .claude/skills/
├── phase-start/SKILL.md              (150) → .agents/skills/ + .claude/skills/
├── prompt-version-review/SKILL.md    (222) → .agents/skills/
├── qa-check/SKILL.md                 (234) → .agents/skills/
├── rag-update/SKILL.md               (232) → .agents/skills/
└── security-review/SKILL.md          (271) → .agents/skills/ + .claude/skills/
```

`skills.zip`에 번들로도 있음 (54KB).

### 4-3. 마이그레이션 절차 문서

```
migration_procedure.md  (1337줄, v1.1.0)  ← 가장 중요. 통째로 읽기.
```

이 문서가 Sprint S0~S5 전체 수행 절차. 모든 결정 매트릭스, 충돌 해결, sanity 스크립트, placeholder marker 형식 포함.

### 4-4. 입력 자료 (GPT 하네스)

```
/tmp/gpt_harness/video_planning_agent_full_harness_md_and_skills/
  → 155 파일, 2862줄
  → 골격 채택 대상 (Skill 본문은 폐기)
```

또는 사용자가 zip 원본 보관 중일 수도 있음: `/mnt/user-data/uploads/video_planning_agent_full_harness_md_and_skills__1_.zip`.

---

## 5. Claude Code 첫 prompt (즉시 복붙용)

다음 prompt를 Claude Code에 그대로 전달:

```
[복붙 시작]

영상기획 AI 에이전트 프로젝트의 Sprint S0 (하네스 마이그레이션 초기화)를 수행한다.

## 첨부 파일

1. handoff_to_claude_code_sprint_S0.md  ← 이 문서 (전체 컨텍스트)
2. migration_procedure.md (v1.1.0)       ← 절차 명세
3. /mnt/user-data/outputs/ 전체            ← 이식 콘텐츠 + Skills

## 작업 범위

migration_procedure.md의 Sprint S0만 수행한다. S1~S5는 다음 세션.

S0 작업 항목 (순서대로):
1. HARNESS_ROOT 결정 (사용자에게 확인 받아라)
   - 권장: ${HOME}/projects/video-planning-agent (또는 사용자 선호)
2. 폴더 셋업 (migration_procedure §11.1 bash 스크립트 따라)
3. GPT 하네스 복제 + git init + initial commit
4. 우리 deliverables를 .migration_source/에 보관
5. 누락 폴더 14개 추가 (§11.2 목록)
6. 각 누락 폴더에 표준 README.md 생성
7. PROJECT_STATE.md 갱신:
   - confirmed_decisions에 이 핸드오프의 결정 25개 명시
   - migration_progress 필드 추가 (current_sprint: S0, step: in_progress)
   - current_phase: phase-0-migration
8. PHASE_REGISTRY.md 갱신:
   - Phase 0 추가 (active, 이 마이그레이션 자체)
   - Phase 1 → pending (active에서 강등)
   - Phase 2~3에 Discovery+Quick 분기 명시
9. CLAUDE.md, AGENTS.md 갱신:
   - 우리 신규 Skill 3개 (prompt-version-review, multi-llm-validation, context-compact) 라우팅 추가
   - 흡수/폐기 Skill 정리
10. instruction_index/{catalog,routes,dependency_map}.yaml 갱신
11. phases/active/phase-0-migration/{goals,scope,non_goals,acceptance,dependencies}.md 생성
    - acceptance.md는 §11.8의 11개 항목 그대로
12. sanity_start.sh, sanity_end_S0.sh 작성 (§11.4 형식)
13. sanity_end_S0.sh 실행 → 모두 PASS 확인
14. git commit: "harness: integrate GPT skeleton + routing decisions (S0)"
15. PROJECT_STATE.migration_progress 갱신 (S0 → completed)

## 절대 하지 말 것 (Negative Constraints)

❌ apps/web/design.md를 GPT 163줄 그대로 두지 마라 (Sprint S1에서 교체)
   단, S0에서는 아직 건들지 마라
❌ docs/contracts/db_schema.md 건드리지 마라 (S1 대상)
❌ ai_system/prompts/prompt_registry.md 건드리지 마라 (S1 대상)
❌ .agents/skills/ 또는 .claude/skills/의 SKILL.md 본문 건드리지 마라 (S2 대상)
❌ contract 본문 직접 편집 금지 (contract-change Skill 절차 필요. 단 S0는 라우팅·상태만)
❌ MVP 제외 항목 (Mobile/Spring/billing 등) 폴더에 새 파일 만들지 마라
❌ HARNESS_ROOT 결정을 사용자 없이 단독으로 하지 마라
❌ Sprint S1로 자동 진입하지 마라 (이번 세션은 S0만)

## 결과 보고 형식

S0 완료 후 다음을 보고:
1. HARNESS_ROOT 최종 경로
2. 생성된 폴더 14개 목록
3. PROJECT_STATE.md, PHASE_REGISTRY.md 변경 diff
4. sanity_end_S0.sh 출력 결과
5. git log (S0 commit hash)
6. 다음 세션 (S1) 진입 시 주의 사항

## 막힐 때

- HARNESS_ROOT 결정 못함 → 사용자에게 질문 (단독 결정 금지)
- 충돌 발견 → migration_procedure §8, §11.7의 9개 충돌 케이스 참조
- 절차 모호 → migration_procedure 본문 재읽기, 그래도 모호하면 사용자에게 질문
- sanity_end_S0.sh 실패 → 원인 보고, 단독 우회 금지

[복붙 끝]
```

---

## 6. 함정 / 주의사항

이전 세션에서 발견한 함정들. Claude Code가 반복하지 않게 명시.

### 6-1. 절차 함정

```
🚨 contract 직접 편집 충동
   contract-change Skill 절차 무시하고 docs/contracts/*.md 직접 수정 위험.
   → S0는 PROJECT_STATE, PHASE_REGISTRY, CLAUDE.md, AGENTS.md, instruction_index만 건드린다.
   → contract 본문은 S1, S3에서.

🚨 Sprint 자동 진행
   "S0 끝났으니 S1도 가자" 충동.
   → 각 Sprint마다 사용자 승인 필요. S0 commit + 보고 후 멈춘다.

🚨 9줄 stub 그대로 보존 시도
   GPT의 9줄 stub 16개를 "이미 작성됨"으로 착각 위험.
   → S0는 안 건드리지만, S3에서 8개 보강 + 8개 placeholder marker 변환.

🚨 active phase 두 개
   GPT 하네스가 Phase 1을 active로 표기. S0에서 Phase 0 active로 두고 Phase 1을 pending.
   → 한 번에 active는 1개만.
```

### 6-2. 결정 함정

```
🚨 HARNESS_ROOT를 캡스톤 폴더와 형제로 두지 마라
   캡스톤 SSAK-LOG와 혼동.
   → 완전히 별도 위치 권장.

🚨 .agents/.claude 분리 결정을 흔들지 마라
   이전 세션은 단일 .skills/ 결정이었음. 이번 세션에서 분리로 변경.
   migration_procedure §8 충돌 3 참조.

🚨 30 Phase 다 깊게 작성하려 들지 마라
   GPT 본인 원칙: 30개는 지도, active 1개만 깊게.
   → Phase 0만 깊게. 나머지는 골격만.
```

### 6-3. 토큰 함정

```
🚨 모든 산출물 한 번에 로드
   /mnt/user-data/outputs/ 전체 + GPT 하네스 전체 + migration_procedure 통째로 = 
   매우 큰 컨텍스트. S0는 사실 routes/state 파일만 필요.
   → S0 작업에 필요한 것만 선별 로드.

🚨 매 파일마다 raw read
   instruction_index/routes.yaml로 미리 묶음 처리 가능.
   → S0 끝나면 routes.yaml에 작업 유형별 묶음 등록.
```

---

## 7. Sprint S0 acceptance (검증)

S0 완료 = 다음 11개 모두 통과:

```
[ ] HARNESS_ROOT 설정 + git repo 초기화 + 첫 commit
[ ] GPT 하네스 155 파일 복제 완료
[ ] .migration_source/에 우리 deliverables 보관 완료
[ ] 누락 폴더 14개 생성 + 각 README.md 표준 형식
[ ] PROJECT_STATE.md 갱신 (confirmed_decisions 25개, migration_progress 필드)
[ ] PHASE_REGISTRY.md 갱신 (Phase 0 active, Phase 1 pending, Phase 2-3 Discovery+Quick)
[ ] phases/active/phase-0-migration/ 폴더 + 5 파일 생성
[ ] CLAUDE.md, AGENTS.md 갱신 (신규 Skill 3개 라우팅)
[ ] instruction_index/ 3 yaml 갱신
[ ] sanity_start.sh + sanity_end_S0.sh 작성
[ ] sanity_end_S0.sh 실행 결과 모두 PASS
[ ] git commit: "harness: integrate GPT skeleton + routing decisions (S0)"
```

---

## 8. 다음 세션 진입 (Sprint S1)

S0 완료 후 사용자가 Claude Code 또는 다른 세션을 새로 시작할 때:

```
첫 단계:
1. PROJECT_STATE.md 읽기 → migration_progress 확인
2. 이 핸드오프 (handoff_to_claude_code_sprint_S0.md) 다시 읽기
3. migration_procedure.md §S1 (Sprint 1) 섹션 참조

S1 작업 미리보기:
- apps/web/design.md 교체 (GPT 163 → 우리 688)
- docs/contracts/db_schema.md 교체 (GPT 80 → 우리 580)
- ai_system/prompts/prompt_registry.md 교체 (GPT 8 → 우리 628)
- apps/web/page_map.md, component_map.md 갱신
```

다음 세션은 Claude Code 또는 Codex 중 선택 가능. 권장: Claude Code (콘텐츠 정합성 필요한 작업).

---

## 9. 막힐 때 사용자에게 묻기

다음은 단독 결정 금지. 사용자에게 명시적 확인:

```
1. HARNESS_ROOT 최종 경로
2. 기존 폴더 덮어쓰기 vs 새 폴더 선택
3. git remote (origin) 설정 여부
4. sanity 스크립트의 추가 점검 항목
5. S0 commit 메시지 형식 변경 (관례 다를 시)
6. Sprint S1 진입 여부 (자동 진행 금지)
```

질문 형식 예시:
```
"HARNESS_ROOT를 다음 중 하나로 설정해도 됩니까?
 A) ~/projects/video-planning-agent (권장)
 B) ~/dev/video-planning-agent
 C) 다른 경로 (입력해주세요)"
```

---

## 10. 종료 후 사용자 액션

S0 완료 후 사용자가 다음 세션 전에 할 일:

```
1. Claude Code의 S0 결과 검토 (HARNESS_ROOT, 폴더 14개, commit)
2. sanity_end_S0.sh 결과 확인
3. 미해결 질문 있으면 답하기
4. S1 진입 시점 결정 (즉시 / 잠시 후 / 별도 세션)
5. (선택) git remote 연결 + push
```

---

## 부록 A. 산출물 zip 번들

이 핸드오프와 함께 모든 deliverables를 zip 하나로 묶어 전달:

```
/mnt/user-data/outputs/handoff_package.zip 포함:
  - handoff_to_claude_code_sprint_S0.md  (이 문서)
  - migration_procedure.md  (v1.1.0)
  - design.md
  - db_schema.md
  - prompt_registry.md
  - agent_html_spec.md
  - skills/ (전체, INDEX.md + 14 SKILL.md)
```

Claude Code에 zip 통째로 첨부하면 됨.

---

## 부록 B. 이번 세션에서 결정 못한 것 (S0 진입 전 사용자 결정 필요)

```
1. HARNESS_ROOT 최종 경로
2. git remote (있으면 어디로)
3. design.md 7개 Open Questions (시급 안 함, Phase 1~2 진입 전까지)
4. db_schema.md 6개 Open Questions (시급 안 함, Phase 4~7 전까지)
5. prompt_registry.md 6개 Open Questions (시급 안 함, Phase 5~6 전까지)
```

S0 작업 자체는 위 결정 없이도 가능. 단 1, 2번은 S0 시작 직전 결정.

---

## 부록 C. 이번 세션 누적 요약 (Claude Code 이해용)

```
세션 1 (이전): design.md, db_schema.md, prompt_registry.md 작성
세션 2 (이전): 14 Skill 작성, agent_html_spec 작성
세션 3 (이번): 
  - GPT 하네스 객관적 검토 (5/10 점수)
  - migration_procedure v1.0 작성 (10 섹션)
  - 자체 검토 → 7개 갭 발견
  - v1.1.0 보강 (11 섹션, 1337줄)
  - 이 핸드오프 작성

총 누적 산출물: ~9,400줄 (this handoff 제외)
총 세션 토큰 추정: ~250K~350K (모든 세션 합산)
```

---

## 변경 이력

```
v1.0.0 (2026-01-XX): Claude 채팅 세션에서 작성. Sprint S0 진입용 핸드오프.
```
