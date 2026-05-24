# architecture.md

```text
사용자 입력 → Intent Agent → 부족 정보 질문 → 한 줄 방향 승인 → LLM Wiki → RAG → Planner Agent → Critic Agent → Rewriter Agent → Package Agent → 저장/피드백
```

MVP는 Intent, Planner, Critic, Rewriter, RAG Lite, Output Schema 검증에 집중한다.
