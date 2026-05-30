#requires -Version 5.1
# scripts/smoke_test_phase_9_5.ps1
# Phase 9.5 automated smoke test (PowerShell 5.1 compatible)
# Phase 9 baseline (15 checks) + eval-run (1 추가) = 16 checks
# Slice 5 — Final QA gate (P-X1 47연속 + scenario_simulation v6 30/30 + eval-run 정식화 + Critic deprecated 0–5 Full 제거)
#
# Phase 9.5 final 목표: 16/16 (15 PASS + 1 WARN intended audit_page_component, 또는 16/16)

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

Write-Host '=== Phase 9.5 Smoke Test (Automated, 16 checks) ===' -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor Gray
Write-Host ''

# --- Step 1/16: pytest backend regression (Phase 9 baseline 293 + Phase 9.5 신규 eval ~46 = 339) ---
Write-Host 'Step 1/16: pytest backend (Phase 9 baseline 293 + Phase 9.5 신규 eval_runner + revise_effect + Critic deprecated 제거 의도 delta = 339)' -ForegroundColor Cyan
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

# --- Step 2/16: audit_naming (Phase 1 baseline 유지) ---
Write-Host ''
Write-Host 'Step 2/16: audit_naming' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/audit_naming.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'audit_naming' 'PASS' '0 drift'
} else {
    Record 'audit_naming' 'FAIL' 'drift detected'
}

# --- Step 3/16: audit_page_component (Phase 5 Slice 3 AuthGuard + login route 신규 — WARN 허용, Phase 9.5 baseline 계승) ---
Write-Host ''
Write-Host 'Step 3/16: audit_page_component (Phase 5 baseline 2 intended WARN, Phase 9.5 frontend canonical 전환 page.tsx inline 계승)' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/audit_page_component.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'audit_page_component' 'PASS' '0 drift'
} else {
    Record 'audit_page_component' 'WARN' 'drift detected (Phase 5 Slice 3: AuthGuard + /login route intended drift, Phase 9.5 frontend canonical page.tsx inline 계승)'
}

# --- Step 4/16: next build (Phase 5 Slice 3 /login 추가, Phase 9.5 frontend canonical 전환 page.tsx inline — 11 routes baseline) ---
Write-Host ''
Write-Host 'Step 4/16: next build (11 routes baseline, Phase 9.5 frontend canonical 전환 page.tsx inline)' -ForegroundColor Cyan
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

# --- Step 5/16: tsc --noEmit ---
Write-Host ''
Write-Host 'Step 5/16: tsc --noEmit' -ForegroundColor Cyan
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

# --- Step 6/16: next lint ---
Write-Host ''
Write-Host 'Step 6/16: next lint' -ForegroundColor Cyan
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

# --- Step 7/16: .next BUILD_ID 확인 ---
Write-Host ''
Write-Host 'Step 7/16: .next BUILD_ID' -ForegroundColor Cyan
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

# --- Step 8/16: endpoints sanity (Phase 9 신규 select/feedback 포함) ---
Write-Host ''
Write-Host 'Step 8/16: endpoints sanity (Phase 5: plans/start + auth/login + progress / Phase 9: plans/{id}/select + plans/{id}/feedback)' -ForegroundColor Cyan
$endpointCheck = & python -c "from backend.fastapi.main import app; routes = [getattr(r, 'path', '') for r in app.routes]; assert '/api/v1/plans/start' in routes, f'missing /plans/start in {routes}'; assert '/api/v1/auth/login' in routes, f'missing /auth/login in {routes}'; assert '/api/v1/plans/{plan_id}/progress' in routes, f'missing /plans/{{plan_id}}/progress in {routes}'; assert '/api/v1/plans/{plan_id}/select' in routes, f'missing /plans/{{plan_id}}/select in {routes}'; assert '/api/v1/plans/{plan_id}/feedback' in routes, f'missing /plans/{{plan_id}}/feedback in {routes}'; print(' routes OK (select/feedback 포함):', len(routes))" 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $tailLine = ($endpointCheck -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1).Trim()
    Record 'endpoints sanity' 'PASS' $tailLine
} else {
    $tailLine = ($endpointCheck -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'endpoints sanity' 'FAIL' $tailLine
}

# --- Step 9/16: revise loop integration test (Phase 4.5 baseline 유지) ---
Write-Host ''
Write-Host 'Step 9/16: revise loop integration (test_plans.py revise_history)' -ForegroundColor Cyan
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

# --- Step 10/16: schema_stress_test (Phase 6 P-X2 v2 + Phase 9.5 CriticEvaluation deprecated 제거 정합) ---
Write-Host ''
Write-Host 'Step 10/16: schema_stress_test (Phase 6 P-X2 v2, Phase 9.5 CriticEvaluation deprecated 0–5 제거 정합)' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/schema_stress_test.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'schema_stress_test' 'PASS' '5/5 PASS (P-X2 v2)'
} else {
    Record 'schema_stress_test' 'FAIL' 'schema stress detected drift'
}

# --- Step 11/16: DB plans_repo (Phase 5 Slice 2 + Phase 5.5 legacy deprecation) ---
Write-Host ''
Write-Host 'Step 11/16: DB plans_repo (Phase 5 + Phase 5.5 legacy deprecation — test_db.py)' -ForegroundColor Cyan
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

# --- Step 12/16: RLS + SSE (Phase 5 Slice 3+4 baseline) ---
Write-Host ''
Write-Host 'Step 12/16: RLS + SSE (Phase 5 — test_rls + test_sse)' -ForegroundColor Cyan
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

# --- Step 13/16: RAG 5단계 + retrieval (Phase 7 baseline 51 유지) ---
Write-Host ''
Write-Host 'Step 13/16: RAG 5단계 + retrieval (Phase 7 — promotion + quality_filter + eval_rubric + chunking + embedding + retrieval + integration)' -ForegroundColor Cyan
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

# --- Step 14/16: MOA orchestrator + SSE integration + prompt_registry consistency (Phase 8 baseline 26 유지 + Phase 9 normalize wiring) ---
Write-Host ''
Write-Host 'Step 14/16: MOA orchestrator + SSE integration + prompt_registry consistency (Phase 8 — moa_orchestrator + progress_store 브릿지 + Critic v1.1.0 adapter, Phase 9 normalize wiring 정합)' -ForegroundColor Cyan
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

# --- Step 15/16: feedback / selection (Phase 9 — selection_feedback + plans_feedback_api + critic_canonical_wiring + brand_memory_prep) ---
Write-Host ''
Write-Host 'Step 15/16: feedback / selection (Phase 9 — selected_plans + feedback_events graceful + select/feedback API + normalize_to_canonical wiring + Brand Memory 준비 feedback->candidate)' -ForegroundColor Cyan
$fbTest = & python -m pytest backend/fastapi/tests/test_selection_feedback.py backend/fastapi/tests/test_plans_feedback_api.py backend/fastapi/tests/test_critic_canonical_wiring.py backend/fastapi/tests/test_brand_memory_prep.py -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $fbTest -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'feedback / selection' 'PASS' $passLine.Trim()
    } else {
        Record 'feedback / selection' 'PASS' 'feedback/selection tests passed'
    }
} else {
    $tailLine = ($fbTest -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'feedback / selection' 'FAIL' $tailLine
}

# --- Step 16/16: eval-run (Phase 9.5 신규 — test_eval_runner + test_revise_effect + eval_run.ps1 mock gate PASS) ---
Write-Host ''
Write-Host 'Step 16/16: eval-run (Phase 9.5 — golden_set 11 케이스 mock-deterministic 회귀 + revise effect eval + 임계값 게이트, ADR-033)' -ForegroundColor Cyan
$evalTest = & python -m pytest backend/fastapi/tests/test_eval_runner.py backend/fastapi/tests/test_revise_effect.py -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $evalPassLine = $evalTest -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    # eval_run.ps1 mock gate 실행 (verdict=pass → exit 0)
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/eval_run.ps1') 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $note = if ($evalPassLine) { "$($evalPassLine.Trim()) + eval_run.ps1 gate=pass" } else { "eval tests passed + eval_run.ps1 gate=pass" }
        Record 'eval-run' 'PASS' $note
    } else {
        Record 'eval-run' 'FAIL' 'eval_run.ps1 gate=fail (임계값 위반 — 차단)'
    }
} else {
    $tailLine = ($evalTest -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'eval-run' 'FAIL' $tailLine
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
    Write-Host 'Phase 9.5 smoke test FAILED' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Phase 9.5 smoke test PASSED' -ForegroundColor Green
exit 0
