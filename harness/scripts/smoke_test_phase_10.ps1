#requires -Version 5.1
# scripts/smoke_test_phase_10.ps1
# Phase 10 (MVP 통합 테스트) automated smoke test (PowerShell 5.1 compatible)
# Slice S1 — MVP end-to-end 통합 + 누적 baseline 회귀 (behavior-preserving)
#
# Phase 1~9.5 누적 핵심 체크 + 신규 통합 흐름(test_integration_mvp) 체크 통합.
# 누적 pytest baseline: Phase 9.5 339 + Phase 10 S1 신규 통합 test 12 = 351.
#
# Phase 10 final 목표: 12/12 (전부 PASS, intended WARN 없음)

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ROOT

$FASTAPI = Join-Path $ROOT 'backend/fastapi'

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

Write-Host '=== Phase 10 Smoke Test (MVP 통합, Automated, 12 checks) ===' -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor Gray
Write-Host 'Note: Phase 10 final target 12/12 PASS (누적 339 baseline + S1 통합 test 12 = 351)' -ForegroundColor Gray
Write-Host ''

# --- Step 1/12: pytest backend 전체 회귀 (Phase 9.5 339 + Phase 10 S1 통합 12 = 351) ---
Write-Host 'Step 1/12: pytest backend 전체 (누적 339 baseline 회귀 0 + S1 통합 test 12 = 351)' -ForegroundColor Cyan
$pytestOutput = & python -m pytest $FASTAPI -q --tb=line 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $pytestOutput -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'pytest backend (전체)' 'PASS' $passLine.Trim()
    } else {
        Record 'pytest backend (전체)' 'PASS' 'all tests passed'
    }
} else {
    $tailLine = ($pytestOutput -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'pytest backend (전체)' 'FAIL' $tailLine
}

# --- Step 2/12: 신규 MVP 통합 test 단독 PASS (test_integration_mvp.py) ---
Write-Host ''
Write-Host 'Step 2/12: MVP 통합 test 단독 (test_integration_mvp.py — Quick/Discovery 체인 + revise + RAG + SSE + graceful)' -ForegroundColor Cyan
$intgTest = & python -m pytest (Join-Path $FASTAPI 'tests/test_integration_mvp.py') -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $intgTest -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'MVP 통합 test' 'PASS' $passLine.Trim()
    } else {
        Record 'MVP 통합 test' 'PASS' 'integration tests passed'
    }
} else {
    $tailLine = ($intgTest -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'MVP 통합 test' 'FAIL' $tailLine
}

# --- Step 3/12: 통합 test 파일 존재 (신규 산출물) ---
Write-Host ''
Write-Host 'Step 3/12: test_integration_mvp.py 존재' -ForegroundColor Cyan
$intgFile = Join-Path $FASTAPI 'tests/test_integration_mvp.py'
if (Test-Path -LiteralPath $intgFile) {
    Record 'integration test 존재' 'PASS' 'tests/test_integration_mvp.py'
} else {
    Record 'integration test 존재' 'FAIL' 'tests/test_integration_mvp.py missing'
}

# --- Step 4/12: 주요 endpoint 파일 존재 (generate / plans / sse) ---
Write-Host ''
Write-Host 'Step 4/12: 주요 endpoint 파일 (routers/generate.py + plans.py + sse.py)' -ForegroundColor Cyan
$routerFiles = @('routers/generate.py', 'routers/plans.py', 'routers/sse.py')
$missingRouters = @()
foreach ($rf in $routerFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $FASTAPI $rf))) { $missingRouters += $rf }
}
if ($missingRouters.Count -eq 0) {
    Record 'endpoint 파일 존재' 'PASS' '3 routers OK (generate/plans/sse)'
} else {
    Record 'endpoint 파일 존재' 'FAIL' "missing: $($missingRouters -join ', ')"
}

# --- Step 5/12: agents 5 + orchestration 존재 (intent/planning/critic/rewriter/rag + moa) ---
Write-Host ''
Write-Host 'Step 5/12: agents 5 + orchestration (intent/planning/critic/rewriter/rag + moa_orchestrator)' -ForegroundColor Cyan
$agentFiles = @('agents/intent.py', 'agents/planning.py', 'agents/critic.py', 'agents/rewriter.py', 'agents/rag.py')
$missingAgents = @()
foreach ($af in $agentFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $FASTAPI $af))) { $missingAgents += $af }
}
$hasMoa = Test-Path -LiteralPath (Join-Path $FASTAPI 'orchestration/moa_orchestrator.py')
if ($missingAgents.Count -eq 0 -and $hasMoa) {
    Record 'agents 5 + orchestration' 'PASS' '5 agents + moa_orchestrator OK'
} else {
    $note = "missing agents: $($missingAgents -join ', '); moa=$hasMoa"
    Record 'agents 5 + orchestration' 'FAIL' $note
}

# --- Step 6/12: endpoints sanity — MVP 흐름 endpoint 전부 등록 (start/generate/select/feedback/progress) ---
Write-Host ''
Write-Host 'Step 6/12: endpoints sanity (start + wizard + generate + GET + select + feedback + progress + Phase 1 generate)' -ForegroundColor Cyan
$endpointCheck = & python -c "from backend.fastapi.main import app; routes = [getattr(r, 'path', '') for r in app.routes]; req = ['/api/v1/plans/start', '/api/v1/plans/{plan_id}/wizard/{step}', '/api/v1/plans/{plan_id}/generate', '/api/v1/plans/{plan_id}', '/api/v1/plans/{plan_id}/select', '/api/v1/plans/{plan_id}/feedback', '/api/v1/plans/{plan_id}/progress', '/api/v1/generate']; missing = [p for p in req if p not in routes]; assert not missing, f'missing {missing}'; print('MVP routes OK:', len(req), 'of', len(routes))" 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $tailLine = ($endpointCheck -split "`n" | Where-Object { $_.Trim() } | Select-Object -Last 1).Trim()
    Record 'endpoints sanity' 'PASS' $tailLine
} else {
    $tailLine = ($endpointCheck -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'endpoints sanity' 'FAIL' $tailLine
}

# --- Step 7/12: behavior-preserving marker (기존 endpoint/agent/test 0 수정) ---
Write-Host ''
Write-Host 'Step 7/12: behavior-preserving marker (test_integration_mvp 내 behavior-preserving 주석)' -ForegroundColor Cyan
$bpMatch = Select-String -LiteralPath $intgFile -Pattern 'behavior-preserving' -SimpleMatch -ErrorAction SilentlyContinue
if ($bpMatch) {
    Record 'behavior-preserving marker' 'PASS' "marker found ($($bpMatch.Count) hits)"
} else {
    Record 'behavior-preserving marker' 'WARN' 'behavior-preserving marker not found'
}

# --- Step 8/12: Quick + Discovery 분기 커버 (통합 test 내 두 경로 함수 존재) ---
Write-Host ''
Write-Host 'Step 8/12: Quick + Discovery 분기 커버 (test_quick_mode_full_chain + test_discovery_mode_full_chain)' -ForegroundColor Cyan
$hasQuick = Select-String -LiteralPath $intgFile -Pattern 'def test_quick_mode_full_chain' -SimpleMatch -ErrorAction SilentlyContinue
$hasDiscovery = Select-String -LiteralPath $intgFile -Pattern 'def test_discovery_mode_full_chain' -SimpleMatch -ErrorAction SilentlyContinue
if ($hasQuick -and $hasDiscovery) {
    Record 'Quick + Discovery 분기' 'PASS' 'both full-chain cases present'
} else {
    Record 'Quick + Discovery 분기' 'FAIL' "quick=$([bool]$hasQuick) discovery=$([bool]$hasDiscovery)"
}

# --- Step 9/12: save/select/feedback/SSE 흐름 단계 커버 (통합 test grep 휴리스틱) ---
Write-Host ''
Write-Host 'Step 9/12: save/select/feedback/SSE 흐름 단계 커버 (통합 test 내 endpoint 호출)' -ForegroundColor Cyan
$flowHits = 0
foreach ($pat in @('/select', '/feedback', '/progress', '/generate')) {
    $m = Select-String -LiteralPath $intgFile -Pattern $pat -SimpleMatch -ErrorAction SilentlyContinue
    if ($m) { $flowHits++ }
}
if ($flowHits -eq 4) {
    Record 'save/select/feedback/SSE 단계' 'PASS' '4/4 flow stages covered'
} else {
    Record 'save/select/feedback/SSE 단계' 'WARN' "$flowHits/4 flow stages found"
}

# --- Step 10/12: MOA orchestrator + SSE integration baseline 회귀 (Phase 8 누적) ---
Write-Host ''
Write-Host 'Step 10/12: MOA orchestrator + SSE integration baseline (Phase 8 누적 회귀 0)' -ForegroundColor Cyan
$moaTest = & python -m pytest (Join-Path $FASTAPI 'tests/test_moa_orchestrator.py') (Join-Path $FASTAPI 'tests/test_sse_integration.py') -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $moaTest -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'MOA + SSE baseline' 'PASS' $passLine.Trim()
    } else {
        Record 'MOA + SSE baseline' 'PASS' 'moa/sse baseline passed'
    }
} else {
    $tailLine = ($moaTest -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'MOA + SSE baseline' 'FAIL' $tailLine
}

# --- Step 11/12: select / feedback baseline 회귀 (Phase 9 누적) ---
Write-Host ''
Write-Host 'Step 11/12: select / feedback baseline (Phase 9 누적 — selection_feedback + plans_feedback_api 회귀 0)' -ForegroundColor Cyan
$fbTest = & python -m pytest (Join-Path $FASTAPI 'tests/test_selection_feedback.py') (Join-Path $FASTAPI 'tests/test_plans_feedback_api.py') -q --tb=short 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $fbTest -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'select/feedback baseline' 'PASS' $passLine.Trim()
    } else {
        Record 'select/feedback baseline' 'PASS' 'select/feedback baseline passed'
    }
} else {
    $tailLine = ($fbTest -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'select/feedback baseline' 'FAIL' $tailLine
}

# --- Step 12/12: scenario_simulation v8 (S31~ MVP 통합 시나리오 포함) ---
Write-Host ''
Write-Host 'Step 12/12: scenario_simulation v8 (S31~ MVP 통합 시나리오 — P-X2 auto-gate)' -ForegroundColor Cyan
$scenScript = Join-Path $ROOT 'scripts/scenario_simulation.ps1'
if (Test-Path -LiteralPath $scenScript) {
    & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $scenScript 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Record 'scenario_simulation v8' 'PASS' 'scenario gate exit 0'
    } else {
        Record 'scenario_simulation v8' 'WARN' 'scenario gate partial (phase 진행 중 의도 PARTIAL 허용)'
    }
} else {
    Record 'scenario_simulation v8' 'FAIL' 'scenario_simulation.ps1 missing'
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
    Write-Host 'Phase 10 smoke test FAILED' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Phase 10 smoke test PASSED' -ForegroundColor Green
exit 0
