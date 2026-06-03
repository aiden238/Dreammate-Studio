# Phase 16 — Non-Goals (명시적 제외)

```
✗ 실 PKM/RAG Orchestrator 빌드 — 본 페이즈는 "시뮬 fixture 주입의 효과"만 측정.
  실 orchestrator(6 scope/BM25/instruction/trend 수집)는 verdict가 GO일 때 후속 Phase.
✗ 실사용자 데이터 / 실 누적 — compounding은 시뮬 페르소나 proxy. 실 데이터 moat는 별도 숙제(기획안 §5.1).
✗ commercial_viral 모드 — PKM/RAG 결과에 종속, 이 페이즈 범위 밖.
✗ 운영 default 경로 변경 — Arm A = 현재 use_rag=False 경로 byte-identical. rich/director default 전환 무관.
✗ 신규 endpoint / 신규 agent / migration — 실험은 기존 플래그 토글 + eval 영역 additive만.
✗ 영상 제작 기능 — product_boundary 영구 non-goal 계승.
✗ go/no-go 임계값을 코드로 강제 — 임계값은 multi-llm-validation으로 확정, 측정은 숫자만 산출.
```

## 회피할 함정 (기획안 §9 리스크)

- **기획 무한루프**: 이 페이즈는 문서가 아니라 **go/no-go 숫자**를 내야 끝난다.
- **시뮬 과적합**: 시뮬 PKM ↔ 채점 케이스 분리 + 사람 blind 교차확인.
- **통제 깨짐**: output_mode/모델/프롬프트/temp 전부 고정 — 단일 변수 강제.
- **하류 페이즈 조기 재정립**: PKM/RAG provisional은 verdict 후에만 실 번호 배정.
