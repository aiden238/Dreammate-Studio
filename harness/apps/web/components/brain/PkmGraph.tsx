"use client";

/**
 * Phase 19 S3 → Phase 29 B1 — 데스크톱 전용 PKM **동적 force 그래프** (react-flow + d3-force).
 *
 * `/brain` 데스크톱 경로에서만 lazy-load 되는 읽기 중심 그래프 뷰.
 *   - S2 카드/리스트(모바일)와 **동일한** getPkmGraph 데이터(`{nodes, edges}`)를 소비 — 추가 fetch 0.
 *   - 큐레이션(잠금/편집/삭제)은 카드 뷰에 유지 — 그래프는 구조 파악(읽기)에 집중.
 *
 * ★ Phase 29 B1 (동적화): 기존 고정 계층(user→brand→leaf 컬럼) 좌표를 **d3-force 물리
 *   시뮬레이션**으로 교체 → 유기적(Obsidian 풍) force-directed 배치. 노드 드래그 + 타입 필터 칩 추가.
 *   - 레이아웃은 전체 그래프에 대해 **1회 settle**(deterministic, 동기 tick) → 좌표 안정.
 *     필터 토글은 노드를 숨길 뿐 생존 노드를 **재배치하지 않는다**(안정 UX + 재계산 0).
 *   - 동기 settle + 명시 width/height → headless/preview(ResizeObserver 부재)에서도 엣지/fitView 결정적.
 *   - 노드 드래그: nodesDraggable + onNodeschange(applyNodeChanges) 로 위치 변경 반영(snap-back 없음).
 *
 * 스타일(design.md / tokens.md 토큰값 — globals.css :root 와 동일 hex):
 *   user  = 루트 강조 (primary 채움, 흰 텍스트)
 *   brand = 허브 (surface + primary 보더, 굵게)
 *   pkm   = leaf (scope 별 보더색: personal=accent / brand=primary, locked 시 🔒 prefix)
 *   domain/series/source = 4계층·출처 (Phase 21)
 *
 * 참조:
 *   - apps/web/app/brain/page.tsx (S2 카드/리스트 + S4 큐레이션, getPkmGraph 보유)
 *   - apps/web/lib/types.ts (PkmGraphNode / PkmGraphEdge)
 *   - apps/web/design.md §18 (색/토큰), §16-17 (데스크톱 레이아웃)
 */

import { useCallback, useEffect, useMemo, useState } from "react";
import {
  applyNodeChanges,
  Background,
  Controls,
  Position,
  ReactFlow,
  type Edge,
  type Node,
  type NodeChange,
} from "@xyflow/react";
import {
  forceCollide,
  forceLink,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY,
  type SimulationLinkDatum,
  type SimulationNodeDatum,
} from "d3-force";

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

// 노드 고정 치수 — ★ react-flow v12 는 ResizeObserver 로 노드를 비동기 측정해야 엣지/fitView 가
// 그려진다. headless/preview/SSR 등 ResizeObserver 가 안 도는 환경에선 노드만 뜨고 엣지·fitView 가
// 누락된다. width/height 를 명시하면 측정 의존 없이 결정적으로 엣지+fitView 동작(실 브라우저 동일).
const NODE_W = 188;
const NODE_H = 42;

// ── d3-force 파라미터 ─────────────────────────────────────────────────
// 엣지 종류별 이상 거리 — owns(user↔brand) 는 멀게(허브 분리), leaf 는 가깝게(클러스터).
const LINK_DIST: Record<string, number> = {
  owns: 190,
  has_domain: 150,
  has_series: 130,
  has_brand_pkm: 96,
  has_personal: 96,
  sourced_from: 84,
};
const SETTLE_TICKS = 420; // 동기 settle 반복 (결정적 — 라이브 tick 없이 안정 좌표).

interface PkmGraphProps {
  nodes: PkmGraphNode[];
  edges: PkmGraphEdge[];
}

// ── 필터 그룹 (타입/scope → 사람이 읽는 묶음) ──────────────────────────
type FilterGroup = "personal" | "brand" | "structure" | "source";

const FILTER_META: ReadonlyArray<{
  key: FilterGroup;
  label: string;
  color: string;
}> = [
  { key: "personal", label: "개인", color: TOKEN.accent },
  { key: "brand", label: "브랜드", color: TOKEN.primary },
  { key: "structure", label: "구조", color: TOKEN.accent },
  { key: "source", label: "출처·영상", color: TOKEN.textMuted },
];

/** 노드를 필터 그룹으로 분류. user 는 루트라 항상 보임(그룹 없음 → null). */
function nodeGroup(n: PkmGraphNode): FilterGroup | null {
  if (n.type === "user") return null;
  if (n.type === "brand") return "brand";
  if (n.type === "domain" || n.type === "series") return "structure";
  if (n.type === "source" || n.type === "video") return "source";
  // pkm leaf — scope 로 개인/브랜드 구분.
  return n.scope === "personal" ? "personal" : "brand";
}

// ── force 레이아웃 (전체 그래프 1회 settle, 결정적) ─────────────────────
interface SimNode extends SimulationNodeDatum {
  id: string;
}

/**
 * 전체 그래프에 d3-force 를 동기 적용해 노드별 좌표 Map 을 만든다.
 * 초기 좌표는 golden-angle 나선(결정적) → 매 settle 이 유사 배치로 수렴(안정 UX).
 * 순수 함수 — useMemo 로 (nodes, edges) 가 바뀔 때만 재계산.
 */
function computeForceLayout(
  graphNodes: PkmGraphNode[],
  graphEdges: PkmGraphEdge[],
): Map<string, { x: number; y: number }> {
  const GOLDEN = Math.PI * (3 - Math.sqrt(5)); // ≈2.39996 rad
  const simNodes: SimNode[] = graphNodes.map((n, i) => {
    const r = 26 * Math.sqrt(i + 1);
    const a = i * GOLDEN;
    return { id: n.id, x: r * Math.cos(a), y: r * Math.sin(a) };
  });
  const idSet = new Set(simNodes.map((s) => s.id));
  const links: SimulationLinkDatum<SimNode>[] = graphEdges
    .filter((e) => idSet.has(e.source) && idSet.has(e.target))
    .map((e) => ({ source: e.source, target: e.target, kind: e.kind }) as never);

  const sim = forceSimulation<SimNode>(simNodes)
    .force("charge", forceManyBody().strength(-460))
    .force(
      "link",
      forceLink<SimNode, SimulationLinkDatum<SimNode>>(links)
        .id((d) => d.id)
        .distance((l) => LINK_DIST[(l as { kind?: string }).kind ?? ""] ?? 120)
        .strength(0.38),
    )
    .force("collide", forceCollide(74))
    .force("x", forceX(0).strength(0.045))
    .force("y", forceY(0).strength(0.045))
    .stop();

  for (let i = 0; i < SETTLE_TICKS; i++) sim.tick();

  const pos = new Map<string, { x: number; y: number }>();
  for (const s of simNodes) pos.set(s.id, { x: s.x ?? 0, y: s.y ?? 0 });
  return pos;
}

/** getPkmGraph → react-flow Node[]/Edge[] (필터 적용 + force 좌표 주입). */
function buildFlow(
  graphNodes: PkmGraphNode[],
  graphEdges: PkmGraphEdge[],
  positions: Map<string, { x: number; y: number }>,
  enabled: Set<FilterGroup>,
): { flowNodes: Node[]; flowEdges: Edge[] } {
  const visible = new Set<string>();
  for (const n of graphNodes) {
    const g = nodeGroup(n);
    if (g === null || enabled.has(g)) visible.add(n.id);
  }

  const flowNodes: Node[] = graphNodes
    .filter((n) => visible.has(n.id))
    .map((n) => ({
      id: n.id,
      position: positions.get(n.id) ?? { x: 0, y: 0 },
      data: { label: nodeLabel(n) },
      width: NODE_W,
      height: NODE_H,
      style: nodeStyle(n),
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      draggable: true,
      selectable: true,
    }));

  const flowEdges: Edge[] = graphEdges
    .filter((e) => visible.has(e.source) && visible.has(e.target))
    .map((e, i) => ({
      id: `${e.source}->${e.target}:${e.kind}:${i}`,
      source: e.source,
      target: e.target,
      style: {
        stroke:
          e.kind === "owns"
            ? TOKEN.primary
            : e.kind === "has_domain" || e.kind === "has_series"
              ? TOKEN.accent
              : TOKEN.borderDefault,
        strokeWidth: e.kind === "owns" ? 2 : 1.5,
        strokeDasharray: e.kind === "sourced_from" ? "4 3" : undefined,
      },
      animated: false,
    }));

  return { flowNodes, flowEdges };
}

/** locked 면 🔒 prefix. 너무 길면 잘라 노드 가독성 유지. */
function nodeLabel(n: PkmGraphNode): string {
  const base = n.label.length > 26 ? `${n.label.slice(0, 25)}…` : n.label;
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
  if (n.type === "domain") {
    return {
      ...common,
      background: TOKEN.surface,
      color: TOKEN.textDefault,
      border: `1.5px dashed ${TOKEN.accent}`,
      fontWeight: 600,
    };
  }
  if (n.type === "series") {
    return {
      ...common,
      background: TOKEN.bgSubtle,
      color: TOKEN.textDefault,
      border: `1.5px solid ${TOKEN.accent}`,
    };
  }
  if (n.type === "source" || n.type === "video") {
    return {
      ...common,
      background: TOKEN.surface,
      color: TOKEN.textMuted,
      border: `1.5px dotted ${TOKEN.textMuted}`,
      fontSize: 11,
      fontWeight: 500,
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
 * 데스크톱 PKM 동적 force 그래프. 부모(/brain page)가 데스크톱일 때만 dynamic import → 렌더.
 * 높이는 부모 컨테이너에 맞춤(부모가 명시적 높이를 줌).
 */
export default function PkmGraph({ nodes, edges }: PkmGraphProps) {
  // 전체 그래프 force 좌표 — (nodes, edges) 가 바뀔 때만 재계산(필터엔 불변 → 안정).
  const positions = useMemo(
    () => computeForceLayout(nodes, edges),
    [nodes, edges],
  );

  // 필터: 기본 전체 ON. user 루트는 항상 표시.
  const [enabled, setEnabled] = useState<Set<FilterGroup>>(
    () => new Set<FilterGroup>(FILTER_META.map((f) => f.key)),
  );

  // 그룹별 노드 수(칩 라벨 표시 + 0개 그룹 비활성).
  const counts = useMemo(() => {
    const c: Record<FilterGroup, number> = {
      personal: 0,
      brand: 0,
      structure: 0,
      source: 0,
    };
    for (const n of nodes) {
      const g = nodeGroup(n);
      if (g) c[g] += 1;
    }
    return c;
  }, [nodes]);

  const built = useMemo(
    () => buildFlow(nodes, edges, positions, enabled),
    [nodes, edges, positions, enabled],
  );

  // 드래그 위치 변경을 반영하기 위해 노드는 state 로 관리(필터/데이터 변경 시 재설정).
  const [rfNodes, setRfNodes] = useState<Node[]>(built.flowNodes);
  useEffect(() => {
    setRfNodes(built.flowNodes);
  }, [built.flowNodes]);

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setRfNodes((nds) => applyNodeChanges(changes, nds)),
    [],
  );

  const toggle = useCallback((key: FilterGroup) => {
    setEnabled((prev) => {
      const next = new Set(prev);
      if (next.has(key)) next.delete(key);
      else next.add(key);
      return next;
    });
  }, []);

  return (
    <div
      className="relative w-full h-full rounded-lg border border-border-default bg-surface"
      role="img"
      aria-label="내 2nd brain 동적 노드 그래프 (사용자·브랜드·PKM 관계도, 드래그·필터 가능)"
    >
      {/* 필터 칩 — 좌상단 오버레이. 그룹 토글로 노드 숨김(생존 노드 재배치 없음). */}
      <div className="absolute left-3 top-3 z-10 flex flex-wrap gap-1.5">
        {FILTER_META.map((f) => {
          const on = enabled.has(f.key);
          const n = counts[f.key];
          return (
            <button
              key={f.key}
              type="button"
              onClick={() => toggle(f.key)}
              disabled={n === 0}
              aria-pressed={on}
              className={[
                "flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-xs font-semibold transition-colors duration-fast",
                "disabled:opacity-40 disabled:cursor-not-allowed",
                on
                  ? "border-border-default bg-surface text-text-default shadow-sm"
                  : "border-border-default bg-bg-subtle text-text-muted line-through",
              ].join(" ")}
            >
              <span
                className="inline-block h-2 w-2 rounded-full"
                style={{ background: f.color, opacity: on ? 1 : 0.35 }}
              />
              {f.label}
              <span className="text-text-muted">{n}</span>
            </button>
          );
        })}
      </div>

      <ReactFlow
        nodes={rfNodes}
        edges={built.flowEdges}
        onNodesChange={onNodesChange}
        fitView
        fitViewOptions={{ padding: 0.2 }}
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
