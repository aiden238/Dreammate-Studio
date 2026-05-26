# orchestration_strategy.md — 오케스트레이션 전략 결정 기록 (ADR)

> 위치: `docs/decisions/orchestration_strategy.md`
> 상태: Phase 0 Sprint S5 deep 작성
> 참조: `ai_system/orchestration/moa_policy.md`, `ai_system/orchestration/flow.md`, `docs/contracts/agent_io_contract.md`

---

## 0. 본 문서의 위치

본 ADR은 MOA Lite (4 agent) 채택 결정, agent 협력 모델, 비동기 처리 도입 시점, MCP 통합 후보에 대한 기록이다.

---

## 1. 결정 요약

```
MVP (Phase 1-10):        MOA Lite (Intent → Planning → Critic → Rewriter)
                         동기 처리 + SSE progress stepper
                         revise_round 최대 2회 (무한 루프 차단)
Phase 11-20:             비동기 처리 도입 (Celery / Arq) 검토
                         MCP server 분리 검토 (각 agent를 독립 MCP로)
Phase 21+:               멀티 provider routing (OpenAI / Anthropic / Gemini)
                         자체 모델 fine-tune 검토
```

---

## 2. 대안 비교

| 방식 | 장점 | 단점 | 채택 |
|------|------|------|------|
| **MOA Lite (4 agent)** | 단순, 디버깅 쉬움, 비용 낮음 | 복잡한 분기 어려움 | **MVP** |
| LangGraph | DAG 기반, 시각화 좋음 | 학습 곡선, lock-in | Phase 11+ 검토 |
| AutoGen | 자율 대화 기반 | 비용 폭증 위험 | 부적합 |
| MCP 분리 | 표준 인터페이스, 재사용 | 셋업 부담 | Phase 11+ |
| 단일 거대 prompt | 가장 단순 | 품질 한계, 디버깅 불가 | 부적합 |

---

## 3. 선택 이유

- **단순성**: 4 agent는 사람이 추적 가능한 최대 복잡도
- **비용**: gpt-4o-mini 기본 + Critic만 gpt-4o → 사용자당 월 $5 이하 달성 가능
- **품질**: Critic의 8차원 검증으로 단일 LLM 대비 명백한 품질 향상
- **확장 여지**: Phase 11+에서 LangGraph / MCP로 마이그레이션 가능 (envelope 구조 유지 시)

---

## 4. 트레이드오프

- 동기 처리 → 30-60초 사용자 대기 (4단계 progress stepper로 완화)
- 4 agent 고정 → 새로운 패턴 (예: 멀티 Critic) 도입 시 구조 변경 필요
- gpt-4o-mini 의존 → OpenAI 장애 시 전체 정지 (fallback_policy로 완화)

---

## 5. 핵심 정책

### 5.1 revise_round 무한 루프 차단
- server-side count, 2회 도달 시 강제 approve + 사용자 안내
- error_response_contract E-LLM-010 "AI 개선이 한계에 도달했어요"

### 5.2 agent 간 데이터 전달
- envelope 구조 (output_schema §2): `meta` + `body` + `validation`
- 직접 prompt 결합 금지, 항상 schema 검증

### 5.3 실패 격리 (fallback_policy 연동)
- Intent 실패 → 기본 가정 + 사용자 경고
- Planning 실패 → 1회 재시도 → 캐시된 일반 템플릿
- Critic 실패 → 자동 approve + 안내
- Rewriter 실패 → 원본 plan 유지

---

## 6. 재검토 트리거

- 사용자 만족도 70% 미만 → agent 추가/재배치 검토
- Critic 8차원 평균 점수 정체 → multi-Critic 또는 self-consistency 도입
- 응답 시간 p95 > 60초 → 비동기 처리 즉시 도입
- MCP 생태계 성숙 (Phase 11+) → agent 분리 검토

---

## 7. MCP 통합 후보 (Phase 11+)

각 agent를 MCP server로 분리 시 장점:
- 다른 client (예: Claude Desktop)에서 재사용
- 독립 배포 / 스케일링
- 인터페이스 표준화

후보 분리 단위:
- `intent-mcp`: Intent + intent_filter
- `planning-mcp`: Planning (Discovery + Quick 분기)
- `critic-mcp`: Critic (gpt-4o)
- `rewriter-mcp`: Rewriter
- `rag-mcp`: RAG retrieval + candidate_knowledge 운영

---

## 8. 관련 Skill

- `ai-architecture-review`: 정기 아키텍처 검토
- `agent-io-check`: agent IO contract 정합성
- `multi-llm-validation`: 큰 결정 (예: LangGraph 도입) 시 권장

---

## 9. Open Questions

1. **비동기 처리 전환 시점**: Phase 11+ 명시했으나 정확한 트리거 (사용자 수? 응답 시간?) 미확정
2. **MCP 분리 vs 모놀리식 유지**: Phase 11+ 결정. 사용자 클라이언트 다양화 시점에 따라 변동
3. **자체 모델 fine-tune**: Phase 21+ 검토. 비용 효율 / 품질 / 인프라 부담 비교 필요
4. **multi-Critic ensemble**: Phase 5+ 평가 차원 보강 시 검토
5. **agent timeout 동적 조정**: 사용자 응답 시간 SLA에 따라 모델 / 토큰 한도 동적 조정

---

## 10. 변경 이력

- 2026-05-26: Phase 0 S5에서 placeholder 해소, ADR 형식으로 작성
