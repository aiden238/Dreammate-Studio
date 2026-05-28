#requires -Version 5.1
# Phase 6 Slice 3 — Schema stress test (P-X2 v2 evolution)
#
# Phase 4.5 scenario_simulation.ps1 (P-X2 v1: file presence + ADR drift) 한 단계 강화:
#   - pytest matrix 실행 (test_schema_stress.py)
#   - backend Pydantic 모델 import sanity
#   - backend agent import sanity (select_best_plan_index / RewriterInput / RewriterOutput)
#   - frontend tsc --noEmit (types.ts ↔ backend mirror 정합)
#   - frontend types.ts canonical key 존재 검증
#
# 5/5 PASS 목표. PowerShell 5.1 호환 + Windows + UTF-8 BOM.

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ROOT

Write-Host '=== schema_stress_test (Phase 6 P-X2 v2) ===' -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor Gray
Write-Host ''

$script:results = New-Object System.Collections.ArrayList
$script:pass = 0
$script:fail = 0

function Record($step, $status, $detail) {
    [void]$script:results.Add([pscustomobject]@{
        Step   = $step
        Status = $status
        Detail = $detail
    })
    if ($status -eq 'PASS') {
        $color = 'Green'
        $script:pass++
    } elseif ($status -eq 'WARN') {
        $color = 'Yellow'
    } else {
        $color = 'Red'
        $script:fail++
    }
    Write-Host "[$status] $step  $detail" -ForegroundColor $color
}

# --- Check 1/5: pytest test_schema_stress ---
Write-Host 'Check 1/5: pytest backend/fastapi/tests/test_schema_stress.py' -ForegroundColor Cyan
$pytestOutput = & python -m pytest backend/fastapi/tests/test_schema_stress.py -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $pytestOutput -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'pytest test_schema_stress' 'PASS' $passLine.Trim()
    } else {
        Record 'pytest test_schema_stress' 'PASS' 'all stress tests passed'
    }
} else {
    $tailLine = ($pytestOutput -split "`n" | Select-Object -Last 5) -join ' | '
    Record 'pytest test_schema_stress' 'FAIL' $tailLine
}
Write-Host ''

# --- Check 2/5: backend Pydantic models import sanity ---
Write-Host 'Check 2/5: backend Pydantic models import (CriticEvaluation / ReviseAttempt / Body)' -ForegroundColor Cyan
$importOutput = & python -c "from backend.fastapi.schemas.output import CriticEvaluation, ReviseAttempt, Body, CriticScores; ce = CriticEvaluation(overall_score=0.5, dimensions={'a': 0.5}, overall_verdict='approve'); ra = ReviseAttempt(attempt=0, action='approve', revised=False); print('models OK:', type(ce).__name__, type(ra).__name__)" 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $detailLine = ($importOutput -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1).Trim()
    Record 'backend Pydantic models import' 'PASS' $detailLine
} else {
    $tailLine = ($importOutput -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'backend Pydantic models import' 'FAIL' $tailLine
}
Write-Host ''

# --- Check 3/5: backend agent imports (select_best_plan_index + RewriterInput/Output) ---
Write-Host 'Check 3/5: backend agent imports (critic.select_best_plan_index + rewriter.RewriterInput/Output)' -ForegroundColor Cyan
$agentOutput = & python -c "from backend.fastapi.agents.critic import select_best_plan_index; from backend.fastapi.agents.rewriter import run_rewriter, RewriterInput, RewriterOutput, PROMPT_VERSION; print('agents OK rewriter_version=' + PROMPT_VERSION)" 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $detailLine = ($agentOutput -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1).Trim()
    Record 'backend agent imports' 'PASS' $detailLine
} else {
    $tailLine = ($agentOutput -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'backend agent imports' 'FAIL' $tailLine
}
Write-Host ''

# --- Check 4/5: frontend tsc --noEmit (types.ts <-> backend mirror) ---
Write-Host 'Check 4/5: frontend tsc --noEmit (types.ts <-> backend mirror)' -ForegroundColor Cyan
$webDir = Join-Path $ROOT 'apps/web'
if (Test-Path (Join-Path $webDir 'tsconfig.json')) {
    Push-Location $webDir
    $tscOutput = & npx tsc --noEmit 2>&1 | Out-String
    if ($LASTEXITCODE -eq 0) {
        Record 'frontend tsc --noEmit' 'PASS' '0 type errors'
    } else {
        $tailLine = ($tscOutput -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 5) -join ' | '
        Record 'frontend tsc --noEmit' 'FAIL' $tailLine
    }
    Pop-Location
} else {
    Record 'frontend tsc --noEmit' 'FAIL' 'apps/web/tsconfig.json not found'
}
Write-Host ''

# --- Check 5/5: frontend types.ts canonical key 존재 검증 ---
Write-Host 'Check 5/5: frontend types.ts canonical keys (CriticEvaluation / ReviseAttempt / CriticDimensions / CriticVerdictAction)' -ForegroundColor Cyan
$typesFile = Join-Path $webDir 'lib/types.ts'
if (-not (Test-Path -LiteralPath $typesFile)) {
    Record 'frontend types.ts canonical present' 'FAIL' "missing file: $typesFile"
} else {
    $content = Get-Content -LiteralPath $typesFile -Raw
    $required = @(
        'CriticEvaluation',
        'ReviseAttempt',
        'CriticDimensions',
        'CriticVerdictAction',
        'overall_score',
        'dimensions'
    )
    $missing = New-Object System.Collections.ArrayList
    foreach ($r in $required) {
        if ($content -notmatch [regex]::Escape($r)) {
            [void]$missing.Add($r)
        }
    }
    if ($missing.Count -eq 0) {
        Record 'frontend types canonical present' 'PASS' "found all: $($required -join ', ')"
    } else {
        Record 'frontend types canonical present' 'FAIL' "missing: $($missing -join ', ')"
    }
}
Write-Host ''

# --- Summary ---
Write-Host '=== Summary ===' -ForegroundColor Cyan
$script:results | Format-Table -AutoSize | Out-String | Write-Host

Write-Host ''
$totalColor = 'Green'
if ($script:fail -gt 0) { $totalColor = 'Red' }
Write-Host "PASS: $script:pass / 5  -  FAIL: $script:fail / 5" -ForegroundColor $totalColor

if ($script:fail -gt 0) {
    Write-Host ''
    Write-Host 'schema_stress_test FAILED' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'schema_stress_test PASSED' -ForegroundColor Green
exit 0
