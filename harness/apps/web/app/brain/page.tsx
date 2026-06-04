"use client";

/**
 * Phase 19 Slice S2 — 내 2nd brain (PKM) 카드/리스트 페이지 (`/brain`).
 *
 * 사용자의 개인 PKM + 브랜드별 PKM 을 scope 로 묶어 보여주는 **모바일 우선 카드/리스트** 뷰.
 *   - 데스크톱 그래프 뷰는 S3, 큐레이션(편집/삭제) 액션은 S4 (본 슬라이스는 read-only 표시).
 *   - S1 backend GET /api/v1/me/pkm-graph 가 {nodes, edges, summary} 를 반환 →
 *     본 페이지가 scope 로 그룹핑해 칩/카드로 렌더.
 *
 * 구조:
 *   상단 요약(개인 N · 브랜드 N)
 *   개인 PKM 섹션: scope==="personal" 노드 → 칩 카드 (label + entry_type 배지 + 🔒 if locked)
 *   브랜드별 섹션: brand 노드별 sub-header + 그 brand 의 scope==="brand" PKM 칩 카드
 *     (has_brand_pkm 엣지로 brand→pkm 연결)
 *   empty state: 노드가 user 만이거나 PKM 0 → 친근한 안내 + "브랜딩 세션으로 채우기"(/new/branding)
 *
 * StrictMode: GET 은 멱등(side-effect 없음) — startedRef 가드 불필요. 단순 loading/error/data 상태만.
 *
 * 참조:
 *   - apps/web/lib/api.ts (getPkmGraph)
 *   - apps/web/lib/types.ts (PkmGraphNode / PkmGraphEdge / PkmGraphResponse)
 *   - apps/web/components/AuthGuard.tsx (authed page wrapper 패턴)
 *   - apps/web/app/new/branding/page.tsx (header / 카드 / 토큰 / 모바일 한 손 UX 원형)
 *   - apps/web/design.md §2 (카드 단위 / 모바일 한 손 / 제작 기능 미포함)
 */

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import AuthGuard from "@/components/AuthGuard"; // 외부 wrapper (다른 authed page 와 동일 패턴)
import { getPkmGraph } from "@/lib/api";
import type { PkmGraphNode, PkmGraphResponse } from "@/lib/types";

type Phase = "loading" | "error" | "data";

/** brand 노드 + 그 brand 에 속한 PKM 노드 묶음 (UI 렌더 단위). */
interface BrandGroup {
  brand: PkmGraphNode;
  entries: PkmGraphNode[];
}

export default function BrainPage() {
  return (
    <AuthGuard>
      <BrainPageContent />
    </AuthGuard>
  );
}

function BrainPageContent() {
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>("loading");
  const [graph, setGraph] = useState<PkmGraphResponse | null>(null);

  useEffect(() => {
    let mounted = true;
    // GET 멱등 — StrictMode 이중 invoke 해도 side-effect 없음. mounted 가드로 unmount 후 setState 만 방지.
    void getPkmGraph()
      .then((res) => {
        if (!mounted) return;
        setGraph(res);
        setPhase("data");
      })
      .catch(() => {
        if (!mounted) return;
        setPhase("error");
      });
    return () => {
      mounted = false;
    };
  }, []);

  // scope 로 그룹핑 (렌더 안정성 위해 graph 기준 memo).
  const { personal, brandGroups } = useMemo(
    () => groupByScope(graph),
    [graph],
  );

  const summary = graph?.summary ?? { personal: 0, brand: 0, brands: 0 };
  // user 노드만 있거나(=PKM 0) summary 가 전부 0 → empty state.
  const isEmpty =
    phase === "data" && personal.length === 0 && brandGroups.length === 0;

  return (
    <main className="min-h-screen bg-bg-default flex flex-col">
      {/* Header */}
      <header className="border-b border-border-default px-4 py-3 sticky top-0 bg-bg-default z-10">
        <div className="max-w-2xl mx-auto flex items-center justify-between">
          <button
            type="button"
            className="text-text-muted text-sm font-medium hover:text-text-default transition-colors duration-fast"
            onClick={() => router.push("/")}
            aria-label="홈으로"
          >
            {"←"} home
          </button>
          <div className="text-text-muted text-sm font-medium">내 brain</div>
          <div className="w-12" aria-hidden="true" />
        </div>
      </header>

      {/* Title + 요약 */}
      <section className="px-4 py-6 max-w-2xl mx-auto w-full">
        <h1 className="text-3xl font-bold text-text-default mb-2">
          내 2nd brain
        </h1>
        <p className="text-sm text-text-muted">
          AI가 당신의 취향·브랜드를 기억해 기획에 반영해요. 피드백을 줄수록 더 똑똑해져요.
        </p>
        {phase === "data" && !isEmpty && (
          <div className="mt-3 flex flex-wrap gap-2" aria-label="요약">
            <span className="text-xs px-2 py-0.5 rounded-full bg-bg-subtle text-text-muted">
              개인 {summary.personal}
            </span>
            <span className="text-xs px-2 py-0.5 rounded-full bg-bg-subtle text-text-muted">
              브랜드 {summary.brand}
              {summary.brands > 0 && ` · ${summary.brands}개 브랜드`}
            </span>
          </div>
        )}
      </section>

      {/* 로딩 스피너 */}
      {phase === "loading" && (
        <section className="flex-1 flex items-center justify-center px-4 py-10">
          <div
            className="w-8 h-8 border-2 border-border-default border-t-primary rounded-full animate-spin"
            aria-label="불러오는 중"
            role="status"
          />
        </section>
      )}

      {/* 에러 */}
      {phase === "error" && (
        <section className="px-4 pb-4 max-w-2xl mx-auto w-full">
          <div
            role="alert"
            className="rounded-md border border-border-default bg-bg-subtle px-4 py-3 text-sm text-text-default"
          >
            brain 을 불러오지 못했어요. 잠시 후 다시 시도해주세요.
          </div>
          <button
            type="button"
            onClick={() => window.location.reload()}
            className="mt-4 w-full py-3 rounded-md font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed transition-colors duration-fast"
            aria-label="다시 시도"
          >
            다시 시도 ↻
          </button>
        </section>
      )}

      {/* Empty state */}
      {isEmpty && (
        <section className="flex-1 px-4 pb-10 max-w-2xl mx-auto w-full">
          <div className="rounded-lg border border-border-default bg-surface p-6 text-center">
            <div className="text-4xl mb-3" aria-hidden="true">
              🧠
            </div>
            <h2 className="font-semibold text-lg text-text-default mb-2">
              아직 brain 이 비어 있어요
            </h2>
            <p className="text-sm text-text-muted leading-normal mb-1">
              브랜딩 세션으로 취향·방향을 정하면 여기에 차곡차곡 쌓여요.
            </p>
            <p className="text-sm text-text-muted leading-normal">
              기획안에 남긴 피드백(좋아요/반려)도 AI가 학습해 채워 나가요.
            </p>
            <Link
              href="/new/branding"
              className="mt-5 inline-flex w-full items-center justify-center py-3 rounded-md font-semibold text-text-inverse bg-primary hover:bg-primary-hover active:bg-primary-pressed transition-colors duration-fast"
              aria-label="브랜딩 세션으로 채우기"
            >
              브랜딩 세션으로 채우기 ▶
            </Link>
          </div>
        </section>
      )}

      {/* 데이터 — scope 섹션 */}
      {phase === "data" && !isEmpty && (
        <section className="flex-1 px-4 pb-10 max-w-2xl mx-auto w-full flex flex-col gap-8">
          {/* 개인 PKM */}
          {personal.length > 0 && (
            <div>
              <h2 className="font-semibold text-lg text-text-default mb-3">
                개인 PKM
              </h2>
              <div className="flex flex-col gap-3" aria-label="개인 PKM 목록">
                {personal.map((node) => (
                  <PkmChip key={node.id} node={node} />
                ))}
              </div>
            </div>
          )}

          {/* 브랜드별 */}
          {brandGroups.length > 0 && (
            <div>
              <h2 className="font-semibold text-lg text-text-default mb-3">
                브랜드별
              </h2>
              <div className="flex flex-col gap-6">
                {brandGroups.map((group) => (
                  <div key={group.brand.id}>
                    <h3 className="text-sm font-semibold text-text-muted mb-2">
                      {group.brand.label}
                    </h3>
                    {group.entries.length > 0 ? (
                      <div
                        className="flex flex-col gap-3"
                        aria-label={`${group.brand.label} PKM 목록`}
                      >
                        {group.entries.map((node) => (
                          <PkmChip key={node.id} node={node} />
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-text-placeholder">
                        아직 이 브랜드의 PKM 이 없어요.
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </section>
      )}
    </main>
  );
}

/**
 * PKM 노드 1개 → 칩/카드. label + entry_type 배지 + 🔒(locked).
 * read-only — 큐레이션 액션은 S4 (클릭 동작 없음).
 */
function PkmChip({ node }: { node: PkmGraphNode }) {
  return (
    <div className="w-full text-left p-4 rounded-lg border border-border-default bg-surface">
      <div className="flex items-start justify-between gap-2">
        <span className="text-base text-text-default leading-normal">
          {node.label}
        </span>
        {node.locked ? (
          <span
            className="shrink-0 text-base"
            role="img"
            aria-label="잠금(사용자 고정)"
            title="사용자가 고정한 항목"
          >
            🔒
          </span>
        ) : null}
      </div>
      {node.entry_type && (
        <span className="mt-2 inline-block text-xs px-2 py-0.5 rounded-full bg-bg-subtle text-text-muted">
          {node.entry_type}
        </span>
      )}
    </div>
  );
}

/**
 * graph 응답을 scope 섹션 렌더용으로 그룹핑.
 *   - personal: scope==="personal" PKM 노드
 *   - brandGroups: brand 노드별 + has_brand_pkm 엣지로 연결된 scope==="brand" PKM 노드
 */
function groupByScope(graph: PkmGraphResponse | null): {
  personal: PkmGraphNode[];
  brandGroups: BrandGroup[];
} {
  if (!graph) return { personal: [], brandGroups: [] };

  const nodeById = new Map<string, PkmGraphNode>();
  for (const n of graph.nodes) nodeById.set(n.id, n);

  const personal = graph.nodes.filter(
    (n) => n.type === "pkm" && n.scope === "personal",
  );

  const brands = graph.nodes.filter((n) => n.type === "brand");
  // brand id → 그 brand 에 매달린 PKM 노드들 (has_brand_pkm: brand→pkm).
  const entriesByBrand = new Map<string, PkmGraphNode[]>();
  for (const b of brands) entriesByBrand.set(b.id, []);
  for (const e of graph.edges) {
    if (e.kind !== "has_brand_pkm") continue;
    const bucket = entriesByBrand.get(e.source);
    const child = nodeById.get(e.target);
    if (bucket && child && child.type === "pkm" && child.scope === "brand") {
      bucket.push(child);
    }
  }

  const brandGroups: BrandGroup[] = brands.map((brand) => ({
    brand,
    entries: entriesByBrand.get(brand.id) ?? [],
  }));

  return { personal, brandGroups };
}
