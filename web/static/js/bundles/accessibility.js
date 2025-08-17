import{a as l}from"./chunk-YVLJX3HV.js";var d=l((h,s)=>{var r=class{constructor(){this.currentFocus=null,this.focusHistory=[],this.voiceControlActive=!1,this.highContrastMode=!1,this.reducedMotionMode=!1,this.darkMode=!1,this.fontSize=16,this.loadPreferences(),this.init()}init(){let e=document.getElementById("voice-control-toggle");e&&e.remove(),this.setupKeyboardNavigation(),this.setupScreenReaderSupport(),this.setupFocusManagement(),this.setupHighContrastMode(),this.setupReducedMotion(),this.setupFontSizeControls(),this.setupCognitiveAccessibility(),this.setupDarkMode(),this.monitorAccessibilityPreferences(),this.setupAccessibilityTesting()}monitorAccessibilityPreferences(){window.matchMedia&&(window.matchMedia("(prefers-reduced-motion: reduce)").addEventListener("change",i=>{i.matches?this.applyReducedMotion():this.removeReducedMotion()}),window.matchMedia("(prefers-contrast: high)").addEventListener("change",i=>{i.matches&&this.applyHighContrastStyles()}),window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",i=>{window.darkModeManager&&window.darkModeManager.setTheme(i.matches?"dark":"light")})),this.loadPreferences(),this.monitorAccessibilityIssues()}setupKeyboardNavigation(){document.addEventListener("keydown",e=>{this.handleKeyboardNavigation(e)}),this.enhanceTabNavigation()}handleKeyboardNavigation(e){let t=e.target;e.key==="Tab"&&e.shiftKey===!1&&t.classList.contains("skip-link")&&(e.preventDefault(),this.focusMainContent()),(t.classList.contains("wellness-card")||t.closest(".wellness-card"))&&this.handleCardNavigation(e,t),e.altKey&&e.key==="v"&&(e.preventDefault(),this.toggleVoiceControl()),e.altKey&&e.key==="h"&&(e.preventDefault(),this.toggleHighContrast()),e.altKey&&e.key==="="&&(e.preventDefault(),this.increaseFontSize()),e.altKey&&e.key==="-"&&(e.preventDefault(),this.decreaseFontSize()),e.altKey&&e.key==="0"&&(e.preventDefault(),this.resetFontSize())}createSkipLink(){let e=document.createElement("a");e.href="#main-content",e.className="skip-link",e.textContent="Skip to main content",e.style.cssText=`
            position: absolute;
            top: -40px;
            left: 6px;
            background: #FF9800;
            color: white;
            padding: 8px;
            text-decoration: none;
            border-radius: 4px;
            z-index: 10000;
            transition: top 0.3s;
        `,e.addEventListener("focus",()=>{e.style.top="6px"}),e.addEventListener("blur",()=>{e.style.top="-40px"}),document.body.insertBefore(e,document.body.firstChild)}focusMainContent(){let e=document.querySelector("main")||document.querySelector("#main-content");e&&(e.setAttribute("tabindex","-1"),e.focus(),this.announceToScreenReader("Main content area"))}enhanceTabNavigation(){document.querySelectorAll("button, a, input, select, textarea, [tabindex]").forEach(e=>{e.hasAttribute("tabindex")||e.setAttribute("tabindex","0"),e.addEventListener("focus",()=>{this.addFocusIndicator(e)}),e.addEventListener("blur",()=>{this.removeFocusIndicator(e)})})}handleCardNavigation(e,t){let o=t.closest(".wellness-card")||t,i=Array.from(document.querySelectorAll(".wellness-card")),n=i.indexOf(o);switch(e.key){case"ArrowRight":e.preventDefault(),this.focusNextCard(i,n);break;case"ArrowLeft":e.preventDefault(),this.focusPreviousCard(i,n);break;case"Enter":case" ":e.preventDefault(),this.activateCard(o);break}}focusNextCard(e,t){let o=(t+1)%e.length;e[o].focus(),this.announceToScreenReader(`Card ${o+1} of ${e.length}`)}focusPreviousCard(e,t){let o=t===0?e.length-1:t-1;e[o].focus(),this.announceToScreenReader(`Card ${o+1} of ${e.length}`)}activateCard(e){let t=e.querySelector("button")||e;t&&t.click&&t.click()}setupScreenReaderSupport(){this.createLiveRegion(),this.enhanceARIALabels(),this.addDescriptiveText(),this.setupHeadingStructure()}createLiveRegion(){let e=document.createElement("div");e.id="screen-reader-announcements",e.setAttribute("aria-live","polite"),e.setAttribute("aria-atomic","true"),e.className="sr-only",e.style.cssText=`
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `,document.body.appendChild(e)}announceToScreenReader(e){let t=document.getElementById("screen-reader-announcements");t&&(t.textContent=e,setTimeout(()=>{t.textContent=""},1e3))}enhanceARIALabels(){document.querySelectorAll("button:not([aria-label]):not([aria-labelledby])").forEach(e=>{if(!e.textContent.trim()){let t=e.querySelector("i");if(t){let o=t.className,i="";o.includes("fa-plus")?i="Add new item":o.includes("fa-edit")?i="Edit":o.includes("fa-delete")?i="Delete":o.includes("fa-save")?i="Save":o.includes("fa-cancel")?i="Cancel":o.includes("fa-search")?i="Search":o.includes("fa-filter")?i="Filter":o.includes("fa-sort")?i="Sort":i="Button",e.setAttribute("aria-label",i)}}}),document.querySelectorAll("input, select, textarea").forEach(e=>{if(!e.hasAttribute("aria-label")&&!e.hasAttribute("aria-labelledby")){let t=e.closest("label")||document.querySelector(`label[for="${e.id}"]`);t&&e.setAttribute("aria-labelledby",t.id||this.generateId(t))}})}addDescriptiveText(){document.querySelectorAll(".wellness-card").forEach((e,t)=>{var n,c;let o=((n=e.querySelector("h3, h4"))==null?void 0:n.textContent)||"Card",i=((c=e.querySelector("p"))==null?void 0:c.textContent)||"";e.setAttribute("aria-label",`${o}. ${i}. Press Enter to activate.`),e.setAttribute("role","button"),e.setAttribute("tabindex","0")}),document.querySelectorAll(".progress-bar, .progress-ring").forEach(e=>{let t=e.getAttribute("aria-valuenow")||"0",o=e.getAttribute("aria-valuemax")||"100",i=e.getAttribute("aria-label")||"Progress";e.setAttribute("aria-label",`${i}: ${t}% complete`)})}setupHeadingStructure(){let e=document.querySelectorAll("h1, h2, h3, h4, h5, h6"),t=0;e.forEach(o=>{let i=parseInt(o.tagName.charAt(1));i>t+1&&// console.warn("Skipped heading level:",o),t=i})}setupFocusManagement(){document.addEventListener("focusin",e=>{this.focusHistory.push(e.target),this.focusHistory.length>10&&this.focusHistory.shift()}),this.setupFocusTrapping(),this.setupFocusRestoration()}setupFocusTrapping(){document.querySelectorAll('[role="dialog"], .modal').forEach(e=>{let t=e.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'),o=t[0],i=t[t.length-1];e.addEventListener("keydown",n=>{n.key==="Tab"&&(n.shiftKey?document.activeElement===o&&(n.preventDefault(),i.focus()):document.activeElement===i&&(n.preventDefault(),o.focus()))})})}setupFocusRestoration(){document.querySelectorAll("[data-modal-trigger]").forEach(e=>{e.addEventListener("click",()=>{this.currentFocus=document.activeElement})}),document.querySelectorAll("[data-modal-close]").forEach(e=>{e.addEventListener("click",()=>{this.currentFocus&&setTimeout(()=>{this.currentFocus.focus()},100)})})}addFocusIndicator(e){e.style.outline="2px solid #FF9800",e.style.outlineOffset="2px"}removeFocusIndicator(e){e.style.outline="",e.style.outlineOffset=""}setupVoiceControl(){this.createVoiceControlToggle(),this.setupVoiceCommands()}createVoiceControlToggle(){let e=document.createElement("button");e.id="voice-control-toggle",e.className="accessibility-toggle",e.setAttribute("aria-label","Toggle voice control"),e.innerHTML='<i class="fas fa-microphone"></i>',e.style.cssText=`
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #FF9800;
            color: white;
            border: none;
            cursor: pointer;
            z-index: 1000;
            display: flex;
            align-items: center;
            justify-content: center;
        `,e.addEventListener("click",()=>{this.toggleVoiceControl()}),document.body.appendChild(e)}toggleVoiceControl(){this.voiceControlActive=!this.voiceControlActive;let e=document.getElementById("voice-control-toggle");this.voiceControlActive?(e.innerHTML='<i class="fas fa-microphone-slash"></i>',e.style.background="#E74C3C",this.startVoiceRecognition(),this.announceToScreenReader("Voice control activated")):(e.innerHTML='<i class="fas fa-microphone"></i>',e.style.background="#FF9800",this.stopVoiceRecognition(),this.announceToScreenReader("Voice control deactivated"))}setupVoiceCommands(){if("webkitSpeechRecognition"in window||"SpeechRecognition"in window){let e=window.SpeechRecognition||window.webkitSpeechRecognition;this.recognition=new e,this.recognition.continuous=!0,this.recognition.interimResults=!1,this.recognition.lang=navigator.language||"en-US",this.recognition.onresult=t=>{let o=t.results[t.results.length-1][0].transcript.toLowerCase();this.processVoiceCommand(o)},this.recognition.onerror=t=>{// console.error("Voice recognition error:",t.error),t.error==="no-speech"?this.announceToScreenReader("No speech detected. Please try again."):this.announceToScreenReader("Voice recognition error. Please check your microphone.")},this.recognition.onend=()=>{this.voiceControlActive&&setTimeout(()=>{this.voiceControlActive&&this.startVoiceRecognition()},1e3)}}}startVoiceRecognition(){this.recognition&&this.recognition.start()}stopVoiceRecognition(){this.recognition&&this.recognition.stop()}processVoiceCommand(e){var t,o,i,n;this.announceToScreenReader(`Processing command: ${e}`),e.includes("go to dashboard")||e.includes("dashboard")?window.location.href="/dashboard":e.includes("go to expenses")||e.includes("expenses")?window.location.href="/expenses":e.includes("add expense")||e.includes("new expense")?(t=document.querySelector("#quickAddBtn"))==null||t.click():e.includes("search")?(o=document.querySelector('input[type="search"]'))==null||o.focus():e.includes("help")?this.showHelp():e.includes("close")||e.includes("cancel")?(i=document.querySelector(".modal .close"))==null||i.click():e.includes("next")?this.navigateNext():e.includes("previous")||e.includes("back")?this.navigatePrevious():e.includes("save")?(n=document.querySelector('button[type="submit"]'))==null||n.click():e.includes("logout")||e.includes("sign out")?window.location.href="/logout":e.includes("settings")?window.location.href="/settings":this.announceToScreenReader('Command not recognized. Say "help" for available commands.')}navigateNext(){let e=document.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'),t=document.activeElement,o=Array.from(e).indexOf(t);o<e.length-1&&e[o+1].focus()}navigatePrevious(){let e=document.querySelectorAll('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'),t=document.activeElement,o=Array.from(e).indexOf(t);o>0&&e[o-1].focus()}setupHighContrastMode(){try{this.applyHighContrastStyles&&this.applyHighContrastStyles()}catch{}}setupReducedMotion(){window.matchMedia("(prefers-reduced-motion: reduce)").matches&&(this.reducedMotionMode=!0,this.applyReducedMotion()),window.matchMedia("(prefers-reduced-motion: reduce)").addEventListener("change",e=>{this.reducedMotionMode=e.matches,this.reducedMotionMode?this.applyReducedMotion():this.removeReducedMotion()})}applyReducedMotion(){let e=document.createElement("style");e.id="reduced-motion-styles",e.textContent=`
            *, *::before, *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
                scroll-behavior: auto !important;
            }
        `,document.head.appendChild(e)}removeReducedMotion(){let e=document.getElementById("reduced-motion-styles");e&&e.remove()}setupFontSizeControls(){this.createFontSizeControls(),this.applyFontSize()}createFontSizeControls(){let e=document.createElement("div");e.id="font-size-controls",e.className="accessibility-controls",e.style.cssText=`
            position: fixed;
            bottom: 80px;
            left: 20px;
            display: flex;
            gap: 10px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.85);
            padding: 8px;
            border-radius: 25px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
        `;let t=document.createElement("button");t.innerHTML="A-",t.setAttribute("aria-label","Decrease font size"),t.addEventListener("click",()=>this.decreaseFontSize());let o=document.createElement("button");o.innerHTML="A+",o.setAttribute("aria-label","Increase font size"),o.addEventListener("click",()=>this.increaseFontSize());let i=document.createElement("button");i.innerHTML="A",i.setAttribute("aria-label","Reset font size"),i.addEventListener("click",()=>this.resetFontSize()),t.style.cssText=`
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #FF9800;
            color: #1a1a1a !important;
            border: none;
            cursor: pointer;
            font-weight: 700 !important;
            transition: all 0.3s ease;
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            font-size: 16px !important;
            letter-spacing: 0.5px !important;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        `,o.style.cssText=`
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #FF9800;
            color: #1a1a1a !important;
            border: none;
            cursor: pointer;
            font-weight: 700 !important;
            transition: all 0.3s ease;
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            font-size: 16px !important;
            letter-spacing: 0.5px !important;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        `,i.style.cssText=`
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background: #FF9800;
            color: #1a1a1a !important;
            border: none;
            cursor: pointer;
            font-weight: 700 !important;
            transition: all 0.3s ease;
            font-family: 'Inter', system-ui, -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
            font-size: 16px !important;
            letter-spacing: 0.5px !important;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            text-rendering: optimizeLegibility;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        `,e.appendChild(t),e.appendChild(i),e.appendChild(o),document.body.appendChild(e);
        let n=document.createElement("style");
        n.textContent=`
            #font-size-controls {background: rgba(0,0,0,0.85) !important;box-shadow: 0 2px 10px rgba(0,0,0,0.4) !important;border-radius: 25px !important;padding: 8px !important;}
            #font-size-controls button {background:#FF9800 !important;color:#1a1a1a !important;border:none !important;width:40px !important;height:40px !important;border-radius:50% !important;font-family:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif !important;font-weight:700 !important;font-size:16px !important;letter-spacing:0.5px !important;display:inline-flex !important;align-items:center !important;justify-content:center !important;text-rendering:optimizeLegibility !important;-webkit-font-smoothing:antialiased !important;-moz-osx-font-smoothing:grayscale !important;}
        `,document.head.appendChild(n)}setupCognitiveAccessibility(){this.addReadingTimeEstimates(),this.simplifyLanguage(),this.addProgressIndicators(),this.setupErrorPrevention()}addReadingTimeEstimates(){document.querySelectorAll("article, .content-section").forEach(e=>{let o=e.textContent.split(" ").length,i=Math.ceil(o/200),n=document.createElement("div");n.className="reading-time",n.textContent=`Estimated reading time: ${i} minute${i!==1?"s":""}`,n.style.cssText=`
                font-size: 0.875rem;
                color: #666;
                margin-bottom: 1rem;
            `,e.insertBefore(n,e.firstChild)})}simplifyLanguage(){let e={utilize:"use",facilitate:"help",implement:"start",optimize:"improve",leverage:"use",streamline:"simplify"};document.querySelectorAll(".content p, .content h1, .content h2, .content h3, article p").forEach(t=>{if(t.querySelector("code")||t.classList.contains("technical"))return;let o=t.textContent;Object.entries(e).forEach(([i,n])=>{o=o.replace(new RegExp(`\\b${i}\\b`,"gi"),n)}),t.textContent=o})}addProgressIndicators(){document.querySelectorAll(".onboarding-step, .wizard-step").forEach((e,t,o)=>{let i=document.createElement("div");i.className="step-progress",i.textContent=`Step ${t+1} of ${o.length}`,i.style.cssText=`
                font-size: 0.875rem;
                color: #666;
                margin-bottom: 0.5rem;
            `,e.insertBefore(i,e.firstChild)})}setupErrorPrevention(){document.querySelectorAll("button[data-destructive]").forEach(e=>{e.addEventListener("click",t=>{confirm("Are you sure you want to perform this action? This cannot be undone.")||t.preventDefault()})}),this.setupUndoFunctionality()}setupUndoFunctionality(){let e=[];if(document.addEventListener("click",t=>{t.target.matches("button[data-trackable]")&&e.push({action:t.target.textContent,timestamp:Date.now(),element:t.target})}),e.length>0){let t=document.createElement("button");t.textContent="Undo",t.addEventListener("click",()=>{let o=e.pop();o&&this.announceToScreenReader(`Undid: ${o.action}`)})}}setupAccessibilityTesting(){this.runAccessibilityChecks(),this.monitorAccessibilityIssues()}runAccessibilityChecks(){document.querySelectorAll("img:not([alt])").forEach(e=>{// console.warn("Image missing alt text:",e)}),document.querySelectorAll("input:not([aria-label]):not([aria-labelledby])").forEach(e=>{e.closest("label")||// console.warn("Input missing label:",e)}),this.validateHeadingStructure(),this.checkColorContrast()}validateHeadingStructure(){let e=document.querySelectorAll("h1, h2, h3, h4, h5, h6"),t=0;e.forEach(o=>{let i=parseInt(o.tagName.charAt(1));i>t+1&&// console.warn("Skipped heading level:",o),t=i})}checkColorContrast(){document.querySelectorAll("*").forEach(e=>{let t=window.getComputedStyle(e),o=t.backgroundColor,i=t.color;o&&i&&o===i&&// console.warn("Potential contrast issue:",e)})}monitorAccessibilityIssues(){this.mutationObserver=new MutationObserver(e=>{e.forEach(t=>{t.addedNodes.forEach(o=>{o.nodeType===Node.ELEMENT_NODE&&this.checkNewElement(o)})})}),this.mutationObserver.observe(document.body,{childList:!0,subtree:!0})}checkNewElement(e){e.tagName==="IMG"&&!e.hasAttribute("alt")&&// console.warn("New image missing alt text:",e),e.tagName==="BUTTON"&&!e.textContent.trim()&&!e.hasAttribute("aria-label")&&// console.warn("New button missing accessible label:",e)}loadPreferences(){let e=localStorage.getItem("coraAccessibilityPrefs");if(e)try{let t=JSON.parse(e);this.voiceControlActive=t.voiceControlActive||!1,this.highContrastMode=t.highContrastMode||!1,this.darkMode=t.darkMode||!1,this.fontSize=t.fontSize||16,this.highContrastMode&&document.body.classList.add("high-contrast"),this.darkMode&&document.body.classList.add("dark-mode"),this.applyFontSize()}catch(t){// console.error("Error loading accessibility preferences:",t)}window.matchMedia("(prefers-color-scheme: dark)").matches&&(this.darkMode=!0,document.body.classList.add("dark-mode"))}savePreferences(){let e={voiceControlActive:this.voiceControlActive,highContrastMode:this.highContrastMode,darkMode:this.darkMode,fontSize:this.fontSize};localStorage.setItem("coraAccessibilityPrefs",JSON.stringify(e))}setupDarkMode(){window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change",t=>{this.highContrastMode||(this.darkMode=t.matches,document.body.classList.toggle("dark-mode",this.darkMode),this.savePreferences())});let e=document.createElement("style");e.textContent=`
            .dark-mode {
                background: #1a1a1a !important;
                color: #e0e0e0 !important;
            }
            
            .dark-mode .wellness-card {
                background: #2a2a2a !important;
                border-color: #3a3a3a !important;
                color: #e0e0e0 !important;
            }
            
            .dark-mode input, .dark-mode select, .dark-mode textarea {
                background: #2a2a2a !important;
                border-color: #3a3a3a !important;
                color: #e0e0e0 !important;
            }
            
            .dark-mode .wellness-btn {
                background: linear-gradient(135deg, #7B4EA8, #48C87B) !important;
            }
        `,document.head.appendChild(e)}generateId(e){return e.id||(e.id="element-"+Math.random().toString(36).substr(2,9)),e.id}showHelp(){let e=document.createElement("div");e.className="accessibility-help",e.innerHTML=`
            <h2>Accessibility Help</h2>
            <ul>
                <li><strong>Alt + V:</strong> Toggle voice control</li>
                <li><strong>Alt + H:</strong> Toggle high contrast</li>
                <li><strong>Alt + =:</strong> Increase font size</li>
                <li><strong>Alt + -:</strong> Decrease font size</li>
                <li><strong>Alt + 0:</strong> Reset font size</li>
                <li><strong>Tab:</strong> Navigate with keyboard</li>
                <li><strong>Enter/Space:</strong> Activate buttons</li>
            </ul>
        `,e.style.cssText=`
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 2rem;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
            z-index: 10000;
            max-width: 400px;
        `;let t=document.createElement("button");t.innerHTML="&times;",t.setAttribute("aria-label","Close help dialog"),t.style.cssText=`
            position: absolute;
            top: 10px;
            right: 10px;
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            color: #666;
        `,t.addEventListener("click",()=>e.remove()),e.appendChild(t),document.body.appendChild(e),document.addEventListener("keydown",o=>{o.key==="Escape"&&e.remove()})}cleanup(){this.recognition&&this.stopVoiceRecognition(),this.mutationObserver&&this.mutationObserver.disconnect()}getAccessibilityStatus(){return{voiceControlActive:this.voiceControlActive,highContrastMode:this.highContrastMode,reducedMotionMode:this.reducedMotionMode,fontSize:this.fontSize}}enableAccessibility(){this.setupKeyboardNavigation(),this.setupScreenReaderSupport(),this.setupFocusManagement()}},a=new r;window.CORAAccessibility=a;document.addEventListener("DOMContentLoaded",()=>{a.enableAccessibility()});window.addEventListener("beforeunload",()=>{a.cleanup()});typeof s!="undefined"&&s.exports&&(s.exports=r)});export default d();
//# sourceMappingURL=accessibility.js.map
