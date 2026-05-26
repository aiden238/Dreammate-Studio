"""Dreammate Studio — FastAPI Backend.

Phase 1 Slice 3: Intent + Planning + Critic 직렬 호출, INV-001 ErrorEnvelope, 8 차원 평가.

Layout:
    main.py              — FastAPI app boot
    config.py            — Settings (env-based)
    routers/generate.py  — POST /api/v1/generate (Intent → Planning → Critic 직렬)
    schemas/             — Pydantic models (input + output_schema v1.0 + ErrorEnvelope
                                            + CriticEvaluation)
    agents/intent.py     — P-001 Intent Agent
    agents/planning.py   — P-006 Planning Agent
    agents/critic.py     — P-007 Critic Agent (Slice 3, revise 없이 평가만)
    tests/               — pytest

See: backend/fastapi/README.md
"""

__version__ = "0.3.0"  # Phase 1 Slice 3
