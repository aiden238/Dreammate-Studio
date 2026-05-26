# agent_html_spec.md — Agent HTML Spec v1.1.0

> 위치: `tools/agent_html_spec.md`
> 상태: Phase 0 Sprint S5 신규 작성 (acceptance.md A11 충족)
> 참조: `.claude/skills/INDEX.md`, `migration_procedure.md`, `CLAUDE.md`

---

## 0. 목적

본 문서는 Skill / 라우터 / contract 등 하네스 문서의 **압축된 HTML 표현 표준**을 정의한다.

- **원래 목적**: 모델 호출 시 토큰 절약 (장문 markdown → 압축 HTML)
- **현재 상태 (v1.2.0)**: `.claude/skills/` 단일 폴더 + `applies_to` 태그 결정 이후 **자동 압축 빌드는 불필요**
- **보존 이유**: 향후 Skill 카탈로그 export, 외부 도구 통합, 토큰 한도가 본격 문제 되는 Phase 11+ 대비

---

## 1. v1.2.0 결정과의 관계

v1.1.0 spec은 `.agents/` + `.claude/` 분리 구조를 전제했다.
v1.2.0에서 단일 `.claude/skills/` + `applies_to` 태그로 통합됨에 따라:

- `applies_to: [claude]` Skill → CLAUDE.md 라우터가 자동 해석
- `applies_to: [agents]` Skill → AGENTS.md 라우터가 자동 해석
- `applies_to: [agents, claude]` Skill → 양쪽 모두

→ Skill 자체의 자동 변환은 **현재 불필요**.

다만 본 spec은 다음 목적으로 보존된다:
- **Phase 11+ 토큰 최적화** (Skill 정의 수 30+ 도달 시)
- **외부 도구 통합** (다른 IDE / 다른 model client에서 우리 Skill 활용)
- **Skill 카탈로그 export** (web UI 표시용)

---

## 2. HTML Spec 형식 (정의)

### 2.1 기본 구조

```html
<skill id="phase-start" version="v1.0" applies_to="agents,claude">
  <name>phase-start</name>
  <desc>새 Phase 시작 / 재개 절차</desc>
  <triggers>
    <kw>Phase X 시작</kw>
    <kw>다음 phase</kw>
    <kw>phase 진입</kw>
  </triggers>
  <related_contracts>
    <ref>docs/contracts/db_schema.md</ref>
    <ref>PHASE_REGISTRY.md</ref>
  </related_contracts>
  <body src="SKILL.md" hash="sha256:..."/>
</skill>
```

### 2.2 압축 룰

- markdown bullet → `<li>` 변환
- YAML frontmatter → `<meta>` element
- 코드 블록 → 외부 참조 (`<code-ref src="..."/>`)
- 본문은 별도 파일로 분리, 압축본은 메타데이터만 보유

### 2.3 빌드 트리거 (현재 미운영)

```
조건:
  - .claude/skills/ 변경 감지
  - Phase 11+ 진입
실행:
  - SKILL.md → SKILL.html 변환
  - INDEX.md → INDEX.html 변환
  - sanity check (link 유효성, hash 일치)
출력:
  - dist/skills/*.html
```

---

## 3. 현 시점 사용 가이드

**Phase 0-10 (현재 ~ MVP 출시):**
- 본 spec은 참고 문서로만 유지
- 자동 변환 빌드 미운영
- INDEX.md (markdown) 단일 진실 소스

**Phase 11+ 검토 시점:**
- Skill 수 30+ 도달 또는 외부 통합 요구 시 본 spec 활성화
- 별도 `harness-audit` Skill로 변환 정합성 검사

---

## 4. v1.0 → v1.1.0 → v1.2.0 변경 이력

### v1.0 (S0 이전)
- `.agents/skills/` + `.claude/skills/` 분리 전제
- 자동 변환 빌드 명세

### v1.1.0 (S0)
- `applies_to` 태그 신설 (분리 폴더 보존하면서 메타 표시)

### v1.2.0 (S0 ~ S2)
- **단일 폴더 결정**: `.claude/skills/` 통합 + `applies_to` 태그로 라우팅
- 자동 변환 빌드 → 미운영 처리
- 본 spec은 Phase 11+ 대비로 보존

---

## 5. 관련 Skill / 절차

- `harness-audit`: 본 spec과 실제 Skill 정합성 정기 점검
- `contract-change`: 본 spec 변경 시 절차 적용
- `multi-llm-validation`: spec v2.0 검토 시 권장

---

## 6. Open Questions

1. **자동 빌드 활성화 시점**: Skill 수 정확한 임계값?
2. **HTML vs JSON 표현**: HTML 채택 이유는 가독성 + brower display. JSON이 도구 통합에 더 적합한지 재검토 필요.
3. **본문 hash 검증**: SKILL.md 변경 시 자동 갱신 흐름?
4. **외부 client 통합 사례**: 어떤 도구가 본 spec을 활용할 가능성이 가장 높은지?
5. **archive 처리**: deprecated Skill의 spec 보관 정책

---

## 7. Phase별 작업 계획 (추후 필요 시)

- Phase 11+ 활성화 검토 시:
  - spec v2.0 작성 (현 결정 반영)
  - 자동 빌드 스크립트 (Node.js / Python)
  - CI 통합 (Skill 변경 시 자동 변환)
  - 정합성 검증 sanity 추가

---

## 8. 변경 이력

- v1.0 (Phase -1): GPT 하네스 초안
- v1.1.0 (S0): applies_to 태그 신설
- v1.2.0 (S2): 단일 폴더 결정, 자동 빌드 미운영 처리
- 2026-05-26 (S5): tools/agent_html_spec.md로 신규 위치 확정, acceptance A11 충족
