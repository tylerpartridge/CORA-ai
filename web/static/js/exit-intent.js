(function(){
  if (window.location.pathname.startsWith('/dashboard')) return;
  if (sessionStorage.getItem('exit_intent_shown')) return;
  function show(){
    sessionStorage.setItem('exit_intent_shown','1');
    const modal=document.createElement('div'); modal.className='exit-intent-modal'; modal.innerHTML=`
      <div class="exit-intent-backdrop"></div>
      <div class="exit-intent-content">
        <button class="close-btn">×</button>
        <h2>Wait! Don't Miss Out 🎁</h2>
        <p>Save 30% on your first 3 months</p>
        <form id="ei-form"><input type="email" required placeholder="Enter your email"><button class="btn-claim">Claim</button></form>
      </div>`;
    document.body.appendChild(modal);
    modal.querySelector('.close-btn').onclick=()=>modal.remove();
    modal.querySelector('.exit-intent-backdrop').onclick=()=>modal.remove();
    modal.querySelector('#ei-form').onsubmit=async(e)=>{ e.preventDefault(); const email=e.target.querySelector('input').value; const fd=new FormData(); fd.append('email',email); fd.append('source','exit_intent_30_percent'); await fetch('/api/v1/capture-email',{method:'POST',body:fd}); localStorage.setItem('signupEmail',email); localStorage.setItem('specialOffer','30_PERCENT_3_MONTHS'); window.location.href='/signup'; };
  }
  const s=document.createElement('style'); s.textContent=`.exit-intent-modal{position:fixed;inset:0;z-index:10000;display:block}.exit-intent-backdrop{position:absolute;inset:0;background:rgba(0,0,0,0.6)}.exit-intent-content{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);background:#fff;color:#333;padding:20px;border-radius:8px;min-width:320px}.close-btn{position:absolute;right:8px;top:8px;border:none;background:none;font-size:20px;cursor:pointer}.btn-claim{margin-top:10px}`; document.head.appendChild(s);
  document.addEventListener('mouseout', (e)=>{ if(e.clientY<=0) show(); }, {once:true});
})();


