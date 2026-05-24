#!/usr/bin/env pwsh
# Sprint S2 종료 sanity check (Windows PowerShell-compatible)
# Usage: pwsh ./scripts/sanity_end_S2.ps1
# Returns: exit 0 on PASS, exit 1 on FAIL

$ErrorActionPreference = "Stop"

$harness = Split-Path -Parent $PSScriptRoot
$workspace = Split-Path -Parent $harness

Write-Host "=== Sprint S2 End Check ===" -ForegroundColor Cyan
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

$skillsDir = Join-Path $harness ".claude\skills"
$agentsDir = Join-Path $harness ".agents"

# 1. .agents 폴더가 존재하지 않아야 한다
Test-Item ".agents/ folder removed" (-not (Test-Path $agentsDir))

# 2. .claude/skills 가 존재
Test-Item ".claude/skills/ exists" (Test-Path $skillsDir)

# 3. .claude/skills 에 정확히 20개 디렉터리
$skillDirs = @(Get-ChildItem -Path $skillsDir -Directory)
Test-Item ".claude/skills/ has exactly 20 subdirs" ($skillDirs.Count -eq 20) "(actual: $($skillDirs.Count))"

# 4. 예상되는 20개 skill 이름 매핑
$expected = @(
    # 우리 14
    "phase-start","phase-complete","contract-change","bug-triage","rag-update",
    "eval-run","qa-check","cost-review","meta-retrospective","design-review",
    "security-review","prompt-version-review","multi-llm-validation","context-compact",
    # GPT origin 6 (재작성)
    "agent-io-check","ai-architecture-review","eval-design","harness-audit",
    "phase-review","rag-design"
)

foreach ($name in $expected) {
    $p = Join-Path $skillsDir "$name\SKILL.md"
    Test-Item "skill present: $name" (Test-Path $p)
}

# 5. 각 SKILL.md frontmatter 검증 (name, description, applies_to, version 존재)
foreach ($name in $expected) {
    $p = Join-Path $skillsDir "$name\SKILL.md"
    if (-not (Test-Path $p)) { continue }
    $content = [System.IO.File]::ReadAllText($p)
    $hasName = ($content -match "(?m)^name:\s*$name\s*$")
    $hasDesc = ($content -match "(?m)^description:\s*\|")
    $hasApplies = ($content -match "(?m)^applies_to:\s*\[")
    $hasVersion = ($content -match "(?m)^version:\s*v\d")
    Test-Item "$name frontmatter: name/desc/applies_to/version" ($hasName -and $hasDesc -and $hasApplies -and $hasVersion)
}

# 6. 폐기 Skill 디렉터리가 존재하지 않아야 함
$discarded = @("docs-design","frontend-design-review","product-scope-review","planning-phase-create")
foreach ($d in $discarded) {
    $p = Join-Path $skillsDir $d
    Test-Item "discarded skill removed: $d" (-not (Test-Path $p))
}

# 7. INDEX.md 존재 + 20 skills 언급
$indexPath = Join-Path $skillsDir "INDEX.md"
Test-Item "INDEX.md exists" (Test-Path $indexPath)
if (Test-Path $indexPath) {
    $indexContent = [System.IO.File]::ReadAllText($indexPath)
    Test-Item "INDEX.md mentions 20" ($indexContent -match "20\s*Skill|20\s*개")
    Test-Item "INDEX.md mentions .claude/skills" ($indexContent -match "\.claude/skills")
}

# 8. 각 GPT origin 재작성 Skill의 line count (130–200)
$rewritten = @("agent-io-check","ai-architecture-review","eval-design","harness-audit","phase-review","rag-design")
foreach ($name in $rewritten) {
    $p = Join-Path $skillsDir "$name\SKILL.md"
    $lines = Get-LineCount $p
    Test-Item "$name line count in [130, 200]" ($lines -ge 130 -and $lines -le 200) "(actual: $lines)"
}

# 9. description 키워드 충돌 휴리스틱
# 각 SKILL.md frontmatter description 영역의 인용부호로 묶인 키워드를 모아 중복 검사
$keywordToSkill = @{}
foreach ($name in $expected) {
    $p = Join-Path $skillsDir "$name\SKILL.md"
    if (-not (Test-Path $p)) { continue }
    $text = [System.IO.File]::ReadAllText($p)
    # frontmatter 추출 (--- 사이)
    if ($text -match "(?s)^---\s*\n(.*?)\n---") {
        $fm = $Matches[1]
        # description 블록 추출 (description: | 부터 다음 top-level 키까지)
        if ($fm -match "(?s)description:\s*\|\s*\n(.*?)(?=\n\S+:)") {
            $descBlock = $Matches[1]
            # "..." 패턴 추출
            $kws = [regex]::Matches($descBlock, '"([^"]+)"') | ForEach-Object { $_.Groups[1].Value }
            foreach ($kw in $kws) {
                if (-not $keywordToSkill.ContainsKey($kw)) { $keywordToSkill[$kw] = @() }
                $keywordToSkill[$kw] += $name
            }
        }
    }
}
$dupKeywords = $keywordToSkill.GetEnumerator() | Where-Object { $_.Value.Count -gt 1 }
if ($dupKeywords) {
    foreach ($d in $dupKeywords) {
        Test-Item "no duplicate keyword: '$($d.Key)'" $false "(in: $($d.Value -join ', '))"
    }
} else {
    Test-Item "no duplicate description keywords across skills" $true
}

# 결과
Write-Host ""
if ($failed -eq 0) {
    Write-Host "PASS Sprint S2 verified — all checks OK" -ForegroundColor Green
    exit 0
} else {
    Write-Host "FAIL Sprint S2 verification failed: $failed check(s)" -ForegroundColor Red
    exit 1
}
