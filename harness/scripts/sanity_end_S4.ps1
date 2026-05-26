#!/usr/bin/env pwsh
# Sprint S4 종료 sanity check (Windows PowerShell-compatible)
# Usage: pwsh ./scripts/sanity_end_S4.ps1
# Returns: exit 0 on PASS, exit 1 on FAIL
#
# 검증 범위:
#   - eval/ 15 파일 (>= 50줄), golden_set.md (>= 200줄, 10+ case)
#   - knowledge/rag/ 8 파일 (>= 50줄)
#   - knowledge/llm_wiki/ 6 파일 (>= 50줄)
#   - knowledge/datasets/ 4 파일 (>= 50줄)
#   - ai_system/agents/ 4 deep (intent/planning/critic/rewrite) + 2 placeholder (package/research)
#   - ai_system/orchestration/ 5 파일 (>= 50줄)
#   - ai_system/memory/ 5 파일 (>= 50줄)
#   - ai_system/architecture.md (>= 150줄)
#   - prompts/prompt_registry.md 에 P-EVAL-1 정의 추가
#   - Planner -> Planning 명명 통일 (S3 contracts 갱신 확인)
#   - PROJECT_STATE migration_progress 갱신

$ErrorActionPreference = "Stop"

$harness = Split-Path -Parent $PSScriptRoot
$workspace = Split-Path -Parent $harness

Write-Host "=== Sprint S4 End Check ===" -ForegroundColor Cyan
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

# =============================================================
# 1. eval/ 15 파일 (>= 50줄)
# =============================================================
$evalFiles = @(
    "accessibility_checklist.md",
    "brand_consistency_eval.md",
    "confidence_score.md",
    "design_review_checklist.md",
    "execution_feasibility_eval.md",
    "failure_taxonomy.md",
    "hook_quality_eval.md",
    "human_review_rubric.md",
    "phase_eval.md",
    "regression_eval.md",
    "security_eval.md",
    "target_fit_eval.md",
    "ux_eval.md",
    "video_planning_eval.md"
)

foreach ($f in $evalFiles) {
    $p = Join-Path $harness "eval\$f"
    $lines = Get-LineCount $p
    Test-Item "eval: $f >= 50 lines" ($lines -ge 50) "(actual: $lines)"
}

# golden_set.md (>= 200 줄, 10+ case)
$goldenPath = Join-Path $harness "eval\golden_set.md"
$goldenLines = Get-LineCount $goldenPath
Test-Item "eval: golden_set.md >= 200 lines" ($goldenLines -ge 200) "(actual: $goldenLines)"
$goldenContent = Read-FileText $goldenPath
$caseMatches = [regex]::Matches($goldenContent, "(?m)^##+\s*.*GS-\d{3}")
Test-Item "eval: golden_set has 10+ cases" ($caseMatches.Count -ge 10) "(actual cases: $($caseMatches.Count))"

# =============================================================
# 2. knowledge/rag/ 8 파일 (>= 50줄)
# =============================================================
$ragFiles = @(
    "chunking_policy.md",
    "custom_rag_plan.md",
    "metadata_schema.md",
    "promotion_rule.md",
    "quality_filter.md",
    "retrieval_policy.md",
    "sdk_rag_policy.md",
    "sources.md"
)
foreach ($f in $ragFiles) {
    $p = Join-Path $harness "knowledge\rag\$f"
    $lines = Get-LineCount $p
    Test-Item "knowledge/rag: $f >= 50 lines" ($lines -ge 50) "(actual: $lines)"
}

# =============================================================
# 3. knowledge/llm_wiki/ 6 파일 (>= 50줄)
# =============================================================
$wikiFiles = @(
    "branding_video.md",
    "evaluation_criteria.md",
    "hook_patterns.md",
    "index.md",
    "promo_video.md",
    "shortform_planning.md"
)
foreach ($f in $wikiFiles) {
    $p = Join-Path $harness "knowledge\llm_wiki\$f"
    $lines = Get-LineCount $p
    Test-Item "knowledge/llm_wiki: $f >= 50 lines" ($lines -ge 50) "(actual: $lines)"
}

# =============================================================
# 4. knowledge/datasets/ 4 파일 (>= 50줄)
# =============================================================
$datasetFiles = @(
    "external_seed_data.md",
    "internal_generated_data.md",
    "user_choice_data.md",
    "user_feedback_data.md"
)
foreach ($f in $datasetFiles) {
    $p = Join-Path $harness "knowledge\datasets\$f"
    $lines = Get-LineCount $p
    Test-Item "knowledge/datasets: $f >= 50 lines" ($lines -ge 50) "(actual: $lines)"
}

# =============================================================
# 5. ai_system/agents/ 4 deep + 2 placeholder
# =============================================================
$deepAgents = @("intent_agent.md", "planning_agent.md", "critic_agent.md", "rewrite_agent.md")
foreach ($f in $deepAgents) {
    $p = Join-Path $harness "ai_system\agents\$f"
    $lines = Get-LineCount $p
    Test-Item "ai_system/agents: $f >= 80 lines" ($lines -ge 80) "(actual: $lines)"
}

$placeholderAgents = @("package_agent.md", "research_agent.md")
foreach ($f in $placeholderAgents) {
    $p = Join-Path $harness "ai_system\agents\$f"
    $txt = Read-FileText $p
    $hasMarker = ($txt -match "PLACEHOLDER")
    $hasStatus = ($txt -match "status:\s*placeholder")
    $hasFillIn = ($txt -match "fill_in_phase|Fill-In Trigger|fill_in_trigger")
    Test-Item "ai_system/agents: $f placeholder format" ($hasMarker -and $hasStatus -and $hasFillIn)
}

# =============================================================
# 6. ai_system/orchestration/ 5 파일 (>= 50줄)
# =============================================================
$orchFiles = @(
    "cost_control_policy.md",
    "fallback_policy.md",
    "flow.md",
    "moa_policy.md",
    "service_boundary.md"
)
foreach ($f in $orchFiles) {
    $p = Join-Path $harness "ai_system\orchestration\$f"
    $lines = Get-LineCount $p
    Test-Item "ai_system/orchestration: $f >= 50 lines" ($lines -ge 50) "(actual: $lines)"
}

# =============================================================
# 7. ai_system/memory/ 5 파일 (>= 50줄)
# =============================================================
$memoryFiles = @(
    "candidate_knowledge_policy.md",
    "feedback_loop_policy.md",
    "knowledge_promotion_policy.md",
    "project_memory_policy.md",
    "user_memory_policy.md"
)
foreach ($f in $memoryFiles) {
    $p = Join-Path $harness "ai_system\memory\$f"
    $lines = Get-LineCount $p
    Test-Item "ai_system/memory: $f >= 50 lines" ($lines -ge 50) "(actual: $lines)"
}

# =============================================================
# 8. ai_system/architecture.md (>= 150줄)
# =============================================================
$archPath = Join-Path $harness "ai_system\architecture.md"
$archLines = Get-LineCount $archPath
Test-Item "ai_system/architecture.md >= 150 lines" ($archLines -ge 150) "(actual: $archLines)"

# =============================================================
# 9. prompt_registry.md 에 P-EVAL-1 정의 추가
# =============================================================
$promptReg = Read-FileText (Join-Path $harness "ai_system\prompts\prompt_registry.md")
Test-Item "prompt_registry has P-EVAL-1" ($promptReg -match "P-EVAL-1")
Test-Item "prompt_registry P-EVAL-1 mentions filtered -> evaluated" `
    ($promptReg -match "P-EVAL-1" -and ($promptReg -match "filtered.*evaluated|evaluated.*filtered"))

# =============================================================
# 10. Planner -> Planning 명명 통일
# =============================================================
$agentIo = Read-FileText (Join-Path $harness "docs\contracts\agent_io_contract.md")
Test-Item "agent_io_contract uses 'Planning' (renamed from Planner)" ($agentIo -match "Planning")

# (선택) Planner 표기 잔존 검사: agent_io_contract 본문에서는 Planner 표기를 제거하거나
# legacy alias로만 남길 것. 강제 fail로는 두지 않고 정보 출력만.
$planerOccurrences = ([regex]::Matches($agentIo, "Planner")).Count
Write-Host "INFO : 'Planner' occurrences in agent_io_contract = $planerOccurrences (legacy alias 허용)" -ForegroundColor Yellow

# planning_agent.md 파일 존재
$planningAgent = Join-Path $harness "ai_system\agents\planning_agent.md"
Test-Item "ai_system/agents/planning_agent.md exists" (Test-Path $planningAgent)

# planner_agent.md 파일 부재 (또는 명시적 redirect)
$plannerAgent = Join-Path $harness "ai_system\agents\planner_agent.md"
Test-Item "ai_system/agents/planner_agent.md absent (or unified into planning_agent.md)" `
    (-not (Test-Path $plannerAgent))

# =============================================================
# 11. PROJECT_STATE migration_progress 갱신
# =============================================================
$projectState = Read-FileText (Join-Path $harness "PROJECT_STATE.md")
Test-Item "PROJECT_STATE current_sprint = S4 or beyond" ($projectState -match "current_sprint:\s*S[45]")
Test-Item "PROJECT_STATE last_completed mentions S4" ($projectState -match "S4.*eval|S4.*knowledge|S4.*ai_system|Sprint S4")

# =============================================================
# 결과
# =============================================================
Write-Host ""
if ($failed -eq 0) {
    Write-Host "PASS Sprint S4 verified — all checks OK" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAIL Sprint S4 verification failed: $failed check(s)" -ForegroundColor Red
    exit 1
}
