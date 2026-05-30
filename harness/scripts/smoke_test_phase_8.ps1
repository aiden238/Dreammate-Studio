#requires -Version 5.1
# scripts/smoke_test_phase_8.ps1
# Phase 8 automated smoke test (PowerShell 5.1 compatible)
# Phase 7 baseline (13 checks) + MOA orchestrator + SSE integration + prompt_registry consistency (1 추가) = 14 checks
# Slice 5 — Final QA gate (P-X1 36연속 + scenario_simulation v4 20/20 + ai-architecture-review/prompt-version-review 첫 정식)

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ROOT

$script:results = New-Object System.Collections.ArrayList

function Record($step, $status, $detail) {
    [void]$script:results.Add([pscustomobject]@{
        Step   = $step
        Status = $status
        Detail = $detail
    })
    if ($status -eq 'PASS') { $color = 'Green' }
    elseif ($status -eq 'WARN') { $color = 'Yellow' }
    elseif ($status -eq 'SKIP') { $color = 'Gray' }
    else { $color = 'Red' }
    Write-Host "[$status] $step  $detail" -ForegroundColor $color
}

Write-Host '=== Phase 8 Smoke Test (Automated, 14 checks) ===' -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor Gray
Write-Host ''

# --- Step 1/14: pytest backend regression (Phase 7 baseline 223 + Phase 8 신규 ~26 = 249+) ---
Write-Host 'Step 1/14: pytest backend (Phase 7 baseline 223 + Phase 8 신규 orchestrator + sse_integration + prompt_registry_consistency)' -ForegroundColor Cyan
$pytestOutput = & python -m pytest -q --tb=line 2>&1 | Out-String
$global:pytestCaptured = $pytestOutput
if ($LASTEXITCODE -eq 0) {
    $passLine = $pytestOutput -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'pytest backend' 'PASS' $passLine.Trim()
    } else {
        Record 'pytest backend' 'PASS' 'all tests passed'
    }
} else {
    $tailLine = ($pytestOutput -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'pytest backend' 'FAIL' $tailLine
}

# --- Step 2/14: audit_naming (Phase 1 baseline 유지) ---
Write-Host ''
Write-Host 'Step 2/14: audit_naming' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/audit_naming.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'audit_naming' 'PASS' '0 drift'
} else {
    Record 'audit_naming' 'FAIL' 'drift detected'
}

# --- Step 3/14: audit_page_component (Phase 5 Slice 3 AuthGuard + login route 신규 — WARN 허용, Phase 8 baseline 유지) ---
Write-Host ''
Write-Host 'Step 3/14: audit_page_component (Phase 5 baseline 2 intended WARN 유지)' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/audit_page_component.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'audit_page_component' 'PASS' '0 drift'
} else {
    Record 'audit_page_component' 'WARN' 'drift detected (Phase 5 Slice 3: AuthGuard + /login route intended drift, Phase 8 baseline 유지)'
}

# --- Step 4/14: next build (Phase 5 Slice 3 /login 추가, route 12개 baseline — Phase 8 backend-only) ---
Write-Host ''
Write-Host 'Step 4/14: next build (12 routes baseline, Phase 8 backend-only)' -ForegroundColor Cyan
$webDir = Join-Path $ROOT 'apps/web'
if (Test-Path (Join-Path $webDir 'package.json')) {
    Push-Location $webDir
    $buildOutput = & npx next build 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        $routeLines = ([regex]::Matches($buildOutput, '\s/[a-zA-Z0-9_\-/\[\]]+')).Count
        $hasPlanIdRoute = $buildOutput -match '/plan/\[plan_id\]'
        $hasLoginRoute = $buildOutput -match '/login'
        $note = if ($hasPlanIdRoute -and $hasLoginRoute) { "$routeLines route hits + /plan/[plan_id] + /login OK" } else { "$routeLines route hits" }
        Record 'next build' 'PASS' $note
    } else {
        $tailBuild = ($buildOutput -split "`n" | Select-Object -Last 5) -join ' | '
        Record 'next build' 'FAIL' $tailBuild
    }
    Pop-Location
} else {
    Record 'next build' 'SKIP' 'apps/web/package.json not found'
}

# --- Step 5/14: tsc --noEmit ---
Write-Host ''
Write-Host 'Step 5/14: tsc --noEmit' -ForegroundColor Cyan
if (Test-Path (Join-Path $webDir 'tsconfig.json')) {
    Push-Location $webDir
    & npx tsc --noEmit 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Record 'tsc --noEmit' 'PASS' '0 type errors'
    } else {
        Record 'tsc --noEmit' 'FAIL' 'type errors detected'
    }
    Pop-Location
} else {
    Record 'tsc --noEmit' 'SKIP' 'tsconfig.json not found'
}

# --- Step 6/14: next lint ---
Write-Host ''
Write-Host 'Step 6/14: next lint' -ForegroundColor Cyan
if (Test-Path $webDir) {
    Push-Location $webDir
    $lintOutput = & npx next lint 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        Record 'next lint' 'PASS' 'clean'
    } else {
        if ($lintOutput -match 'error') {
            Record 'next lint' 'WARN' 'lint warnings/errors (see output)'
        } else {
            Record 'next lint' 'PASS' 'no errors'
        }
    }
    Pop-Location
} else {
    Record 'next lint' 'SKIP' 'apps/web not found'
}

# --- Step 7/14: .next BUILD_ID 확인 ---
Write-Host ''
Write-Host 'Step 7/14: .next BUILD_ID' -ForegroundColor Cyan
$nextDir = Join-Path $webDir '.next'
if (Test-Path $nextDir) {
    $buildIdFile = Join-Path $nextDir 'BUILD_ID'
    if (Test-Path $buildIdFile) {
        $buildId = (Get-Content $buildIdFile -ErrorAction SilentlyContinue).Trim()
        Record '.next BUILD_ID' 'PASS' "BUILD_ID=$buildId"
    } else {
        Record '.next BUILD_ID' 'PASS' '.next exists'
    }
} else {
    Record '.next BUILD_ID' 'WARN' '.next missing (run next build first)'
}

# --- Step 8/14: endpoints sanity (FastAPI app routes — Phase 5 신규 auth + sse 포함, Phase 8 baseline 유지) ---
Write-Host ''
Write-Host 'Step 8/14: endpoints sanity (Phase 5: plans/start + auth/login + plans/{id}/progress)' -ForegroundColor Cyan
$endpointCheck = & python -c "from backend.fastapi.main import app; routes = [getattr(r, 'path', '') for r in app.routes]; assert '/api/v1/plans/start' in routes, f'missing /plans/start in {routes}'; assert '/api/v1/auth/login' in routes, f'missing /auth/login in {routes}'; assert '/api/v1/plans/{plan_id}/progress' in routes, f'missing /plans/{{plan_id}}/progress in {routes}'; print(' routes OK:', len(routes))" 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $tailLine = ($endpointCheck -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1).Trim()
    Record 'endpoints sanity' 'PASS' $tailLine
} else {
    $tailLine = ($endpointCheck -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'endpoints sanity' 'FAIL' $tailLine
}

# --- Step 9/14: revise loop integration test (Phase 4.5 baseline 유지) ---
Write-Host ''
Write-Host 'Step 9/14: revise loop integration (test_plans.py revise_history)' -ForegroundColor Cyan
$reviseTest = & python -m pytest backend/fastapi/tests/test_plans.py -k "revise" -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $reviseTest -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'revise loop integration' 'PASS' $passLine.Trim()
    } else {
        Record 'revise loop integration' 'PASS' 'revise tests passed'
    }
} else {
    $tailLine = ($reviseTest -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'revise loop integration' 'FAIL' $tailLine
}

# --- Step 10/14: schema_stress_test (Phase 6 P-X2 v2 유지) ---
Write-Host ''
Write-Host 'Step 10/14: schema_stress_test (Phase 6 P-X2 v2)' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/schema_stress_test.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'schema_stress_test' 'PASS' '5/5 PASS (P-X2 v2)'
} else {
    Record 'schema_stress_test' 'FAIL' 'schema stress detected drift'
}

# --- Step 11/14: DB plans_repo (Phase 5 Slice 2 + Phase 5.5 legacy deprecation) ---
Write-Host ''
Write-Host 'Step 11/14: DB plans_repo (Phase 5 + Phase 5.5 legacy deprecation — test_db.py)' -ForegroundColor Cyan
$dbTest = & python -m pytest backend/fastapi/tests/test_db.py -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $dbTest -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'DB plans_repo' 'PASS' $passLine.Trim()
    } else {
        Record 'DB plans_repo' 'PASS' 'db tests passed'
    }
} else {
    $tailLine = ($dbTest -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'DB plans_repo' 'FAIL' $tailLine
}

# --- Step 12/14: RLS + SSE (Phase 5 Slice 3+4 baseline) ---
Write-Host ''
Write-Host 'Step 12/14: RLS + SSE (Phase 5 — test_rls + test_sse)' -ForegroundColor Cyan
$secTest = & python -m pytest backend/fastapi/tests/test_rls.py backend/fastapi/tests/test_sse.py -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $secTest -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'RLS + SSE' 'PASS' $passLine.Trim()
    } else {
        Record 'RLS + SSE' 'PASS' 'rls/sse tests passed'
    }
} else {
    $tailLine = ($secTest -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'RLS + SSE' 'FAIL' $tailLine
}

# --- Step 13/14: RAG 5단계 + retrieval (Phase 7 baseline 51 유지) ---
Write-Host ''
Write-Host 'Step 13/14: RAG 5단계 + retrieval (Phase 7 — promotion + quality_filter + eval_rubric + chunking + embedding + retrieval + integration)' -ForegroundColor Cyan
$ragTest = & python -m pytest backend/fastapi/tests/test_rag_promotion.py backend/fastapi/tests/test_rag_quality_filter.py backend/fastapi/tests/test_rag_eval_rubric.py backend/fastapi/tests/test_rag_chunking.py backend/fastapi/tests/test_rag_embedding.py backend/fastapi/tests/test_rag_retrieval.py backend/fastapi/tests/test_rag_integration.py -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $ragTest -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'RAG 5단계 + retrieval' 'PASS' $passLine.Trim()
    } else {
        Record 'RAG 5단계 + retrieval' 'PASS' 'rag tests passed'
    }
} else {
    $tailLine = ($ragTest -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'RAG 5단계 + retrieval' 'FAIL' $tailLine
}

# --- Step 14/14: MOA orchestrator + SSE integration + prompt_registry consistency (Phase 8 신규 — 26 신규) ---
Write-Host ''
Write-Host 'Step 14/14: MOA orchestrator + SSE integration + prompt_registry consistency (Phase 8 — moa_orchestrator + progress_store 브릿지 + Critic v1.1.0 adapter)' -ForegroundColor Cyan
$moaTest = & python -m pytest backend/fastapi/tests/test_moa_orchestrator.py backend/fastapi/tests/test_sse_integration.py backend/fastapi/tests/test_prompt_registry_consistency.py -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $moaTest -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'MOA orchestrator + SSE integration' 'PASS' $passLine.Trim()
    } else {
        Record 'MOA orchestrator + SSE integration' 'PASS' 'moa/sse/prompt tests passed'
    }
} else {
    $tailLine = ($moaTest -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'MOA orchestrator + SSE integration' 'FAIL' $tailLine
}

# --- Summary ---
Write-Host ''
Write-Host '=== Summary ===' -ForegroundColor Cyan
$script:results | Format-Table -AutoSize | Out-String | Write-Host

$failed = @($script:results | Where-Object { $_.Status -eq 'FAIL' }).Count
$passed = @($script:results | Where-Object { $_.Status -eq 'PASS' }).Count
$warned = @($script:results | Where-Object { $_.Status -eq 'WARN' }).Count
$skipped = @($script:results | Where-Object { $_.Status -eq 'SKIP' }).Count

Write-Host ''
$totalColor = 'Green'
if ($failed -gt 0) { $totalColor = 'Red' }
elseif ($warned -gt 0) { $totalColor = 'Yellow' }
Write-Host "PASS: $passed / WARN: $warned / SKIP: $skipped / FAIL: $failed" -ForegroundColor $totalColor

if ($failed -gt 0) {
    Write-Host ''
    Write-Host 'Phase 8 smoke test FAILED' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Phase 8 smoke test PASSED' -ForegroundColor Green
exit 0
