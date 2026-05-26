"""Dreammate Studio — FastAPI Backend.

Phase 1 Slice 2: Intent + Planning 분리 + INV-001 ErrorEnvelope.

Layout:
    main.py              — FastAPI app boot
    config.py            — Settings (env-based)
    routers/generate.py  — POST /api/v1/generate (Intent → Planning 직렬)
    schemas/             — Pydantic models (input + output_schema v1.0 + ErrorEnvelope)
    agents/intent.py     — P-001 Intent Agent
    agents/planning.py   — P-006 Planning Agent
    tests/               — pytest

See: backend/fastapi/README.md
"""

__version__ = "0.2.0"  # Phase 1 Slice 2
