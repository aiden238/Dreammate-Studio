# Contract Change Proposal — Orange × Beige Visual System

> 이 문서는 canonical contract를 직접 수정하지 않고 검토를 요청하기 위한 제안 초안이다.

## 변경 대상

- `apps/web/design_system/tokens.md`
- `docs/contracts/frontend_design_contract.md`
- `apps/web/design.md`의 Visual Style 부분

## 변경 이유

현재 canonical token은 indigo primary와 차가운 neutral을 기준으로 한다.
검토된 디자인 방향은 주황 포인트와 아이보리·베이지 작업 공간이다.

코드만 바꾸고 contract를 유지하면 다음 drift가 생긴다.

- 문서: indigo
- 코드: orange
- reference: orange + beige

따라서 구현 승인 시 canonical token contract도 함께 갱신해야 한다.

## 제안 변경

### Primary

```text
base      #F47B20
light     #FFB23F
hover     #E96818
pressed   #D94C1A
disabled  #E8B58E
```

### Surface

```text
bg default       #F5EFE6
bg subtle        #EEE3D5
surface          #FFFAF4
surface subtle   #F1E3D4
```

### Text

```text
default      #352A24
muted        #78685F
placeholder  #A08E82
inverse      #FFF9F2
```

### Font

```text
display    Paperlogy
ui         SUIT Variable
editorial  Noto Serif KR
```

## 호환성

기존 `primary-50~900`, `neutral-*` 직접 사용 컴포넌트가 있으므로:

- 동일 commit에서 scale mapping을 갱신하거나
- semantic alias로 점진 이행해야 한다.

## 비변경

- API
- output schema
- DB
- 라우트
- AI flow
- accessibility baseline
