# agent_io_contract.md

## Intent Agent

Input:

```json
{
  "user_input": "string",
  "project_context": {},
  "user_memory": {}
}
```

Output:

```json
{
  "goal": "string",
  "target": "string",
  "format": "string",
  "tone": "string",
  "missing_questions": ["string"],
  "one_line_direction_draft": "string",
  "confidence": 0
}
```

## Planner Agent

Input:

```json
{
  "approved_direction": "string",
  "intent": {},
  "rag_context": [],
  "project_context": {}
}
```

Output:

`output_schema.md`의 초안 구조를 따른다.

## Critic Agent

Output:

```json
{
  "scores": {
    "intent_fit": 0,
    "target_clarity": 0,
    "hook_strength": 0,
    "message_clarity": 0,
    "structure_quality": 0,
    "execution_feasibility": 0,
    "brand_consistency": 0,
    "differentiation": 0
  },
  "weaknesses": ["string"],
  "revision_suggestions": []
}
```

## Rewriter Agent

Critic Agent의 개선 제안을 반영하여 `output_schema.md` 구조로 수정한다.
