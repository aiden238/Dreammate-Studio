#!/usr/bin/env pwsh
# Sprint 시작 전 sanity check (PowerShell, Windows-compatible)
# Usage: pwsh ./scripts/sanity_start.ps1 -Sprint S0
# Returns: exit 0 on PASS, exit 1 on FAIL

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("S0","S1","S2","S3","S4","S5")]
    [string]$Sprint
)

$ErrorActionPreference = "Stop"

$harness = Split-Path -Parent $PSScriptRoot
$workspace = Split-Path -Parent $harness

Write-Host "=== Sprint $Sprint Start Check ===" -ForegroundColor Cyan
Write-Host "harness root: $harness"
Write-Host "workspace   : $workspace"
Write-Host ""

# 1. HARNESS 폴더 존재
if (-not (Test-Path $harness)) {
    Write-Host "FAIL: harness folder not found" -ForegroundColor Red
    exit 1
}
Write-Host "OK   : harness folder exists" -ForegroundColor Green

# 2. git 상태 clean (uncommitted 변경 없음)
Push-Location $workspace
try {
    $status = git status --porcelain
    if ($status) {
        Write-Host "FAIL: uncommitted changes present:" -ForegroundColor Red
        Write-Host $status
        exit 1
    }
    Write-Host "OK   : git working tree clean" -ForegroundColor Green

    # 3. 이전 Sprint commit 존재 확인 (S0 제외)
    if ($Sprint -ne "S0") {
        $prevMap = @{ "S1"="S0"; "S2"="S1"; "S3"="S2"; "S4"="S3"; "S5"="S4" }
        $prev = $prevMap[$Sprint]
        $log = (git log --oneline | Out-String)
        if ($log -notmatch "\($prev\)") {
            Write-Host "FAIL: previous Sprint $prev not committed" -ForegroundColor Red
            exit 1
        }
        Write-Host "OK   : previous Sprint $prev commit present" -ForegroundColor Green
    } else {
        Write-Host "OK   : S0 (no previous Sprint required)" -ForegroundColor Green
    }
} finally {
    Pop-Location
}

# 4. Sprint별 필수 파일 존재
switch ($Sprint) {
    "S0" {
        $required = @("PROJECT_STATE.md", "PHASE_REGISTRY.md", "migration_procedure.md")
    }
    "S1" {
        $required = @("PROJECT_STATE.md")
        $stagingRequired = @("design.md", "db_schema.md", "prompt_registry.md")
        foreach ($f in $stagingRequired) {
            if (-not (Test-Path "$workspace\_staging\$f")) {
                Write-Host "FAIL: _staging/$f not found (required for S1)" -ForegroundColor Red
                exit 1
            }
        }
    }
    "S2" {
        $required = @("PROJECT_STATE.md")
        if (-not (Test-Path "$workspace\_staging\skills")) {
            Write-Host "FAIL: _staging/skills not found (required for S2)" -ForegroundColor Red
            exit 1
        }
    }
    "S3" { $required = @("PROJECT_STATE.md", "docs\contracts\db_schema.md") }
    "S4" { $required = @("PROJECT_STATE.md", "ai_system\prompts\prompt_registry.md") }
    "S5" { $required = @("PROJECT_STATE.md") }
}

foreach ($f in $required) {
    $p = Join-Path $harness $f
    if (-not (Test-Path $p)) {
        Write-Host "FAIL: $f not found" -ForegroundColor Red
        exit 1
    }
}
Write-Host "OK   : required files present for $Sprint" -ForegroundColor Green

Write-Host ""
Write-Host "PASS Sanity OK, Sprint $Sprint can start" -ForegroundColor Green
exit 0
