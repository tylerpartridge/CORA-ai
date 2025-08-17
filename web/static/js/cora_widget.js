// Single-source CORA chat bootstrapper for all pages
(function(){
  if (window.__coraWidgetBootstrapped) return; 
  window.__coraWidgetBootstrapped = true;

  function ensureCss(){
    if (!document.getElementById('cora-chat-css')){
      const l = document.createElement('link');
      l.id = 'cora-chat-css';
      l.rel = 'stylesheet';
      l.href = '/static/css/cora-chat-consolidated.css';
      document.head.appendChild(l);
    }
  }

  function ensureScriptAndInit(){
    if (window.coraChatEnhanced && typeof window.coraChatEnhanced.openChat === 'function') return;
    if (typeof window.CoraChatEnhanced === 'function'){
      if (!window.coraChatEnhanced){
        try { window.coraChatEnhanced = new CoraChatEnhanced(); } catch(e) { /* no-op */ }
      }
      return;
    }
    // Add script only once
    if (!document.getElementById('cora-chat-js')){
      const s = document.createElement('script');
      s.id = 'cora-chat-js';
      // Cache-bust version updated after UI/drag fixes
      s.src = '/static/js/cora-chat-enhanced.js?v=5.4';
      s.onload = function(){
        try {
          if (!window.coraChatEnhanced && typeof window.CoraChatEnhanced === 'function'){
            window.coraChatEnhanced = new CoraChatEnhanced();
          }
        } catch(e) { /* no-op */ }
      };
      document.body.appendChild(s);
    }
    // Keep loader minimal to avoid any nav jank
  }

  function boot(){
    ensureCss();
    ensureScriptAndInit();
    // Retry after navigation/late loads
    setTimeout(ensureScriptAndInit, 800);
  }

  if (document.readyState === 'loading'){
    document.addEventListener('DOMContentLoaded', boot);
  } else { boot(); }
  document.addEventListener('visibilitychange', function(){ if (!document.hidden) ensureScriptAndInit(); });

  // Safety: re-init after 2s if bubble is missing
  setTimeout(function(){
    if (!document.querySelector('.cora-chat-bubble')){ ensureScriptAndInit(); }
  }, 2000);
})();


