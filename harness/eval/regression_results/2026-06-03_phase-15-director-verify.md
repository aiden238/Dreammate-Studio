# Phase 15 director 라이브 검증 + 회귀 결과

> 2026-06-03 | phase-complete (S6). director = output_mode 3rd tier.

## 자동 게이트
| 게이트 | 결과 |
|---|---|
| pytest (backend) | **536 passed** (Phase 14 508 + S1 14 + S2 5 + S3 4 + S4 5; 기존 508 수정 0 = compact/rich byte-identical) |
| 프론트 typecheck / lint / build | PASS (12 routes) |
| scenario_simulation.ps1 (P-X2) | **36/36 PASS** |
| 키 commit | 0 |

## director 라이브 API 검증 (실 LLM, OUTPUT_MODE=director)
입력(영상 표현): `대학생활 꿀팁을 알려주는 30초 정보형 쇼츠 영상` → `POST /api/v1/generate`:
```
director 슬롯 전부 채워짐:
  hook_system: 2개 (첫 후크 + 재후크)
  retention_architecture: 채워짐 (이탈 예상 + 호기심 갭/페이싱)
  scene_breakdown: 2 씬, 각 5필드(scene_intent/viewer_emotion/retention_device/why_this_works/fallback_scene)
critic: 10차원 (retention_design 포함)
rich 12슬롯도 계승 채움.
```
→ director 출력 end-to-end 동작 (프롬프트 라우팅 + Plan 구성 read + 직렬화 + critic 10차원).

## ★ 발견·수정 (라이브 검증 가치)
1. **Intent 오반려**(맨 토픽 "대학생활 TIP" → INV-001) — 별개 UX 이슈, 후속 작업(별도).
2. **director Plan-read wiring 누락**(핵심 버그): generate.py + moa_orchestrator(×2)가 LLM dict 에서 rich 는 읽지만 director 3필드는 안 읽어 항상 빈 채로 출력 → director read 추가로 수정(fix ce6cf99). (보조: director 프롬프트 강화 + max_tokens 3500.)

## 깊이/품질 (정직)
- director 슬롯 **구조적 충족** 확인(슬롯 채워짐 + critic 10차원). ★ **사용자 피드백**: director 출력은 **초안 수준(기획 브리프)** — 이대로 완성 대본을 쓰기엔 부족. = 제품 경계(product_boundary, "기획 브리프") 부합. 깊이/품질 보강은 이후 phase(commercial_viral + PKM/RAG 데이터레이어).
- 정밀 depth 점수/anchor 채점은 실 LLM 표본 확대 + human review(로드맵 ②)에서.

## 결론
- Phase 15 director **완료·검증**. compact/rich byte-identical(536) + director 라이브 동작 + 신규 endpoint 0 + 키 0.
- 후속: ① Intent 오반려 개선 ② 검증 보강(human review) ③ PKM/RAG → commercial_viral (director 품질 보강).
