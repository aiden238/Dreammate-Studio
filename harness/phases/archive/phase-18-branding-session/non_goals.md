# Phase 18 — Non-Goals

```
✗ Quick/Discovery 대체 — 세 번째 진입(보완)일 뿐, 기존 무변경.
✗ 정통 예/아니오 20고개 고정 — 적응형 LLM(N고개 상한 내) + 카드+자유입력.
✗ brand_memory 자동 승격 — 브랜딩 방향도 후보/제안까지(ADR-031 NG12 계승, 확정 후 적재).
✗ output_schema/planning/critic 변경 — 입력(주제·방향) 생성까지만, 그 뒤 기존 3안 생성 흐름.
✗ 영상 제작 — product_boundary 영구 계승.
✗ 2nd brain 시각화 — Phase 19~20(별도).
```

## 회피할 함정
- scope creep: 본 phase = 주제 발굴 + 방향 제안 + planning 연결까지. 브랜드 관리 UI/2nd brain 은 별도.
- LLM 질문 루프 비용/지연: N고개 상한 + 카드 짧은 응답 + workhorse 모델.
- 회귀: 기존 진입(Quick/Discovery) byte-identical.
