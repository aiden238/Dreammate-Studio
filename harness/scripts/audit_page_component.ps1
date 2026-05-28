#requires -Version 5.1
# audit_page_component.ps1 - Phase 3 Slice 6 (D5)
# page_map.md <-> apps/web/app/ routes 정합
# component_map.md <-> apps/web/components/ 정합
#
# (조정 4번) component_map.md / page_map.md 직접 수정 금지 - 본 도구는 검출만.
# drift 발견 시 deviations.md에만 기록.

$ErrorActionPreference = 'Continue'
$ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ROOT

$total_drift = 0

# ─── 1. page_map.md spec routes 추출 ──────────────────────────────────
$pageMapPath = "apps/web/page_map.md"
if (-not (Test-Path $pageMapPath)) {
    Write-Host "[FAIL] $pageMapPath not found" -ForegroundColor Red
    exit 1
}
$pageMapContent = Get-Content $pageMapPath -Raw -Encoding UTF8

$spec_routes = @()
# route 헤더 패턴 (page_map.md 실 사용):
#   ### 1.1 `/`   (Phase 1 active routes)
#   ### 1.2 `/plan`
#   #### `/new`   (Phase 2 spec routes)
#   #### `/new/discovery/step/1`
foreach ($line in ($pageMapContent -split "`r?`n")) {
    # ### X.Y `/path` or #### `/path`
    if ($line -match '^\s*#{2,4}\s+(?:\d+(?:\.\d+)?\s+)?`(/[^`]*)`') {
        $route = $matches[1]
        if ($route -ne '/') { $route = $route.TrimEnd('/') }
        $spec_routes += $route
    }
}
$spec_routes = $spec_routes | Sort-Object -Unique

# ─── 2. 실 routes 추출 (apps/web/app/) ────────────────────────────────
$actual_routes = @()
$appDir = Join-Path $ROOT "apps/web/app"
if (Test-Path $appDir) {
    Get-ChildItem -Path $appDir -Recurse -File -Filter "page.tsx" -ErrorAction SilentlyContinue | ForEach-Object {
        $rel = $_.FullName.Substring($appDir.Length + 1) -replace '\\', '/'
        $route = '/' + ($rel -replace '/page\.tsx$', '' -replace '^page\.tsx$', '')
        if ($route -eq '/') { $route = '/' }
        $actual_routes += $route
    }
}
$actual_routes = $actual_routes | Sort-Object -Unique

# ─── 3. 비교 ──────────────────────────────────────────────────────────
Write-Host '=== audit_page_component ===' -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor Gray
Write-Host ''
Write-Host "Spec routes ($($spec_routes.Count)) :" -ForegroundColor Yellow
foreach ($r in $spec_routes) { Write-Host "  $r" }
Write-Host ''
Write-Host "Actual routes ($($actual_routes.Count)) :" -ForegroundColor Yellow
foreach ($r in $actual_routes) { Write-Host "  $r" }
Write-Host ''

# spec에만 있는 routes (구현 누락 가능성 — Phase 4+ deferred는 spec에 placeholder)
$spec_only = @($spec_routes | Where-Object { $_ -notin $actual_routes })
# actual에만 있는 routes (spec 누락 — drift)
$actual_only = @($actual_routes | Where-Object { $_ -notin $spec_routes })

# Phase 3 동적 라우트 정규화:
#   spec: /new/discovery/step/1, /new/discovery/step/2 ... step/7
#   actual: /new/discovery/step/1, /new/discovery/step/[n]
# /new/discovery/step/[n] 은 step/2~7 모두를 커버하는 dynamic route
$dynamic_coverage = @{}
if ('/new/discovery/step/[n]' -in $actual_routes) {
    foreach ($r in @('/new/discovery/step/2','/new/discovery/step/3','/new/discovery/step/4','/new/discovery/step/5','/new/discovery/step/6','/new/discovery/step/7')) {
        if ($r -in $spec_only) { $dynamic_coverage[$r] = $true }
    }
    # spec_only에서 dynamic_coverage 항목 제거
    $spec_only = @($spec_only | Where-Object { -not $dynamic_coverage.ContainsKey($_) })
    # actual_only에서 /new/discovery/step/[n] 제거 (dynamic route는 spec /step/2~7과 매핑)
    $actual_only = @($actual_only | Where-Object { $_ -ne '/new/discovery/step/[n]' })
}

if ($spec_only.Count -gt 0) {
    Write-Host "[INFO] spec only (Phase 4+ deferred 또는 dynamic 커버) :" -ForegroundColor Cyan
    foreach ($r in $spec_only) { Write-Host "  $r" -ForegroundColor Cyan }
    Write-Host '  (위 routes는 spec에 명세되었으나 실 구현 없음 - Phase 3+ deferred 가능)' -ForegroundColor Gray
}
if ($dynamic_coverage.Count -gt 0) {
    Write-Host ''
    Write-Host "[INFO] dynamic route 커버됨 (step/[n] -> step/2~7) :" -ForegroundColor Cyan
    foreach ($r in $dynamic_coverage.Keys) { Write-Host "  $r" -ForegroundColor Cyan }
}

if ($actual_only.Count -gt 0) {
    Write-Host ''
    Write-Host "[FAIL] actual only (spec 누락 - drift):" -ForegroundColor Red
    foreach ($r in $actual_only) { Write-Host "  $r" -ForegroundColor Red }
    $total_drift += $actual_only.Count
}

# ─── 4. component_map.md spec components 추출 ─────────────────────────
# component_map.md 형식:
#   ## ComponentName (Phase 2 Slice X)   ← 4-layer component
#   | ComponentName | ... | ... |          ← 매트릭스 table 첫 셀
# section 헤더 (## Layout, ## Input Components 등) + 비-컴포넌트 헤더는 stop-list 제외.
$compMapPath = "apps/web/component_map.md"
$spec_components = @()
$stop_list = @(
    'Layout','Input','Discovery','Quick','AI','Output','Project','Feedback',
    'Replaceability','Routes','Slice','State','PlanComparisonCard',  # PlanComparisonCard는 Phase 4 placeholder
    # design token / 매트릭스 cell 가짜 매칭 제외
    'Route','bg','border','motion','radius','text'
)
if (Test-Path $compMapPath) {
    $compMapContent = Get-Content $compMapPath -Raw -Encoding UTF8
    foreach ($line in ($compMapContent -split "`r?`n")) {
        # ## ComponentName (Phase ...) 4-layer header — case-sensitive (PowerShell -cmatch)
        if ($line -cmatch '^\s*##\s+([A-Z][A-Za-z0-9_]+)(\s|\(|$)') {
            $name = $matches[1]
            if ($name -cnotin $stop_list) {
                $spec_components += $name
            } elseif ($name -ceq 'PlanComparisonCard') {
                $spec_components += $name
            }
        }
        # | ComponentName | desc | ... matrix row
        if ($line -cmatch '^\|\s+([A-Z][A-Za-z0-9_]+)\s+\|') {
            $name = $matches[1]
            if ($name -cnotin $stop_list -and $name -cne 'Component') {
                $spec_components += $name
            }
        }
        # | N | ComponentName | ... numbered matrix row
        if ($line -cmatch '^\|\s+\d+\s+\|\s+([A-Z][A-Za-z0-9_]+)') {
            $name = $matches[1]
            if ($name -cnotin $stop_list) {
                $spec_components += $name
            }
        }
    }
    $spec_components = $spec_components | Sort-Object -Unique
}

# ─── 5. 실 components 추출 ────────────────────────────────────────────
$actual_components = @()
$compDir = Join-Path $ROOT "apps/web/components"
if (Test-Path $compDir) {
    Get-ChildItem -Path $compDir -Recurse -File -Filter "*.tsx" -ErrorAction SilentlyContinue | Where-Object {
        $_.Name -notlike "*.test.tsx" -and $_.FullName -notlike "*__tests__*"
    } | ForEach-Object {
        $actual_components += $_.BaseName
    }
}
$actual_components = $actual_components | Sort-Object -Unique

Write-Host ''
Write-Host "Spec components ($($spec_components.Count)) :" -ForegroundColor Yellow
Write-Host "  $($spec_components -join ', ')"
Write-Host ''
Write-Host "Actual components ($($actual_components.Count)) :" -ForegroundColor Yellow
Write-Host "  $($actual_components -join ', ')"
Write-Host ''

# Phase 4+ deferred placeholder는 spec_only로 검출됨 (drift 아님)
$comp_spec_only = @($spec_components | Where-Object { $_ -notin $actual_components })
$comp_actual_only = @($actual_components | Where-Object { $_ -notin $spec_components })

if ($comp_spec_only.Count -gt 0) {
    Write-Host "[INFO] components spec only (Phase 4+ deferred placeholder 가능) :" -ForegroundColor Cyan
    foreach ($c in $comp_spec_only) { Write-Host "  $c" -ForegroundColor Cyan }
}
if ($comp_actual_only.Count -gt 0) {
    Write-Host ''
    Write-Host "[FAIL] components actual only (spec 누락 - drift):" -ForegroundColor Red
    foreach ($c in $comp_actual_only) { Write-Host "  $c" -ForegroundColor Red }
    $total_drift += $comp_actual_only.Count
}

# ─── Summary ──────────────────────────────────────────────────────────
Write-Host ''
Write-Host '=== Summary ===' -ForegroundColor Cyan
Write-Host "spec routes: $($spec_routes.Count) / actual routes: $($actual_routes.Count)"
Write-Host "spec components: $($spec_components.Count) / actual components: $($actual_components.Count)"
Write-Host ''
if ($total_drift -eq 0) {
    Write-Host "audit_page_component PASS - 0 drift" -ForegroundColor Green
    Write-Host '(spec only는 의도된 Phase 4+ deferred placeholder, dynamic route는 [n] 정규화)' -ForegroundColor Gray
    exit 0
} else {
    Write-Host "audit_page_component FAIL - $total_drift drift hit(s)" -ForegroundColor Red
    Write-Host '조정 4번 위반 시: phases/active/.../deviations.md 기록만. spec 파일 직접 수정 X.' -ForegroundColor Yellow
    exit 1
}
