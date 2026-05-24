# db_schema.md

## MVP Tables

```sql
users(id uuid primary key, email text, created_at timestamp);

projects(
  id uuid primary key,
  user_id uuid,
  name text,
  description text,
  created_at timestamp,
  updated_at timestamp
);

video_plans(
  id uuid primary key,
  project_id uuid,
  user_id uuid,
  one_line_direction text,
  output_json jsonb,
  overall_score int,
  created_at timestamp,
  updated_at timestamp
);

plan_versions(
  id uuid primary key,
  plan_id uuid,
  version int,
  output_json jsonb,
  created_at timestamp
);

user_feedback(
  id uuid primary key,
  plan_id uuid,
  user_id uuid,
  feedback_type text,
  reason text,
  edited_text text,
  created_at timestamp
);

knowledge_documents(
  id uuid primary key,
  source_type text,
  title text,
  content text,
  metadata jsonb,
  status text,
  created_at timestamp
);

rag_chunks(
  id uuid primary key,
  document_id uuid,
  chunk_text text,
  embedding vector,
  metadata jsonb,
  quality_score int,
  created_at timestamp
);

llm_call_logs(
  id uuid primary key,
  user_id uuid,
  project_id uuid,
  request_id text,
  model text,
  input_tokens int,
  output_tokens int,
  estimated_cost numeric,
  latency_ms int,
  status text,
  error_type text,
  created_at timestamp
);
```
