"use client";

/**
 * Phase 19 Slice S3 — 데스크톱 전용 PKM 노드 그래프 (react-flow / @xyflow/react).
 *
 * `/brain` 데스크톱 경로에서만 lazy-load 되는 읽기 중심 그래프 뷰.
 *   - S2 카드/리스트(모바일)와 **동일한** getPkmGraph 데이터(`{nodes, edges}`)를 소비 — 추가 fetch 0.
 *   - 큐레이션(잠금/편집/삭제)은 카드 뷰에 유지 — 그래프는 구조 파악(읽기)에 집중.
 *
 * 레이아웃(자체 좌표 — dagre 등 추가 의존성 없이):
 *   user 노드를 중심(0,0)에 두고, owns 엣지로 연결된 brand 노드를 user 우측 컬럼에 세로 배치.
 *   각 brand 의 has_brand_pkm leaf 는 그 brand 우측에 세로로 펼친다(brand 별 leaf 블록).
 *   user 의 has_personal leaf(개인 PKM)는 user 좌측 컬럼에 세로 배치.
 *   엣지로 연결되지 않은 잔여 노드(방어적)는 맨 아래 줄에 흘려 배치.
 *
 * 스타일(design.md / tokens.md 토큰값 — globals.css :root 와 동일 hex):
 *   user  = 루트 강조 (primary 채움, 흰 텍스트)
 *   brand = 허브 (surface + primary 보더, 굵게)
 *   pkm   = leaf (scope 별 보더색: personal=accent / brand=primary, locked 시 🔒 prefix)
 *
 * react-flow Controls(pan/zoom/fit) + fitView. nodesDraggable=false(읽기 전용 안정).
 *
 * 참조:
 *   - apps/web/app/brain/page.tsx (S2 카드/리스트 + S4 큐레이션, getPkmGraph 보유)
 *   - apps/web/lib/types.ts (PkmGraphNode / PkmGraphEdge)
 *   - apps/web/design.md §18 (색/토큰), §16-17 (데스크톱 레이아웃)
 */

import { useMemo } from "react";
import {
  Background,
  Controls,
  Position,
  ReactFlow,
  type Edge,
  type Node,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import type { PkmGraphEdge, PkmGraphNode } from "@/lib/types";

// ── 토큰값 (globals.css :root 와 1:1, design.md §18) ───────────────────
// react-flow 노드 style 은 인라인 객체라 Tailwind 토큰 클래스를 못 받으므로
// 동일 hex 를 상수로 둔다 (토큰 변경 시 이 블록만 동기화).
const TOKEN = {
  primary: "#6366F1",
  accent: "#06B6D4",
  surface: "#FFFFFF",
  bgSubtle: "#F5F5F5",
  textDefault: "#171717",
  textInverse: "#FFFFFF",
  textMuted: "#525252",
  borderDefault: "#E5E5E5",
} as const;

// ── 자체 좌표 레이아웃 상수 ─────────────────────────────────────────────
const COL_USER_X = 0; // user 중심 컬럼
const COL_BRAND_X = 320; // brand 허브 컬럼 (user 우측)
const COL_BRAND_LEAF_X = 640; // brand 의 pkm leaf 컬럼
const COL_PERSONAL_X = -320; // 개인 pkm leaf 컬럼 (user 좌측)
const ROW_GAP = 90; // 세로 간격
const LEAF_ROW_GAP = 72; // leaf 세로 간격

// 노드 고정 치수 — ★ react-flow v12 는 ResizeObserver 로 노드를 비동기 측정해야 엣지/fitView 가
// 그려진다. headless/preview/SSR 등 ResizeObserver 가 안 도는 환경에선 노드만 뜨고 엣지·fitView 가
// 누락된다. width/height 를 명시하면 측정 의존 없이 결정적으로 엣지+fitView 동작(실 브라우저 동일).
const NODE_W = 200;
const NODE_H = 44;

interface PkmGraphProps {
  nodes: PkmGraphNode[];
  edges: PkmGraphEdge[];
}

/**
 * getPkmGraph 결과를 react-flow Node[] / Edge[] 로 변환 + 자체 좌표 배치.
 * 순수 함수 — useMemo 로 nodes/edges 가 바뀔 때만 재계산.
 */
function toFlow(
  graphNodes: PkmGraphNode[],
  graphEdges: PkmGraphEdge[],
): { flowNodes: Node[]; flowEdges: Edge[] } {
  const byId = new Map<string, PkmGraphNode>();
  for (const n of graphNodes) byId.set(n.id, n);

  // 관계 인덱싱.
  const brandIds: string[] = [];
  const personalIds: string[] = [];
  const brandLeafIds = new Map<string, string[]>(); // brandId → pkm leaf ids
  let userId: string | null = null;

  for (const n of graphNodes) {
    if (n.type === "user") userId = userId ?? n.id;
  }
  for (const e of graphEdges) {
    if (e.kind === "owns" && byId.get(e.target)?.type === "brand") {
      brandIds.push(e.target);
      if (!brandLeafIds.has(e.target)) brandLeafIds.set(e.target, []);
    } else if (
      e.kind === "has_personal" &&
      byId.get(e.target)?.type === "pkm"
    ) {
      personalIds.push(e.target);
    } else if (
      e.kind === "has_brand_pkm" &&
      byId.get(e.source)?.type === "brand" &&
      byId.get(e.target)?.type === "pkm"
    ) {
      const bucket = brandLeafIds.get(e.source) ?? [];
      bucket.push(e.target);
      brandLeafIds.set(e.source, bucket);
    }
  }

  const placed = new Set<string>();
  const positions = new Map<string, { x: number; y: number }>();

  // brand 컬럼 + 각 brand 의 leaf 블록 높이를 고려해 세로 중심 정렬.
  // 각 brand block 의 높이 = max(1, leaf 수) 행. 누적 y 로 쌓는다.
  let brandCursorY = 0;
  const brandBlockCenters: number[] = [];
  for (const bId of brandIds) {
    const leaves = brandLeafIds.get(bId) ?? [];
    const rows = Math.max(1, leaves.length);
    const blockTop = brandCursorY;
    const blockHeight = (rows - 1) * LEAF_ROW_GAP;
    const blockCenter = blockTop + blockHeight / 2;
    brandBlockCenters.push(blockCenter);

    positions.set(bId, { x: COL_BRAND_X, y: blockCenter });
    placed.add(bId);

    leaves.forEach((leafId, i) => {
      positions.set(leafId, {
        x: COL_BRAND_LEAF_X,
        y: blockTop + i * LEAF_ROW_GAP,
      });
      placed.add(leafId);
    });

    brandCursorY = blockTop + blockHeight + ROW_GAP;
  }

  // user 는 brand 블록 전체의 세로 중심에 배치 (brand 없으면 0).
  const userY =
    brandBlockCenters.length > 0
      ? brandBlockCenters.reduce((a, b) => a + b, 0) / brandBlockCenters.length
      : 0;
  if (userId) {
    positions.set(userId, { x: COL_USER_X, y: userY });
    placed.add(userId);
  }

  // 개인 pkm leaf 는 user 좌측에 user 중심 기준 세로로 펼친다.
  const personalCount = personalIds.length;
  const personalStartY = userY - ((personalCount - 1) * LEAF_ROW_GAP) / 2;
  personalIds.forEach((pId, i) => {
    positions.set(pId, {
      x: COL_PERSONAL_X,
      y: personalStartY + i * LEAF_ROW_GAP,
    });
    placed.add(pId);
  });

  // 방어적: 엣지 어디에도 안 걸린 잔여 노드(있으면)는 맨 아래 줄에 흘려 배치.
  let strayCursorX = COL_PERSONAL_X;
  const strayY = Math.max(brandCursorY, personalStartY + personalCount * LEAF_ROW_GAP) + ROW_GAP;
  for (const n of graphNodes) {
    if (placed.has(n.id)) continue;
    positions.set(n.id, { x: strayCursorX, y: strayY });
    placed.add(n.id);
    strayCursorX += 260;
  }

  const flowNodes: Node[] = graphNodes.map((n) => {
    const pos = positions.get(n.id) ?? { x: 0, y: 0 };
    return {
      id: n.id,
      position: pos,
      data: { label: nodeLabel(n) },
      // ★ 명시적 측정값 — react-flow v12 가 비동기 측정을 기다리지 않고 즉시 엣지/fitView 계산.
      width: NODE_W,
      height: NODE_H,
      style: nodeStyle(n),
      // 좌→우 흐름: user(중심) 기준 brand/leaf 는 우측, personal 은 좌측.
      // 핸들 방향을 수평으로 두면 엣지가 자연스럽게 가로로 흐른다.
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      draggable: false,
      selectable: true,
    };
  });

  const flowEdges: Edge[] = graphEdges.map((e, i) => ({
    id: `${e.source}->${e.target}:${e.kind}:${i}`,
    source: e.source,
    target: e.target,
    // owns(user→brand) 는 강조, leaf 연결은 옅게.
    style: {
      stroke: e.kind === "owns" ? TOKEN.primary : TOKEN.borderDefault,
      strokeWidth: e.kind === "owns" ? 2 : 1.5,
    },
    animated: false,
  }));

  return { flowNodes, flowEdges };
}

/** locked 면 🔒 prefix. 너무 길면 잘라 노드 가독성 유지. */
function nodeLabel(n: PkmGraphNode): string {
  const base = n.label.length > 28 ? `${n.label.slice(0, 27)}…` : n.label;
  return n.locked ? `🔒 ${base}` : base;
}

/** type / scope 별 노드 스타일 (인라인 — react-flow 요구). */
function nodeStyle(n: PkmGraphNode): React.CSSProperties {
  const common: React.CSSProperties = {
    borderRadius: 10,
    padding: "8px 12px",
    fontSize: 12,
    fontWeight: 600,
    textAlign: "center",
    // 고정 치수(NODE_W/H 와 일치) + 1줄 말줄임 — 측정 비의존 + 가독성.
    width: NODE_W,
    height: NODE_H,
    boxSizing: "border-box",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    whiteSpace: "nowrap",
    overflow: "hidden",
    textOverflow: "ellipsis",
  };
  if (n.type === "user") {
    return {
      ...common,
      background: TOKEN.primary,
      color: TOKEN.textInverse,
      border: `2px solid ${TOKEN.primary}`,
      fontSize: 13,
      fontWeight: 700,
    };
  }
  if (n.type === "brand") {
    return {
      ...common,
      background: TOKEN.surface,
      color: TOKEN.textDefault,
      border: `2px solid ${TOKEN.primary}`,
    };
  }
  // pkm leaf — scope 별 보더색으로 개인/브랜드 구분.
  const scopeColor = n.scope === "personal" ? TOKEN.accent : TOKEN.primary;
  return {
    ...common,
    background: TOKEN.bgSubtle,
    color: TOKEN.textMuted,
    border: `1.5px solid ${scopeColor}`,
    fontWeight: 500,
  };
}

/**
 * 데스크톱 PKM 그래프. 부모(/brain page)가 데스크톱일 때만 dynamic import → 렌더한다.
 * 높이는 부모 컨테이너에 맞춤(부모가 명시적 높이를 줌).
 */
export default function PkmGraph({ nodes, edges }: PkmGraphProps) {
  const { flowNodes, flowEdges } = useMemo(
    () => toFlow(nodes, edges),
    [nodes, edges],
  );

  return (
    <div
      className="w-full h-full rounded-lg border border-border-default bg-surface"
      role="img"
      aria-label="내 2nd brain 노드 그래프 (사용자·브랜드·PKM 관계도)"
    >
      <ReactFlow
        nodes={flowNodes}
        edges={flowEdges}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        nodesDraggable={false}
        nodesConnectable={false}
        elementsSelectable
        proOptions={{ hideAttribution: true }}
        minZoom={0.2}
        maxZoom={2}
      >
        <Background color={TOKEN.borderDefault} gap={20} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  );
}
