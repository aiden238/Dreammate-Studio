"""LLM provider 키 검증 -인증/연결만 확인 (models.list, 생성 호출 0 = 비용 ~0).

★ 키를 절대 출력하지 않는다 (앞 6 + 뒤 4 만 마스킹 표시).
★ 키는 .env (user-provided, gitignore) 또는 환경변수에서만 읽는다.
사용:
  1) harness/backend/fastapi/.env 에 키 작성 (OPENAI_API_KEY / ANTHROPIC_API_KEY / GOOGLE_API_KEY)
  2) cd harness && python scripts/verify_llm_keys.py
미설정 provider 는 SKIP, 인증 실패는 FAIL 로 표시 (graceful).
"""
from __future__ import annotations

import os
import sys

# Windows 콘솔(cp949)에서도 깨지지 않도록 stdout 을 utf-8 로 강제.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass


def mask(k: str) -> str:
    if not k:
        return "(none)"
    return f"{k[:6]}...{k[-4:]}" if len(k) > 12 else "(short)"


def _load_dotenv() -> None:
    """단순 .env 파서 (의존성 0). 여러 경로 시도, 이미 설정된 env 는 보존."""
    candidates = [
        os.path.join("backend", "fastapi", ".env"),
        os.path.join("..", "backend", "fastapi", ".env"),
        ".env",
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, val = line.split("=", 1)
                    val = val.strip().strip('"').strip("'")
                    if val:  # .env 값이 있으면 항상 우선 (빈 OS env 덮어쓰기)
                        os.environ[key.strip()] = val
            return path
    return None


def check_openai(key: str) -> None:
    from openai import OpenAI

    OpenAI(api_key=key).models.list()  # 인증 확인 (생성 0)


def check_anthropic(key: str) -> None:
    import anthropic

    anthropic.Anthropic(api_key=key).models.list()


def check_gemini(key: str) -> None:
    from google import genai

    client = genai.Client(api_key=key)  # ★ 클라이언트를 변수로 잡아 수명 유지
    pager = client.models.list()
    for _ in pager:  # 첫 페이지만 소비 (여기서 인증 발생)
        break


PROVIDERS = [
    ("OpenAI", ("OPENAI_API_KEY",), check_openai),
    ("Anthropic", ("ANTHROPIC_API_KEY",), check_anthropic),
    ("Google", ("GOOGLE_API_KEY", "GEMINI_API_KEY"), check_gemini),
]


def main() -> int:
    loaded = _load_dotenv()
    print("=== LLM 키 검증 (인증만, 생성 0) ===")
    print(f".env: {loaded or '(미발견 -환경변수만 사용)'}\n")
    any_fail = False
    for name, env_names, fn in PROVIDERS:
        key = next((os.environ.get(e) for e in env_names if os.environ.get(e)), "")
        if not key:
            print(f"[SKIP] {name:10} {'/'.join(env_names)} 미설정")
            continue
        try:
            fn(key)
            print(f"[ OK ] {name:10} {mask(key)} -인증 성공")
        except Exception as exc:  # noqa: BLE001
            any_fail = True
            print(f"[FAIL] {name:10} {mask(key)} -{type(exc).__name__}: {str(exc)[:140]}")
    print("\n결과:", "일부 FAIL" if any_fail else "검사한 provider 모두 OK (또는 SKIP)")
    return 1 if any_fail else 0


if __name__ == "__main__":
    sys.exit(main())
