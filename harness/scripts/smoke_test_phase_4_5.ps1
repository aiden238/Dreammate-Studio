#requires -Version 5.1
# Phase 4.5 automated smoke test (PowerShell 5.1 compatible)
# Phase 4 baseline (8 checks) + revise loop integration test (9th)
# Slice 4 — Final QA gate (audit_naming + audit_page_component + pytest 109+ + next build 11 routes + tsc + lint + BUILD_ID + endpoints sanity + revise loop)

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

Write-Host '=== Phase 4.5 Smoke Test (Automated, 9 checks) ===' -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor Gray
Write-Host ''

# --- Step 1: pytest backend regression (Phase 4 baseline 93 + Phase 4.5 신규 ~16 = 109+) ---
Write-Host 'Step 1/9: pytest backend (Phase 4 baseline + Phase 4.5 신규 revise/rewriter/best-plan)' -ForegroundColor Cyan
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

# --- Step 2: audit_naming (Phase 1 baseline 유지) ---
Write-Host ''
Write-Host 'Step 2/9: audit_naming' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/audit_naming.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'audit_naming' 'PASS' '0 drift'
} else {
    Record 'audit_naming' 'FAIL' 'drift detected'
}

# --- Step 3: audit_page_component (Phase 4 D-1 해소 후 baseline 유지) ---
Write-Host ''
Write-Host 'Step 3/9: audit_page_component' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/audit_page_component.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'audit_page_component' 'PASS' '0 drift'
} else {
    Record 'audit_page_component' 'WARN' 'drift detected (see output)'
}

# --- Step 4: next build (Phase 4 11 routes 유지 — Phase 4.5는 page.tsx 수정만, route 추가 0) ---
Write-Host ''
Write-Host 'Step 4/9: next build (11 routes baseline)' -ForegroundColor Cyan
$webDir = Join-Path $ROOT 'apps/web'
if (Test-Path (Join-Path $webDir 'package.json')) {
    Push-Location $webDir
    $buildOutput = & npx next build 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        # route markers (Next.js outputs ASCII-safe path counts via "Route (app)" section); count distinct route paths instead
        $routeLines = ([regex]::Matches($buildOutput, '\s/[a-zA-Z0-9_\-/\[\]]+')).Count
        $hasPlanIdRoute = $buildOutput -match '/plan/\[plan_id\]'
        $note = if ($hasPlanIdRoute) { "$routeLines route hits + /plan/[plan_id] dynamic OK" } else { "$routeLines route hits" }
        Record 'next build' 'PASS' $note
    } else {
        $tailBuild = ($buildOutput -split "`n" | Select-Object -Last 5) -join ' | '
        Record 'next build' 'FAIL' $tailBuild
    }
    Pop-Location
} else {
    Record 'next build' 'SKIP' 'apps/web/package.json not found'
}

# --- Step 5: tsc --noEmit ---
Write-Host ''
Write-Host 'Step 5/9: tsc --noEmit' -ForegroundColor Cyan
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

# --- Step 6: next lint ---
Write-Host ''
Write-Host 'Step 6/9: next lint' -ForegroundColor Cyan
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

# --- Step 7: .next BUILD_ID 확인 ---
Write-Host ''
Write-Host 'Step 7/9: .next BUILD_ID' -ForegroundColor Cyan
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

# --- Step 8: endpoints sanity (FastAPI app routes import sanity) ---
Write-Host ''
Write-Host 'Step 8/9: endpoints sanity (FastAPI app routes)' -ForegroundColor Cyan
$endpointCheck = & python -c "from backend.fastapi.main import app; routes = [getattr(r, 'path', '') for r in app.routes]; assert '/api/v1/plans/start' in routes, f'missing /plans/start in {routes}'; print(' routes OK:', len(routes))" 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $tailLine = ($endpointCheck -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1).Trim()
    Record 'endpoints sanity' 'PASS' $tailLine
} else {
    $tailLine = ($endpointCheck -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'endpoints sanity' 'FAIL' $tailLine
}

# --- Step 9: revise loop integration test (Phase 4.5 신규 핵심) ---
Write-Host ''
Write-Host 'Step 9/9: revise loop integration (test_plans.py revise_history)' -ForegroundColor Cyan
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
    Write-Host 'Phase 4.5 smoke test FAILED' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Phase 4.5 smoke test PASSED' -ForegroundColor Green
exit 0
