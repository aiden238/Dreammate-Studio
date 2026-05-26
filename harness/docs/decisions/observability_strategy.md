# observability_strategy.md — 관찰성 전략 결정 기록 (ADR)

> 위치: `docs/decisions/observability_strategy.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `docs/contracts/tech_stack_contract.md`, `meta/security_metrics.md`, `docs/contracts/agent_io_contract.md`

---

## 0. 본 문서의 위치

본 문서는 **ADR (Architecture Decision Record)** 형식의 의사결정 기록이다.
관찰성(Observability) 도입 시점, 도구 선정, 측정 지표 체계의 배경과 대안을 기록한다.

---

## 1. 결정 요약

```
Phase 1-6 (MVP 기본):    Sentry (errors) + Supabase 기본 로그 + agent_io_logs (DB)
Phase 7+ (보안 단계):     OpenTelemetry 도입 (trace + metric) + security_metrics 본격 운영
Phase 11+ (안정화):       Grafana / Datadog 검토 (운영 비용 vs 가시성 트레이드오프)
Phase 21+ (확장):         자체 dashboard / SLA 모니터링 / 분산 트레이싱
```

핵심 측정 지표 4축:
- **Latency**: 요청-응답 시간 (p50/p95/p99), agent별 / endpoint별
- **Error rate**: 에러 카테고리별 빈도 (error_response_contract §4 prefix)
- **Cost**: LLM 호출 비용 / 사용자별 / brand별 / endpoint별
- **Quality**: golden_set 회귀 통과율, Critic 8차원 평균 점수

---

## 2. 대안 비교

| 도구 | 장점 | 단점 | 채택 시점 |
|------|------|------|---------|
| Sentry | 빠른 구축, 무료 tier 충분 | trace 깊이 부족 | **MVP** |
| OpenTelemetry | 표준, 벤더 lock-in 없음 | 셋업 복잡 | **Phase 7+** |
| Datadog | 통합 UX, APM 강력 | 비용 큼 (월 $300+) | Phase 11+ 검토 |
| Grafana + Prometheus | 오픈소스, 커스터마이징 | 운영 부담 | Phase 11+ 대안 |
| 자체 dashboard | 도메인 특화 | 개발 비용 | Phase 21+ |

---

## 3. 선택 이유

- **MVP 단순성**: Sentry + Supabase 로그면 Phase 1-6 진단 충분
- **점진 도입**: OpenTelemetry는 보안 강화 Phase 7부터 (security_metrics와 연동)
- **비용 통제**: Datadog/New Relic은 사용자 1만 이상 시점에서 비용 정당화 가능

---

## 4. 트레이드오프

- Sentry만으로는 비용 추적 부족 → agent_io_logs (DB) 보조 사용
- OpenTelemetry 늦은 도입 → Phase 1-6에서 분산 트레이싱 불가 (모놀리식이라 큰 문제 아님)
- 자체 dashboard 미구축 → 비즈니스 지표(전환율, retention)는 Supabase SQL + 외부 BI

---

## 5. 재검토 트리거

- 사용자 1만 명 도달 → Datadog/Grafana 비용 분석 재실시
- p95 latency 60초 초과 빈발 → 분산 트레이싱 즉시 도입
- 보안 사고 발생 → security_metrics + audit log 확장
- 비용 폭주 (월 LLM 비용 $1000 초과) → cost-review Skill 강제 적용

---

## 6. 측정 지표 상세

### 6.1 Latency
- 측정 위치: API gateway, agent invocation, RAG retrieval, DB query
- 임계값: p95 < 30초 (생성 endpoint), p95 < 1초 (조회 endpoint)
- 기록: agent_io_logs.latency_ms (db_schema §7.1)

### 6.2 Error rate
- 카테고리별 (E-INV/E-LLM/E-RAG/E-DB/E-RL/E-SEC/E-UNK)
- 임계값: 전체 < 2%, E-SEC < 0.1%
- 알림 트리거: 5분 내 동일 카테고리 10건 이상

### 6.3 Cost
- per-call / per-session / per-user / per-brand
- 임계값: 사용자 월 평균 < $5, 단일 session < $0.5
- 알림: 일 누적 비용 $100 초과

### 6.4 Quality
- golden_set 회귀: 매 prompt 변경 시 100% 실행
- Critic 8차원 평균 점수 추세 (주간)
- 사용자 만족도 (feedback rating)

---

## 7. 관련 Skill

- `cost-review`: 비용 분석 + 최적화 제안
- `security-review`: security_metrics 정기 분석
- `harness-audit`: observability 누락 항목 자동 검출

---

## 8. Open Questions

1. **Sentry 무료 tier 한도 초과 시점**: 어떤 plan으로 갈지? Phase 4+ 결정.
2. **OpenTelemetry collector 호스팅**: self-host vs Grafana Cloud free tier?
3. **PII 마스킹 정책**: trace에 사용자 입력 포함 시 자동 마스킹 (llm_security §3 PII 정책 연동)
4. **agent_io_logs 보존 기간**: 90일 / 1년 / 영구? data_retention_policy (Phase 7+) 확정 후 결정.
5. **알림 채널**: Slack? Email? PagerDuty? Phase 5+ 결정.
6. **비즈니스 지표 dashboard**: Metabase / Supabase Studio SQL view / 자체 구축?

---

## 9. 변경 이력

- 2026-05-26: Phase 0 S5에서 placeholder 해소, ADR 형식으로 작성
