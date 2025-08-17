var d=class{constructor(){this.defaultTimeout=3e4,this.timeoutConfig={short:5e3,medium:15e3,long:3e4,upload:6e4},this.activeRequests=new Map,this.retryConfig={maxRetries:3,baseDelay:1e3,maxDelay:1e4,backoffMultiplier:2},this.timeoutIndicators=new Map,this.init()}init(){if(window.location.pathname==="/"){// console.log("\u23F1\uFE0F CORA Timeout Handler - Skipped on landing page");return}this.createTimeoutContainer(),this.setupGlobalHandlers(),// console.log("\u23F1\uFE0F CORA Timeout Handler initialized")}createTimeoutContainer(){let t=document.createElement("div");t.id="cora-timeout-container",t.className="cora-timeout-container",t.setAttribute("aria-live","polite");let e=document.createElement("style");e.textContent=`
            .cora-timeout-container {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                z-index: 10001;
                pointer-events: none;
            }
            
            .cora-timeout-indicator {
                background: var(--wellness-bg-card);
                border: 2px solid var(--wellness-border-primary);
                border-radius: var(--wellness-radius-lg);
                padding: var(--wellness-space-lg);
                box-shadow: var(--wellness-shadow-xl);
                pointer-events: auto;
                text-align: center;
                min-width: 300px;
                max-width: 400px;
                transform: scale(0.8);
                opacity: 0;
                transition: all 300ms ease;
            }
            
            .cora-timeout-indicator.show {
                transform: scale(1);
                opacity: 1;
            }
            
            .cora-timeout-indicator.hide {
                transform: scale(0.8);
                opacity: 0;
            }
            
            .cora-timeout-icon {
                font-size: 2rem;
                margin-bottom: var(--wellness-space-md);
                animation: pulse 2s ease-in-out infinite;
            }
            
            .cora-timeout-title {
                font-weight: 600;
                color: var(--wellness-text-primary);
                font-size: var(--wellness-font-size-lg);
                margin-bottom: var(--wellness-space-sm);
            }
            
            .cora-timeout-message {
                color: var(--wellness-text-secondary);
                font-size: var(--wellness-font-size-base);
                line-height: 1.5;
                margin-bottom: var(--wellness-space-lg);
            }
            
            .cora-timeout-progress {
                width: 100%;
                height: 6px;
                background: var(--wellness-bg-tertiary);
                border-radius: var(--wellness-radius-full);
                overflow: hidden;
                margin-bottom: var(--wellness-space-md);
            }
            
            .cora-timeout-progress-bar {
                height: 100%;
                background: linear-gradient(90deg, var(--wellness-primary), var(--wellness-peace));
                border-radius: var(--wellness-radius-full);
                transition: width linear;
                position: relative;
            }
            
            .cora-timeout-progress-bar::after {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(90deg, 
                    transparent 0%, 
                    rgba(255, 255, 255, 0.3) 50%, 
                    transparent 100%);
                animation: shimmer 2s ease-in-out infinite;
            }
            
            .cora-timeout-actions {
                display: flex;
                gap: var(--wellness-space-sm);
                justify-content: center;
            }
            
            .cora-timeout-btn {
                padding: var(--wellness-space-sm) var(--wellness-space-md);
                border: 1px solid var(--wellness-border-primary);
                background: var(--wellness-bg-secondary);
                color: var(--wellness-text-primary);
                border-radius: var(--wellness-radius-md);
                font-size: var(--wellness-font-size-sm);
                cursor: pointer;
                transition: all 200ms ease;
            }
            
            .cora-timeout-btn:hover {
                background: var(--wellness-bg-tertiary);
                border-color: var(--wellness-border-secondary);
            }
            
            .cora-timeout-btn.primary {
                background: var(--wellness-primary);
                color: white;
                border-color: var(--wellness-primary);
            }
            
            .cora-timeout-btn.primary:hover {
                background: var(--wellness-primary-hover);
            }
            
            .cora-timeout-time {
                font-size: var(--wellness-font-size-sm);
                color: var(--wellness-text-muted);
                margin-top: var(--wellness-space-sm);
            }
            
            @keyframes pulse {
                0%, 100% { transform: scale(1); }
                50% { transform: scale(1.1); }
            }
            
            @keyframes shimmer {
                0% { transform: translateX(-100%); }
                100% { transform: translateX(100%); }
            }
            
            @media (max-width: 768px) {
                .cora-timeout-indicator {
                    min-width: 280px;
                    margin: 0 var(--wellness-space-md);
                }
            }
        `,document.head.appendChild(e),document.body.appendChild(t)}setupGlobalHandlers(){this.interceptFetch(),document.addEventListener("visibilitychange",()=>{document.hidden?this.pauseActiveTimeouts():this.resumeActiveTimeouts()})}interceptFetch(){if(window.location.pathname==="/")return;let t=window.fetch;window.fetch=async(...e)=>{let[i,o={}]=e,s=o.timeout||this.defaultTimeout,a=new AbortController,l=setTimeout(()=>{a.abort()},s),c={...o,signal:a.signal},n=this.generateRequestId();this.showTimeoutIndicator(n,s);try{let r=await t(i,c);return clearTimeout(l),this.hideTimeoutIndicator(n),r}catch(r){throw clearTimeout(l),this.hideTimeoutIndicator(n),r.name==="AbortError"&&this.handleTimeout(n,i,s),r}}}showTimeoutIndicator(t,e){let i=document.getElementById("cora-timeout-container");if(!i)return;let o=document.createElement("div");o.className="cora-timeout-indicator",o.id=`timeout-${t}`;let s=document.createElement("div");s.className="cora-timeout-icon",s.innerHTML="\u23F1\uFE0F";let a=document.createElement("div");a.className="cora-timeout-title",a.textContent="Processing Request";let l=document.createElement("div");l.className="cora-timeout-message",l.textContent="Please wait while we process your request...";let c=document.createElement("div");c.className="cora-timeout-progress";let n=document.createElement("div");n.className="cora-timeout-progress-bar",n.style.width="100%",c.appendChild(n);let r=document.createElement("div");r.className="cora-timeout-time",r.textContent=`Timeout: ${e/1e3}s`,o.appendChild(s),o.appendChild(a),o.appendChild(l),o.appendChild(c),o.appendChild(r),i.appendChild(o),setTimeout(()=>{o.classList.add("show")},100),setTimeout(()=>{n.style.width="0%"},100),this.timeoutIndicators.set(t,{element:o,startTime:Date.now(),timeout:e,progressBar:n}),this.updateProgress(t)}updateProgress(t){let e=this.timeoutIndicators.get(t);if(!e)return;let i=Date.now()-e.startTime,o=Math.max(0,100-i/e.timeout*100);e.progressBar&&(e.progressBar.style.width=`${o}%`),o>0&&requestAnimationFrame(()=>this.updateProgress(t))}hideTimeoutIndicator(t){let e=this.timeoutIndicators.get(t);e&&(e.element.classList.add("hide"),setTimeout(()=>{e.element.remove(),this.timeoutIndicators.delete(t)},300))}handleTimeout(t,e,i){let o=this.timeoutIndicators.get(t);if(!o)return;let s=o.element.querySelector(".cora-timeout-title"),a=o.element.querySelector(".cora-timeout-message"),l=o.element.querySelector(".cora-timeout-icon"),c=o.element.querySelector(".cora-timeout-actions");if(s&&(s.textContent="Request Timeout"),a&&(a.textContent="The request took too long to complete. Would you like to retry?"),l&&(l.innerHTML="\u23F0"),!c){let n=document.createElement("div");n.className="cora-timeout-actions";let r=document.createElement("button");r.className="cora-timeout-btn primary",r.textContent="Retry",r.onclick=()=>this.retryRequest(t,e,i);let m=document.createElement("button");m.className="cora-timeout-btn",m.textContent="Cancel",m.onclick=()=>this.hideTimeoutIndicator(t),n.appendChild(r),n.appendChild(m),o.element.appendChild(n)}// console.warn(`[CORA Timeout] Request timed out after ${i}ms:`,e)}retryRequest(t,e,i){this.hideTimeoutIndicator(t),window.errorManager&&window.errorManager.showNotification({type:"info",title:"Retrying Request",message:"Attempting to retry the request...",icon:"\u{1F504}",duration:2e3}),setTimeout(()=>{fetch(e,{timeout:i*1.5})},1e3)}pauseActiveTimeouts(){for(let[t,e]of this.timeoutIndicators)e.paused=!0,e.pauseTime=Date.now()}resumeActiveTimeouts(){for(let[t,e]of this.timeoutIndicators)if(e.paused){let i=Date.now()-e.pauseTime;e.startTime+=i,e.paused=!1,delete e.pauseTime}}fetchWithTimeout(t,e={}){let i=e.timeout||this.defaultTimeout,o=new AbortController,s=setTimeout(()=>{o.abort()},i),a={...e,signal:o.signal};return fetch(t,a).finally(()=>{clearTimeout(s)})}setTimeout(t,e){this.timeoutConfig.hasOwnProperty(t)&&(this.timeoutConfig[t]=e)}getTimeout(t){return this.timeoutConfig[t]||this.defaultTimeout}clearAllTimeouts(){for(let[t,e]of this.timeoutIndicators)this.hideTimeoutIndicator(t)}generateRequestId(){return`req_${Date.now()}_${Math.random().toString(36).substr(2,9)}`}getTimeoutStats(){return{activeTimeouts:this.timeoutIndicators.size,timeoutConfig:this.timeoutConfig,retryConfig:this.retryConfig}}},u;window.location.pathname!=="/"?(u=new d,window.timeoutHandler=u):(u={fetchWithTimeout:fetch,setTimeout:()=>{},getTimeout:()=>3e4,clearAllTimeouts:()=>{},getTimeoutStats:()=>({activeTimeouts:0,timeoutConfig:{},retryConfig:{}})},window.timeoutHandler=u,// console.log("\u23F1\uFE0F CORA Timeout Handler - Disabled on landing page"));window.TimeoutHandler=d;typeof console!="undefined"&&window.location.pathname!=="/"&&(// console.log("\u23F1\uFE0F CORA Timeout Handler initialized"),// console.log("Available commands:"),// console.log("- timeoutHandler.fetchWithTimeout(url, options)"),// console.log("- timeoutHandler.setTimeout(type, duration)"),// console.log("- timeoutHandler.clearAllTimeouts()"),// console.log("- timeoutHandler.getTimeoutStats()"));
//# sourceMappingURL=timeout-handler.js.map
