class CookieConsent{
  constructor(){ this.key='cora_cookie_consent'; this.prefs=this.load(); if(!this.prefs){ this.show(); } else { this.apply(); } }
  load(){ try{ const v=localStorage.getItem(this.key); return v?JSON.parse(v):null; }catch(_){ return null; } }
  save(p){ this.prefs=p; try{ localStorage.setItem(this.key, JSON.stringify(p)); }catch(_){ } this.apply(); this.hide(); }
  acceptAll(){ this.save({necessary:true,analytics:true,marketing:true,functional:true,timestamp:Date.now()}); }
  rejectAll(){ this.save({necessary:true,analytics:false,marketing:false,functional:false,timestamp:Date.now()}); }
  customize(){ window.location.href='/cookie-preferences'; }
  apply(){ if(this.prefs&&this.prefs.analytics&&window.gtag){ gtag('consent','update',{'analytics_storage':'granted'}); } }
  show(){ const b=document.createElement('div'); b.id='cookie-consent-banner'; b.innerHTML=`
    <div class="cookie-consent-content">
      <p>We use cookies to improve your experience. By using CORA, you agree to our use of cookies.</p>
      <div class="cookie-consent-buttons">
        <button id="cc-accept" class="btn-accept">Accept All</button>
        <button id="cc-customize" class="btn-customize">Customize</button>
        <button id="cc-reject" class="btn-reject">Reject All</button>
      </div>
    </div>`; document.body.appendChild(b);
    b.querySelector('#cc-accept').onclick=()=>this.acceptAll();
    b.querySelector('#cc-customize').onclick=()=>this.customize();
    b.querySelector('#cc-reject').onclick=()=>this.rejectAll();
  }
  hide(){ const b=document.getElementById('cookie-consent-banner'); if(b) b.remove(); }
}
window.cookieConsent = new CookieConsent();


