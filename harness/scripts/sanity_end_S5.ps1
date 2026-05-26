#!/usr/bin/env pwsh
# Sprint S5 종료 sanity check (Windows PowerShell-compatible)
# Usage: pwsh ./scripts/sanity_end_S5.ps1
# Returns: exit 0 on PASS, exit 1 on FAIL
#
# 검증 범위:
#   - product/ 7 deep (>= 50줄)
#   - meta/ 8 운영 deep (>= 50줄)
#   - docs/decisions/ 7 deep (>= 30줄)
#   - tools/agent_html_spec.md (>= 50줄, A11)
#   - instruction_index/priority_rules.md (>= 30줄)
#   - tests/ 3 placeholder
#   - packages/ 3 placeholder
#   - apps/mobile/ + backend/ 4 placeholder
#   - phases/planned/ 6 placeholder
#   - logs/ 4 placeholder
#   - 9줄 이하 stub 0개 (전체)
#   - PROJECT_STATE migration_progress = completed
#   - phases/active/phase-0-migration/ archive 이동 확인
#   - PHASE_REGISTRY Phase 0 done

$ErrorActionPreference = "Stop"

$harness = Split-Path -Parent $PSScriptRoot
$workspace = Split-Path -Parent $harness

Write-Host "=== Sprint S5 End Check ===" -ForegroundColor Cyan
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

function Get-LineCount {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return 0 }
    $content = [System.IO.File]::ReadAllText($Path)
    return ($content.ToCharArray() | Where-Object { $_ -eq "`n" }).Count
}

function Read-FileText {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return "" }
    return [System.IO.File]::ReadAllText($Path)
}

function Test-Placeholder {
    param([string]$Path)
    $txt = Read-FileText $Path
    $hasMarker = ($txt -match "PLACEHOLDER")
    $hasStatus = ($txt -match "status:\s*placeholder")
    $hasFillIn = ($txt -match "fill_in_phase|Fill-In Trigger|fill_in_trigger")
    return ($hasMarker -and $hasStatus -and $hasFillIn)
}

# =============================================================
# 1. product/ 7 deep (>= 50줄)
# =============================================================
$productFiles = @(
    "mvp_scope.md", "positioning.md", "pricing_model.md", "roadmap.md",
    "target_users.md", "user_scenarios.md", "vision.md"
)
foreach ($f in $productFiles) {
    $p = Join-Path $harness "product\$f"
    $lines = Get-LineCount $p
    Test-Item "product: $f >= 50 lines" ($lines -ge 50) "(actual: $lines)"
}

# =============================================================
# 2. meta/ 8 운영 deep (>= 50줄)
# =============================================================
$metaFiles = @(
    "error_taxonomy.md", "guardrails.md", "harness_improvement_proposals.md",
    "human_review_policy.md", "lessons_learned.md", "meta_summary.md",
    "rollback_policy.md", "self_improvement_loop.md"
)
foreach ($f in $metaFiles) {
    $p = Join-Path $harness "meta\$f"
    $lines = Get-LineCount $p
    Test-Item "meta: $f >= 50 lines" ($lines -ge 50) "(actual: $lines)"
}

# =============================================================
# 3. docs/decisions/ 7 deep (>= 30줄)
# =============================================================
$decisionFiles = @(
    "backend_strategy.md", "frontend_design_strategy.md", "mobile_strategy.md",
    "observability_strategy.md", "orchestration_strategy.md",
    "rag_strategy.md", "tech_stack_decision.md"
)
foreach ($f in $decisionFiles) {
    $p = Join-Path $harness "docs\decisions\$f"
    $lines = Get-LineCount $p
    Test-Item "docs/decisions: $f >= 30 lines" ($lines -ge 30) "(actual: $lines)"
}

# =============================================================
# 4. tools/agent_html_spec.md (>= 50줄, A11)
# =============================================================
$agentSpec = Join-Path $harness "tools\agent_html_spec.md"
Test-Item "tools/agent_html_spec.md exists" (Test-Path $agentSpec)
$agentSpecLines = Get-LineCount $agentSpec
Test-Item "tools/agent_html_spec.md >= 50 lines" ($agentSpecLines -ge 50) "(actual: $agentSpecLines)"

# =============================================================
# 5. instruction_index/priority_rules.md (>= 30줄)
# =============================================================
$priRules = Join-Path $harness "instruction_index\priority_rules.md"
$priLines = Get-LineCount $priRules
Test-Item "priority_rules.md >= 30 lines" ($priLines -ge 30) "(actual: $priLines)"

# =============================================================
# 6. tests/ 3 placeholder
# =============================================================
$testsFiles = @("regression_checklist.md", "smoke_test_checklist.md", "test_index.md")
foreach ($f in $testsFiles) {
    $p = Join-Path $harness "tests\$f"
    Test-Item "tests: $f placeholder format" (Test-Placeholder $p)
}

# =============================================================
# 7. packages/ 3 placeholder
# =============================================================
$packagesFiles = @("api-client", "shared-types", "shared-utils")
foreach ($d in $packagesFiles) {
    $p = Join-Path $harness "packages\$d\README.md"
    Test-Item "packages: $d/README.md placeholder format" (Test-Placeholder $p)
}

# =============================================================
# 8. apps/mobile/ + backend/ 4 placeholder
# =============================================================
$mobileBackend = @(
    "apps\mobile\design.md", "apps\mobile\README.md",
    "backend\fastapi\README.md", "backend\spring\README.md"
)
foreach ($f in $mobileBackend) {
    $p = Join-Path $harness $f
    Test-Item "placeholder: $f" (Test-Placeholder $p)
}

# =============================================================
# 9. phases/planned/ 6 placeholder (phase_1 제외)
# =============================================================
$plannedFiles = @(
    "expo_migration_plan.md", "java_migration_plan.md",
    "moa_expansion_plan.md", "observability_expansion_plan.md",
    "pwa_mvp_plan.md", "rag_customization_plan.md"
)
foreach ($f in $plannedFiles) {
    $p = Join-Path $harness "phases\planned\$f"
    Test-Item "phases/planned: $f placeholder format" (Test-Placeholder $p)
}

# =============================================================
# 10. logs/ 4 placeholder
# =============================================================
$logsFiles = @("decision_log.md", "eval_log.md", "handoff_log.md", "log_index.md")
foreach ($f in $logsFiles) {
    $p = Join-Path $harness "logs\$f"
    Test-Item "logs: $f placeholder format" (Test-Placeholder $p)
}

# =============================================================
# 11. 9줄 이하 stub 0개 (전체 .md, 단 README 제외)
# =============================================================
$mdFiles = @(Get-ChildItem -Path $harness -Filter "*.md" -Recurse -File |
    Where-Object {
        $_.FullName -notmatch "\\(node_modules|\.git|_staging|archive)\\" -and
        $_.Name -ne "README.md"
    })
$stubCount = 0
$stubList = @()
foreach ($mf in $mdFiles) {
    $lc = Get-LineCount $mf.FullName
    if ($lc -le 9 -and $lc -gt 0) {
        $stubCount++
        $stubList += "  ($lc lines) $($mf.FullName.Substring($harness.Length+1))"
    }
}
if ($stubCount -eq 0) {
    Test-Item "no 9-line stub remaining" $true
} else {
    Test-Item "no 9-line stub remaining" $false "(found $stubCount)"
    foreach ($s in $stubList) { Write-Host $s -ForegroundColor Yellow }
}

# =============================================================
# 12. PROJECT_STATE migration_progress = completed
# =============================================================
$projectState = Read-FileText (Join-Path $harness "PROJECT_STATE.md")
Test-Item "PROJECT_STATE current_sprint = S5 or completed" `
    ($projectState -match "current_sprint:\s*(S5|completed)")
Test-Item "PROJECT_STATE migration_progress mentions completed" `
    ($projectState -match "completed" -or $projectState -match "Phase 0\s*완료|Phase 0 done")

# =============================================================
# 13. phases/active/phase-0-migration/ archive 이동
# =============================================================
$activePhase0 = Join-Path $harness "phases\active\phase-0-migration"
$archivePhase0 = Join-Path $harness "phases\archive\phase-0-migration"
Test-Item "phase-0-migration archived (not in active/)" (-not (Test-Path $activePhase0))
Test-Item "phase-0-migration present in archive/" (Test-Path $archivePhase0)

# =============================================================
# 14. PHASE_REGISTRY Phase 0 done
# =============================================================
$phaseReg = Read-FileText (Join-Path $harness "PHASE_REGISTRY.md")
Test-Item "PHASE_REGISTRY Phase 0 done/completed" `
    ($phaseReg -match "Phase 0.*(done|completed|완료|archived)" -or
     $phaseReg -match "0\.\s*Migration.*(done|completed|완료|archived)")

# =============================================================
# 결과
# =============================================================
Write-Host ""
if ($failed -eq 0) {
    Write-Host "PASS Sprint S5 verified — all checks OK, Phase 0 complete" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAIL Sprint S5 verification failed: $failed check(s)" -ForegroundColor Red
    exit 1
}
