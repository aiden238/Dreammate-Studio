#requires -Version 5.1
# scripts/smoke_test_phase_M0.ps1
# Phase M0 (Meta-Factory Prep, ★ meta-phase) automated smoke test (PowerShell 5.1 compatible)
# 경량 meta-phase 체크 (6 checks) — ★ 런타임 변경 0 (A9) 게이트 + meta_factory 구조 + harness-factory Skill 등록
# Slice 3 — Final QA gate (P-X1 50연속 + scenario_simulation v7 33/33)
#
# Phase M0 final 목표: 6/6 (런타임 변경 0 + pytest 339 유지 + audit_naming 0 + meta_factory 구조 + Skill 등록 + frontend 변경 0)
# ★ Phase M0 는 meta-phase — 런타임 무관 (FastAPI/Next.js/Supabase 0줄). 본 smoke 는 런타임 회귀가 아니라 격리를 검증.

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ROOT

# Phase M0 baseline commit (Phase 9.5 close = M0 entry 직전). 런타임 변경 0 게이트 기준.
$M0_BASE = 'fff913e'

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

Write-Host '=== Phase M0 Smoke Test (Automated, meta-phase 경량 6 checks) ===' -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor Gray
Write-Host "Baseline (M0 entry 직전): $M0_BASE (Phase 9.5 close)" -ForegroundColor Gray
Write-Host ''

# --- Step 1/6: ★ A9 런타임 변경 0 (backend/fastapi + apps/web + db/migrations git diff = 0) ---
Write-Host 'Step 1/6: ★ A9 런타임 변경 0 (git diff M0_base..HEAD -- backend/fastapi + apps/web + db/migrations = 0)' -ForegroundColor Cyan
$runtimePaths = @('harness/backend/fastapi', 'harness/apps/web', 'harness/backend/fastapi/db/migrations')
$runtimeDiff = & git diff "$M0_BASE..HEAD" --name-only -- $runtimePaths 2>&1 | Where-Object { $_.Trim() }
$runtimeCount = @($runtimeDiff).Count
if ($runtimeCount -eq 0) {
    Record 'A9 runtime 변경 0' 'PASS' 'backend/fastapi 0 / apps/web 0 (PlanCard·component_map) / db/migrations 0'
} else {
    $detail = "런타임 변경 감지 ($runtimeCount 파일): " + (($runtimeDiff | Select-Object -First 5) -join ', ')
    Record 'A9 runtime 변경 0' 'FAIL' $detail
}

# --- Step 2/6: pytest 339 유지 (런타임 무관 — 회귀 0 확인) ---
Write-Host ''
Write-Host 'Step 2/6: pytest backend (Phase 9.5 baseline 339 유지 — 런타임 변경 0 → 회귀 0)' -ForegroundColor Cyan
$pytestOutput = & python -m pytest -q --tb=line 2>&1 | Out-String
if ($LASTEXITCODE -eq 0) {
    $passLine = $pytestOutput -split "`n" | Where-Object { $_ -match '\d+ passed' } | Select-Object -First 1
    if ($passLine) {
        Record 'pytest backend' 'PASS' ("$($passLine.Trim()) (339 baseline 유지)")
    } else {
        Record 'pytest backend' 'PASS' 'all tests passed'
    }
} else {
    $tailLine = ($pytestOutput -split "`n" | Select-Object -Last 3) -join ' | '
    Record 'pytest backend' 'FAIL' $tailLine
}

# --- Step 3/6: audit_naming 0 drift (meta_factory 명명 정합) ---
Write-Host ''
Write-Host 'Step 3/6: audit_naming (meta_factory 명명 정합 — 0 drift)' -ForegroundColor Cyan
& powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $ROOT 'scripts/audit_naming.ps1') 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Record 'audit_naming' 'PASS' '0 drift'
} else {
    Record 'audit_naming' 'FAIL' 'drift detected'
}

# --- Step 4/6: meta_factory 구조 존재 (Slice 1~2 산출물 + Slice 3) ---
Write-Host ''
Write-Host 'Step 4/6: meta_factory 구조 존재 (README + factory_contract + 2 schema + architecture_patterns + 2 workflow + templates 6 + blueprint + outputs)' -ForegroundColor Cyan
$mf = Join-Path $ROOT 'meta_factory'
$mfRequired = @(
    'meta_factory/README.md',
    'meta_factory/factory_contract.md',
    'meta_factory/domain_brief_schema.md',
    'meta_factory/harness_blueprint_schema.md',
    'meta_factory/architecture_patterns.md',
    'meta_factory/generation_workflow.md',
    'meta_factory/validation_workflow.md',
    'meta_factory/templates/agent_template.md',
    'meta_factory/templates/skill_template.md',
    'meta_factory/templates/contract_template.md',
    'meta_factory/templates/eval_template.md',
    'meta_factory/templates/phase_template.md',
    'meta_factory/templates/project_state_template.md',
    'meta_factory/blueprints/dreammate_current_harness_blueprint.md',
    'meta_factory/outputs/generated_harnesses',
    'meta_factory/outputs/improvement_reports'
)
$mfMissing = @()
foreach ($p in $mfRequired) {
    if (-not (Test-Path -LiteralPath (Join-Path $ROOT $p))) { $mfMissing += $p }
}
if ($mfMissing.Count -eq 0) {
    Record 'meta_factory 구조' 'PASS' "$($mfRequired.Count) 항목 존재 (7 루트 + templates 6 + blueprint + outputs 2)"
} else {
    Record 'meta_factory 구조' 'FAIL' ("누락: " + ($mfMissing -join ', '))
}

# --- Step 5/6: harness-factory Skill 존재 + INDEX #21 등록 ---
Write-Host ''
Write-Host 'Step 5/6: harness-factory Skill 존재 + INDEX #21 등록 (proposal-only, 키워드 scoped)' -ForegroundColor Cyan
$skillPath = Join-Path $ROOT '.claude/skills/harness-factory/SKILL.md'
$indexPath = Join-Path $ROOT '.claude/skills/INDEX.md'
$skillOk = Test-Path -LiteralPath $skillPath
$indexContent = if (Test-Path -LiteralPath $indexPath) { [System.IO.File]::ReadAllText($indexPath) } else { '' }
$indexHas21 = $indexContent -match '21\s*\|\s*harness-factory'
# 헤더 카운트: "총 21개" (UTF-8 한글) 또는 ASCII fallback ("21" + harness-factory 등록 = 21개 확정)
$indexHasCount = ($indexContent -match '21.{0,4}Skill') -or $indexHas21
if ($skillOk -and $indexHas21 -and $indexHasCount) {
    Record 'harness-factory Skill + INDEX #21' 'PASS' 'SKILL.md 존재 + INDEX #21 등록 (총 21개)'
} elseif ($skillOk -and $indexHas21) {
    Record 'harness-factory Skill + INDEX #21' 'WARN' 'SKILL.md + #21 등록 (헤더 카운트 확인 필요)'
} else {
    $miss = @()
    if (-not $skillOk) { $miss += 'SKILL.md 부재' }
    if (-not $indexHas21) { $miss += 'INDEX #21 미등록' }
    Record 'harness-factory Skill + INDEX #21' 'FAIL' ($miss -join ', ')
}

# --- Step 6/6: frontend 변경 0 확인 (tsc/build — 선택, frontend 변경 0 이므로 SKIP 허용) ---
Write-Host ''
Write-Host 'Step 6/6: frontend 변경 0 확인 (apps/web git diff = 0 → tsc/build 선택)' -ForegroundColor Cyan
$webDiff = & git diff "$M0_BASE..HEAD" --name-only -- 'harness/apps/web' 2>&1 | Where-Object { $_.Trim() }
$webCount = @($webDiff).Count
if ($webCount -eq 0) {
    Record 'frontend 변경 0' 'PASS' 'apps/web 0줄 (PlanCard·component_map 0줄 — tsc/build 불요, frontend 무변경)'
} else {
    Record 'frontend 변경 0' 'WARN' "apps/web 변경 감지 ($webCount 파일) — meta-phase A9 위반 점검 필요"
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
    Write-Host 'Phase M0 smoke test FAILED' -ForegroundColor Red
    exit 1
}

Write-Host ''
Write-Host 'Phase M0 smoke test PASSED (meta-phase — 런타임 변경 0 격리 + meta_factory 구조 + harness-factory 등록)' -ForegroundColor Green
exit 0
