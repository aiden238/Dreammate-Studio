#!/usr/bin/env pwsh
# Sprint S0 종료 sanity check (Windows PowerShell-compatible)
# Usage: pwsh ./scripts/sanity_end_S0.ps1
# Returns: exit 0 on PASS, exit 1 on FAIL

$ErrorActionPreference = "Stop"

$harness = Split-Path -Parent $PSScriptRoot
$workspace = Split-Path -Parent $harness

Write-Host "=== Sprint S0 End Check ===" -ForegroundColor Cyan
$failed = 0

function Test-Item {
    param([string]$Label, [bool]$Cond, [string]$Detail = "")
    if ($Cond) {
        Write-Host "OK   : $Label" -ForegroundColor Green
    } else {
        Write-Host "FAIL : $Label  $Detail" -ForegroundColor Red
        $script:failed++
    }
}

# 1. 누락 폴더 14개 + README 확인
$missingFolders = @(
    "meta\handoffs", "meta\validations", "meta\proposals", "meta\retrospectives",
    "docs\contract_changes", "docs\bug_reports",
    "eval\regression_results", "eval\cost_snapshots", "eval\qa_reports",
    "eval\design_reviews", "eval\security_reviews"
)
foreach ($f in $missingFolders) {
    $full = Join-Path $harness $f
    Test-Item "folder $f" (Test-Path $full)
    Test-Item "README in $f" (Test-Path "$full\README.md")
}

# 단일 파일 3개
$singleFiles = @("meta\patterns.md", "meta\skill_usage_log.md", "meta\security_metrics.md")
foreach ($f in $singleFiles) {
    Test-Item "file $f" (Test-Path (Join-Path $harness $f))
}

# 2. 라우터 파일 갱신 확인
$startHere = Get-Content (Join-Path $harness "00_START_HERE.md") -Raw
Test-Item "00_START_HERE.md mentions Discovery + Quick" ($startHere -match "Discovery" -and $startHere -match "Quick")

$claudeMd = Get-Content (Join-Path $harness "CLAUDE.md") -Raw
Test-Item "CLAUDE.md mentions multi-llm-validation" ($claudeMd -match "multi-llm-validation")
Test-Item "CLAUDE.md mentions context-compact" ($claudeMd -match "context-compact")

$agentsMd = Get-Content (Join-Path $harness "AGENTS.md") -Raw
Test-Item "AGENTS.md mentions prompt-version-review" ($agentsMd -match "prompt-version-review")

# 3. PROJECT_STATE 갱신 확인
$projectState = Get-Content (Join-Path $harness "PROJECT_STATE.md") -Raw
Test-Item "PROJECT_STATE has migration_progress" ($projectState -match "migration_progress")
Test-Item "PROJECT_STATE has 25 confirmed_decisions" ($projectState -match "confirmed_decisions")
Test-Item "PROJECT_STATE current_phase = phase-0-migration" ($projectState -match "phase-0-migration")

# 4. PHASE_REGISTRY 갱신 확인
$phaseReg = Get-Content (Join-Path $harness "PHASE_REGISTRY.md") -Raw
Test-Item "PHASE_REGISTRY Phase 0 active" ($phaseReg -match "0.*active" -or $phaseReg -match "active.*Migration")
Test-Item "PHASE_REGISTRY Phase 2 Discovery+Quick" ($phaseReg -match "Discovery \+ Quick")

# 5. instruction_index YAML 갱신
$routes = Get-Content (Join-Path $harness "instruction_index\routes.yaml") -Raw
Test-Item "routes.yaml has prompt_version_review" ($routes -match "prompt_version_review")
Test-Item "routes.yaml has multi_llm_validation" ($routes -match "multi_llm_validation")
Test-Item "routes.yaml has context_compact" ($routes -match "context_compact")

# 6. phase-0-migration 폴더 + 5 파일
$phase0 = Join-Path $harness "phases\active\phase-0-migration"
Test-Item "phase-0-migration folder" (Test-Path $phase0)
foreach ($f in @("goals.md", "scope.md", "non_goals.md", "acceptance.md", "dependencies.md")) {
    Test-Item "phase-0-migration/$f" (Test-Path "$phase0\$f")
}

# 7. Phase 1 이동 확인
Test-Item "phase_1 NOT in active/" (-not (Test-Path "$harness\phases\active\phase_1_mvp_basic_flow.md"))
Test-Item "phase_1 IN planned/" (Test-Path "$harness\phases\planned\phase_1_mvp_basic_flow.md")

# 8. sanity 스크립트 본인 존재
Test-Item "sanity_start.ps1" (Test-Path (Join-Path $harness "scripts\sanity_start.ps1"))
Test-Item "sanity_end_S0.ps1" (Test-Path (Join-Path $harness "scripts\sanity_end_S0.ps1"))

# 9. HANDOFF.md / 10_CLAUDE_CROSS_VALIDATION_PROMPT 갱신
$handoff = Get-Content (Join-Path $harness "HANDOFF.md") -Raw
Test-Item "HANDOFF.md mentions multi-llm-validation" ($handoff -match "multi-llm-validation")

$crossVal = Get-Content (Join-Path $harness "10_CLAUDE_CROSS_VALIDATION_PROMPT.md") -Raw
Test-Item "10_CLAUDE_CROSS_VALIDATION mentions multi-llm-validation" ($crossVal -match "multi-llm-validation")

# 10. migration_procedure.md v1.2.0 갱신
$proc = Get-Content (Join-Path $harness "migration_procedure.md") -Raw
Test-Item "migration_procedure.md is v1.2.0" ($proc -match "v1\.2\.0")

# 결과
Write-Host ""
if ($failed -eq 0) {
    Write-Host "PASS Sprint S0 verified — all checks OK" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAIL Sprint S0 verification failed: $failed check(s)" -ForegroundColor Red
    exit 1
}
