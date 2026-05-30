#requires -Version 5.1
# eval_run.ps1 — eval-run Skill 래퍼 (mock-deterministic golden_set 회귀)
#
# 목적: backend/fastapi/eval/runner.run_golden_set_eval 를 실행하여
#       golden_set 11 케이스(GS-001~011) mock 회귀 채점 + 임계값 게이트 → regression_results 출력.
#       Phase 9.5 Slice 2 (ADR-033) — eval-run Skill 첫 정식 실행.
#
# 사용:
#   pwsh -File scripts/eval_run.ps1                       # trigger=phase-9.5_baseline
#   pwsh -File scripts/eval_run.ps1 -Trigger my-run       # 커스텀 trigger 명
#
# 출력:
#   eval/regression_results/{trigger}.md (eval-run §5 형식)
#
# 종료 코드:
#   0: 게이트 통과 (verdict=pass)
#   1: 게이트 위반 (verdict=fail — 임계값 차단)

param(
    [string]$Trigger = 'phase-9.5_baseline'
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$ROOT = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
Set-Location $ROOT

Write-Host "[eval-run] mode=mock trigger=$Trigger (golden_set 11 케이스 회귀)"

$py = @"
import json
from backend.fastapi.eval import run_golden_set_eval, write_report

result = run_golden_set_eval(mode='mock')
path = write_report(result, trigger='$Trigger')
summary = result['summary']
gate = result['gate']
print('REPORT::' + path)
print('SCHEMA_RATE::' + str(summary['schema_rate']))
print('PASS_RATE::' + str(summary['pass_rate']))
print('GATE_PASSED::' + str(gate['passed']))
for v in gate['violations']:
    print('VIOLATION::' + v)
"@

$out = $py | python -
$out | ForEach-Object { Write-Host $_ }

$gateLine = $out | Where-Object { $_ -like 'GATE_PASSED::*' }
if ($gateLine -like '*True*') {
    Write-Host "[eval-run] verdict=pass (canonical-only 품질 baseline 확정)"
    exit 0
} else {
    Write-Host "[eval-run] verdict=fail (임계값 위반 — 차단)"
    exit 1
}
