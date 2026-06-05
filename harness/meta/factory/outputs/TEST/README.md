# meta_factory/outputs/TEST/ — Sample Test 샌드박스 (Phase M1)

> ★ 이 폴더의 **모든 산출물은 dry-run 테스트 자료**다. **active 하네스 아님.**

## 무엇인가
- Phase M1 (Meta-Factory Sample Test) 의 **팟캐스트 에피소드 기획 AI** 도메인 dry-run 산출물 **전용** 폴더.
- meta_factory machinery(generation_workflow 11단계 + validation_workflow 6검증)가 실제로 도는지 1회 검증하기 위한 샘플.
- 실 생성 산출 영역(`outputs/generated_harnesses/`, `outputs/improvement_reports/`)과 **분리** — 테스트 자료가 실 산출물과 섞이지 않도록 격리.

## 규칙
- **proposal-first**: validation_workflow 6검증 통과 + 사용자 승인 전까지 active 전환 금지 (factory_contract 규칙 7).
- ★ 이 폴더 **외부**(런타임 L1 / 기존 하네스 L2) 변경 **0줄** (A9 + MG1 — dry-run sub-agent 는 `outputs/TEST/**` 에만 쓴다).
- 첫 dry-run 은 fail/pending 이 정상 — 목적은 **GAP 발견**.

## 구조
```
TEST/
├── README.md                          (본 문서)
├── podcast/                           생성된 팟캐스트 harness
│   ├── _without_baseline.md           without 팔 — machinery 미참조 일반 프롬프트 결과
│   ├── domain_brief.md                with 입력 — domain_brief_schema 형식
│   ├── harness_blueprint.md           with 출력 — harness_blueprint_schema 형식 (+ validation 3필드)
│   └── scaffolds/
│       └── {agent,skill,contract,eval,phase,project_state}_draft.md
└── sample_test_podcast_validation.md  6검증(PASS/FAIL/PENDING/GAP) + with/without 6지표 + 5gaps 재현 + GAP + 제안
```
