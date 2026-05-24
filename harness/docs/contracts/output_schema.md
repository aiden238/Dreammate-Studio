# output_schema.md

## 최종 출력 JSON

```json
{
  "plan_id": "string",
  "project_id": "string",
  "one_line_direction": "string",
  "target_analysis": {
    "primary_target": "string",
    "target_need": "string",
    "expected_reaction": "string"
  },
  "format": "shortform | promo | branding | explainer | other",
  "tone": "professional | friendly | emotional | energetic | informative | other",
  "hook_candidates": [
    {
      "id": "string",
      "hook": "string",
      "rationale": "string",
      "risk": "string"
    }
  ],
  "video_structure": [
    {
      "section": "intro | body | transition | ending",
      "time_range": "string",
      "content": "string",
      "visual_note": "string"
    }
  ],
  "shooting_notes": [
    {
      "type": "camera | location | prop | acting | editing",
      "note": "string"
    }
  ],
  "quality_review": {
    "intent_fit": 0,
    "target_clarity": 0,
    "hook_strength": 0,
    "message_clarity": 0,
    "structure_quality": 0,
    "execution_feasibility": 0,
    "brand_consistency": 0,
    "differentiation": 0,
    "overall_score": 0,
    "review_summary": "string"
  },
  "revision_suggestions": [
    {
      "issue": "string",
      "suggestion": "string",
      "priority": "high | medium | low"
    }
  ],
  "rag_references": [
    {
      "source_id": "string",
      "title": "string",
      "used_reason": "string"
    }
  ]
}
```

## 규칙

- 점수는 0~100 범위.
- hook_candidates는 MVP 기준 3개.
- video_structure는 최소 3개 section.
- rag_references는 검색 실패 시 빈 배열.
