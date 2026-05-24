# Phase 1. MVP 기본 플로우 구현

## 1. Goal

모바일 PWA에서 사용자가 영상기획 요청을 입력하고, AI가 의도 분석, 한 줄 방향 승인, RAG Lite, MOA Lite, 품질 평가, 결과 저장을 수행하는 기본 플로우를 구현한다.

## 2. Scope

- Next.js PWA 기본 화면
- FastAPI generate endpoint
- Supabase Auth 최소 연동
- PostgreSQL 기본 테이블
- Output Schema
- Agent IO
- RAG Lite
- MOA Lite
- 결과 저장
- 사용자 피드백 저장

## 3. Non-Goals

- 영상 제작
- 자동 업로드
- 결제
- 팀 기능
- Expo 앱
- Java 백엔드
- Full MOA
- Graph RAG

## 4. Required Inputs

- `product/mvp_scope.md`
- `docs/contracts/output_schema.md`
- `docs/contracts/agent_io_contract.md`
- `docs/contracts/api_contract.md`
- `docs/contracts/db_schema.md`
- `apps/web/design.md`

## 5. Done Definition

- 입력부터 저장까지 end-to-end 동작
- output_schema 일치
- 품질 평가 점수 생성
- RAG reference 존재 또는 fallback
- 사용자 피드백 저장
- MVP 제외 기능 미포함
