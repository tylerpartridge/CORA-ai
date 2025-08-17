import{a as d}from"./chunk-YVLJX3HV.js";var m=d((f,c)=>{var l=class{constructor(){this.performanceMetrics={firstContentfulPaint:0,largestContentfulPaint:0,cumulativeLayoutShift:0,firstInputDelay:0,timeToInteractive:0},this.observers=new Map,this.preloadQueue=[],this.criticalResources=new Set,this.init()}init(){this.startPerformanceMonitoring(),this.optimizeCriticalCSS(),this.setupLazyLoading(),this.optimizeImages(),this.setupResourcePreloading(),this.optimizeFonts(),this.setupServiceWorker(),this.setupIntersectionObservers(),this.monitorPerformanceIssues()}startPerformanceMonitoring(){"PerformanceObserver"in window&&(new PerformanceObserver(s=>{s.getEntries().forEach(n=>{this.performanceMetrics.firstContentfulPaint=n.startTime,this.logPerformanceMetric("FCP",n.startTime)})}).observe({entryTypes:["paint"]}),new PerformanceObserver(s=>{let i=s.getEntries(),n=i[i.length-1];this.performanceMetrics.largestContentfulPaint=n.startTime,this.logPerformanceMetric("LCP",n.startTime)}).observe({entryTypes:["largest-contentful-paint"]}),new PerformanceObserver(s=>{let i=0;for(let n of s.getEntries())n.hadRecentInput||(i+=n.value);this.performanceMetrics.cumulativeLayoutShift=i,this.logPerformanceMetric("CLS",i)}).observe({entryTypes:["layout-shift"]}),new PerformanceObserver(s=>{s.getEntries().forEach(n=>{this.performanceMetrics.firstInputDelay=n.processingStart-n.startTime,this.logPerformanceMetric("FID",this.performanceMetrics.firstInputDelay)})}).observe({entryTypes:["first-input"]})),this.measureTimeToInteractive()}optimizeCriticalCSS(){let e=`
            /* Critical rendering styles */
            body { 
                margin: 0; 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                /* Use site theme background; avoid flash-of-white between pages */
                background: #1a1a1a;
                min-height: 100vh;
            }
            
            /* Critical wellness components */
            .wellness-card {
                background: white;
                border-radius: 24px;
                padding: 2rem;
                box-shadow: 0 8px 32px rgba(155, 110, 200, 0.1);
                border: 2px solid transparent;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                position: relative;
                overflow: hidden;
            }
            
            /* Critical navigation */
            nav {
                /* Do not override site nav background to white */
                background: transparent;
                box-shadow: none;
            }
            
            /* Critical form elements */
            input, button {
                font-family: inherit;
            }
            
            /* Critical responsive utilities */
            @media (max-width: 768px) {
                .wellness-card {
                    padding: 1.5rem;
                }
            }
            
            .wellness-btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                padding: 1rem 2rem;
                border: none;
                border-radius: 16px;
                font-size: 1rem;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                background: linear-gradient(135deg, #9B6EC8, #68D89B);
                color: white;
            }
            
            /* Loading skeleton */
            .skeleton {
                background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
                background-size: 200% 100%;
                animation: shimmer 1.5s infinite;
            }
            
            @keyframes shimmer {
                0% { background-position: -200px 0; }
                100% { background-position: calc(200px + 100%) 0; }
            }
        `,t=document.createElement("style");t.textContent=e,document.head.insertBefore(t,document.head.firstChild)}setupLazyLoading(){if("IntersectionObserver"in window){let e=new IntersectionObserver((t,r)=>{t.forEach(o=>{if(o.isIntersecting){let s=o.target;this.loadImage(s),r.unobserve(s)}})},{rootMargin:"50px 0px",threshold:.01});document.querySelectorAll("img[data-src]").forEach(t=>{e.observe(t)})}this.setupComponentLazyLoading()}optimizeImages(){this.supportsWebP()&&this.convertImagesToWebP(),document.querySelectorAll("img").forEach(e=>{this.isAboveTheFold(e)||(e.loading="lazy"),e.decoding="async",e.addEventListener("error",()=>{this.handleImageError(e)})})}setupResourcePreloading(){[{href:"https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap",as:"style"},{href:"/static/images/logos/cora-logo.png",as:"image"}].forEach(t=>{this.preloadResource(t.href,t.as)}),this.prefetchLikelyResources()}optimizeFonts(){// console.log("Font optimization disabled - using standard font loading"),document.querySelectorAll('link[href*="fonts.googleapis.com"]').forEach(e=>{e.setAttribute("media","print"),e.setAttribute("onload","this.media='all'")})}setupServiceWorker(){},6e4)}).catch(()=>{})})})()}setupIntersectionObservers(){let e=new IntersectionObserver(t=>{t.forEach(r=>{r.isIntersecting&&this.optimizeComponent(r.target)})},{threshold:.1});document.querySelectorAll(".wellness-card, .feature-card, .stat-card").forEach(t=>{e.observe(t)})}monitorPerformanceIssues(){new PerformanceObserver(r=>{r.getEntries().forEach(o=>{o.duration>3e3&&this.reportSlowResource(o)})}).observe({entryTypes:["resource"]}),new PerformanceObserver(r=>{r.getEntries().forEach(o=>{o.value>.1&&this.reportLayoutShift(o)})}).observe({entryTypes:["layout-shift"]})}preloadResource(e,t){let r=document.createElement("link");r.rel="preload",r.href=e,r.as=t,document.head.appendChild(r)}loadImage(e){let t=e.dataset.src;t&&(e.src=t,e.removeAttribute("data-src"),e.classList.remove("lazy"))}supportsWebP(){let e=document.createElement("canvas");return e.width=1,e.height=1,e.toDataURL("image/webp").indexOf("data:image/webp")===0}convertImagesToWebP(){// console.log("WebP conversion disabled - using original image formats")}isAboveTheFold(e){return e.getBoundingClientRect().top<window.innerHeight}handleImageError(e){e.src.includes(".webp")?e.src=e.src.replace(".webp",".png"):e.src="/static/images/placeholder.svg"}setupComponentLazyLoading(){let e=document.querySelectorAll("[data-lazy-component]"),t=new IntersectionObserver(r=>{r.forEach(o=>{o.isIntersecting&&(this.loadComponent(o.target),t.unobserve(o.target))})});e.forEach(r=>{t.observe(r)})}loadComponent(e){switch(e.dataset.lazyComponent){case"chart":this.loadChartComponent(e);break;case"table":this.loadTableComponent(e);break;case"form":this.loadFormComponent(e);break}}optimizeComponent(e){let t=()=>{e.style.willChange="transform",e.addEventListener("transitionend",()=>{e.style.willChange="auto"},{once:!0})};e.addEventListener("mouseenter",t),e.addEventListener("focus",t)}prefetchLikelyResources(){(()=>{let e=["/dashboard","/expenses","/reports"],t=["localhost","127.0.0.1"].includes(location.hostname);!t&&window.addEventListener("load",()=>{setTimeout(()=>{e.forEach(r=>{let o=document.createElement("link");o.rel="prefetch",o.href=r,document.head.appendChild(o)})},2e3)})})()}measureTimeToInteractive(){if("PerformanceObserver"in window&&PerformanceObserver.supportedEntryTypes.includes("longtask")){let e=0;new PerformanceObserver(r=>{r.getEntries().forEach(s=>{e=s.startTime+s.duration})}).observe({entryTypes:["longtask"]}),window.addEventListener("load",()=>{setTimeout(()=>{let r=Math.max(e,performance.timing.domInteractive-performance.timing.navigationStart);this.performanceMetrics.timeToInteractive=r,this.logPerformanceMetric("TTI",r)},5e3)})}}logPerformanceMetric(e,t){// console.log(`Performance Metric - ${e}: ${t}ms`),window.gtag&&gtag("event","performance_metric",{metric_name:e,metric_value:t})}reportSlowResource(e){// console.warn("Slow resource detected:",e.name,e.duration),window.Sentry&&Sentry.captureMessage("Slow resource detected",{level:"warning",extra:{name:e.name,duration:e.duration,entryType:e.entryType}})}reportLayoutShift(e){// console.warn("Layout shift detected:",e.value),window.Sentry&&Sentry.captureMessage("Layout shift detected",{level:"warning",extra:{value:e.value,sources:e.sources}})}loadChartComponent(e){// console.log("Chart component requested for:",e),e.innerHTML='<div class="skeleton" style="height: 300px; border-radius: 8px;"></div>'}loadTableComponent(e){window.location.pathname==="/"||!window.location.pathname.includes("/dashboard")||fetch("/api/data/table").then(t=>{if(!t.ok)throw new Error("Failed to load table data");return t.json()}).then(t=>{this.renderTable(e,t)}).catch(t=>{// console.error("Error loading table data:",t),e.innerHTML='<p class="text-gray-500">Unable to load data</p>'})}loadFormComponent(e){e.querySelectorAll("form").forEach(r=>{r.addEventListener("submit",o=>{let s=r.querySelectorAll("input[required]"),i=!0;s.forEach(n=>{n.value.trim()?n.classList.remove("error"):(i=!1,n.classList.add("error"))}),i||o.preventDefault()})})}renderTable(e,t){let r=document.createElement("table");r.className="wellness-table";let o="<thead><tr>";Object.keys(t[0]||{}).forEach(s=>{o+=`<th>${s}</th>`}),o+="</tr></thead><tbody>",t.forEach(s=>{o+="<tr>",Object.values(s).forEach(i=>{o+=`<td>${i}</td>`}),o+="</tr>"}),o+="</tbody>",r.innerHTML=o,e.appendChild(r)}getPerformanceMetrics(){return this.performanceMetrics}optimizePage(){this.optimizeCriticalCSS(),this.setupLazyLoading(),this.optimizeImages(),this.setupResourcePreloading()}preloadPage(e){let t=document.createElement("link");t.rel="prefetch",t.href=e,document.head.appendChild(t)}},a=new l;window.CORAPerformance=a;document.addEventListener("DOMContentLoaded",()=>{a.optimizePage()});window.addEventListener("beforeunload",()=>{typeof a!="undefined"&&a.cleanup&&a.cleanup()});typeof c!="undefined"&&c.exports&&(c.exports=l)});export default m();
//# sourceMappingURL=performance.js.map


