class FeatureFlagsClient{
  constructor(){ this.flags={}; }
  async load(){
    try{
      const token = (typeof localStorage!=='undefined' && localStorage.getItem('authToken')) || '';
      const headers = token ? { 'Authorization': `Bearer ${token}` } : {};
      const r = await fetch('/api/feature-flags', { headers });
      if(r.status === 401){
        this.flags = {};
        this.apply();
        return;
      }
      this.flags = await r.json();
      this.apply();
    }catch(e){ /* noop */ }
  }
  isEnabled(name){ return !!this.flags[name]; }
  apply(){ document.querySelectorAll('[data-feature-flag]').forEach(el=>{ const f=el.dataset.featureFlag; el.style.display=this.isEnabled(f)?'':'none'; }); }
}
window.featureFlagsClient = new FeatureFlagsClient();
document.addEventListener('DOMContentLoaded', ()=> window.featureFlagsClient.load());


