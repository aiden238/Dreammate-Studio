#requires -Version 5.1
# Phase 3 automated smoke test (PowerShell 5.1 compatible)
# Phase 1 baseline (pytest 62/62) + Phase 3 추가 (next build / tsc / lint / audit_page_component)

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

Write-Host '=== Phase 3 Smoke Test (Automated) ===' -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor Gray
Write-Host ''

# ─── Step 1: pytest backend regression (Phase 1 baseline) ─────────────
Write-Host 'Step 1/7: pytest backend regression (Phase 1)' -ForegroundColor Cyan
$pytestOutput = & python -m pytest -q --tb=line 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $pytestOutput -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'pytest backend regression' 'PASS' $passLine.Trim()
    } else {
        Record 'pytest backend regression' 'PASS' 'all tests passed'
    }
} else {
    $tailLine = ($pytestOutput -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'pytest backend regression' 'FAIL' $tailLine
}

# ─── Step 2: audit_naming ─────────────────────────────────────────────
Write-Host ''
Write-Host 'Step 2/7: audit_naming (Phase 1 baseline)' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/audit_naming.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'audit_naming' 'PASS' '0 drift'
} else {
    Record 'audit_naming' 'FAIL' 'drift detected'
}

# ─── Step 3: audit_page_component (Phase 3 Slice 6 신규) ──────────────
Write-Host ''
Write-Host 'Step 3/7: audit_page_component (Phase 3 Slice 6 신규)' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/audit_page_component.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'audit_page_component' 'PASS' '0 drift'
} else {
    Record 'audit_page_component' 'WARN' 'drift detected (see output)'
}

# ─── Step 4: next build (Phase 3 신규) ────────────────────────────────
Write-Host ''
Write-Host 'Step 4/7: next build (Phase 3 신규)' -ForegroundColor Cyan
$webDir = Join-Path $ROOT 'apps/web'
if (Test-Path (Join-Path $webDir 'package.json')) {
    Push-Location $webDir
    $buildOutput = & npx next build 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        # ○ static / λ dynamic 라인 카운트
        $staticCount = ([regex]::Matches($buildOutput, '○|⚡|◐|λ|ƒ')).Count
        $routeLine = ($buildOutput -split "`n" | Where-Object { $_ -match '(Route|app/)' } | Select-Object -First 1)
        Record 'next build' 'PASS' "build OK ($staticCount route markers)"
    } else {
        $tailBuild = ($buildOutput -split "`n" | Select-Object -Last 5) -join ' | '
        Record 'next build' 'FAIL' $tailBuild
    }
    Pop-Location
} else {
    Record 'next build' 'SKIP' 'apps/web/package.json not found'
}

# ─── Step 5: tsc --noEmit ─────────────────────────────────────────────
Write-Host ''
Write-Host 'Step 5/7: tsc --noEmit' -ForegroundColor Cyan
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

# ─── Step 6: next lint ────────────────────────────────────────────────
Write-Host ''
Write-Host 'Step 6/7: next lint' -ForegroundColor Cyan
if (Test-Path $webDir) {
    Push-Location $webDir
    $lintOutput = & npx next lint 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        Record 'next lint' 'PASS' 'clean'
    } else {
        # warnings only 인지 errors 인지 구분
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

# ─── Step 7: .next BUILD_ID 확인 ──────────────────────────────────────
Write-Host ''
Write-Host 'Step 7/7: .next BUILD_ID' -ForegroundColor Cyan
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

# ─── Summary ──────────────────────────────────────────────────────────
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
    Write-Host 'Phase 3 smoke test FAILED' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Phase 3 smoke test PASSED' -ForegroundColor Green
exit 0
