"""로컬 백엔드 기동 런처 (레포 밖 운용 — 커밋 금지, Temp/).

배경(Gotcha):
  - config.py `env_file=".env"` 는 CWD-상대 로딩 → backend/fastapi 를 CWD 로 둬야 .env(키) 로드.
  - 그러나 `backend.fastapi.main` 패키지 import 는 harness 가 sys.path 에 있어야 함.
  → harness 를 sys.path 에 넣고(절대경로), CWD 를 backend/fastapi 로 chdir.

라이브 검증용으로 RICH_OUTPUT_ENABLED=true (rich 경로). 커밋 default 는 OFF 불변.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HARNESS = os.path.dirname(HERE)  # harness/
sys.path.insert(0, HARNESS)

# rich 라이브 데모 (env var 가 .env 보다 우선 — pydantic-settings 기본 precedence).
os.environ.setdefault("RICH_OUTPUT_ENABLED", "true")

# .env CWD-상대 로딩을 위해 backend/fastapi 로 이동 (sys.path 는 절대 HARNESS 라 import 무관).
os.chdir(os.path.join(HARNESS, "backend", "fastapi"))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    uvicorn.run(
        "backend.fastapi.main:app",
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )
