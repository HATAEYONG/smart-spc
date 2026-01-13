import React from 'react';

function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>SPC 품질관리 시스템 테스트</h1>
      <p>화면이 보이면 React가 정상 작동하는 것입니다.</p>
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0' }}>
        <h2>페이지 목록</h2>
        <ul>
          <li><a href="/">대시보드</a></li>
          <li><a href="/capability">공정능력 분석</a></li>
          <li><a href="/data-entry">데이터 입력</a></li>
          <li><a href="/run-rules">Run Rule 분석</a></li>
          <li><a href="/chatbot">AI 챗봇</a></li>
          <li><a href="/reports">보고서</a></li>
          <li><a href="/advanced-charts">고급 관리도</a></li>
        </ul>
      </div>
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#e0f0ff' }}>
        <h3>API 테스트</h3>
        <p>Backend 상태: <button onClick={() => fetch('/api/spc/products/').then(r => r.json()).then(d => alert(JSON.stringify(d)))}>제품 조회</button></p>
      </div>
    </div>
  );
}

export default App;
