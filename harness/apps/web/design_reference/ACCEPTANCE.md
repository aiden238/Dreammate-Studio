# Acceptance Checklist

## 기능 보존

- [ ] 홈 입력이 실제 plan 생성으로 연결된다.
- [ ] 이미지 첨부가 유지된다.
- [ ] 4개 상황 버튼이 기존 route로 연결된다.
- [ ] Discovery 질문·선택·직접 입력이 동작한다.
- [ ] Quick Mode가 유지된다.
- [ ] 3개 기획안이 실제 API 데이터로 표시된다.
- [ ] 선택 저장이 동작한다.
- [ ] 좋아요·싫어요·반려 이유 저장이 동작한다.
- [ ] SSE 진행 상태가 유지된다.
- [ ] ErrorCard 재시도가 유지된다.
- [ ] Brain 데이터 조회·편집·삭제가 유지된다.
- [ ] AuthGuard가 유지된다.

## 시각

- [ ] 전체의 약 80%가 아이보리·베이지·웜 뉴트럴이다.
- [ ] 주황은 CTA·선택·진행·로고 중심이다.
- [ ] 화면 전체가 주황색으로 보이지 않는다.
- [ ] Paperlogy는 제목에만 사용된다.
- [ ] SUIT는 UI와 본문에 사용된다.
- [ ] 세리프는 대본·책 본문에 제한된다.
- [ ] 데스크톱에는 rail + sidebar + canvas 계층이 보인다.
- [ ] 모바일에는 하단 내비가 보인다.
- [ ] 집중 플로우에서는 AppShell이 CTA를 덮지 않는다.

## 접근성

- [ ] 44×44px 터치 타겟
- [ ] focus-visible
- [ ] 색상 외 선택 표시
- [ ] aria-current
- [ ] radiogroup/aria-checked
- [ ] form label
- [ ] contrast
- [ ] reduced-motion

## 반응형

- [ ] 360px
- [ ] 390px
- [ ] 768px
- [ ] 1024px
- [ ] 1440px

## 품질

- [ ] 목업 데이터 하드코딩 없음
- [ ] route 변경 없음
- [ ] API schema 변경 없음
- [ ] 새 UI 라이브러리 없음
- [ ] `npm run typecheck`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] 변경 파일과 이유 기록
