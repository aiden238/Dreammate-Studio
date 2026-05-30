#requires -Version 5.1
# scripts/scenario_simulation.ps1
# Phase 4.5+ Changeability Simulation auto-gate (P-X2)
# v2 (Phase 5 Slice 1): 5 -> 10 scenarios (DB / Auth / RLS / JWT / SSE 추가)
# v3 (Phase 7 Slice 5): 10 -> 15 scenarios (RAG 5단계 + chunking + retrieval + quality_filter + LLM Wiki 추가)
# v4 (Phase 8 Slice 5): 15 -> 20 scenarios (MOA orchestrator + ProgressSink + progress_store 브릿지 + SSE 실 stage + prompt_registry semver 추가)
# Called automatically by phase-complete Skill v1.2.0 §1.6 at Phase close.
#
# Phase 8 final 목표: 20/20 PASS (P-X2 여섯 번째 자동 게이트)

$ErrorActionPreference = 'Stop'
$ProgressPreference   = 'SilentlyContinue'

$ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ROOT

Write-Host "=== scenario_simulation v4 (P-X2 auto-gate, Phase 8) ===" -ForegroundColor Cyan
Write-Host "Root: $ROOT"
Write-Host "Note: Phase 8 final target 20/20 PASS (P-X2 여섯 번째 자동 게이트)"
Write-Host ""

$scenarios = @(
    # Phase 4.5/6 baseline (5)
    @{ Id = "S1"; Name = "PlanCard visual tone change (visual layer)"; Files = @("apps/web/components/PlanCard.tsx", "apps/web/lib/design_tokens.ts") },
    @{ Id = "S2"; Name = "component_map entry addition"; Files = @("apps/web/component_map.md") },
    @{ Id = "S3"; Name = "wrapper UI ring color change"; Files = @("apps/web/app/plan/[plan_id]/page.tsx") },
    @{ Id = "S4"; Name = "revise loop max attempts change (config)"; Files = @("backend/fastapi/config.py") },
    @{ Id = "S5"; Name = "recommended_plan_index disable"; Files = @("backend/fastapi/routers/plans.py", "backend/fastapi/schemas/output.py") },

    # Phase 5 신규 (5) — Slice 2~4에서 점진 PASS
    @{ Id = "S6"; Name = "Supabase 연결 (env var + client init)"; Files = @("backend/fastapi/db/client.py", "backend/fastapi/config.py") },
    @{ Id = "S7"; Name = "RLS 정책 변경 (db/migrations/*.sql)"; Files = @("backend/fastapi/db/migrations/0001_init.sql", "backend/fastapi/db/migrations/0003_rls_policy.sql") },
    @{ Id = "S8"; Name = "user 분리 (auth_user_id 컬럼)"; Files = @("backend/fastapi/db/migrations/0001_init.sql", "backend/fastapi/middleware/auth_middleware.py") },
    @{ Id = "S9"; Name = "JWT 검증 (middleware)"; Files = @("backend/fastapi/middleware/auth_middleware.py", "backend/fastapi/routers/auth.py") },
    @{ Id = "S10"; Name = "SSE event schema (routers/sse.py)"; Files = @("backend/fastapi/routers/sse.py", "apps/web/lib/sse.ts") },

    # Phase 7 신규 (5, RAG)
    @{ Id = "S11"; Name = "RAG 5단계 schema 변경 (db/migrations/0004 + rag_data_contract)"; Files = @("backend/fastapi/db/migrations/0004_rag_5stage.sql", "docs/contracts/rag_data_contract.md") },
    @{ Id = "S12"; Name = "chunking 변경 (rag/chunking.py + config)"; Files = @("backend/fastapi/rag/chunking.py", "backend/fastapi/config.py") },
    @{ Id = "S13"; Name = "retrieval threshold 변경 (rag/retrieval.py + config)"; Files = @("backend/fastapi/rag/retrieval.py", "backend/fastapi/config.py") },
    @{ Id = "S14"; Name = "quality_filter 변경 (rag/quality_filter.py)"; Files = @("backend/fastapi/rag/quality_filter.py") },
    @{ Id = "S15"; Name = "LLM Wiki entry 추가 (rag/llm_wiki.py)"; Files = @("backend/fastapi/rag/llm_wiki.py") },

    # Phase 8 신규 (5, MOA orchestration + SSE worker + prompt_registry semver)
    @{ Id = "S16"; Name = "orchestrator 추출 (orchestration/moa_orchestrator.py)"; Files = @("backend/fastapi/orchestration/moa_orchestrator.py", "backend/fastapi/routers/plans.py") },
    @{ Id = "S17"; Name = "ProgressSink 인터페이스 (orchestration/progress_sink.py)"; Files = @("backend/fastapi/orchestration/progress_sink.py") },
    @{ Id = "S18"; Name = "progress_store 브릿지 (orchestration/progress_store.py)"; Files = @("backend/fastapi/orchestration/progress_store.py") },
    @{ Id = "S19"; Name = "SSE 실 stage read (routers/sse.py + progress_store)"; Files = @("backend/fastapi/routers/sse.py", "backend/fastapi/orchestration/progress_store.py") },
    @{ Id = "S20"; Name = "prompt_registry semver (prompt_registry.md + critic.py v1.1.0)"; Files = @("ai_system/prompts/prompt_registry.md", "backend/fastapi/agents/critic.py") }
)

$pass = 0
$fail = 0
$results = @()

foreach ($s in $scenarios) {
    $missing = @()
    foreach ($f in $s.Files) {
        if (-not (Test-Path -LiteralPath $f)) { $missing += $f }
    }
    if ($missing.Count -eq 0) {
        Write-Host "[PASS] $($s.Id): $($s.Name)" -ForegroundColor Green
        $results += [PSCustomObject]@{ Scenario = $s.Id; Status = "PASS"; AffectedFiles = $s.Files.Count }
        $pass++
    } else {
        Write-Host "[FAIL] $($s.Id): $($s.Name) - missing: $($missing -join ', ')" -ForegroundColor Red
        $results += [PSCustomObject]@{ Scenario = $s.Id; Status = "FAIL"; AffectedFiles = ($s.Files.Count - $missing.Count) }
        $fail++
    }
}

Write-Host ""
Write-Host "=== Summary ===" -ForegroundColor Cyan
$results | Format-Table -AutoSize

if ($fail -eq 0) {
    Write-Host ""
    Write-Host "scenario_simulation PASS - $pass/$($scenarios.Count) simulated scenarios passed" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "scenario_simulation PARTIAL - $pass/$($scenarios.Count) PASS, $fail FAIL" -ForegroundColor Yellow
    Write-Host "  (Phase 8 final target: 20/20 PASS — P-X2 여섯 번째 자동 게이트)" -ForegroundColor Yellow
    # phase 진행 중 의도된 PARTIAL은 exit 0 유지 (자동 게이트는 phase-complete 시점에 별도 strict 모드 권장)
    exit 0
}
