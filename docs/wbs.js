const items=[
{id:'1.1',area:'기획 흐름',task:'문제 정의와 가치 제안 정리',output:'중간발표 문제 정의 슬라이드',status:'done',priority:'High',time:'완료'},
{id:'1.2',area:'기획 흐름',task:'사용자 시나리오 설계',output:'입력-질문-정리-기획안 생성 흐름',status:'done',priority:'High',time:'완료'},
{id:'1.3',area:'기획 흐름',task:'질문 기반 브랜딩 흐름 고정',output:'브랜드 방향 질문 세트',status:'doing',priority:'High',time:'초반'},
{id:'2.1',area:'Frontend',task:'Next.js PWA 주요 화면 구성',output:'입력 화면과 결과 화면',status:'done',priority:'High',time:'완료'},
{id:'2.2',area:'Frontend',task:'AppShell 네비게이션 보강',output:'첫 사용자 진입 경로',status:'doing',priority:'High',time:'초반'},
{id:'2.3',area:'Frontend',task:'결과 화면 가독성 개선',output:'기획안 카드 UI',status:'doing',priority:'High',time:'초반'},
{id:'3.1',area:'Backend',task:'FastAPI 생성 API 구성',output:'generation API',status:'done',priority:'High',time:'완료'},
{id:'3.2',area:'Backend',task:'rate limit 최소 적용',output:'사용자별 요청 제한',status:'done',priority:'Medium',time:'완료'},
{id:'3.3',area:'Backend',task:'예외 상황 처리 정리',output:'오류 메시지와 폴백 정책',status:'todo',priority:'High',time:'중반'},
{id:'4.1',area:'Data',task:'User-Brand-Domain-Series-Video 계층 CRUD',output:'4계층+Video 데이터 구조',status:'done',priority:'High',time:'완료'},
{id:'4.2',area:'Data',task:'plan 영속 저장 검증',output:'plans 테이블 저장 확인',status:'done',priority:'High',time:'완료'},
{id:'4.3',area:'Data',task:'브랜딩 맥락 자동 연결 개선',output:'브랜드/시리즈/비디오 자동 연결',status:'todo',priority:'Medium',time:'중반'},
{id:'5.1',area:'AI Agent',task:'Director Agent 기획안 후보 생성',output:'기획안 후보 3개',status:'done',priority:'High',time:'완료'},
{id:'5.2',area:'AI Agent',task:'LLM 모델 레이어 개선',output:'모델별 역할 분리와 출력 안정화',status:'doing',priority:'High',time:'초반'},
{id:'5.3',area:'AI Agent',task:'MOA 교차 검증 강화',output:'다중 모델 비교 검증',status:'todo',priority:'Medium',time:'중반'},
{id:'6.1',area:'Harness',task:'출력 슬롯 지침 설계',output:'후킹, 유지 구조, 씬 구성 슬롯',status:'done',priority:'High',time:'완료'},
{id:'6.2',area:'Harness',task:'품질 평가 레이어 개선',output:'사람 기준 평가표와 자동 평가 기준',status:'doing',priority:'High',time:'중반'},
{id:'6.3',area:'Harness',task:'scenario_sim, audit, pytest 회귀 검증',output:'테스트와 감사 루프',status:'done',priority:'High',time:'완료'},
{id:'7.1',area:'Demo',task:'중간발표 데모 흐름 고정',output:'30초 데모 시나리오',status:'done',priority:'High',time:'완료'},
{id:'7.2',area:'Demo',task:'데모 영상 백업 제작',output:'라이브 실패 대비 영상',status:'doing',priority:'High',time:'초반'},
{id:'7.3',area:'Demo',task:'최종 발표 실행 가이드 작성',output:'시연 절차 문서',status:'todo',priority:'High',time:'후반'},
{id:'8.1',area:'Expansion',task:'레퍼런스 검색과 추천 고도화',output:'레퍼런스 추천 흐름',status:'todo',priority:'Medium',time:'후반'},
{id:'8.2',area:'Expansion',task:'멀티모달 입력 강화',output:'이미지/영상 맥락 입력',status:'todo',priority:'Medium',time:'중반'},
{id:'8.3',area:'Expansion',task:'PDF/PPT 산출 자동화 검토',output:'산출물 자동 생성 후보',status:'later',priority:'Low',time:'후순위'},
{id:'8.4',area:'Expansion',task:'AI 영상 자동화 워크플로우 설계',output:'대본 기반 영상 자동화 흐름',status:'later',priority:'Low',time:'후순위'}
];
const labels={done:'완료',doing:'진행',todo:'예정',later:'후순위'};
const body=document.getElementById('wbsBody');
function render(filter='all'){
 const rows=items.filter(x=>filter==='all'||x.status===filter);
 body.innerHTML=rows.map(x=>`<tr><td>${x.id}</td><td>${x.area}</td><td><b>${x.task}</b></td><td>${x.output}</td><td><span class="tag ${x.status}">${labels[x.status]}</span></td><td><span class="priority">${x.priority}</span></td><td>${x.time}</td></tr>`).join('');
}
function setCounts(){
 const done=items.filter(x=>x.status==='done').length;
 const doing=items.filter(x=>x.status==='doing').length;
 const todo=items.filter(x=>x.status==='todo').length;
 document.getElementById('doneCount').textContent=done;
 document.getElementById('doingCount').textContent=doing;
 document.getElementById('todoCount').textContent=todo;
 document.getElementById('progressRate').textContent=Math.round(done/items.length*100)+'%';
}
document.querySelectorAll('.filter').forEach(btn=>btn.addEventListener('click',()=>{
 document.querySelectorAll('.filter').forEach(b=>b.classList.remove('active'));
 btn.classList.add('active');
 render(btn.dataset.filter);
}));
setCounts();render();