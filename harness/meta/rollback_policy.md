# rollback_policy.md — 롤백 정책

> 위치: `meta/rollback_policy.md`
> 상태: Phase 0 Sprint S5 deep 작성 (placeholder 해소)
> 참조: `meta/error_taxonomy.md`, `meta/security_metrics.md`
> 참조: `.claude/skills/prompt-version-review/SKILL.md`, `.claude/skills/meta-retrospective/SKILL.md`

---

## 0. 롤백 정의

> **롤백은 잘못된 변경을 신속히 되돌리는 절차다.**

본 정책은 무엇을 롤백 대상으로 보는지, 어떤 트리거에서 롤백하는지, 어떻게 롤백하는지, 롤백 후 무엇을 분석하는지를 정의한다.

---

## 1. 롤백 대상 (4 종류)

```
1. Prompt version       (semver bump → 이전 버전 활성화)
2. Contract             (docs/contracts/ 변경 → git revert)
3. Skill                (.claude/skills/ 변경 → git revert + INDEX 갱신)
4. Code                 (백엔드 / 프론트 / DB migration)
```

각 대상은 롤백 절차가 다르다 (§4 참조).

---

## 2. 롤백 트리거

다음 트리거 중 하나라도 발생하면 롤백 검토.

### 2.1 회귀 실패 (Critical)

```
- Golden Set 회귀 통과율 90% 미만으로 하락
- Critic 평균 점수 0.65 미만으로 하락
- 광고 표현 차단 정확도 90% 미만
- video_planning_eval 6 차원 중 2개 이상에서 하락
SLA: 즉시 롤백 (24시간 내)
```

### 2.2 보안 사고 (Critical)

```
- 데이터 노출 사고 (PII / Brand 데이터 사용자 간 노출)
- 사용자 격리 위반 (RLS bypass 등)
- 인증 우회 가능 취약점 발견
- prompt injection 차단 무력화
SLA: 즉시 롤백 (1시간 내) + 사용자 통보
```

### 2.3 비용 폭주 (High)

```
- 5분 평균 비용이 평소 3배 이상
- 사용자당 일평균 LLM 비용 $0.50 초과 다수 발생
- LLM API rate limit 도달 빈도 급증
SLA: 즉시 롤백 (1시간 내) + cost 한도 임시 강화
```

### 2.4 성능 저하 (High)

```
- p95 응답 시간이 평소 2배 (60초 → 120초)
- 에러율 5% 초과 (Sentry 기준)
- DB query 평균 시간 2배
SLA: 24시간 내 롤백 결정
```

### 2.5 사용자 불만 급증 (Medium)

```
- 24시간 내 동일 불만 패턴 10건 이상
- NPS 측정에서 부정 응답 비율 50% 초과
- 결제 환불 신청 급증 (Phase 12+)
SLA: 72시간 내 검토 + 롤백 결정
```

### 2.6 컴플라이언스 위반 (High)

```
- 개인정보보호법 / GDPR 위반 가능성
- 광고 표현 사전 위반 누적
- 부적절 콘텐츠 자동 생성 발견
SLA: 24시간 내 롤백 + 법무 검토
```

---

## 3. 롤백 결정 권한

```
즉시 롤백 (사람 승인 없이 자동):
- 데이터 노출 사고 (security A): 시스템 자동 차단 + AI 알림
- 비용 폭주 (1시간 평균 5배 이상): 자동 rate_limit 강화

24시간 SLA 롤백 (사용자 승인):
- 회귀 실패
- 보안 취약점 (즉시 노출은 아님)
- 컴플라이언스 위반 의심

검토 후 롤백 (multi-llm-validation):
- 큰 contract 변경 후 부작용
- prompt major version bump 후 품질 저하
- 가격 모델 변경 후 사용자 이탈

롤백 거절 (조건부):
- 부작용이 큰 롤백 (사용자 데이터 손실 위험)
- → forward fix 우선 + 롤백 보류
```

---

## 4. 롤백 절차 (대상별)

### 4.1 Prompt version 롤백

```
1. prompt_registry.md의 active version 변경
   - 예: P-006 v1.2.0 → v1.1.0 (이전 버전)
2. eval/regression_results/에 회귀 결과 기록
3. agent_io_logs에 prompt_version 갱신 확인
4. 24시간 staging 검증 후 production 적용
5. prompt-version-review Skill 통과
6. 사용자 영향 분석 (Phase 12+ paid tier 영향)

회복 시간: ~24시간 (staging 검증 포함)
주의: P-006 (Planning) 같이 사용자 데이터 형식 영향 prompt는 추가 검증
```

→ `.claude/skills/prompt-version-review/SKILL.md`

### 4.2 Contract 롤백

```
1. git revert {commit_hash}로 이전 contract 복원
2. dependency_map.yaml의 영향 파일 모두 검토
3. eval/regression_results/ 자동 회귀 실행
4. 회귀 통과 시 PR merge → deploy
5. PROJECT_STATE.md "최근 변경" 기록
6. contract-change Skill의 rollback 분기 절차

회복 시간: ~6시간 (회귀 평가 + deploy)
주의: API contract 변경 롤백 시 frontend / mobile 호환성 검토
```

### 4.3 Skill 롤백

```
1. git revert로 .claude/skills/*/SKILL.md 복원
2. .claude/skills/INDEX.md 갱신 (description 키워드 충돌 재확인)
3. harness-audit Skill 실행 (즉시)
4. 새 세션에서 자동 트리거 동작 확인
5. 변경 로그 기록

회복 시간: ~1시간
주의: 같은 description 키워드가 둘 이상 Skill에 있으면 즉시 충돌 해결
```

### 4.4 Code 롤백 (백엔드 / 프론트)

```
백엔드 (FastAPI):
1. git revert + Render/Railway re-deploy
2. DB migration이 함께였다면 Alembic downgrade
3. agent_io_logs 정상화 확인
4. Sentry 에러율 모니터링 (1시간)

프론트 (Next.js):
1. git revert + Vercel preview 검증
2. PWA cache 무효화 (next-pwa 갱신)
3. 사용자 영향 (이미 캐시된 사용자) 분석

DB Migration:
1. Alembic downgrade {previous_revision}
2. 데이터 손실 가능성 평가 (downgrade 함수가 lossy일 때)
3. 영향 사용자 자동 알림
4. 회복 후 forward migration 재설계

회복 시간: 백엔드 ~30분, 프론트 ~15분, DB ~1~2시간
```

---

## 5. 롤백 후 사후 분석

롤백 후 반드시 수행. 자동 회복은 다음 실패를 부른다.

### 5.1 즉시 (24시간 내)

```
1. 영향 분석:
   - 영향 사용자 수
   - 데이터 손실 / 비용 손실
   - 사용자 통보 필요 여부

2. 원인 분석 (preliminary):
   - 어떤 변경이 문제였는가
   - 왜 회귀 평가에서 못 잡았는가
   - 어떤 가드레일이 작동했는가 / 작동 안 했는가
```

### 5.2 7일 내 (meta-retrospective)

```
3. retrospective 작성:
   - meta-retrospective Skill 호출
   - 출력: meta/retrospectives/YYYY-MM-DD-rollback-{topic}.md
   - 5단계 분석: 컨텍스트 / 결정 / 결과 / 학습 / 다음 조치

4. patterns 갱신:
   - 같은 패턴 재발 여부 (meta/patterns.md)
   - 회귀 평가 보완 필요 항목
```

### 5.3 14일 내 (harness-audit)

```
5. 구조 점검:
   - harness-audit Skill 호출
   - 비슷한 위험 다른 영역에 있는지
   - placeholder marker 점검 (보강 우선순위 갱신)

6. 개선 제안:
   - meta/harness_improvement_proposals.md 신규 항목
   - 회귀 평가 강화 / 가드레일 추가 / 모니터링 추가
```

---

## 6. 롤백 실패 시 절차

롤백 자체가 실패하면 (이전 버전도 동작 안 함 등).

```
1. 즉시 운영자 알림 (Slack #ops-alert + PagerDuty)
2. 사용자에게 "잠시 점검 중" 안내 (시스템 단 자동 표시)
3. 두 단계 이전 버전으로 재롤백 (단, 추가 위험 평가 필수)
4. 재롤백도 실패 시: forward fix 강제 (긴급 patch)
5. 사후: meta-retrospective 즉시 + multi-llm-validation으로 패치 검증
```

---

## 7. 롤백 측정 지표

```
1. 롤백 빈도
   - 분기당 0~2건 정상.
   - 5건 이상이면 회귀 평가 / 가드레일 강화 필요.

2. 평균 회복 시간 (MTTR)
   - 보안 사고: 1시간 이내 목표.
   - 회귀 실패: 24시간 이내 목표.
   - 코드: 30분 이내 목표.

3. 롤백 후 재발 빈도
   - 같은 영역 30일 내 재롤백 = 큰 위험 신호.
   - 즉시 multi-llm-validation 강제.

4. 사용자 영향 (롤백당)
   - 영향 사용자 수 / 데이터 손실 / 비용 손실.
   - 0이 목표.

5. 사후 분석 SLA
   - retrospective: 7일 내 작성률.
   - patterns 갱신: 14일 내 갱신률.
   - 목표: 95% 이상.
```

---

## 8. 자주 롤백 대상 영역 (Phase 0 시드)

```
P-006 Planning prompt (영상기획안 3개 생성):
- 사용자 영향 가장 큼.
- 변경 시 가장 신중. major bump 시 10% → 50% → 100% 강제.

광고 단어 사전:
- 단어 추가는 안전.
- 단어 제거는 위험 (롤백 빈도 높음).

intent_filter 임계:
- false positive 조정 시 자주 롤백.

광고 표현 / PII 감지 패턴:
- 정기적 갱신이지만 false positive 위험.
```

→ 향후 데이터 누적 후 확장

---

## 9. forward fix vs 롤백 선택

다음 기준으로 결정.

```
롤백 우선 (대부분의 경우):
- 영향 범위가 큼
- 회복 시간이 빠름 (이전 버전이 안정)
- 사용자 데이터 손실 위험 없음
- 보안 사고 또는 컴플라이언스 위반

forward fix 우선 (특정 케이스):
- 이전 버전이 더 안 좋음 (다른 버그 있음)
- 롤백 자체가 데이터 손실 유발 (DB migration lossy)
- 부분 사용자만 영향 (전체 롤백 비효율)
- 30분 내 fix 가능한 작은 버그
```

forward fix 선택 시:

```
1. 24시간 임시 가드레일 (특정 경로 차단)
2. patch 개발 + staging 검증
3. hotfix deploy + 사용자 영향 모니터링
4. retrospective 시 forward fix 선택 사유 명시
```

---

## 10. 확장 가능성 (Phase X+ 보강 예정)

```
Phase 5+:  롤백 자동화 (특정 트리거 자동 실행).
Phase 11+: 운영자 대시보드에 롤백 history + MTTR 시각화.
Phase 21+: ML 기반 회귀 예측 (롤백 가능성 사전 알림).
연 1회:    본 정책 재검토 + 트리거 임계 갱신.
```

---

## 11. Open Questions

1. 즉시 롤백 (사람 승인 없이) 권한이 데이터 노출 + 비용 폭주 외에 더 있어야 하는지.
2. 롤백 결정의 multi-llm-validation 강제 임계 (가격 / 큰 prompt) 정의 필요.
3. forward fix와 롤백을 모두 시도하는 병렬 처리 (안전 + 빠름) 가능한지.
4. MTTR 목표 (1시간 / 24시간)가 1인 운영에 현실적인지.
5. 롤백 history의 보존 기간 (영구 vs 1년 vs 압축).

---

## 12. 변경 이력

```
v1.0.0 (2026-05-26): Phase 0 Sprint S5-1. placeholder 해소 + deep 작성.
                      4 롤백 대상, 6 트리거, 결정 권한, 대상별 절차,
                      사후 분석, 측정 지표, forward fix vs 롤백 선택.
```
