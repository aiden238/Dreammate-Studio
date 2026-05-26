"""Dreammate Studio — FastAPI Backend.

Phase 1 Slice 1: POST /api/v1/generate skeleton + JSON 반환.

Layout:
    main.py              — FastAPI app boot
    config.py            — Settings (env-based)
    routers/generate.py  — POST /api/v1/generate
    schemas/             — Pydantic models (input + output_schema v1.0)
    agents/              — LLM call layer (Slice 1: combined intent_planning)
    tests/               — pytest

See: backend/fastapi/README.md
"""

__version__ = "0.1.0"  # Phase 1 Slice 1
