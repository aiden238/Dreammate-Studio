#requires -Version 5.1
# audit_naming.ps1 — contract / code / frontend 간 핵심 명명 일관성 점검
#
# 목적: P-DRIFT-001 패턴 자동 감지 (meta/patterns.md 참조).
# 출처: meta/proposals/2026-05-26_phase-1-retrospective-proposals.md P1.
#
# 사용:
#   pwsh -File scripts/audit_naming.ps1
#
# 종료 코드:
#   0: 모든 명명 일관 (PASS)
#   1: drift 발견 (FAIL — 사용자 확인 필요)

$ErrorActionPreference = 'Continue'
$ProgressPreference = 'SilentlyContinue'

$ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ROOT

# ─── Canonical 명명 정책 ──────────────────────────────────────────────
# 형식: @{ canonical = '<name>'; deprecated = @(<aliases>); scope_required = @(<file patterns>) }

$NAMING_POLICY = @(
    @{
        canonical = 'plan_candidates'
        deprecated = @('plan_options')
        # 'plans'는 docs/contracts/api_contract.md 의 URL path (/api/v1/plans/{plan_id}/generate) 와
        # ai_system/orchestration 의 일반 명사로 광범위 사용 → 점검에서 제외 (false positive 회피).
        rationale = 'CC-001 Option B (2026-05-26)'
        scope = @('docs/contracts/**/*.md', 'backend/fastapi/**/*.py', 'apps/web/**/*.ts', 'apps/web/**/*.tsx')
        whitelist = @(
            'docs/contract_changes/2026-05-26_plan_options_vs_plan_candidates.md',  # 결정 기록
            'phases/archive/**',                                                     # 역사 보존
            'eval/qa_reports/**',                                                    # 역사 보존
            'meta/retrospectives/**',                                                # 회고 보존
            'meta/patterns.md',                                                      # 패턴 보존
            'meta/proposals/**'                                                      # 제안 보존
        )
    },
    @{
        canonical = 'video_projects'
        deprecated = @('video_project_table', 'videoProjects')
        rationale = 'db_schema.md §video_projects'
        scope = @('docs/contracts/**/*.md', 'backend/fastapi/**/*.py', 'backend/fastapi/**/*.sql')
        whitelist = @('phases/archive/**', 'eval/qa_reports/**', 'meta/**')
    },
    @{
        canonical = 'critic_evaluation'
        # 'CriticEvaluation' (PascalCase 클래스명)은 정상 — case-sensitive 검사로 false positive 회피.
        # 'critic_eval' (잘린 snake_case) 또는 'criticEval' (잘린 camelCase) 만 deprecated.
        deprecated = @('critic_eval', 'criticEval')
        rationale = 'output_schema.md §9 (JSON field 명)'
        scope = @('docs/contracts/**/*.md', 'backend/fastapi/**/*.py', 'apps/web/**/*.ts', 'apps/web/**/*.tsx')
        whitelist = @('phases/archive/**', 'eval/qa_reports/**', 'meta/**')
    },
    @{
        canonical = 'rag_references'
        # 'RAGReference' / 'RAGReferences' (PascalCase 클래스명) 정상.
        # camelCase 'ragReferences'는 우리 프로젝트에서 사용 금지 (JSON+TS interface 모두 snake_case 통일).
        deprecated = @('ragReferences')
        rationale = 'output_schema.md §body'
        scope = @('docs/contracts/**/*.md', 'apps/web/**/*.ts', 'apps/web/**/*.tsx')
        whitelist = @('phases/archive/**', 'eval/qa_reports/**', 'meta/**')
    }
)

# ─── 진단 함수 ────────────────────────────────────────────────────────

function Test-Whitelist($path, $whitelist) {
    foreach ($pattern in $whitelist) {
        $regex = $pattern -replace '/', '[/\\]' -replace '\*\*', '.*' -replace '\*', '[^/\\]*'
        if ($path -match $regex) { return $true }
    }
    return $false
}

function Search-Deprecated($deprecated, $scope, $whitelist) {
    $hits = @()
    foreach ($depr in $deprecated) {
        foreach ($pattern in $scope) {
            $regex = $pattern -replace '/', '[/\\]' -replace '\*\*', '.*' -replace '\*', '[^/\\]*'
            $files = Get-ChildItem -Recurse -File -ErrorAction SilentlyContinue |
                     Where-Object { $_.FullName -match $regex }

            foreach ($f in $files) {
                $rel = $f.FullName.Substring($ROOT.Length + 1) -replace '\\', '/'
                if (Test-Whitelist $rel $whitelist) { continue }

                try {
                    # case-sensitive: PascalCase 클래스명(정상)이 camelCase deprecated 패턴에 매치되는 false positive 방지
                    $matches = Select-String -Path $f.FullName -Pattern "\b$depr\b" -CaseSensitive -SimpleMatch:$false -ErrorAction SilentlyContinue
                } catch { $matches = $null }
                if ($matches) {
                    foreach ($m in $matches) {
                        $hits += [pscustomobject]@{
                            Deprecated = $depr
                            Canonical  = $canonical
                            File       = $rel
                            Line       = $m.LineNumber
                            Text       = $m.Line.Trim()
                        }
                    }
                }
            }
        }
    }
    return $hits
}

# ─── Main ─────────────────────────────────────────────────────────────

Write-Host '=== audit_naming (contract drift detection) ===' -ForegroundColor Cyan
Write-Host "Root: $ROOT" -ForegroundColor Gray
Write-Host ''

$totalDrift = 0
$summary = @()

foreach ($policy in $NAMING_POLICY) {
    $canonical = $policy.canonical
    Write-Host "Checking: $canonical (deprecated: $($policy.deprecated -join ', '))" -ForegroundColor Cyan

    $hits = Search-Deprecated $policy.deprecated $policy.scope $policy.whitelist

    if ($hits.Count -eq 0) {
        Write-Host "  [PASS] no drift" -ForegroundColor Green
        $summary += [pscustomobject]@{ Canonical = $canonical; Status = 'PASS'; DriftCount = 0 }
    } else {
        Write-Host "  [FAIL] $($hits.Count) drift hit(s)" -ForegroundColor Red
        $hits | ForEach-Object {
            Write-Host ("    " + $_.File + ":" + $_.Line + " — " + $_.Text) -ForegroundColor Yellow
        }
        $summary += [pscustomobject]@{ Canonical = $canonical; Status = 'FAIL'; DriftCount = $hits.Count }
        $totalDrift += $hits.Count
    }
    Write-Host ''
}

# ─── Summary ──────────────────────────────────────────────────────────

Write-Host '=== Summary ===' -ForegroundColor Cyan
$summary | Format-Table -AutoSize | Out-String | Write-Host

Write-Host ''
if ($totalDrift -eq 0) {
    Write-Host "audit_naming PASS — 0 drift detected" -ForegroundColor Green
    exit 0
} else {
    Write-Host "audit_naming FAIL — $totalDrift drift hit(s)" -ForegroundColor Red
    Write-Host 'contract-change Skill 또는 whitelist 보강 필요' -ForegroundColor Yellow
    exit 1
}
