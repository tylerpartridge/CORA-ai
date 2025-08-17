// Minimal app tours without external deps; uses simple hints
(function(){
  function showHint(target, text){
    const el = document.querySelector(target);
    if(!el) return;
    const tip=document.createElement('div');
    tip.className='cora-tour-hint';
    tip.textContent=text;
    document.body.appendChild(tip);
    const r=el.getBoundingClientRect();
    tip.style.top=(r.top-40+window.scrollY)+'px';
    tip.style.left=(r.left+window.scrollX)+'px';
    setTimeout(()=>tip.remove(), 5000);
  }
  function firstTimeTour(){
    showHint('.navbar-brand','Welcome to CORA!');
    showHint('#add-expense-btn','Add your first expense here');
    showHint('.dashboard-card','Your financial overview');
  }
  function shouldRun(){
    try{ return !localStorage.getItem('tour_completed_first_time'); }catch(_){ return true; }
  }
  function markDone(){ try{ localStorage.setItem('tour_completed_first_time','1'); }catch(_){ }
  }
  function init(){
    if(window.location.pathname.startsWith('/dashboard') && shouldRun()){
      setTimeout(()=>{ firstTimeTour(); markDone(); }, 1200);
    }
  }
  // basic styles
  const s=document.createElement('style');
  s.textContent='.cora-tour-hint{position:absolute;background:#FF9800;color:#1a1a1a;padding:6px 10px;border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,0.3);font-weight:700;z-index:10000}';
  document.head.appendChild(s);
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
})();


