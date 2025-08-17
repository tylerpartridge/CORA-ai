(function(){
  function addIcon(el, text){
    const i=document.createElement('span'); i.className='help-icon'; i.textContent='ℹ️'; i.title=text;
    el.parentNode.insertBefore(i, el.nextSibling);
  }
  function init(){
    const items=[
      {sel:'#tax-category', text:'Choose the best IRS category for this expense'},
      {sel:'#mileage-input', text:'2024 mileage rate: $0.67/mile'},
      {sel:'#receipt-upload', text:'AI extracts data from your receipt'}
    ];
    items.forEach(it=>{ const el=document.querySelector(it.sel); if(el) addIcon(el, it.text); });
  }
  const s=document.createElement('style'); s.textContent='.help-icon{margin-left:6px;cursor:help}'; document.head.appendChild(s);
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded', init); else init();
})();


