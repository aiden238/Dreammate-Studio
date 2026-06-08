"use client";

/**
 * Phase 19 Slice S2 — 내 2nd brain (PKM) 카드/리스트 페이지 (`/brain`).
 *
 * 사용자의 개인 PKM + 브랜드별 PKM 을 scope 로 묶어 보여주는 **모바일 우선 카드/리스트** 뷰.
 *   - 데스크톱 그래프 뷰는 S3.
 *   - S4: 각 PKM 칩에 **큐레이션 컨트롤**(잠금 토글 🔒 / 편집 / 삭제) 추가 — PATCH/DELETE
 *     /api/v1/me/pkm/{node_id} 호출 후 그래프 refetch. user/brand(non-pkm) 노드는 대상 아님.
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

import { useCallback, useEffect, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { useRouter } from "next/navigation";

import AuthGuard from "@/components/AuthGuard"; // 외부 wrapper (다른 authed page 와 동일 패턴)
import StructureCreateInput from "@/components/brain/StructureCreateInput";
import StructureRenameInput from "@/components/brain/StructureRenameInput";
import {
  createDomain,
  createSeries,
  createVideo,
  deleteDomain,
  deletePkmNode,
  deleteSeries,
  deleteVideo,
  getConcept,
  getPkmGraph,
  updateDomain,
  updatePkmNode,
  updateSeries,
  updateVideo,
} from "@/lib/api";
import type { ConceptResponse, PkmGraphNode, PkmGraphResponse } from "@/lib/types";
import { useMediaQuery } from "@/lib/use_media_query";

type Phase = "loading" | "error" | "data";

/**
 * S3 — 데스크톱 전용 노드 그래프(react-flow).
 *   - ssr:false + 아래 데스크톱 분기에서만 렌더 → dynamic import 가 데스크톱에서만 트리거 =
 *     **모바일 번들에 react-flow(@xyflow/react) 미포함**.
 *   - loading 은 기존 페이지와 동일한 스피너 톤.
 */
const PkmGraph = dynamic(() => import("@/components/brain/PkmGraph"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-full flex items-center justify-center rounded-lg border border-border-default bg-surface">
      <div
        className="w-8 h-8 border-2 border-border-default border-t-primary rounded-full animate-spin"
        aria-label="그래프 불러오는 중"
        role="status"
      />
    </div>
  ),
});

/** 데스크톱 뷰 모드 — 기본 그래프, "리스트로 보기" 로 카드 복귀. */
type DesktopView = "graph" | "list";

/** brand 노드 + 그 brand 에 속한 PKM 노드 묶음 (UI 렌더 단위). */
interface BrandGroup {
  brand: PkmGraphNode;
  entries: PkmGraphNode[];
}

// ─── Phase 22 S2 — 4계층 구조 트리 (brand → domain → series) ────────────
// 기존 graph(nodes/edges)에서 파생. has_domain(brand→domain)/has_series(domain→series) 엣지로 묶는다.

/** series 노드 + 그 series 에 속한 video 노드들 (Phase 26 — 4계층 최하단). */
interface SeriesNode {
  series: PkmGraphNode;
  videos: PkmGraphNode[];
}

/** domain 노드 + 그 domain 에 속한 series(각자 video 포함). */
interface DomainNode {
  domain: PkmGraphNode;
  series: SeriesNode[];
}

/** brand 노드 + 그 brand 에 속한 domain(각자 series 포함). */
interface StructureBrand {
  brand: PkmGraphNode;
  domains: DomainNode[];
}

/**
 * graph 노드 id("domain:<uuid>"/"series:<uuid>"/"video:<uuid>")에서 접두어를 벗겨 bare uuid 반환.
 * 구조 편집/삭제 API(PATCH/DELETE /me/domains|series|videos/{id})는 접두어 없는 id 를 받는다.
 * 접두어가 없으면(방어적) 원본을 그대로 반환.
 */
function stripNodePrefix(
  nodeId: string,
  prefix: "domain:" | "series:" | "video:",
): string {
  return nodeId.startsWith(prefix) ? nodeId.slice(prefix.length) : nodeId;
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
  // Phase 28 S3 — 나만의 컨셉 수렴 (부가 표시, graceful: 실패/OFF → null = 카드 숨김).
  const [concept, setConcept] = useState<ConceptResponse | null>(null);
  // 큐레이션 동작 중인 node_id (중복 클릭 방지 + 스피너). null = 유휴.
  const [busyNodeId, setBusyNodeId] = useState<string | null>(null);
  // S2(Phase 24): 인라인 rename 중인 구조 노드 id(graph 접두어 그대로). null = 표시 모드.
  const [renamingNodeId, setRenamingNodeId] = useState<string | null>(null);

  // S3: 데스크톱(≥1024px) 분기 + 데스크톱 뷰 모드(그래프 기본 ↔ 리스트).
  // 모바일(false)에서는 PkmGraph 가 렌더되지 않아 react-flow dynamic import 미트리거.
  const isDesktop = useMediaQuery("(min-width: 1024px)");
  const [desktopView, setDesktopView] = useState<DesktopView>("graph");

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
    // 컨셉 수렴 — 그래프와 독립(실패해도 본문 영향 0). gated OFF/무데이터면 enabled=false.
    void getConcept().then((c) => {
      if (mounted) setConcept(c);
    });
    return () => {
      mounted = false;
    };
  }, []);

  // 큐레이션 동작 후 그래프 재조회 (refetch — 단일 source of truth 유지).
  const refetch = useCallback(async () => {
    const res = await getPkmGraph();
    setGraph(res);
    setPhase("data");
  }, []);

  // 잠금 토글 — PATCH {locked}. 동작 후 refetch.
  const handleToggleLock = useCallback(
    async (node: PkmGraphNode) => {
      if (busyNodeId) return; // 동시 동작 방지.
      setBusyNodeId(node.id);
      try {
        await updatePkmNode(node.id, { locked: !node.locked });
        await refetch();
      } catch {
        // graceful — 사용자에게 알리고 현 상태 유지 (그래프 변경 없음).
        if (typeof window !== "undefined") {
          window.alert("변경에 실패했어요. 잠시 후 다시 시도해주세요.");
        }
      } finally {
        setBusyNodeId(null);
      }
    },
    [busyNodeId, refetch],
  );

  // 편집 — prompt 로 새 content 입력 후 PATCH {content}. 동작 후 refetch.
  const handleEdit = useCallback(
    async (node: PkmGraphNode) => {
      if (busyNodeId) return;
      if (typeof window === "undefined") return;
      const next = window.prompt("내용을 수정하세요", node.label);
      if (next === null) return; // 취소.
      const trimmed = next.trim();
      if (trimmed === "" || trimmed === node.label) return; // 빈 값/무변경 → no-op.
      setBusyNodeId(node.id);
      try {
        await updatePkmNode(node.id, { content: trimmed });
        await refetch();
      } catch {
        window.alert("수정에 실패했어요. 잠시 후 다시 시도해주세요.");
      } finally {
        setBusyNodeId(null);
      }
    },
    [busyNodeId, refetch],
  );

  // 삭제 — 확인 후 DELETE. 잠금(보호) 항목은 확인 문구를 강조. 동작 후 refetch.
  const handleDelete = useCallback(
    async (node: PkmGraphNode) => {
      if (busyNodeId) return;
      if (typeof window === "undefined") return;
      const msg = node.locked
        ? "🔒 고정(보호)한 항목이에요. 정말 삭제할까요? 되돌릴 수 없어요."
        : "이 항목을 삭제할까요? 되돌릴 수 없어요.";
      if (!window.confirm(msg)) return;
      setBusyNodeId(node.id);
      try {
        await deletePkmNode(node.id);
        await refetch();
      } catch {
        window.alert("삭제에 실패했어요. 잠시 후 다시 시도해주세요.");
      } finally {
        setBusyNodeId(null);
      }
    },
    [busyNodeId, refetch],
  );

  // 구조 생성(S2) — domain 생성 후 refetch (그래프에 has_domain 노드/엣지 노출).
  const handleCreateDomain = useCallback(
    async (brandId: string, name: string) => {
      await createDomain(brandId, name);
      await refetch();
    },
    [refetch],
  );

  // 구조 생성(S2) — series 생성 후 refetch (그래프에 has_series 노드/엣지 노출).
  const handleCreateSeries = useCallback(
    async (domainId: string, name: string) => {
      await createSeries(domainId, name);
      await refetch();
    },
    [refetch],
  );

  // 구조 생성(Phase 26 S3) — video 생성 후 refetch (그래프에 has_video 노드/엣지 노출).
  //   ★ Video 는 name 이 아닌 title (video_projects 스키마).
  const handleCreateVideo = useCallback(
    async (seriesId: string, title: string) => {
      await createVideo(stripNodePrefix(seriesId, "series:"), title);
      await refetch();
    },
    [refetch],
  );

  // ── Phase 24 S2 — 구조 편집/삭제 (domain/series rename + delete) ──────────
  // graph 노드 id 는 "domain:<uuid>"/"series:<uuid>" 접두어 → API 는 bare uuid 를 받으므로 벗긴다.

  // rename 저장 — updateDomain → refetch. 성공 시 컴포넌트가 onDone 으로 표시 모드 복귀.
  const handleRenameDomain = useCallback(
    async (domainNodeId: string, name: string) => {
      await updateDomain(stripNodePrefix(domainNodeId, "domain:"), name);
      await refetch();
    },
    [refetch],
  );

  const handleRenameSeries = useCallback(
    async (seriesNodeId: string, name: string) => {
      await updateSeries(stripNodePrefix(seriesNodeId, "series:"), name);
      await refetch();
    },
    [refetch],
  );

  // Phase 26 S3 — video 제목 변경. graph 노드 id "video:<uuid>" → bare uuid. ★ title.
  const handleRenameVideo = useCallback(
    async (videoNodeId: string, title: string) => {
      await updateVideo(stripNodePrefix(videoNodeId, "video:"), title);
      await refetch();
    },
    [refetch],
  );

  // 삭제 — 확인 후 DELETE. domain 삭제는 하위 series 캐스케이드를 명시 경고. 동작 후 refetch.
  const handleDeleteDomain = useCallback(
    async (node: PkmGraphNode) => {
      if (busyNodeId) return;
      if (typeof window === "undefined") return;
      if (
        !window.confirm(
          "도메인 삭제 시 하위 시리즈도 함께 삭제됩니다. 정말 삭제할까요? 되돌릴 수 없어요.",
        )
      ) {
        return;
      }
      setBusyNodeId(node.id);
      try {
        await deleteDomain(stripNodePrefix(node.id, "domain:"));
        await refetch();
      } catch {
        window.alert("삭제에 실패했어요. 잠시 후 다시 시도해주세요.");
      } finally {
        setBusyNodeId(null);
      }
    },
    [busyNodeId, refetch],
  );

  const handleDeleteSeries = useCallback(
    async (node: PkmGraphNode) => {
      if (busyNodeId) return;
      if (typeof window === "undefined") return;
      if (
        !window.confirm("이 시리즈를 삭제할까요? 되돌릴 수 없어요.")
      ) {
        return;
      }
      setBusyNodeId(node.id);
      try {
        await deleteSeries(stripNodePrefix(node.id, "series:"));
        await refetch();
      } catch {
        window.alert("삭제에 실패했어요. 잠시 후 다시 시도해주세요.");
      } finally {
        setBusyNodeId(null);
      }
    },
    [busyNodeId, refetch],
  );

  const handleDeleteVideo = useCallback(
    async (node: PkmGraphNode) => {
      if (busyNodeId) return;
      if (typeof window === "undefined") return;
      if (
        !window.confirm("이 영상을 삭제할까요? 되돌릴 수 없어요.")
      ) {
        return;
      }
      setBusyNodeId(node.id);
      try {
        await deleteVideo(stripNodePrefix(node.id, "video:"));
        await refetch();
      } catch {
        window.alert("삭제에 실패했어요. 잠시 후 다시 시도해주세요.");
      } finally {
        setBusyNodeId(null);
      }
    },
    [busyNodeId, refetch],
  );

  // scope 로 그룹핑 (렌더 안정성 위해 graph 기준 memo).
  const { personal, brandGroups } = useMemo(
    () => groupByScope(graph),
    [graph],
  );

  // S2: brand → domain → series 4계층 트리 (구조 생성 섹션용). graph 기준 memo.
  const structureBrands = useMemo(() => buildStructureTree(graph), [graph]);

  const summary = graph?.summary ?? { personal: 0, brand: 0, brands: 0 };
  // user 노드만 있거나(=PKM 0) summary 가 전부 0 → empty state.
  const isEmpty =
    phase === "data" && personal.length === 0 && brandGroups.length === 0;

  // S3: 데이터 있고 데스크톱이며 그래프 모드일 때만 그래프 렌더.
  //   → 모바일/리스트 모드/empty/loading/error 에서는 기존 카드 경로 그대로(무변경).
  const showGraph =
    phase === "data" && !isEmpty && isDesktop && desktopView === "graph";

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
        {/* Phase 28 S3 — 나만의 컨셉 수렴 카드 (gated/graceful: enabled+concept 있을 때만). */}
        {concept?.enabled && concept.concept && (
          <div className="mt-5 rounded-xl border border-border-default bg-surface p-4 shadow-sm">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-primary text-text-inverse">
                내 컨셉
              </span>
              <span className="text-[11px] text-text-muted">
                신호 {concept.based_on}개 종합
              </span>
            </div>
            <p className="text-base font-bold text-text-default leading-snug">
              {concept.concept}
            </p>
            {concept.pillars.length > 0 && (
              <ul className="mt-3 space-y-1.5">
                {concept.pillars.map((p, i) => (
                  <li key={i} className="text-sm text-text-default">
                    <span className="font-semibold text-primary">· {p.label}</span>
                    {p.detail && (
                      <span className="text-text-muted"> — {p.detail}</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
            {concept.conflicts.length > 0 && (
              <div className="mt-3 rounded-lg border border-warning-500 bg-warning-50 p-2.5">
                <p className="text-xs font-semibold text-warning-700 mb-1">
                  ⚠ 방향이 엇갈리는 신호
                </p>
                <ul className="space-y-1">
                  {concept.conflicts.map((c, i) => (
                    <li key={i} className="text-xs text-text-muted leading-relaxed">
                      <span className="text-text-default">{c.a}</span>
                      {" ↔ "}
                      <span className="text-text-default">{c.b}</span>
                      {c.note && <span> — {c.note}</span>}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <p className="mt-2 text-[11px] text-text-muted">
              피드백·레퍼런스를 줄수록 컨셉이 또렷해지고 모순이 정리돼요.
            </p>
          </div>
        )}
        {/* S3: 데스크톱 전용 뷰 토글 (그래프 ↔ 리스트). 모바일은 미노출 → 카드 경로 무변경. */}
        {phase === "data" && !isEmpty && isDesktop && (
          <div
            className="mt-4 inline-flex rounded-md border border-border-default overflow-hidden"
            role="group"
            aria-label="뷰 전환"
          >
            <button
              type="button"
              onClick={() => setDesktopView("graph")}
              aria-pressed={desktopView === "graph"}
              className={`px-3 py-1.5 text-sm font-medium transition-colors duration-fast ${
                desktopView === "graph"
                  ? "bg-primary text-text-inverse"
                  : "bg-surface text-text-muted hover:bg-bg-subtle"
              }`}
            >
              그래프
            </button>
            <button
              type="button"
              onClick={() => setDesktopView("list")}
              aria-pressed={desktopView === "list"}
              className={`px-3 py-1.5 text-sm font-medium transition-colors duration-fast ${
                desktopView === "list"
                  ? "bg-primary text-text-inverse"
                  : "bg-surface text-text-muted hover:bg-bg-subtle"
              }`}
            >
              리스트로 보기
            </button>
          </div>
        )}
      </section>

      {/* S3: 데스크톱 그래프 (그래프 모드일 때만). dynamic ssr:false → 데스크톱에서만 로드. */}
      {showGraph && graph && (
        <section className="flex-1 px-4 pb-10 w-full max-w-6xl mx-auto flex flex-col min-h-0">
          <div className="h-[70vh] min-h-[480px]">
            <PkmGraph nodes={graph.nodes} edges={graph.edges} />
          </div>
          <p className="mt-3 text-xs text-text-muted">
            드래그로 이동 · 스크롤로 확대/축소. 항목 잠금·편집·삭제는 “리스트로 보기”에서 할 수 있어요.
          </p>
        </section>
      )}

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

      {/* 데이터 — scope 섹션 (모바일 항상 / 데스크톱은 리스트 모드일 때. 그래프 모드면 미렌더) */}
      {phase === "data" && !isEmpty && !showGraph && (
        <section className="flex-1 px-4 pb-10 max-w-2xl mx-auto w-full flex flex-col gap-8">
          {/* 개인 PKM */}
          {personal.length > 0 && (
            <div>
              <h2 className="font-semibold text-lg text-text-default mb-3">
                개인 PKM
              </h2>
              <div className="flex flex-col gap-3" aria-label="개인 PKM 목록">
                {personal.map((node) => (
                  <PkmChip
                    key={node.id}
                    node={node}
                    busy={busyNodeId === node.id}
                    disabled={busyNodeId !== null && busyNodeId !== node.id}
                    onToggleLock={handleToggleLock}
                    onEdit={handleEdit}
                    onDelete={handleDelete}
                  />
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
                          <PkmChip
                            key={node.id}
                            node={node}
                            busy={busyNodeId === node.id}
                            disabled={
                              busyNodeId !== null && busyNodeId !== node.id
                            }
                            onToggleLock={handleToggleLock}
                            onEdit={handleEdit}
                            onDelete={handleDelete}
                          />
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

          {/* Phase 22 S2 — 지식 구조 (4계층): brand → domain → series 생성 */}
          <div>
            <h2 className="font-semibold text-lg text-text-default mb-1">
              지식 구조 (4계층)
            </h2>
            <p className="text-sm text-text-muted mb-3">
              브랜드 안에 도메인(주제 묶음)과 시리즈(연재)를 만들어 기획을 정리해요.
            </p>
            {structureBrands.length > 0 ? (
              <div className="flex flex-col gap-6">
                {structureBrands.map((sb) => (
                  <div
                    key={sb.brand.id}
                    className="rounded-lg border border-border-default bg-surface p-4"
                  >
                    <h3 className="text-sm font-semibold text-text-default mb-1">
                      {sb.brand.label}
                    </h3>
                    {/* 도메인 추가 (brand 단위) */}
                    <StructureCreateInput
                      placeholder="새 도메인 이름"
                      buttonLabel="+ 도메인"
                      ariaLabel={`${sb.brand.label} 도메인 추가`}
                      disabled={renamingNodeId !== null}
                      onSubmit={(name) =>
                        handleCreateDomain(sb.brand.id, name)
                      }
                    />
                    {/* 도메인 목록 + 각자의 시리즈 */}
                    {sb.domains.length > 0 ? (
                      <div className="mt-3 flex flex-col gap-3">
                        {sb.domains.map((dn) => (
                          <div
                            key={dn.domain.id}
                            className="rounded-md border border-border-default bg-bg-subtle p-3"
                          >
                            {/* 도메인 헤더 — 이름 + ✏️/🗑 (rename 중이면 인라인 입력) */}
                            {renamingNodeId === dn.domain.id ? (
                              <StructureRenameInput
                                initialValue={dn.domain.label}
                                ariaLabel={`${dn.domain.label} 도메인 이름 수정`}
                                disabled={busyNodeId !== null}
                                onSubmit={(name) =>
                                  handleRenameDomain(dn.domain.id, name)
                                }
                                onDone={() => setRenamingNodeId(null)}
                              />
                            ) : (
                              <StructureRowControls
                                label={dn.domain.label}
                                busy={busyNodeId === dn.domain.id}
                                disabled={
                                  renamingNodeId !== null ||
                                  (busyNodeId !== null &&
                                    busyNodeId !== dn.domain.id)
                                }
                                labelClassName="text-sm font-medium text-text-default"
                                editAriaLabel="도메인 이름 수정"
                                deleteAriaLabel="도메인 삭제"
                                onEdit={() => setRenamingNodeId(dn.domain.id)}
                                onDelete={() => handleDeleteDomain(dn.domain)}
                              />
                            )}
                            {/* 시리즈 목록 (각 시리즈 아래 영상 목록 + "+영상") */}
                            {dn.series.length > 0 ? (
                              <ul className="mt-2 flex flex-col gap-2">
                                {dn.series.map((sn) => (
                                  <li key={sn.series.id}>
                                    {/* 시리즈 헤더 — 이름 + ✏️/🗑 (rename 중이면 인라인 입력) */}
                                    {renamingNodeId === sn.series.id ? (
                                      <StructureRenameInput
                                        initialValue={sn.series.label}
                                        ariaLabel={`${sn.series.label} 시리즈 이름 수정`}
                                        disabled={busyNodeId !== null}
                                        onSubmit={(name) =>
                                          handleRenameSeries(sn.series.id, name)
                                        }
                                        onDone={() => setRenamingNodeId(null)}
                                      />
                                    ) : (
                                      <StructureRowControls
                                        label={sn.series.label}
                                        busy={busyNodeId === sn.series.id}
                                        disabled={
                                          renamingNodeId !== null ||
                                          (busyNodeId !== null &&
                                            busyNodeId !== sn.series.id)
                                        }
                                        labelClassName="text-sm text-text-muted before:content-['•'] before:mr-2 before:text-text-placeholder"
                                        editAriaLabel="시리즈 이름 수정"
                                        deleteAriaLabel="시리즈 삭제"
                                        onEdit={() =>
                                          setRenamingNodeId(sn.series.id)
                                        }
                                        onDelete={() =>
                                          handleDeleteSeries(sn.series)
                                        }
                                      />
                                    )}
                                    {/* 영상 목록 (시리즈보다 한 단계 더 들여쓰기) */}
                                    <div className="ml-4 mt-1">
                                      {sn.videos.length > 0 ? (
                                        <ul className="flex flex-col gap-1">
                                          {sn.videos.map((v) =>
                                            renamingNodeId === v.id ? (
                                              <li key={v.id} className="mt-1">
                                                <StructureRenameInput
                                                  initialValue={v.label}
                                                  ariaLabel={`${v.label} 영상 제목 수정`}
                                                  disabled={busyNodeId !== null}
                                                  onSubmit={(title) =>
                                                    handleRenameVideo(
                                                      v.id,
                                                      title,
                                                    )
                                                  }
                                                  onDone={() =>
                                                    setRenamingNodeId(null)
                                                  }
                                                />
                                              </li>
                                            ) : (
                                              <li key={v.id}>
                                                <StructureRowControls
                                                  label={v.label}
                                                  busy={busyNodeId === v.id}
                                                  disabled={
                                                    renamingNodeId !== null ||
                                                    (busyNodeId !== null &&
                                                      busyNodeId !== v.id)
                                                  }
                                                  labelClassName="text-sm text-text-muted before:content-['▸'] before:mr-2 before:text-text-placeholder"
                                                  editAriaLabel="영상 제목 수정"
                                                  deleteAriaLabel="영상 삭제"
                                                  onEdit={() =>
                                                    setRenamingNodeId(v.id)
                                                  }
                                                  onDelete={() =>
                                                    handleDeleteVideo(v)
                                                  }
                                                />
                                              </li>
                                            ),
                                          )}
                                        </ul>
                                      ) : null}
                                      {/* 영상 추가 (series 단위) */}
                                      <StructureCreateInput
                                        placeholder="새 영상 제목"
                                        buttonLabel="+ 영상"
                                        ariaLabel={`${sn.series.label} 영상 추가`}
                                        disabled={renamingNodeId !== null}
                                        onSubmit={(title) =>
                                          handleCreateVideo(
                                            sn.series.id,
                                            title,
                                          )
                                        }
                                      />
                                    </div>
                                  </li>
                                ))}
                              </ul>
                            ) : null}
                            {/* 시리즈 추가 (domain 단위) */}
                            <StructureCreateInput
                              placeholder="새 시리즈 이름"
                              buttonLabel="+ 시리즈"
                              ariaLabel={`${dn.domain.label} 시리즈 추가`}
                              disabled={renamingNodeId !== null}
                              onSubmit={(name) =>
                                handleCreateSeries(dn.domain.id, name)
                              }
                            />
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="mt-2 text-sm text-text-placeholder">
                        아직 도메인이 없어요. 위에서 첫 도메인을 만들어 보세요.
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-text-placeholder">
                브랜드를 먼저 만들면 그 안에 도메인·시리즈를 만들 수 있어요.
              </p>
            )}
          </div>
        </section>
      )}
    </main>
  );
}

/** PkmChip props — 노드 + 큐레이션 핸들러(S4) + busy/disabled 상태. */
interface PkmChipProps {
  node: PkmGraphNode;
  /** 이 칩이 동작 중(스피너/비활성). */
  busy: boolean;
  /** 다른 칩이 동작 중이라 이 칩의 액션을 잠시 막음. */
  disabled: boolean;
  onToggleLock: (node: PkmGraphNode) => void;
  onEdit: (node: PkmGraphNode) => void;
  onDelete: (node: PkmGraphNode) => void;
}

/**
 * PKM 노드 1개 → 칩/카드. label + entry_type 배지 + 🔒(locked) + 큐레이션 컨트롤(S4).
 *   - 잠금 토글(🔒/🔓): PATCH {locked}.
 *   - 편집(✏️): prompt 로 새 content → PATCH {content}.
 *   - 삭제(🗑): 확인 후 DELETE (잠금 항목은 확인 문구 강조).
 * 한 손 모바일 — 버튼은 충분한 탭 타깃(min 44px 높이), 우측 정렬.
 */
function PkmChip({
  node,
  busy,
  disabled,
  onToggleLock,
  onEdit,
  onDelete,
}: PkmChipProps) {
  const blocked = busy || disabled;
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
      <div className="mt-2 flex items-center justify-between gap-2">
        {node.entry_type ? (
          <span className="inline-block text-xs px-2 py-0.5 rounded-full bg-bg-subtle text-text-muted">
            {node.entry_type}
          </span>
        ) : (
          <span aria-hidden="true" />
        )}
        {/* 큐레이션 컨트롤 (S4) */}
        <div className="flex items-center gap-1 shrink-0" aria-label="큐레이션">
          {busy ? (
            <span
              className="w-5 h-5 border-2 border-border-default border-t-primary rounded-full animate-spin"
              role="status"
              aria-label="처리 중"
            />
          ) : null}
          <button
            type="button"
            onClick={() => onToggleLock(node)}
            disabled={blocked}
            className="min-h-[44px] px-2 rounded-md text-base text-text-muted hover:text-text-default hover:bg-bg-subtle transition-colors duration-fast disabled:opacity-40 disabled:cursor-not-allowed"
            aria-label={node.locked ? "잠금 해제" : "잠금(고정)"}
            title={node.locked ? "잠금 해제" : "고정해서 보호"}
          >
            {node.locked ? "🔒" : "🔓"}
          </button>
          <button
            type="button"
            onClick={() => onEdit(node)}
            disabled={blocked}
            className="min-h-[44px] px-2 rounded-md text-base text-text-muted hover:text-text-default hover:bg-bg-subtle transition-colors duration-fast disabled:opacity-40 disabled:cursor-not-allowed"
            aria-label="편집"
            title="내용 편집"
          >
            ✏️
          </button>
          <button
            type="button"
            onClick={() => onDelete(node)}
            disabled={blocked}
            className="min-h-[44px] px-2 rounded-md text-base text-text-muted hover:text-text-danger hover:bg-bg-subtle transition-colors duration-fast disabled:opacity-40 disabled:cursor-not-allowed"
            aria-label="삭제"
            title="삭제"
          >
            🗑
          </button>
        </div>
      </div>
    </div>
  );
}

/** StructureRowControls props — 도메인/시리즈 1행의 이름 + ✏️/🗑 컨트롤. */
interface StructureRowControlsProps {
  /** 표시 이름. */
  label: string;
  /** 이 행이 동작 중(스피너/비활성). */
  busy: boolean;
  /** 다른 행/rename 중이라 이 행의 액션을 잠시 막음. */
  disabled: boolean;
  /** 이름 텍스트 className (도메인=강조 / 시리즈=• 머리표). */
  labelClassName: string;
  editAriaLabel: string;
  deleteAriaLabel: string;
  onEdit: () => void;
  onDelete: () => void;
}

/**
 * Phase 24 S2 — 구조 트리의 도메인/시리즈 1행. 이름 + ✏️(rename)/🗑(delete) 컨트롤.
 * PkmChip 큐레이션 컨트롤과 동일 아이콘·busy 스피너·44px 탭 타깃·disabled 처리(일관 UX).
 * rename 동작 자체는 부모가 인라인 StructureRenameInput 으로 교체(✏️ → onEdit).
 */
function StructureRowControls({
  label,
  busy,
  disabled,
  labelClassName,
  editAriaLabel,
  deleteAriaLabel,
  onEdit,
  onDelete,
}: StructureRowControlsProps) {
  const blocked = busy || disabled;
  return (
    <div className="flex items-center justify-between gap-2">
      <span className={labelClassName}>{label}</span>
      <div
        className="flex items-center gap-1 shrink-0"
        aria-label="구조 편집"
      >
        {busy ? (
          <span
            className="w-5 h-5 border-2 border-border-default border-t-primary rounded-full animate-spin"
            role="status"
            aria-label="처리 중"
          />
        ) : null}
        <button
          type="button"
          onClick={onEdit}
          disabled={blocked}
          className="min-h-[44px] px-2 rounded-md text-base text-text-muted hover:text-text-default hover:bg-bg-subtle transition-colors duration-fast disabled:opacity-40 disabled:cursor-not-allowed"
          aria-label={editAriaLabel}
          title="이름 수정"
        >
          ✏️
        </button>
        <button
          type="button"
          onClick={onDelete}
          disabled={blocked}
          className="min-h-[44px] px-2 rounded-md text-base text-text-muted hover:text-text-danger hover:bg-bg-subtle transition-colors duration-fast disabled:opacity-40 disabled:cursor-not-allowed"
          aria-label={deleteAriaLabel}
          title="삭제"
        >
          🗑
        </button>
      </div>
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

/**
 * Phase 22 S2 / Phase 26 S3 — graph 응답에서 brand → domain → series → video 4계층 트리를 파생.
 *   - brands: type==="brand" 노드.
 *   - 각 brand 의 domain: has_domain 엣지(source===brand.id)의 target 중 type==="domain".
 *   - 각 domain 의 series: has_series 엣지(source===domain.id)의 target 중 type==="series".
 *   - 각 series 의 video: has_video 엣지(source===series.id)의 target 중 type==="video".
 * (read-only — 생성은 createDomain/createSeries/createVideo + refetch 로 그래프에 반영)
 */
function buildStructureTree(graph: PkmGraphResponse | null): StructureBrand[] {
  if (!graph) return [];

  const nodeById = new Map<string, PkmGraphNode>();
  for (const n of graph.nodes) nodeById.set(n.id, n);

  const brands = graph.nodes.filter((n) => n.type === "brand");

  // brand id → domain 노드들 (has_domain: brand→domain).
  const domainsByBrand = new Map<string, PkmGraphNode[]>();
  // domain id → series 노드들 (has_series: domain→series).
  const seriesByDomain = new Map<string, PkmGraphNode[]>();
  // series id → video 노드들 (has_video: series→video).
  const videosBySeries = new Map<string, PkmGraphNode[]>();
  for (const b of brands) domainsByBrand.set(b.id, []);

  for (const e of graph.edges) {
    if (e.kind === "has_domain") {
      const bucket = domainsByBrand.get(e.source);
      const child = nodeById.get(e.target);
      if (bucket && child && child.type === "domain") bucket.push(child);
    } else if (e.kind === "has_series") {
      const child = nodeById.get(e.target);
      if (child && child.type === "series") {
        const bucket = seriesByDomain.get(e.source);
        if (bucket) bucket.push(child);
        else seriesByDomain.set(e.source, [child]);
      }
    } else if (e.kind === "has_video") {
      const child = nodeById.get(e.target);
      if (child && child.type === "video") {
        const bucket = videosBySeries.get(e.source);
        if (bucket) bucket.push(child);
        else videosBySeries.set(e.source, [child]);
      }
    }
  }

  return brands.map((brand) => ({
    brand,
    domains: (domainsByBrand.get(brand.id) ?? []).map((domain) => ({
      domain,
      series: (seriesByDomain.get(domain.id) ?? []).map((series) => ({
        series,
        videos: videosBySeries.get(series.id) ?? [],
      })),
    })),
  }));
}
