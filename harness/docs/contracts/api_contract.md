# api_contract.md

## POST /api/video-plans/intent

사용자 입력을 분석한다.

Request:

```json
{
  "project_id": "string",
  "user_input": "string"
}
```

Response:

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

## POST /api/video-plans/generate

승인된 방향을 기반으로 기획안을 생성한다.

Request:

```json
{
  "project_id": "string",
  "approved_direction": "string",
  "answers": {},
  "options": {
    "use_rag": true,
    "use_critic": true
  }
}
```

Response:

`docs/contracts/output_schema.md`를 따른다.

## POST /api/video-plans/{plan_id}/feedback

사용자 피드백을 저장한다.
