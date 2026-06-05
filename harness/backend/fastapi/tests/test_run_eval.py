"""HIP-007 S2 golden_set eval 정식 트리거 entrypoint — 단위 (hermetic, 실 LLM 0).

검증: run_and_report mock → regression_results 기록 + gate 산출 /
real 요청이라도 키 부재 시 graceful mock fallback (실 caller 미호출).
참조: meta/audits/2026-06-05.md (HIP-007), meta/improvement_roadmap_hip006-010.md (007-S2).
"""

from __future__ import annotations

from pathlib import Path

from backend.fastapi.eval.run_eval import build_real_llm_caller, run_and_report


def test_run_and_report_mock_writes_report(tmp_path) -> None:
    result, path = run_and_report(
        mode="mock", trigger="hip007-s2-test", out_dir=str(tmp_path)
    )
    assert result["mode"] == "mock"
    assert result["summary"]["total"] > 0
    assert "passed" in result["gate"]
    assert Path(path).exists()
    assert "Eval Run" in Path(path).read_text(encoding="utf-8")


def test_run_and_report_real_without_key_falls_back_to_mock(tmp_path, monkeypatch) -> None:
    # 키 없음 → resolve_mode real→mock graceful fallback (실 LLM 호출 0)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    result, path = run_and_report(
        mode="real", trigger="hip007-s2-real-fallback", out_dir=str(tmp_path)
    )
    assert result["mode"] == "mock"  # graceful — 실 caller 미호출
    assert Path(path).exists()


def test_build_real_llm_caller_returns_callable() -> None:
    # caller 빌드는 부작용 0(실 호출은 invoke 시점) — 빌드 자체는 안전
    caller = build_real_llm_caller()
    assert callable(caller)
