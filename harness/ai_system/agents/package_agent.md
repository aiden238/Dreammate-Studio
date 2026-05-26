# package_agent.md

> ⚠️ **PLACEHOLDER** — 본 agent는 향후 Phase에서 채워질 예정.
> 현재는 스코프와 트리거만 명시. 정상 agent로 사용 금지.

## Status

```yaml
status: placeholder
fill_in_phase: 11+
priority: low
estimated_final_lines: 150
last_updated: 2026-05-26
```

## Why Placeholder?

MVP(Phase 0~10)는 plan_options 저장 + UI 노출만 수행한다. API `/select`(api_contract)가 선택된 plan을 video_projects에 연결하는 것으로 흐름이 종료되며, 결과 패키징/문서화/원클릭 발전 단계는 필요 없다.

영상 제작 단계(스크립트, 콘티, 촬영 가이드)는 MVP non-goals(`docs/contracts/mvp_non_goals.md`)이며, Package Agent는 Phase 11+ 후속 단계가 활성화될 때 분리 검토한다.

## Scope (when filled in)

- 영상기획안 PDF / 슬라이드 자동 변환 (Discovery 5단계 + plan 결과 통합)
- 외부 시스템 export (Google Slides, Notion, PPTX)
- 협업 워크플로 통합 (Slack/Notion 자동 공유)
- 결과 패키징 metadata (생성 시점, 사용 모델, prompt_version 명세)
- 사용자별 템플릿 (브랜드 로고/색상 자동 적용)
- 다국어 export (Phase 21+)
- 원클릭 발전 단계 트리거 (script generation, storyboard prompt)

## Input/Output (when filled in)

- Input: video_projects 최종 plan + selected_context + brand_memory
- Output: 파일 URL (S3/Supabase Storage) + metadata
- Envelope: agent_io_contract §2 공통 envelope 따름

## Known Dependencies (when filled in)

- `docs/contracts/api_contract.md` (/select, /export endpoint)
- `docs/contracts/data_contract.md` (placeholder, export 데이터 정합성)
- `docs/contracts/db_schema.md` (video_projects, plan_options 읽기)
- `docs/contracts/output_schema.md` §8 (P-006 plan 구조)
- `docs/contracts/llm_security_contract.md` (export 시 PII 마스킹)
- `docs/contracts/privacy_contract.md` (외부 export 동의)
- Supabase Storage (파일 보관)

## Fill-In Trigger

- Phase 11+ 진입
- 또는 사용자 요청 누적 (export 기능 요구) 임계 도달
- 또는 영상 제작 후속 단계(script/storyboard) 활성화 시점

## Related Skill / Phase

- Skill: `ai-architecture-review`
- Phase: 11+
- 책임자: AI(초안) + 사용자(검토)
