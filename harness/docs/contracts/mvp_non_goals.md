# mvp_non_goals.md — MVP 제외 항목 Contract

> 위치: `docs/contracts/mvp_non_goals.md`
> 상태: **active_contract** (Phase 1 진입 전 승격, 2026-05-26)
> 참조: `product/mvp_scope.md`, `docs/contracts/product_boundary.md`, `PHASE_REGISTRY.md`

---

## Status

```yaml
status: active_contract
version: v1.0.0
promoted_from: placeholder_partial
promoted_at: 2026-05-26
promoted_by: phase-1-pre-check
last_updated: 2026-05-26
```

---

## 1. 영구 제외 항목 (Permanent Exclusions)

**영구 제외** = 어떤 Phase에도 MVP에 포함하지 않는다.  
단, Phase 21+ 독립 서비스로 분리 검토 가능 (product/roadmap.md 참조).

| 항목 | 이유 | 재검토 가능 여부 |
|---|---|---|
| 자동 영상 생성 | 제품 정의 외 (기획 도구, 제작 도구 아님) | ❌ 영구 제외 |
| 자동 영상 편집 | 위와 동일 | ❌ 영구 제외 |
| TTS 생성 | 위와 동일 | ❌ 영구 제외 |
| BGM 삽입 | 위와 동일 | ❌ 영구 제외 |
| 자막 자동 합성 | 위와 동일 | ❌ 영구 제외 |
| 이미지/영상 소스 생성 | 위와 동일 | ❌ 영구 제외 |
| 컷 편집 자동화 | 위와 동일 | ❌ 영구 제외 |
| 쇼츠 자동 조립 | 위와 동일 | ❌ 영구 제외 |
| YouTube/Instagram 자동 업로드 | 위와 동일 | ❌ 영구 제외 |

> ⚠️ 영구 제외 항목 변경은 **사용자(제품 오너)만** 결정 가능.  
> AI 에이전트가 단독으로 영구 제외를 해제할 수 없다.

---

## 2. MVP 후 검토 가능 항목 (Deferred Features)

Phase 진행에 따라 재검토하며, 해당 Phase 진입 시 scope 포함 여부 결정.

### Phase 5~10 재검토 대상

| 항목 | 예정 Phase | 조건 |
|---|---|---|
| 팀 / 멀티 사용자 | Phase 11+ | 유료 플랜 도입 후 |
| 결제 기능 | Phase 11+ | 유료화 전략 확정 후 |
| 광고 표현 차단 고도화 | Phase 4 | MOA Lite 안정화 후 |
| Brand Memory 자동 추출 | Phase 4 | 기본 피드백 루프 이후 |
| Full MOA (4 Agent 완전) | Phase 8 | RAG Lite 안정화 후 |
| 데이터 내보내기 | Phase 11+ | 사용자 요청 시 |

### Phase 21+ 재검토 대상

| 항목 | 예정 Phase | 조건 |
|---|---|---|
| Expo React Native 앱 | Phase 21 | PWA 안정화 후 |
| Java / Spring Boot 분리 | Phase 21 | 트래픽 임계값 초과 시 |
| Graph RAG / Custom RAG | Phase 21 | 지식 베이스 크기 임계값 초과 시 |
| 대규모 파인튜닝 | Phase 25+ | 데이터셋 10,000+ 케이스 확보 후 |

---

## 3. 변경 절차 (Change Procedure)

### 3.1 영구 제외 항목 해제 절차

```
1. 사용자(제품 오너)가 명시적 요청
2. meta/proposals/ 에 제안 문서 작성 (왜 해제하는지, 범위, 영향)
3. contract-change Skill 실행
4. multi-llm-validation 필수 (큰 제품 방향 변경)
5. PHASE_REGISTRY.md 관련 Phase 범위 갱신
6. 사용자 최종 승인
7. 본 파일 §1 업데이트 + version bump
```

### 3.2 MVP 후 검토 항목 조기 포함 절차

```
1. meta/proposals/ 에 제안 작성 (우선순위 변경 이유)
2. contract-change Skill 실행
3. 현재 active Phase의 scope.md + non_goals.md 갱신
4. 사용자 승인
5. 본 파일 §2 업데이트
```

### 3.3 새 항목 추가 절차

```
1. mvp_scope.md 또는 vision.md와 충돌하지 않는지 확인
2. 적절한 구분(영구/임시) 결정
3. 본 파일에 추가
4. PROJECT_STATE.md confirmed_decisions 갱신 (필요 시)
```

---

## 4. 사용자 승인 필요 조건

다음 상황에서는 **AI 에이전트가 단독 결정 불가**, 사용자(제품 오너) 승인 필수:

| 상황 | 이유 |
|---|---|
| 영구 제외 항목 해제 | 제품 정의 본질 변경 |
| 예정 Phase를 2 이상 앞당기는 경우 | 개발 범위 급변 |
| 새 항목을 영구 제외로 지정하는 경우 | 제품 방향 좁힘 |
| 이미 구현 중인 기능을 이 목록에 추가하는 경우 | 구현 취소 결정 |

AI 에이전트는 이 조건에 해당하는 요청이 오면:
1. 사용자에게 명시적 승인 요청
2. 승인 없이 작업 진행 금지

---

## 5. 현재 MVP Non-Goals 전체 목록

### 5.1 영상 제작 기능 (영구 제외)
- 자동 영상 생성
- 자동 영상 편집
- TTS 생성
- BGM 삽입
- 자막 자동 합성
- 이미지/영상 소스 생성
- 컷 편집 자동화
- 쇼츠 자동 조립
- YouTube/Instagram 자동 업로드

### 5.2 플랫폼 확장 기능 (Phase 11+)
- 팀 기능 / 멀티 사용자
- 결제 기능
- 다국어 지원 (i18n)
- 화이트 레이블 / 에이전시 모드
- 데이터 내보내기 / API 공개

### 5.3 기술 확장 (Phase 21+)
- Expo React Native 앱
- Java / Spring Boot 백엔드
- Graph RAG / Custom RAG
- 대규모 LLM 파인튜닝

### 5.4 AI 고도화 (Phase 4~8에서 순차 추가)
- 기획안 3개 동시 생성 → Phase 4
- Critic revise 2회 루프 → Phase 4
- Brand Memory 자동 추출 → Phase 4
- Full MOA → Phase 8
- RAG 5단계 파이프라인 → Phase 7

---

## 6. 예외 처리

MVP 범위 밖 기능이 필요하다고 판단되면:

```
직접 구현 금지 → meta/proposals/ 또는 docs/contract_changes/ 에 제안 작성
→ contract-change Skill → 사용자 승인 → 범위 조정
```

---

## 7. 관련 문서

- `product/mvp_scope.md` — 포함 범위
- `product/vision.md` — 제품 본질 정의
- `docs/contracts/product_boundary.md` — 시스템 경계
- `PHASE_REGISTRY.md` — Phase별 범위
- `phases/active/phase-1-mvp-basic-flow/non_goals.md` — Phase 1 구체적 제외 목록

---

## 8. 변경 이력

- v1.0.0 (2026-05-26): Phase 1 진입 전 placeholder_partial → active_contract 승격
  - §1 영구 제외 항목 표 추가
  - §2 MVP 후 검토 가능 항목 Phase별 분류
  - §3 변경 절차 3가지 경로 정의
  - §4 사용자 승인 필요 조건 명시
  - §5 현재 목록 전체 정리
