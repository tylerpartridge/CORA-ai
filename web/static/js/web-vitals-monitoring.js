/**
 * Core Web Vitals Monitoring for SEO
 * Tracks LCP, INP (replacing FID), and CLS
 */

// Track Largest Contentful Paint (LCP)
const lcpObserver = new PerformanceObserver((list) => {
    const entries = list.getEntries();
    const lastEntry = entries[entries.length - 1];
    
    // Send to analytics
    if (window.gtag) {
        gtag('event', 'web_vitals', {
            metric_name: 'LCP',
            value: Math.round(lastEntry.renderTime || lastEntry.loadTime),
            metric_rating: getRating('LCP', lastEntry.renderTime || lastEntry.loadTime)
        });
    }
    
    // Log for debugging
    // console.log('LCP:', Math.round(lastEntry.renderTime || lastEntry.loadTime), 'ms');
});

// Observe LCP
try {
    lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
} catch (e) {
    // console.log('LCP observation not supported');
}

// Track Interaction to Next Paint (INP) - replacing FID
let inpValue = 0;
const inpObserver = new PerformanceObserver((list) => {
    list.getEntries().forEach((entry) => {
        if (entry.interactionId) {
            const inp = entry.processingStart - entry.startTime;
            
            // Keep track of the worst INP
            if (inp > inpValue) {
                inpValue = inp;
                
                // Send to analytics
                if (window.gtag) {
                    gtag('event', 'web_vitals', {
                        metric_name: 'INP',
                        value: Math.round(inp),
                        metric_rating: getRating('INP', inp)
                    });
                }
                
                // Log for debugging
                // console.log('INP:', Math.round(inp), 'ms');
            }
        }
    });
});

// Observe INP
try {
    inpObserver.observe({ type: 'event', buffered: true });
} catch (e) {
    // console.log('INP observation not supported');
}

// Track Cumulative Layout Shift (CLS)
let clsValue = 0;
const clsObserver = new PerformanceObserver((list) => {
    list.getEntries().forEach((entry) => {
        if (!entry.hadRecentInput) {
            clsValue += entry.value;
            
            // Send to analytics
            if (window.gtag) {
                gtag('event', 'web_vitals', {
                    metric_name: 'CLS',
                    value: clsValue.toFixed(3),
                    metric_rating: getRating('CLS', clsValue)
                });
            }
            
            // Log for debugging
            // console.log('CLS:', clsValue.toFixed(3));
        }
    });
});

// Observe CLS
try {
    clsObserver.observe({ type: 'layout-shift', buffered: true });
} catch (e) {
    // console.log('CLS observation not supported');
}

// Helper function to rate metrics
function getRating(metric, value) {
    const thresholds = {
        LCP: { good: 2500, poor: 4000 },
        INP: { good: 200, poor: 500 },
        CLS: { good: 0.1, poor: 0.25 }
    };
    
    const threshold = thresholds[metric];
    if (value <= threshold.good) return 'good';
    if (value <= threshold.poor) return 'needs-improvement';
    return 'poor';
}

// Performance optimization techniques
document.addEventListener('DOMContentLoaded', function() {
    // 1. Preload critical resources
    const criticalResources = [
        '/static/css/unified-design-system.css',
        '/static/images/logos/cora-logo.png'
    ];
    
    criticalResources.forEach(resource => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = resource;
        
        if (resource.endsWith('.css')) {
            link.as = 'style';
        } else if (resource.endsWith('.js')) {
            link.as = 'script';
        } else if (resource.match(/\.(png|jpg|webp|svg)$/)) {
            link.as = 'image';
        }
        
        document.head.appendChild(link);
    });
    
    // 2. Lazy load images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    observer.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // 3. Optimize font loading
    if ('fonts' in document) {
        Promise.all([
            document.fonts.load('400 1em Poppins'),
            document.fonts.load('600 1em Poppins'),
            document.fonts.load('400 1em Inter')
        ]).then(() => {
            document.documentElement.classList.add('fonts-loaded');
        });
    }
    
    // 4. Reduce CLS by setting dimensions
    document.querySelectorAll('img:not([width])').forEach(img => {
        if (img.naturalWidth) {
            img.width = img.naturalWidth;
            img.height = img.naturalHeight;
        }
    });
});

// Report final metrics when page is about to unload
window.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'hidden') {
        // Send final metrics
        if (window.gtag) {
            gtag('event', 'web_vitals_final', {
                lcp_final: Math.round(performance.getEntriesByType('largest-contentful-paint').pop()?.renderTime || 0),
                inp_final: Math.round(inpValue),
                cls_final: clsValue.toFixed(3)
            });
        }
    }
});

// Export metrics for debugging
window.getWebVitals = function() {
    return {
        LCP: Math.round(performance.getEntriesByType('largest-contentful-paint').pop()?.renderTime || 0),
        INP: Math.round(inpValue),
        CLS: clsValue.toFixed(3)
    };
};