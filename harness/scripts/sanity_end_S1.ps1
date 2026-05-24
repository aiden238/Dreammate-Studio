#!/usr/bin/env pwsh
# Sprint S1 종료 sanity check (Windows PowerShell-compatible)
# Usage: pwsh ./scripts/sanity_end_S1.ps1
# Returns: exit 0 on PASS, exit 1 on FAIL

$ErrorActionPreference = "Stop"

$harness = Split-Path -Parent $PSScriptRoot
$workspace = Split-Path -Parent $harness

Write-Host "=== Sprint S1 End Check ===" -ForegroundColor Cyan
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
    # Counts LF chars in the file (robust to UTF-16 / UTF-8 / mixed encodings).
    param([string]$Path)
    if (-not (Test-Path $Path)) { return 0 }
    $content = [System.IO.File]::ReadAllText($Path)
    return ($content.ToCharArray() | Where-Object { $_ -eq "`n" }).Count
}

# 1. Core 3 contracts: line count thresholds
$designLines = Get-LineCount (Join-Path $harness "apps\web\design.md")
Test-Item "apps/web/design.md >= 680 lines" ($designLines -ge 680) "(actual: $designLines)"

$dbLines = Get-LineCount (Join-Path $harness "docs\contracts\db_schema.md")
Test-Item "docs/contracts/db_schema.md >= 570 lines" ($dbLines -ge 570) "(actual: $dbLines)"

$promptLines = Get-LineCount (Join-Path $harness "ai_system\prompts\prompt_registry.md")
Test-Item "ai_system/prompts/prompt_registry.md >= 620 lines" ($promptLines -ge 620) "(actual: $promptLines)"

# 2. db_schema.md keyword checks
$dbContent = [System.IO.File]::ReadAllText((Join-Path $harness "docs\contracts\db_schema.md"))
Test-Item "db_schema.md contains 'candidate_knowledge'" ($dbContent -match "candidate_knowledge")
Test-Item "db_schema.md contains 'brand_memory_entries'" ($dbContent -match "brand_memory_entries")
Test-Item "db_schema.md contains 'plan_options'" ($dbContent -match "plan_options")

# 3. prompt_registry.md keyword checks
$promptContent = [System.IO.File]::ReadAllText((Join-Path $harness "ai_system\prompts\prompt_registry.md"))
Test-Item "prompt_registry.md contains 'P-001'" ($promptContent -match "P-001")
Test-Item "prompt_registry.md contains 'P-008'" ($promptContent -match "P-008")
Test-Item "prompt_registry.md contains 'P-AUX'" ($promptContent -match "P-AUX")

# 4. page_map.md / component_map.md line range checks (90 <= lines <= 140)
$pageLines = Get-LineCount (Join-Path $harness "apps\web\page_map.md")
Test-Item "page_map.md in [90, 140] lines" ($pageLines -ge 90 -and $pageLines -le 140) "(actual: $pageLines)"

$compLines = Get-LineCount (Join-Path $harness "apps\web\component_map.md")
Test-Item "component_map.md in [90, 140] lines" ($compLines -ge 90 -and $compLines -le 140) "(actual: $compLines)"

# 5. page_map.md mentions Discovery + Quick
$pageContent = [System.IO.File]::ReadAllText((Join-Path $harness "apps\web\page_map.md"))
Test-Item "page_map.md mentions 'Discovery'" ($pageContent -match "Discovery")
Test-Item "page_map.md mentions 'Quick'" ($pageContent -match "Quick")

# 6. component_map.md mentions key components
$compContent = [System.IO.File]::ReadAllText((Join-Path $harness "apps\web\component_map.md"))
Test-Item "component_map.md mentions 'PlanOptionCard'" ($compContent -match "PlanOptionCard")
Test-Item "component_map.md mentions 'OneLineDirectionCard'" ($compContent -match "OneLineDirectionCard")

# 7. dependency_map.yaml references
$depContent = [System.IO.File]::ReadAllText((Join-Path $harness "instruction_index\dependency_map.yaml"))
Test-Item "dependency_map.yaml mentions 'candidate_knowledge'" ($depContent -match "candidate_knowledge")
Test-Item "dependency_map.yaml mentions 'P-006'" ($depContent -match "P-006")

# 결과
Write-Host ""
$total = $failed + ($script:failedCount)
if ($failed -eq 0) {
    Write-Host "PASS Sprint S1 verified — all checks OK" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAIL Sprint S1 verification failed: $failed check(s)" -ForegroundColor Red
    exit 1
}
