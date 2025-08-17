var m=class{constructor(){this.errorTypes={NETWORK:"network",TIMEOUT:"timeout",VALIDATION:"validation",AUTHENTICATION:"authentication",AUTHORIZATION:"authorization",SERVER:"server",UNKNOWN:"unknown"},this.errorMessages={[this.errorTypes.NETWORK]:{title:"Connection Issue",message:"Unable to connect to the server. Please check your internet connection and try again.",icon:"\u{1F310}",retry:!0,duration:5e3},[this.errorTypes.TIMEOUT]:{title:"Request Timeout",message:"The request took too long to complete. Please try again.",icon:"\u23F1\uFE0F",retry:!0,duration:4e3},[this.errorTypes.VALIDATION]:{title:"Invalid Input",message:"Please check your input and try again.",icon:"\u26A0\uFE0F",retry:!1,duration:6e3},[this.errorTypes.AUTHENTICATION]:{title:"Authentication Required",message:"Please log in to continue.",icon:"\u{1F510}",retry:!1,duration:0},[this.errorTypes.AUTHORIZATION]:{title:"Access Denied",message:"You don't have permission to perform this action.",icon:"\u{1F6AB}",retry:!1,duration:5e3},[this.errorTypes.SERVER]:{title:"Server Error",message:"Something went wrong on our end. We're working to fix it.",icon:"\u{1F527}",retry:!0,duration:8e3},[this.errorTypes.UNKNOWN]:{title:"Unexpected Error",message:"An unexpected error occurred. Please try again.",icon:"\u2753",retry:!0,duration:5e3}},this.retryConfig={maxRetries:3,baseDelay:1e3,maxDelay:1e4,backoffMultiplier:2},this.activeErrors=new Map,this.retryAttempts=new Map,this.init()}init(){if(window.location.pathname==="/"){// console.log("\u{1F527} CORA Error Manager - Skipped on landing page");return}this.createErrorContainer(),this.setupGlobalHandlers(),this.setupOfflineDetection(),// console.log("\u{1F527} CORA Error Manager initialized")}createErrorContainer(){let e=document.createElement("div");e.id="cora-error-container",e.className="cora-error-container",e.setAttribute("aria-live","polite"),e.setAttribute("aria-atomic","true");let r=document.createElement("style");r.textContent=`
            .cora-error-container {
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 10000;
                max-width: 400px;
                pointer-events: none;
            }
            
            .cora-error-notification {
                background: var(--wellness-bg-card);
                border: 2px solid var(--wellness-border-primary);
                border-left: 4px solid var(--wellness-danger);
                border-radius: var(--wellness-radius-lg);
                padding: var(--wellness-space-md);
                margin-bottom: var(--wellness-space-sm);
                box-shadow: var(--wellness-shadow-lg);
                pointer-events: auto;
                transform: translateX(100%);
                opacity: 0;
                transition: all 300ms ease;
                max-width: 100%;
            }
            
            .cora-error-notification.show {
                transform: translateX(0);
                opacity: 1;
            }
            
            .cora-error-notification.hide {
                transform: translateX(100%);
                opacity: 0;
            }
            
            .cora-error-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: var(--wellness-space-sm);
            }
            
            .cora-error-title {
                font-weight: 600;
                color: var(--wellness-text-primary);
                font-size: var(--wellness-font-size-base);
                display: flex;
                align-items: center;
                gap: var(--wellness-space-sm);
            }
            
            .cora-error-close {
                background: none;
                border: none;
                color: var(--wellness-text-muted);
                cursor: pointer;
                padding: 4px;
                border-radius: var(--wellness-radius-sm);
                transition: all 200ms ease;
                font-size: 18px;
                line-height: 1;
            }
            
            .cora-error-close:hover {
                background: var(--wellness-bg-tertiary);
                color: var(--wellness-text-primary);
            }
            
            .cora-error-message {
                color: var(--wellness-text-secondary);
                font-size: var(--wellness-font-size-sm);
                line-height: 1.5;
                margin-bottom: var(--wellness-space-sm);
            }
            
            .cora-error-actions {
                display: flex;
                gap: var(--wellness-space-sm);
                justify-content: flex-end;
            }
            
            .cora-error-btn {
                padding: var(--wellness-space-xs) var(--wellness-space-sm);
                border: 1px solid var(--wellness-border-primary);
                background: var(--wellness-bg-secondary);
                color: var(--wellness-text-primary);
                border-radius: var(--wellness-radius-sm);
                font-size: var(--wellness-font-size-xs);
                cursor: pointer;
                transition: all 200ms ease;
            }
            
            .cora-error-btn:hover {
                background: var(--wellness-bg-tertiary);
                border-color: var(--wellness-border-secondary);
            }
            
            .cora-error-btn.primary {
                background: var(--wellness-primary);
                color: white;
                border-color: var(--wellness-primary);
            }
            
            .cora-error-btn.primary:hover {
                background: var(--wellness-primary-hover);
            }
            
            .cora-error-progress {
                height: 3px;
                background: var(--wellness-bg-tertiary);
                border-radius: var(--wellness-radius-full);
                overflow: hidden;
                margin-top: var(--wellness-space-sm);
            }
            
            .cora-error-progress-bar {
                height: 100%;
                background: var(--wellness-danger);
                transition: width linear;
            }
            
            @media (max-width: 768px) {
                .cora-error-container {
                    top: 10px;
                    right: 10px;
                    left: 10px;
                    max-width: none;
                }
                
                .cora-error-notification {
                    max-width: none;
                }
            }
        `,document.head.appendChild(r),document.body.appendChild(e)}setupGlobalHandlers(){window.addEventListener("unhandledrejection",e=>{if(e.preventDefault(),window.location.pathname==="/"){// console.log("Skipping error popup for landing page");return}this.handleError(e.reason,this.errorTypes.UNKNOWN)}),window.addEventListener("error",e=>{if(e.preventDefault(),window.location.pathname==="/"){// console.log("Skipping error popup for landing page");return}this.handleError(e.error,this.errorTypes.UNKNOWN)}),this.interceptFetch()}interceptFetch(){if(window.location.pathname==="/")return;let e=window.fetch;window.fetch=async(...r)=>{try{let t=await e(...r);if(!t.ok){let s=this.getErrorTypeFromStatus(t.status),o=new Error(`HTTP ${t.status}: ${t.statusText}`);throw o.status=t.status,o.response=t,this.handleError(o,s),o}return t}catch(t){throw t.name==="TypeError"&&t.message.includes("fetch")?this.handleError(t,this.errorTypes.NETWORK):t.name==="AbortError"?this.handleError(t,this.errorTypes.TIMEOUT):this.handleError(t,this.errorTypes.UNKNOWN),t}}}setupOfflineDetection(){window.addEventListener("online",()=>{this.showNotification({type:"success",title:"Connection Restored",message:"You're back online!",icon:"\u2705",duration:3e3})}),window.addEventListener("offline",()=>{this.handleError(new Error("No internet connection"),this.errorTypes.NETWORK)})}getErrorTypeFromStatus(e){return e>=500?this.errorTypes.SERVER:e===401?this.errorTypes.AUTHENTICATION:e===403?this.errorTypes.AUTHORIZATION:e===408||e===504?this.errorTypes.TIMEOUT:e>=400?this.errorTypes.VALIDATION:this.errorTypes.UNKNOWN}handleError(e,r=null){if(window.location.pathname==="/"){// console.log("Skipping error handling on landing page");return}r||(r=this.determineErrorType(e));let t=this.errorMessages[r]||this.errorMessages[this.errorTypes.UNKNOWN],s=this.generateErrorId();return this.activeErrors.set(s,{error:e,type:r,config:t,timestamp:Date.now()}),this.showErrorNotification(s,t,e),this.logError(e,r),t.retry&&this.scheduleRetry(s,e,r),s}determineErrorType(e){return e.name==="NetworkError"||e.message.includes("network")?this.errorTypes.NETWORK:e.name==="TimeoutError"||e.message.includes("timeout")?this.errorTypes.TIMEOUT:e.name==="ValidationError"||e.message.includes("validation")?this.errorTypes.VALIDATION:e.status===401?this.errorTypes.AUTHENTICATION:e.status===403?this.errorTypes.AUTHORIZATION:e.status>=500?this.errorTypes.SERVER:this.errorTypes.UNKNOWN}showErrorNotification(e,r,t){let s=document.getElementById("cora-error-container");if(!s)return;let o=document.createElement("div");o.className="cora-error-notification",o.id=`error-${e}`,o.setAttribute("role","alert");let c=document.createElement("div");c.className="cora-error-header";let n=document.createElement("div");n.className="cora-error-title",n.innerHTML=`${r.icon} ${r.title}`;let l=document.createElement("button");l.className="cora-error-close",l.innerHTML="\xD7",l.setAttribute("aria-label","Close error notification"),l.onclick=()=>this.dismissError(e),c.appendChild(n),c.appendChild(l);let d=document.createElement("div");if(d.className="cora-error-message",d.textContent=r.message,o.appendChild(c),o.appendChild(d),r.retry){let i=document.createElement("div");i.className="cora-error-actions";let a=document.createElement("button");a.className="cora-error-btn primary",a.textContent="Retry",a.onclick=()=>this.retryError(e),i.appendChild(a),o.appendChild(i)}if(r.duration>0){let i=document.createElement("div");i.className="cora-error-progress";let a=document.createElement("div");a.className="cora-error-progress-bar",a.style.width="100%",i.appendChild(a),o.appendChild(i),setTimeout(()=>{a.style.width="0%"},100),setTimeout(()=>{this.dismissError(e)},r.duration)}s.appendChild(o),setTimeout(()=>{o.classList.add("show")},100)}showNotification({type:e,title:r,message:t,icon:s,duration:o=5e3}){let c=document.getElementById("cora-error-container");if(!c)return;let n=document.createElement("div");n.className="cora-error-notification",n.style.borderLeftColor=e==="success"?"var(--wellness-success)":"var(--wellness-primary)",n.setAttribute("role","status");let l=document.createElement("div");l.className="cora-error-header";let d=document.createElement("div");d.className="cora-error-title",d.innerHTML=`${s} ${r}`;let i=document.createElement("button");i.className="cora-error-close",i.innerHTML="\xD7",i.setAttribute("aria-label","Close notification"),i.onclick=()=>n.remove(),l.appendChild(d),l.appendChild(i);let a=document.createElement("div");a.className="cora-error-message",a.textContent=t,n.appendChild(l),n.appendChild(a),c.appendChild(n),setTimeout(()=>{n.classList.add("show")},100),o>0&&setTimeout(()=>{n.classList.add("hide"),setTimeout(()=>n.remove(),300)},o)}dismissError(e){let r=document.getElementById(`error-${e}`);r&&(r.classList.add("hide"),setTimeout(()=>{r.remove(),this.activeErrors.delete(e)},300))}scheduleRetry(e,r,t){let s=this.retryAttempts.get(e)||0;if(s>=this.retryConfig.maxRetries)return;let o=Math.min(this.retryConfig.baseDelay*Math.pow(this.retryConfig.backoffMultiplier,s),this.retryConfig.maxDelay);setTimeout(()=>{this.retryError(e)},o)}retryError(e){let r=this.activeErrors.get(e);if(!r)return;let t=this.retryAttempts.get(e)||0;this.retryAttempts.set(e,t+1),this.dismissError(e),this.showNotification({type:"info",title:"Retrying...",message:`Attempt ${t+1} of ${this.retryConfig.maxRetries}`,icon:"\u{1F504}",duration:2e3}),setTimeout(()=>{this.handleError(r.error,r.type)},1e3)}generateErrorId(){return`error_${Date.now()}_${Math.random().toString(36).substr(2,9)}`}logError(e,r){// console.error(`[CORA Error] Type: ${r}`,e),window.coraAnalytics&&typeof window.coraAnalytics.track=="function"&&window.coraAnalytics.track("error_occurred",{type:r,message:e.message,stack:e.stack,timestamp:Date.now()})}clearAllErrors(){this.activeErrors.clear(),this.retryAttempts.clear();let e=document.getElementById("cora-error-container");e&&(e.innerHTML="")}getErrorStats(){let e={totalErrors:this.activeErrors.size,errorTypes:{},retryAttempts:this.retryAttempts.size};for(let[r,t]of this.activeErrors){let s=t.type;e.errorTypes[s]=(e.errorTypes[s]||0)+1}return e}},p;window.location.pathname!=="/"?(p=new m,window.errorManager=p):(p={handleError:()=>{},showNotification:()=>{},clearAllErrors:()=>{},getErrorStats:()=>({totalErrors:0,errorTypes:{},retryAttempts:0})},window.errorManager=p,// console.log("\u{1F527} CORA Error Manager - Disabled on landing page"));window.ErrorManager=m;typeof console!="undefined"&&window.location.pathname!=="/"&&(// console.log("\u{1F527} CORA Error Manager initialized"),// console.log("Available commands:"),// console.log("- errorManager.handleError(error, type)"),// console.log("- errorManager.showNotification(config)"),// console.log("- errorManager.clearAllErrors()"),// console.log("- errorManager.getErrorStats()"));
//# sourceMappingURL=error-manager.js.map
