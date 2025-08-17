// Bootstrapper that guarantees zoom controls exist on every page
(function(){
  const STORAGE_KEY = 'coraFontSizePx';

  function applyFontSize(px){
    const size = Math.min(Math.max(px, 12), 24);
    document.documentElement.style.fontSize = size + 'px';
    try { localStorage.setItem(STORAGE_KEY, String(size)); } catch(e) {}
  }

  function readInitialSize(){
    try { const v = parseInt(localStorage.getItem(STORAGE_KEY), 10); if (!isNaN(v)) return v; } catch(e) {}
    return 16;
  }

  function createControls(parent){
    const controls = parent && parent.id === 'font-size-controls' ? parent : document.createElement('div');
    if (!controls.id) controls.id = 'font-size-controls';
    controls.setAttribute('role','group');
    controls.setAttribute('aria-label','Font size controls');
    controls.style.cssText = [
      'position:fixed','bottom:80px','left:20px','display:flex','gap:10px','z-index:1000',
      'background:rgba(0,0,0,0.85)','padding:8px','border-radius:25px','box-shadow:0 2px 10px rgba(0,0,0,0.4)'
    ].join(';');

    function makeBtn(label, aria, onClick){
      const b = document.createElement('button');
      b.textContent = label;
      b.setAttribute('aria-label', aria);
      b.style.cssText = [
        'width:40px','height:40px','border-radius:50%','background:#FF9800','color:#1a1a1a !important',
        'border:none','cursor:pointer','font-weight:700','transition:all 0.3s ease',
        "font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif",
        'font-size:16px','letter-spacing:0.5px','display:inline-flex','align-items:center','justify-content:center'
      ].join(';');
      b.addEventListener('click', onClick);
      return b;
    }

    const current = { value: readInitialSize() };
    applyFontSize(current.value);

    const dec = makeBtn('A-','Decrease font size', ()=>{ current.value = Math.max(current.value-2,12); applyFontSize(current.value); });
    const inc = makeBtn('A+','Increase font size', ()=>{ current.value = Math.min(current.value+2,24); applyFontSize(current.value); });
    const rst = makeBtn('A','Reset font size', ()=>{ current.value = 16; applyFontSize(current.value); });

    controls.appendChild(dec); controls.appendChild(inc); controls.appendChild(rst);
    if (!parent || controls === parent) {
      // already appended via provided parent or append to body if newly created
      if (!controls.parentNode) document.body.appendChild(controls);
    } else {
      parent.appendChild(controls);
    }
  }

  function ensureControls(){
    const root = document.getElementById('font-size-controls');
    if (root && root.querySelector('button')) return; // already populated
    // Prefer app bundle if available
    if (window.CORAAccessibility && typeof window.CORAAccessibility.setupFontSizeControls === 'function'){
      try { window.CORAAccessibility.setupFontSizeControls(); } catch(e) {}
      // If still absent or empty, create/populate fallback
      const after = document.getElementById('font-size-controls');
      if (after && after.querySelector('button')) return;
    }
    createControls(root || null);
  }

  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', ensureControls);
  } else { ensureControls(); }
  document.addEventListener('visibilitychange', function(){ if (!document.hidden) ensureControls(); });
})();


