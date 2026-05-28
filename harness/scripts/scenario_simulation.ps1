#requires -Version 5.1
# scripts/scenario_simulation.ps1
# Phase 4.5+ Changeability Simulation auto-gate (P-X2)
# Called automatically by phase-complete Skill v1.2.0 §1.6 at Phase close.

$ErrorActionPreference = 'Stop'
$ProgressPreference   = 'SilentlyContinue'

$ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ROOT

Write-Host "=== scenario_simulation (P-X2 auto-gate) ===" -ForegroundColor Cyan
Write-Host "Root: $ROOT"
Write-Host ""

$scenarios = @(
    @{ Id = "S1"; Name = "PlanCard visual tone change (visual layer)"; Files = @("apps/web/components/PlanCard.tsx", "apps/web/lib/design_tokens.ts") },
    @{ Id = "S2"; Name = "component_map entry addition"; Files = @("apps/web/component_map.md") },
    @{ Id = "S3"; Name = "wrapper UI ring color change"; Files = @("apps/web/app/plan/[plan_id]/page.tsx") },
    @{ Id = "S4"; Name = "revise loop max attempts change (config)"; Files = @("backend/fastapi/config.py") },
    @{ Id = "S5"; Name = "recommended_plan_index disable"; Files = @("backend/fastapi/routers/plans.py", "backend/fastapi/schemas/output.py") }
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
    Write-Host "scenario_simulation FAIL - $fail/$($scenarios.Count) failed" -ForegroundColor Red
    exit 1
}
