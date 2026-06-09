# run_realuse_local.ps1 — 1차 MVP 실사용 프로파일로 백엔드 로컬 기동 (Phase 27 S1 / B-1)
#
# "처음 온 사용자가 도움 없이 director 기획안 1개 생성 → 저장 → brain 축적 → 다음 반영"
# 핵심 루프를 켠 채로 FastAPI 를 띄운다. APP_PROFILE=realuse 단일 스위치 사용.
#
# 사용법:
#   powershell -ExecutionPolicy Bypass -NoProfile -File scripts/run_realuse_local.ps1
#   (옵션) -Port 8000  -OutputMode director|rich|commercial_viral
#
# 전제: backend/fastapi/.env 에 OPENAI_API_KEY (+ 실 영속 원하면 SUPABASE_*) 설정.
#       migration 0001~0008 은 Supabase 적용 필요(영속/PKM). 미설정 시 graceful(휘발).

param(
    [int]$Port = 8000,
    [string]$OutputMode = ""   # 비우면 프로파일 기본(director). 명시 시 override.
)

$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot

Write-Host "=== Dreammate 실사용 프로파일 로컬 기동 (APP_PROFILE=realuse) ===" -ForegroundColor Cyan

# 핵심 루프 ON (단일 스위치).
$env:APP_PROFILE = "realuse"
if ($OutputMode -ne "") {
    $env:OUTPUT_MODE = $OutputMode   # 개별 명시는 프로파일보다 우선(override).
    Write-Host "output_mode override: $OutputMode" -ForegroundColor Yellow
}

# .env 존재 안내 (없어도 graceful 동작하나 키 없으면 생성 실패).
$envFile = Join-Path $repoRoot "backend/fastapi/.env"
if (-not (Test-Path $envFile)) {
    Write-Host "⚠ backend/fastapi/.env 없음 — OPENAI_API_KEY 가 있어야 기획안 생성됨." -ForegroundColor Yellow
} else {
    Write-Host "✓ .env 발견" -ForegroundColor Green
}

Write-Host "프로파일 ON: output_mode=director + PKM 주입·추출 + 브랜딩 시드 + plans_repo" -ForegroundColor Green
Write-Host "기동: http://127.0.0.1:$Port  (Ctrl+C 종료)" -ForegroundColor Cyan

Set-Location $repoRoot
& python -m uvicorn backend.fastapi.main:app --host 127.0.0.1 --port $Port --log-level info
