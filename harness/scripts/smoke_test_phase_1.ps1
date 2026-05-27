#requires -Version 5.1
# Phase 1 automated smoke test (PowerShell 5.1 compatible)

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

Write-Host '=== Phase 1 Smoke Test (Automated) ===' -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor Gray
Write-Host ''

# Step 1: pytest
Write-Host 'Step 1/5: pytest' -ForegroundColor Cyan
$pytestOutput = & python -m pytest -q --tb=line 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $pytestOutput -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    Record 'pytest e2e + unit' 'PASS' $passLine.Trim()
} else {
    $tailLine = ($pytestOutput -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'pytest e2e + unit' 'FAIL' $tailLine
}

# Step 2: uvicorn boot + /health
Write-Host ''
Write-Host 'Step 2/5: uvicorn boot + /health' -ForegroundColor Cyan
$uvicornJob = Start-Job -ScriptBlock {
    param($projectRoot)
    Set-Location $projectRoot
    $env:OPENAI_API_KEY = 'sk-test-dummy-for-boot'
    & python -m uvicorn backend.fastapi.main:app --host 127.0.0.1 --port 8765 --log-level warning 2>&1
} -ArgumentList $ROOT

Start-Sleep -Seconds 4
$healthOk = $false
$healthDetail = ''
for ($i = 0; $i -lt 6; $i++) {
    try {
        $resp = Invoke-RestMethod -Uri 'http://127.0.0.1:8765/health' -Method GET -TimeoutSec 3
        if ($resp.status -eq 'ok') {
            $healthOk = $true
            $healthDetail = "phase=$($resp.phase) slice=$($resp.slice) version=$($resp.version)"
            break
        }
    } catch {
        Start-Sleep -Seconds 1
    }
}
if ($healthOk) {
    Record 'uvicorn /health' 'PASS' $healthDetail
} else {
    Record 'uvicorn /health' 'FAIL' '/health did not respond within 10s'
}

# Step 3: POST /api/v1/generate empty input -> 422
Write-Host ''
Write-Host 'Step 3/5: POST /api/v1/generate (empty input -> 422)' -ForegroundColor Cyan
if ($healthOk) {
    $statusCode = 0
    try {
        $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8765/api/v1/generate' -Method POST `
            -Body '{"input":""}' -ContentType 'application/json' -TimeoutSec 5 -UseBasicParsing
        $statusCode = [int]$r.StatusCode
    } catch {
        try { $statusCode = [int]$_.Exception.Response.StatusCode } catch { $statusCode = -1 }
    }
    if ($statusCode -eq 422) {
        Record 'pydantic input validation (empty)' 'PASS' '422 Unprocessable'
    } else {
        Record 'pydantic input validation (empty)' 'FAIL' "expected 422, got $statusCode"
    }
} else {
    Record 'pydantic input validation (empty)' 'SKIP' 'uvicorn not running'
}

# Step 4: /openapi.json
Write-Host ''
Write-Host 'Step 4/5: /openapi.json' -ForegroundColor Cyan
if ($healthOk) {
    try {
        $spec = Invoke-RestMethod -Uri 'http://127.0.0.1:8765/openapi.json' -Method GET -TimeoutSec 5
        $pathCount = ($spec.paths | Get-Member -MemberType NoteProperty).Count
        $hasGenerate = $null -ne $spec.paths.'/api/v1/generate'
        if ($hasGenerate) {
            Record '/openapi.json' 'PASS' "paths=$pathCount, /api/v1/generate present"
        } else {
            Record '/openapi.json' 'FAIL' '/api/v1/generate path missing'
        }
    } catch {
        Record '/openapi.json' 'FAIL' $_.Exception.Message
    }
} else {
    Record '/openapi.json' 'SKIP' 'uvicorn not running'
}

# Stop uvicorn
Write-Host ''
Write-Host 'Stopping uvicorn...' -ForegroundColor Gray
Stop-Job -Job $uvicornJob -ErrorAction SilentlyContinue
Remove-Job -Job $uvicornJob -Force -ErrorAction SilentlyContinue

# Step 5: frontend build artifact
Write-Host ''
Write-Host 'Step 5/5: frontend build artifact' -ForegroundColor Cyan
$nextDir = Join-Path $ROOT 'apps/web/.next'
if (Test-Path $nextDir) {
    $buildIdFile = Join-Path $nextDir 'BUILD_ID'
    if (Test-Path $buildIdFile) {
        $buildId = (Get-Content $buildIdFile -ErrorAction SilentlyContinue).Trim()
        Record 'apps/web/.next' 'PASS' "BUILD_ID=$buildId"
    } else {
        Record 'apps/web/.next' 'PASS' '.next folder exists'
    }
} else {
    Record 'apps/web/.next' 'WARN' '.next missing (npm run build required)'
}

# Summary
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
Write-Host "PASS: $passed / WARN: $warned / SKIP: $skipped / FAIL: $failed" -ForegroundColor $totalColor

if ($failed -gt 0) {
    Write-Host ''
    Write-Host 'Phase 1 automated smoke test FAILED' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Phase 1 automated smoke test PASSED' -ForegroundColor Green
Write-Host 'Manual portion: phase-1-smoke-test-instructions_2026-05-26.md' -ForegroundColor Gray
exit 0
