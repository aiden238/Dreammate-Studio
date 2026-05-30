# domain_brief — podcast_episode_planning_ai (WITH 입력)

> 위치: `harness/meta_factory/outputs/TEST/podcast/domain_brief.md`
> 상태: Phase M1 (Meta-Factory Sample Test) Slice S1 — generation dry-run **입력 명세**
> 형식: `meta_factory/domain_brief_schema.md` (11 필드)
> ★ dry-run 테스트 자료 — active 하네스 아님 (outputs/TEST/ 격리, factory_contract 규칙 3/7)
> ★ 자격증명/API 키 없음 — placeholder 만.

---

## 0. 이 문서의 위치

`domain_brief_schema.md` 형식을 그대로 따라 작성한 **팟캐스트 에피소드 기획 AI** 도메인 입력 명세.
generation_workflow 단계 1(domain_brief 수집)의 산출. 단계 2~11 이 이 brief 를 입력으로 harness_blueprint 를 설계한다.

도메인은 Dreammate(영상기획)와 **인접하지만 다른** 도메인이다:
- 공통: 브랜드/타깃/톤/후킹/시리즈/에피소드 기획.
- 차이: 시각자료→대화흐름, 썸네일→오프닝 멘트·질문 설계, 영상 flow→오디오 segment, 게스트 브리프/쇼노트.

---

## 1. domain_brief (schema 11 필드 — YAML)

```yaml
domain_name: podcast_episode_planning_ai
domain_summary: "팟캐스트를 제작하는 것이 아니라 팟캐스트 에피소드를 기획하는 것을 돕는 AI 에이전트 (오디오 대화 흐름 + 오프닝 후킹 + 게스트 브리프 + 쇼노트 중심)"

target_users:
  - 1인 팟캐스터 (호스트 겸 PD)
  - 소규모 제작팀 (호스트 + 작가/PD 1~2명)
  - 브랜드 팟캐스트 운영 마케터

primary_tasks:
  - 의도 분석 (시리즈 신규 컨셉 / 단발 에피소드 자동 분기 — Discovery / Quick 대응)
  - 부족 정보 질문 (게스트 유무 / 포맷(인터뷰·솔로·패널) / 회차 위치 등)
  - 에피소드 기획안 3개 생성 (각: 주제 앵글 + 오디오 segment 흐름 + 오프닝 후킹 멘트)
  - 게스트 브리프 + 인터뷰 질문 리스트 생성 (게스트 모드일 때)
  - 쇼노트 + 에피소드 제목 후보 생성
  - Critic 검증 + revise (최대 2회 — 후킹 강도/대화 흐름 자연스러움 중심)
  - 결과 저장 + 사용자 피드백 (Show Memory 추출은 후속 phase)

output_artifacts:
  - 에피소드 기획안 (episode_plan_candidates 3개 — angle + segment_flow[] + opening_hook)
  - 게스트 브리프 (guest_brief — 소개/섭외 각도/사전 질문)
  - 인터뷰 질문 리스트 (question_list — 진부도 회피 표시)
  - 쇼노트 + 제목 후보 (shownotes + title_candidates)
  - Critic 평가 (canonical overall_score + dimensions)
  - 선택/피드백 기록

runtime_type: product_saas        # FastAPI/Next/DB 런타임을 갖는 제품 SaaS (Dreammate 와 동형)

risk_level: medium                # PII(사용자 입력/게스트 인물정보/피드백) + LLM 비용. high 아님(민감 카테고리 데이터 비저장 가정)

required_contracts:
  - agent_io_contract             # MOA agent 입출력/실행 정책 (intent/planning/critic/rewriter + guest/shownotes)
  - output_schema                 # Envelope / EpisodePlan / GuestBrief / QuestionList / Shownotes / Critic 본문
  - db_schema                     # 데이터 계층 (User→Brand→Show→Season→Episode + guests + plans + feedback)
  - llm_security                  # PII 마스킹(게스트 인물정보) + prompt injection 차단

required_evals:
  - golden_set                    # 회귀 케이스 (PE-001~ : 솔로/인터뷰/패널/시리즈오프닝/단발)
  - regression_eval               # mock-deterministic CI 회귀
  - podcast_planning_eval         # 도메인 채점 차원 (후킹/대화흐름/질문품질 등)
  - human_review_rubric           # 사람 검토 (오프닝 후킹/게스트 적절성 정성 판단)

forbidden_scope:                  # ★ 필수 — 이 하네스가 하지 않는 것 (scope creep 차단)
  - 오디오 녹음/편집/믹싱            # 제작 영역 영구 제외 (Dreammate 의 "영상 자동 편집 제외" 대응)
  - TTS/음성합성으로 실제 오디오 생성  # 기획 AI 이지 음성 생성 AI 아님
  - 게스트 실제 섭외/연락 (이메일·DM 자동 발송)  # 사람 행위 — AI 가 외부 액션 금지
  - 음원 배포/RSS·플랫폼 업로드 자동화  # 퍼블리싱 영역 제외
  - 자동 promotion (사람 검토 없이 RAG/Memory 승격)  # rag-update 5단계 경유 (factory_contract 규칙 8)
  - Show Memory 자동 추출            # 후속 phase (Dreammate Brand Memory Phase 10+ 대응)

preferred_architecture_patterns:  # architecture_patterns.md 6 패턴에서만 선택
  - supervisor                    # orchestrator 중개 (agent 격리)
  - fan_out_fan_in                # 기획안 3개 parallel 생성
  - producer_reviewer             # Planner → Critic → Rewriter (revise max 2)
  - pipeline                      # Intent → (RAG) → Planning → Guest/Question → Shownotes → Critic → Save
  - expert_pool                   # ★ 후보 — 포맷별(인터뷰/솔로/패널) 전문 생성 라우팅 (Dreammate 엔 없던 패턴, GAP 관찰점)

# ★ M2 G-fix 적용 (G6 — domain_brief_schema §1.2 data_model 선택 필드). M1 §2 별도 섹션 우회 → schema 안 1급 필드로 수용:
data_model:                       # (선택 필드 — §2 prose 와 동일 내용을 schema 형식으로 표현)
  hierarchy: "User → Brand → Show → Season → Episode"   # Dreammate User→Brand→Domain→Series→Video 대응
  entities: [User, Brand, Show, Season, Episode, Guest, EpisodePlan, Feedback]
  pii:                            # 각 엔티티 PII 표시 (제3자 PII 포함 — §1.1 risk 상향 트리거와 연결)
    User: 사용자 PII (계정/입력/피드백)
    Guest: ★ 제3자(비사용자) PII — 이름·소속·발언·섭외메모 (동의·노출 책임 ↑, risk 상향 트리거)
    Feedback: 사용자 PII (좋아요/수정 요청)
```

---

## 2. 데이터 계층 (User → Brand → Show → Season → Episode)

```
User              사용자 계정
 └─ Brand         브랜드/채널 정체성 (톤·타깃·금지표현) — Dreammate Brand 계층 대응
     └─ Show      팟캐스트 쇼 (포맷 기본값·진행자·평균 길이)
         └─ Season  시즌 (선택 — 시즌별 테마)
             └─ Episode  에피소드 (주제·포맷·게스트·segment_flow·shownotes)
                 ├─ Guest        게스트 인물정보 (PII — 마스킹 대상)
                 ├─ EpisodePlan  기획안 후보 (3개 → 1개 선택)
                 └─ Feedback     사용자 피드백 (좋아요/수정 요청)
```

- Dreammate 4계층(User→Brand→Domain→Series→Video) 대비: `Domain`→`Show`, `Series`→`Season`, `Video`→`Episode` 로 매핑되며 **Guest** 가 신규 엔티티(영상기획엔 없음).

---

## 3. 핵심 흐름

```
사용자 입력 (에피소드 아이디어 or 시리즈 컨셉)
  → 의도 분석 (시리즈 신규 / 단발 자동 분기 + Intent Filter)
  → 부족 정보 질문 (게스트·포맷·회차 위치)
  → 한 줄 기획 방향 승인
  → (RAG: 과거 에피소드/유사 쇼 참고 — graceful skip)
  → 에피소드 기획안 3개 생성 (parallel)
  → [게스트 모드] 게스트 브리프 + 질문 리스트
  → 쇼노트 + 제목 후보
  → Critic 검증 (후킹/대화흐름/질문품질) → revise 최대 2회
  → 결과 저장 → 사용자 피드백 저장
```

---

## 4. 필요한 agent / skill / contract / eval 후보

| 종류 | 후보 | 비고 |
|---|---|---|
| agent | intent, planning, guest_brief, question, shownotes, critic, rewriter | Dreammate 4 → 7 (guest/question/shownotes 신규) |
| skill | podcast-eval-run (또는 기존 eval-run 재사용), contract-change(재사용), 그 외 절차 Skill 재사용 | ★ 대부분 기존 Skill 재사용 가능성 — S2 with-without 검토 대상 |
| contract | agent_io_contract, output_schema, db_schema, llm_security | §1 required_contracts |
| eval | golden_set, regression_eval, podcast_planning_eval, human_review_rubric | §1 required_evals |

> ★ 후보는 단계 2~7 에서 harness_blueprint 로 구조화된다 (다음 파일).

---

## 5. 작성 규칙 점검 (domain_brief_schema §3)

1. ✅ forbidden_scope 필수 — 6 항목 명시 (오디오 제작/TTS/게스트 섭외/배포/자동 promotion/Show Memory).
2. risk_level: medium → human_review 권장 (required_evals 에 human_review_rubric 포함). high 아니므로 security-review 필수 아님(단 llm_security contract 는 PII 위해 포함).
3. runtime_type: product_saas → contract/eval 최소 아님(런타임 contract 필요) — 충족.
4. ✅ preferred_architecture_patterns 는 6 패턴에서만 선택 (supervisor/fan_out_fan_in/producer_reviewer/pipeline + expert_pool 후보).
5. ✅ 사람이 작성 (meta_factory 자동 생성 아님).

---

## §M2. M2 G-fix 적용 시연 (G5·G6 — additive, S3 re-validate)

> ★ M1 원본(`risk_level: medium`, §2 데이터 계층 prose)은 그대로 보존하고, S1 이 domain_brief_schema 에 반영한 개선 슬롯을 추가 적용한 시연.

- **G6 (data_model 1급 필드)**: M1 은 데이터 계층을 schema 11필드 **밖** §2 별도 prose 섹션으로 우회했다. M2 는 domain_brief_schema §1.2 의 `data_model` 선택 필드(hierarchy/entities/pii)로 동일 내용을 schema 안에 표현 — 위 YAML `data_model` 블록. (해소: expressible → addressed)
- **G5 (제3자 PII risk 상향 트리거)**: M1 은 `risk_level: medium` 에 머물러 게스트(제3자) PII 위험을 미반영(미해결 표기)했다. M2 는 domain_brief_schema §1.1 의 **제3자 PII 상향 트리거**를 적용한다:
  - `data_model.pii.Guest` 가 **제3자(비사용자) PII** 로 표시됨 → 상향 트리거 발동 조건 충족.
  - **재판정**: 기존 `medium` 은 사용자 PII 만 가정한 등급. 게스트 제3자 PII(동의·노출 책임 ↑)가 추가되므로 **`medium → high` 상향 후보**로 명시 판정 가능 (M1 의 "high 재검토 여지" 수동 표기를 schema 트리거로 대체). high 상향 시 required_evals 에 security-review 강제(factory_contract 규칙 8) 경로 연결.
  - ★ 본 dry-run 은 risk_level 원본값(medium)을 보존하되, **상향 판정이 이제 schema 축으로 표현·도출 가능**해졌음을 시연 (해소: 안전 risk 가 사전 판정 가능).

---

이 domain_brief 는 meta_factory machinery(domain_brief_schema)를 참조하여 작성됨 (WITH arm). [+ M2 S3: G5/G6 개선 슬롯 적용 시연 (additive)]
