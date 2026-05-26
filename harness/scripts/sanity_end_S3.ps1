#!/usr/bin/env pwsh
# Sprint S3 종료 sanity check (Windows PowerShell-compatible)
# Usage: pwsh ./scripts/sanity_end_S3.ps1
# Returns: exit 0 on PASS, exit 1 on FAIL
#
# 검증 범위:
#   - Core 9 contract 깊은 작성 (line count + 키워드 cross-ref)
#   - Placeholder 11 표준 형식 (status: placeholder + fill_in_phase 헤더)
#   - dependency_map.yaml 갱신 반영
#   - PROJECT_STATE migration_progress 갱신
#   - 9줄 stub 잔존 0개

$ErrorActionPreference = "Stop"

$harness = Split-Path -Parent $PSScriptRoot
$workspace = Split-Path -Parent $harness

Write-Host "=== Sprint S3 End Check ===" -ForegroundColor Cyan
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

$contractsDir = Join-Path $harness "docs\contracts"

# =============================================================
# 1. Core 9 contract 존재 + 최소 줄 수
# =============================================================
$coreMins = @{
    "output_schema.md"             = 400
    "agent_io_contract.md"         = 350
    "api_contract.md"              = 400
    "error_response_contract.md"   = 250
    "llm_security_contract.md"     = 300
    "rate_limit_policy.md"         = 200
    "rag_data_contract.md"         = 250
    "frontend_design_contract.md"  = 300
    "tech_stack_contract.md"       = 150
}

foreach ($f in $coreMins.Keys) {
    $p = Join-Path $contractsDir $f
    $lines = Get-LineCount $p
    $min = $coreMins[$f]
    Test-Item "core: $f >= $min lines" ($lines -ge $min) "(actual: $lines)"
}

# =============================================================
# 2. Placeholder 11 표준 형식
#    - "PLACEHOLDER" 마커
#    - status: placeholder
#    - fill_in_phase 헤더 (yaml 또는 텍스트)
# =============================================================
$placeholders = @(
    "accessibility_contract.md",
    "data_retention_policy.md",
    "event_log_contract.md",
    "privacy_contract.md",
    "user_consent_contract.md",
    "data_contract.md",
    "env_contract.md",
    "product_boundary.md",
    "backend_boundary.md",
    "frontend_boundary.md",
    "mvp_non_goals.md"
)

foreach ($f in $placeholders) {
    $p = Join-Path $contractsDir $f
    $txt = Read-FileText $p
    $hasMarker = ($txt -match "PLACEHOLDER")
    $hasStatus = ($txt -match "status:\s*placeholder")
    $hasFillIn = ($txt -match "fill_in_phase|Fill-In Trigger|fill_in_trigger")
    $hasScope = ($txt -match "Scope|scope")
    Test-Item "placeholder: $f format (marker+status+fill_in+scope)" `
        ($hasMarker -and $hasStatus -and $hasFillIn -and $hasScope)
}

# =============================================================
# 3. 9줄 stub 0개 (contracts/ 내 모든 .md가 30줄 이상)
# =============================================================
$allContracts = @(Get-ChildItem -Path $contractsDir -Filter "*.md")
foreach ($file in $allContracts) {
    $lc = Get-LineCount $file.FullName
    Test-Item "no 9-line stub: $($file.Name) >= 30 lines" ($lc -ge 30) "(actual: $lc)"
}

# =============================================================
# 4. Cross-reference 키워드 검증
# =============================================================

# output_schema: P-001~P-008, P-AUX-1, P-AUX-2 모두 언급
$outputSchema = Read-FileText (Join-Path $contractsDir "output_schema.md")
$promptIds = @("P-001","P-002","P-003","P-004","P-005","P-006","P-007","P-008","P-AUX-1","P-AUX-2")
foreach ($id in $promptIds) {
    Test-Item "output_schema mentions $id" ($outputSchema -match [regex]::Escape($id))
}

# agent_io_contract: 4 agent 모두 정의
$agentIo = Read-FileText (Join-Path $contractsDir "agent_io_contract.md")
$agents = @("Intent","Planner","Critic","Rewriter")
foreach ($a in $agents) {
    Test-Item "agent_io mentions $a" ($agentIo -match $a)
}

# api_contract: 핵심 endpoint 키워드
$apiContract = Read-FileText (Join-Path $contractsDir "api_contract.md")
$apiKeywords = @("/api","POST","GET","auth","error")
foreach ($k in $apiKeywords) {
    Test-Item "api_contract mentions '$k'" ($apiContract -match [regex]::Escape($k))
}

# error_response_contract: 에러 분류 + 회복 규칙
$errResp = Read-FileText (Join-Path $contractsDir "error_response_contract.md")
Test-Item "error_response has code/category" ($errResp -match "code|category|분류")
Test-Item "error_response has retry/fallback" ($errResp -match "retry|fallback|재시도")

# llm_security_contract: PII + injection + 2-stage automation + P-AUX-1
$llmSec = Read-FileText (Join-Path $contractsDir "llm_security_contract.md")
Test-Item "llm_security mentions PII" ($llmSec -match "PII")
Test-Item "llm_security mentions injection" ($llmSec -match "injection|인젝션")
Test-Item "llm_security mentions P-AUX-1 (intent_filter)" ($llmSec -match "P-AUX-1|intent_filter")
Test-Item "llm_security mentions 2-stage automation" ($llmSec -match "2.?stage|2단계|2.?step|Step 1.*Step 2|자동 검사")

# rate_limit_policy: tier + per-user/brand
$rateLimit = Read-FileText (Join-Path $contractsDir "rate_limit_policy.md")
Test-Item "rate_limit has tier" ($rateLimit -match "tier|등급")
Test-Item "rate_limit has per-user/brand" ($rateLimit -match "user|brand")

# rag_data_contract: candidate_knowledge 5+1 상태
$ragData = Read-FileText (Join-Path $contractsDir "rag_data_contract.md")
$ragStates = @("pending","filtered","evaluated","approved","promoted","rejected")
foreach ($s in $ragStates) {
    Test-Item "rag_data mentions state '$s'" ($ragData -match $s)
}

# frontend_design_contract: design tokens + responsive + a11y
$feDesign = Read-FileText (Join-Path $contractsDir "frontend_design_contract.md")
Test-Item "frontend_design has design tokens" ($feDesign -match "token|토큰")
Test-Item "frontend_design has responsive" ($feDesign -match "responsive|반응형|breakpoint")
Test-Item "frontend_design has a11y" ($feDesign -match "a11y|accessibility|접근성|WCAG")

# tech_stack_contract: Supabase + PostgreSQL 병행, Next.js, FastAPI, Phase 확장성, MVP 후 조정
$techStack = Read-FileText (Join-Path $contractsDir "tech_stack_contract.md")
Test-Item "tech_stack mentions Supabase" ($techStack -match "Supabase")
Test-Item "tech_stack mentions PostgreSQL" ($techStack -match "PostgreSQL|postgres")
Test-Item "tech_stack mentions Next.js" ($techStack -match "Next\.?js")
Test-Item "tech_stack mentions FastAPI" ($techStack -match "FastAPI")
Test-Item "tech_stack mentions Phase expansion / future adjust" ($techStack -match "Phase|확장|조정|adjust|expansion")
Test-Item "tech_stack mentions MVP 후 조정 가능성" ($techStack -match "MVP.*조정|MVP.*변경|post-MVP|MVP 이후|MVP 완성 후")

# =============================================================
# 5. dependency_map.yaml 갱신 확인
# =============================================================
$depMap = Read-FileText (Join-Path $harness "instruction_index\dependency_map.yaml")
Test-Item "dependency_map mentions tech_stack_contract" ($depMap -match "tech_stack_contract")
Test-Item "dependency_map mentions llm_security_contract" ($depMap -match "llm_security_contract")
Test-Item "dependency_map mentions rate_limit_policy" ($depMap -match "rate_limit_policy")

# =============================================================
# 6. PROJECT_STATE migration_progress 갱신
# =============================================================
$projectState = Read-FileText (Join-Path $harness "PROJECT_STATE.md")
Test-Item "PROJECT_STATE current_sprint = S3 or beyond" ($projectState -match "current_sprint:\s*S[345]")
Test-Item "PROJECT_STATE last_completed mentions S3" ($projectState -match "S3.*core|S3.*contract|S3.*완료|Sprint S3")

# =============================================================
# 결과
# =============================================================
Write-Host ""
if ($failed -eq 0) {
    Write-Host "PASS Sprint S3 verified — all checks OK" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAIL Sprint S3 verification failed: $failed check(s)" -ForegroundColor Red
    exit 1
}
