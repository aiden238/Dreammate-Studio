# Phase 1 — Smoke Test Instructions (Manual)

> Type: end-to-end manual verification guide
> 작성일: 2026-05-26
> 대상 사용자: 본 프로젝트 owner (songbyeongcheol)
> 전제: Phase 1 Slice 1~7 모두 완료 + git push 완료 후 실행
> 소요 시간: 약 15~20분

---

## 0. 사전 준비

```
□ git pull origin main 으로 최신 commit 확보 (backend Slice 5 + frontend Slice 7)
□ Python 3.11+ 설치 확인 (`python --version`)
□ Node.js 20+ 설치 확인 (`node --version`)
□ Supabase 프로젝트 1개 준비 (선택 — 미설정 시 7번 단계 skip, project_id 가 null 로 표시되는지 확인)
□ OpenAI API key 또는 동등한 LLM 제공자 key 준비
```

---

## 1. 백엔드 기동

```bash
cd "C:/Users/songb/OneDrive/바탕 화면/Dreammate_Studio/harness"

# 가상환경 (최초 1회만)
python -m venv .venv
.venv\Scripts\activate           # Windows PowerShell

# 의존성 설치 (최초 1회만)
pip install -r backend/fastapi/requirements.txt

# 환경 변수 설정 (최초 1회만)
cp backend/fastapi/.env.example backend/fastapi/.env
# 편집기로 backend/fastapi/.env 열어서:
#   OPENAI_API_KEY=sk-...
#   SUPABASE_URL=https://...   (선택; 미설정 시 graceful fallback)
#   SUPABASE_ANON_KEY=...      (선택)

# 서버 기동
cd backend/fastapi
uvicorn main:app --reload --port 8000
```

✅ **체크**: 브라우저에서 http://localhost:8000/docs 열어 FastAPI swagger UI 표시 확인.

---

## 2. 프론트엔드 기동 (별도 터미널)

```bash
cd "C:/Users/songb/OneDrive/바탕 화면/Dreammate_Studio/harness/apps/web"

# 의존성 설치 (최초 1회만)
npm install

# 환경 변수 (최초 1회만)
cp .env.local.example .env.local
# 기본값 NEXT_PUBLIC_API_URL=http://localhost:8000 그대로 유지

# 개발 서버
npm run dev
```

✅ **체크**: `▲ Next.js 14.2.5 - Local: http://localhost:3000` 메시지 확인.

---

## 3. 입력 페이지 접근

브라우저에서 http://localhost:3000 접속.

✅ **체크**:
- `Dreammate Studio` 헤더 + `영상기획 AI 에이전트` 타이틀 표시
- 텍스트 영역 (5줄) + `기획안 만들기` 버튼 노출
- 모바일 시뮬레이션 (Chrome DevTools → Device Toolbar → iPhone SE 375px) 시 가로 스크롤 없음
- 푸터 `Phase 1 MVP — 단일 기획안 1개를 보여드려요.` 텍스트 확인

---

## 4. 정상 입력 → 기획안 생성

텍스트 영역에 다음 문장 입력:

```
유튜브 채널 첫 영상 기획해줘
```

`기획안 만들기` 버튼 클릭.

✅ **체크 (제출 직후)**:
- 버튼이 `생성 중...` 으로 바뀌고 비활성화
- **4단계 ProgressStepper** 노출 (Intent → 자료 검색 → 기획안 생성 → 품질 평가)
- 현재 활성 단계 (기획안 생성) 가 indigo 색 + 펄스 애니메이션
- 캡션 텍스트 `기획안을 만드는 중` 표시

✅ **체크 (응답 도착 후, 약 30~60초)**:
- `/plan` 페이지로 자동 이동
- 헤더 `AI가 정리한 영상 기획안` 표시
- `request_id` UUID 노출
- `저장됨` (Supabase 연결 시) 또는 `임시 결과 (저장 안 됨)` (DB 미연결 시) 배지

---

## 5. 결과 페이지 콘텐츠 검증

`/plan` 페이지에서 다음 요소 확인:

✅ **품질 평가 섹션 (Critic — Slice 3)**:
- `품질 점수 X.X / 5` 노출 (예: `품질 점수 4.2 / 5`)
- verdict 배지: `승인` (초록) / `보완 필요` (노랑) / `재시도 권장` (빨강) 중 하나
- `blocking_issues` 가 있다면 빨강 list 노출

✅ **참고 자료 섹션 (RAG — Slice 4)**:
- `참고 자료 N개를 활용했어요` (N ≥ 0) 또는 `참고 자료 없이 생성했어요`

✅ **PlanCard 본문**:
- 제목 + approach 배지 (`서사형` / `정보 전달형` / `공감형` / `실험형` / `리뷰형` / `기타` 중 1)
- approach 별 배경색이 다름 (info / neutral / primary / warning / success / neutral)
- `concept` 설명 텍스트
- `후킹` 강조 박스 (왼쪽 indigo 세로 선)
- `영상 흐름` 우측에 `총 X분 Y초 · N개 비트` 라벨
- numbered list (2~8개 비트), 각 비트에 `XX초` 라벨
- `장점` / `리스크` 2 컬럼 (sm 이상에서 좌우, 모바일에서 위아래)

✅ **푸터**:
- `다시 만들기` 버튼 클릭 시 입력 페이지로 복귀 + sessionStorage 비워짐

---

## 6. (선택) Supabase 저장 확인

`.env` 에 `SUPABASE_URL` + `SUPABASE_ANON_KEY` 가 설정된 경우만.

Supabase 대시보드 → `Table editor` 접근:

✅ **체크**:
- `video_projects` 테이블에 새 row 1개 추가 (created_at = 방금 시각)
- `plan_candidates` 테이블에 새 row 1개 추가 (video_project_id = 위 row id)
- 응답 페이지의 `request_id` 가 row 의 `request_id` (또는 동등 컬럼) 와 일치
- 응답 페이지에 `저장됨` 배지가 표시되었는지 확인

설정 안 했거나 DB 연결 실패한 경우:
- 응답 페이지에 `임시 결과 (저장 안 됨)` 회색 배지
- 백엔드 로그에 graceful fallback 메시지 확인 (저장 실패가 사용자 차단으로 이어지지 않음)

---

## 7. Intent Filter (INV-001) 차단 동작

입력 페이지로 돌아가서 (`/` 또는 `다시 만들기` 버튼) 다음 문장 입력:

```
오늘 날씨 어때?
```

`기획안 만들기` 버튼 클릭.

✅ **체크 (응답 도착 후, 약 5~10초)**:
- `/plan` 으로 이동하지 **않고** 입력 페이지 상단에 **ErrorCard** 노출
- 큰 빨강 헤더: `영상기획과 거리가 있는 요청 같아요`
- 본문: 영상 아이디어를 다른 방식으로 적어달라는 안내 메시지
- 작은 회색 글자: `code: INV-001 · request_id: ...`
- `처음으로` 버튼만 노출 (다시 시도 버튼 없음 — retry_allowed=false)
- 입력 텍스트는 그대로 유지 (사용자가 수정 후 재시도 가능)

추가 케이스 (선택):
- 빈 입력 후 제출 → 노란 inline warning `어떤 영상을 기획하실지 한 줄이라도 적어주세요.`
- (백엔드 셧다운 후 제출) → `서버에 연결하지 못했어요` ErrorCard (`code: NET-000`, `다시 시도` 버튼 노출)

---

## 8. PWA Manifest 유효성 검사

Chrome DevTools 열기 (F12) → `Application` 탭 → `Manifest` 사이드바.

✅ **체크**:
- `Identity` 섹션: name `Dreammate Studio — 영상기획 AI 에이전트`, short_name `Dreammate`
- `Presentation` 섹션: start_url `/`, scope `/`, display `standalone`, orientation `portrait`,
   background_color `#FAFAFA`, theme_color `#6366F1`
- `Icons` 섹션: 3개 아이콘 (`icon-192.svg`, `icon-512.svg`, `maskable-512.svg`)
- 에러 / 경고 0건 (좌측 사이드바에서 빨간 점 없음)

선택:
- Chrome 주소창 우측 `Install Dreammate` 아이콘 노출 시 클릭 → 앱이 별도 창으로 설치
- 설치 후 OS 앱 목록에서 `Dreammate` 아이콘 확인 (윈도우: 시작 메뉴, 맥: Launchpad)

---

## 9. 종료

```
□ 정상 입력 1회 통과 (단계 4~5)
□ INV-001 차단 1회 통과 (단계 7)
□ PWA manifest 유효 (단계 8)
□ (선택) Supabase row 생성 확인 (단계 6)
□ frontend / backend 터미널 Ctrl+C 종료
```

위 4 + 1 항목 모두 통과 시 **Phase 1 MVP 완전 동작 확인**.

---

## 10. 문제 발생 시

### 백엔드 500 / 502

- 백엔드 터미널 로그 확인 (`uvicorn` 출력)
- `.env` 의 `OPENAI_API_KEY` 유효성 확인
- `pip install` 누락 라이브러리 확인

### 프론트 빌드 실패

```bash
cd harness/apps/web
rm -rf .next node_modules
npm install
npm run build
```

### ErrorCard 가 영문 메시지를 표시한다

- backend 가 user_message 를 한국어로 제공하지 않는 경우 발생 가능
- `lib/errors.ts` 의 RULES fallbackBody 가 사용되므로 빈 한국어 메시지는 나오지 않아야 함
- 만약 영문이 나온다면 backend 응답을 점검 (error_response_contract.md §11.2 위반)

### CORS 오류

- 백엔드 `main.py` 의 CORSMiddleware origins 에 `http://localhost:3000` 포함 확인
- 미포함 시 backend Slice 1 점검 필요

---

## 11. 보고 양식 (사용자가 작성할 위치)

본 smoke test 실행 결과는 `eval/qa_reports/phase-1-final_2026-05-26.md` 또는 동등한 Phase 1 종료 리포트에
사용자가 직접 기록 (또는 다음 sub-agent 가 본 가이드 결과를 입력받아 작성).

기록 항목:
- 8단계 통과 / 부분 통과 / 실패
- 발견된 이슈 (있을 경우)
- 권장 후속 조치 (Phase 2 진입 전 보강 항목)

---

## 12. 변경 이력

- 2026-05-26: Phase 1 Slice 7 완료 직후 작성. backend Slice 5 + frontend Slice 7 통합 검증 가이드.
