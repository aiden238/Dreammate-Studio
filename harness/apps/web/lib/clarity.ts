/**
 * Phase 34 S2 (cross-project 수렴) — 의도 명확도(clarity) 점수.
 *
 * plotter 확인 턴의 clarity_score("명확도 N%")를 Dreammate에 흡수한다. plotter는 백엔드
 * 슬롯-필 휴리스틱으로 산출하지만, 여기서는 LLM·백엔드 호출 없이 *사용자가 이미 채운 신호의
 * 풍부함*만으로 결정적으로 계산한다(무비용·재현가능). "구체적으로 채울수록 또렷해진다"는
 * 동일 정신 — DirectionApprovalCard가 이 값을 받아 확인 턴 배지로 표면화한다.
 *
 * 반환은 0~1, [0.2, 0.98]로 클램프(0%·100% 과잉확신 회피). 카드는 ≥0.6이면 강조 배지.
 *
 * 정직성: 이는 LLM 채점이 아니라 *입력 구체성 휴리스틱*이다. 추후 백엔드 채점으로 승급 가능
 * (그때 clarity_score를 응답에 실어 보내면 동일 prop으로 그대로 흐른다).
 */

/** 0~1, [0.2, 0.98] 클램프 + 소수 2자리 반올림. */
function clampClarity(x: number): number {
  return Math.min(0.98, Math.max(0.2, Number(x.toFixed(2))));
}

/**
 * Quick 모드 명확도 — 짧은 자유 입력의 구체성 + 보강 여부.
 *
 * - promptLen: Step1 initialPrompt 길이(구체성 proxy). Quick은 ~20자 이하면 clarify로 보냄.
 * - clarified: Step2 추가 답변을 했나(스킵·미답이면 false).
 * - edited:    사용자가 방향 문장을 직접 다듬었나(의도 확정도↑).
 */
export function quickClarity(args: {
  promptLen: number;
  clarified: boolean;
  edited?: boolean;
}): number {
  let s = 0.34;
  // 구체성: 12자 근방에서 낮고(=clarify 임계대), 132자에서 +0.34 만렙.
  s += Math.min(0.34, (Math.max(0, args.promptLen - 12) / 120) * 0.34);
  if (args.clarified) s += 0.18;
  if (args.edited) s += 0.1;
  return clampClarity(s);
}

/**
 * Discovery 모드 명확도 — 명시적으로 채운 축(reasons) 비율.
 *
 * - reasonsFilled: Step1~5 중 사용자가 명시 선택/입력한 축 수(스킵-위임도 1개로 카운트 가능).
 * - total:         축 총수(기본 5).
 * - edited:        방향 문장 직접 수정 여부.
 */
export function discoveryClarity(args: {
  reasonsFilled: number;
  total?: number;
  edited?: boolean;
}): number {
  const total = args.total ?? 5;
  const ratio = total > 0 ? Math.min(1, args.reasonsFilled / total) : 0;
  let s = 0.4 + ratio * 0.5; // 전부 채우면 0.9
  if (args.edited) s += 0.05;
  return clampClarity(s);
}
