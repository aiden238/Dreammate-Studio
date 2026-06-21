# Phase 31 — non_goals

- **default judge 전환(openai → anthropic)** — major model swap = 별도 prompt-version-review.
  본 phase는 consensus-min(안전 default 후보)까지만. 전환 자체는 미포함.
- **rater B κ / 다중 human 재평가** — rater B 인간 채점 미도착(외부 의존) = BLOCKED. 도착 시 별건
  (`scripts/analyze_blind_ab.py --rater A --rater B`).
- **코퍼스 확대(큐레이션 + 2nd-brain feedback)** — RAG "값"을 키우는 별도 아크. 본 phase는 측정(A6)까지.
  큐레이션 고가치 패턴 수작업 시드 / 2nd-brain 피드백 누적은 후속 phase.
- **critic_calibration 활성/multi_provider_plans 빌드** — HIP-B 결착(retain·defer)대로 OFF 유지.
- **실 staging 배포(Gate B~G)** — 인프라 user-provided, Phase 32+.
- **신규 제품 기능** — 본 phase는 품질 계측기 마감 + 측정 + 통합. 기능 추가 아님.
- **differentiation을 프롬프트로 해결** — B0/B1이 불가 입증(개념층은 RAG/PKM grounding 필요).
  S2는 표면 레버만, 차별화는 S3 측정 + 후속 코퍼스 아크로.
