"""Dreammate Studio — FastAPI Backend.

Phase 1 Slice 5: Intent + RAG (graceful fallback) + Planning(rag_context) + Critic + DB save (graceful).
INV-001 ErrorEnvelope, 8 차원 평가, body.rag_references, meta.project_id 활성화.

Layout:
    main.py              — FastAPI app boot
    config.py            — Settings (env-based, pgvector + Supabase 추가)
    routers/generate.py  — POST /api/v1/generate
                              (Intent → RAG → Planning(rag_context) → Critic → DB save)
    schemas/             — Pydantic models (input + output_schema v1.0 + ErrorEnvelope
                                            + CriticEvaluation + body.rag_references
                                            + meta.project_id)
    agents/intent.py     — P-001 Intent Agent
    agents/planning.py   — P-006 Planning Agent (rag_context 주입 지원)
    agents/critic.py     — P-007 Critic Agent (Slice 3, revise 없이 평가만)
    rag/                  — Slice 4
        types.py          — RAGReference / RetrievalResult
        retriever.py      — pgvector 검색 + graceful fallback
        fallback.py       — 빈 references + 사유 반환
    db/                   — Slice 5
        supabase_client.py     — get_supabase_client() (None if env missing)
        repositories/          — insert_video_project, insert_plan_candidate
        types.py               — PersistenceResult / SaveStatus
        migrations/001_init.sql — video_projects + plan_candidates DDL
    tests/                — pytest

See: backend/fastapi/README.md
"""

__version__ = "0.5.0"  # Phase 1 Slice 5
