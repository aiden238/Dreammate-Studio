# Session Handoff — Phase 13 출력 확장 (Output Enrichment)

> 작성: 2026-06-03 (세션 롤 준비 — 새 채팅에서 S4부터 재개)
> ★ canonical 은 PROJECT_STATE.md / PHASE_REGISTRY.md / `phases/active/phase-13-output-enrichment/` (entry 8파일). 본 문서는 "지금 어디·다음 무엇·gotcha" 요약.
> origin/main = **339da50**, 로컬=원격 동기 clean. pytest **493 passed**.

---

## 0. 새 세션 첫 행동 (재개 절차)
1. `PROJECT_STATE.md` 상단(line 8 "최신 = Phase 13 ... 다음=S4") + line 57~ Phase 13 슬라이스 블록 읽기.
2. `phases/active/phase-13-output-enrichment/` scope.md / acceptance.md / multi_slice_plan.md 읽기.
3. 본 handoff 읽기.
4. **S4 (Critic depth)** 진행. (첫 메시지 예: "Phase 13 S4(Critic depth) 진행, 서브에이전트 활용")

---

## 1. Phase 13 한 줄
Phase 12가 실측한 **깊이 격차(compact 0.231 vs rich 1.000, 4.3x)** 를 운영 출력에 반영 — compact 7필드 → rich(후크변형·타임코드·화면·대사·자막·샷·썸네일·제목·CTA·레퍼런스·길이변형·타깃·톤). ★ **이 프로젝트 첫 의도적 출력 변경** → **gated 단계 롤아웃**(`rich_output_enabled` default **False** → 검증 후 ON) + **additive 스키마**(rich 슬롯 전부 Optional → OFF byte-identical). 범위=풀(backend+frontend). 제품경계=기획 브리프(완성 대본/제작 아님).

## 2. 6 슬라이스 / 진행
| Slice | 내용 | 상태 |
|---|---|---|
| S1 | `Plan`/`PlanFlowBeat` rich 12슬롯 Optional additive + `model_dump_compact()` + `PLAN_RICH_FIELDS`/`BEAT_RICH_FIELDS` (CC-012, output_schema v1.2.0) | ✅ 1665dc0 |
| S2 | `RICH_SYSTEM_PROMPT`(JSON 키=스키마 필드 정확 일치) + `_build_rich_system_prompt_with_hint` + P-006 v1.1.0 (CC-013, gated 공존) | ✅ ed1cf1f |
| S3 | gated wiring: `rich_output_enabled` + 프롬프트/직렬화 분기 (OFF byte-identical / ON rich) (CC-014) | ✅ 339da50 |
| **S4** | **Critic depth 반영** (depth_actionability 차원 → "88점 함정" 해소: 얕으면 감점), P-007 bump, gated 정합 | ⬜ **다음** |
| S5 | **frontend** PlanCard rich 렌더 (후크변형/타임코드/대사/자막/샷/썸네일/제목/길이) — ★ 이거 해야 /generate **화면**이 rich로 보임 | ⬜ |
| S6 | cost 재조정(B-RES-1) + golden_set **depth 재측정(목표 ≥0.8)** + flag ON 라이브 데모 + phase-complete | ⬜ |

## 3. 핵심 설계 (S4+ 가 알아야 할 것)
- **flag**: `settings.rich_output_enabled`(config.py, default False, env `RICH_OUTPUT_ENABLED`).
- **스키마**: rich 슬롯 = `PLAN_RICH_FIELDS`(9) + `BEAT_RICH_FIELDS`(3), 전부 Optional. OFF 직렬화 = `Plan.model_dump_compact()` (rich 제외 → byte-identical).
- **프롬프트**: ON=`RICH_SYSTEM_PROMPT`/`_build_rich_system_prompt_with_hint` (P-006 v1.1.0) / OFF=`SYSTEM_PROMPT`/`_build_system_prompt_with_hint` (v1.0.0). 둘 다 보존(deprecate 아님).
- **직렬화 헬퍼**: `schemas/output.py::envelope_to_response_dict(envelope, plans, *, rich_enabled)` — OFF면 plan_candidates 를 model_dump_compact 로 교체.
- **응답 경로 2개**:
  - `/generate` (단일, routers/generate.py, response_model=Envelope): ON=return envelope / OFF=JSONResponse(compact)+`X-API-Deprecation` header.
  - `/plans/{id}/generate` (3안, moa_orchestrator → plans.py thin adapter): orchestrator 가 `plan_entry["envelope"]`에 OFF면 compact dict 저장. ★ POST 라우트 response_model 미지정이라 Envelope 직접 반환 시 rich Optional 누수 → plans.py 가 OFF live-POST 를 stored compact dict 의 JSONResponse 로 반환해 차단. GET /plans/{id} 도 stored dict.
- **라이브 입증됨**: flag ON + 실 gpt-4o-mini → run_planning 이 rich 12슬롯 채움(hook_variants 2개/visual/thumbnail 등). OFF → rich 키 0.

## 4. S4 설계 힌트 (Critic depth)
- `agents/critic.py` (P-007) 에 **depth_actionability** 평가 차원 additive 추가 — eval rubric(video_planning_eval §2.A.1, CC-011) 정의와 정합. "얕은 compact 가 88점" 문제 해소(깊이 낮으면 overall 감점).
- ★ **gated 정합**: rich_output_enabled OFF 일 때 Critic 동작/점수 **불변**(기존 회귀 0) — depth 차원은 ON 경로(rich plan)에서만 의미. 기존 Critic canonical(overall_score+dimensions) 스키마는 additive 유지.
- prompt-version-review 경유(P-007 semver bump) + golden_set 회귀. normalize_to_canonical 호환 확인.
- ★ behavior-preserving: 기존 critic test 0 수정(또는 의도된 version assert delta만).

## 5. Gotcha (필수)
- ★ **OFF byte-identical = 절대 게이트**: 기존 **493 테스트가 OFF default 회귀 증거**. 깨지면 설계 잘못 → 수정. 신규는 ON 경로/additive 만.
- **slice 단위 = sub-agent + P-X1 §SELF-VERIFICATION**(git diff/forbidden area/revert) + 매 slice 후 commit+push.
- **push 전 키 점검**: `git diff origin/main..HEAD | grep -oE "sk-proj-...|sk-ant-api03-...|AIza..."` = 0 필수. 키는 `.env`(gitignore)에만.
- **.env 로딩**: config `env_file=".env"` = CWD-상대. 스크립트로 실 LLM 호출 시 `backend/fastapi/.env` 를 os.environ 에 먼저 주입(런처 패턴, Temp/run_local_backend.py 참조).
- **cp949 콘솔**: Windows 콘솔 출력에 em-dash/이모지 → UnicodeEncodeError. `PYTHONIOENCODING=utf-8` + ASCII.
- **config get_settings() lru_cache**: 테스트/스크립트 flag override = `monkeypatch.setenv` 또는 `os.environ[...]` 후 `get_settings.cache_clear()`.
- **LF→CRLF 경고**: 정보성(무시 가능).
- **frontend**: `apps/web` (Next.js 14, PlanCard). S5 전까지 건드리지 말 것. design.md 기준 design-review.
- **로컬 서버**: 이전 세션이 백엔드(:8000)/프론트(:3000) 백그라운드 기동(구 코드). 새 세션은 필요 시 재기동(`Temp/run_local_backend.py` + `cd apps/web && npm run dev`). rich 화면 확인은 S5 후 + `RICH_OUTPUT_ENABLED=true`.

## 6. baseline / 참조
- pytest **493** / origin **339da50** / Skill 21 / agent 6.
- 참조: `phases/active/phase-13-output-enrichment/` (entry), `docs/contract_changes/2026-06-02_phase-13-*.md` (CC-012/013/014), `eval/regression_results/2026-06-02_phase-12-s2-s3-depth-gap.md` (깊이 격차 근거), `eval/human_review/2026-06-02_phase-12-s4-review-kit.md` (사용자 채점 대기, optional).
- B안(Phase 11) 비차단 잔여(cost_control 재조정 등)는 Phase 13 S6 에 흡수 예정 (dependencies.md §B안 잔여).
