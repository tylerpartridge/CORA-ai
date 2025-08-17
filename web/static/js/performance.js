/**
 * CORA Performance Optimization Suite
 * 
 * This module provides comprehensive performance optimizations for the CORA wellness experience:
 * - Critical CSS inlining and optimization
 * - Intelligent lazy loading
 * - Image optimization and WebP support
 * - Performance monitoring and analytics
 * - Resource preloading and caching
 * - Accessibility performance enhancements
 */

class CORAPerformance {
    constructor() {
        this.performanceMetrics = {
            firstContentfulPaint: 0,
            largestContentfulPaint: 0,
            cumulativeLayoutShift: 0,
            firstInputDelay: 0,
            timeToInteractive: 0
        };
        
        this.observers = new Map();
        this.preloadQueue = [];
        this.criticalResources = new Set();
        
        this.init();
    }
    
    init() {
        // Start performance monitoring immediately
        this.startPerformanceMonitoring();
        
        // Initialize critical optimizations
        this.optimizeCriticalCSS();
        this.setupLazyLoading();
        this.optimizeImages();
        this.setupResourcePreloading();
        this.optimizeFonts();
        this.setupServiceWorker();
        
        // Setup intersection observers for performance
        this.setupIntersectionObservers();
        
        // Monitor for performance issues
        this.monitorPerformanceIssues();
    }
    
    /**
     * Performance Monitoring
     */
    startPerformanceMonitoring() {
        // Monitor Core Web Vitals
        if ('PerformanceObserver' in window) {
            // First Contentful Paint
            const fcpObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    this.performanceMetrics.firstContentfulPaint = entry.startTime;
                    this.logPerformanceMetric('FCP', entry.startTime);
                });
            });
            fcpObserver.observe({ entryTypes: ['paint'] });
            
            // Largest Contentful Paint
            const lcpObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                this.performanceMetrics.largestContentfulPaint = lastEntry.startTime;
                this.logPerformanceMetric('LCP', lastEntry.startTime);
            });
            lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
            
            // Cumulative Layout Shift
            const clsObserver = new PerformanceObserver((list) => {
                let clsValue = 0;
                for (const entry of list.getEntries()) {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                    }
                }
                this.performanceMetrics.cumulativeLayoutShift = clsValue;
                this.logPerformanceMetric('CLS', clsValue);
            });
            clsObserver.observe({ entryTypes: ['layout-shift'] });
            
            // First Input Delay
            const fidObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    this.performanceMetrics.firstInputDelay = entry.processingStart - entry.startTime;
                    this.logPerformanceMetric('FID', this.performanceMetrics.firstInputDelay);
                });
            });
            fidObserver.observe({ entryTypes: ['first-input'] });
        }
        
        // Monitor Time to Interactive
        this.measureTimeToInteractive();
    }
    
    /**
     * Critical CSS Optimization
     */
    optimizeCriticalCSS() {
        // Inline critical CSS for above-the-fold content
        const criticalStyles = `
            /* Critical rendering styles */
            body { 
                margin: 0; 
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
                background: linear-gradient(135deg, #FFF9F0 0%, white 100%);
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
                background: white;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
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
        `;
        
        // Inject critical CSS
        const style = document.createElement('style');
        style.textContent = criticalStyles;
        document.head.insertBefore(style, document.head.firstChild);
        
        // Preload non-critical CSS (wellness.css disabled for construction theme)
        // this.preloadResource('/static/css/wellness.css', 'style');
    }
    
    /**
     * Intelligent Lazy Loading
     */
    setupLazyLoading() {
        // Lazy load images with intersection observer
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        this.loadImage(img);
                        observer.unobserve(img);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });
            
            // Observe all images with data-src
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });
        }
        
        // Lazy load components
        this.setupComponentLazyLoading();
    }
    
    /**
     * Image Optimization
     */
    optimizeImages() {
        // Convert images to WebP if supported
        if (this.supportsWebP()) {
            this.convertImagesToWebP();
        }
        
        // Optimize image loading
        document.querySelectorAll('img').forEach(img => {
            // Add loading="lazy" for images below the fold
            if (!this.isAboveTheFold(img)) {
                img.loading = 'lazy';
            }
            
            // Add decoding="async" for better performance
            img.decoding = 'async';
            
            // Add error handling
            img.addEventListener('error', () => {
                this.handleImageError(img);
            });
        });
    }
    
    /**
     * Resource Preloading
     */
    setupResourcePreloading() {
        // Preload critical resources
        const criticalResources = [
            // { href: '/static/css/wellness.css', as: 'style' }, // Disabled for construction theme
            { href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap', as: 'style' },
            { href: '/static/images/logos/cora-logo.png', as: 'image' }
        ];
        
        criticalResources.forEach(resource => {
            this.preloadResource(resource.href, resource.as);
        });
        
        // Prefetch likely resources
        this.prefetchLikelyResources();
    }
    
    /**
     * Font Optimization
     */
    optimizeFonts() {
        // Disabled font preloading to prevent unused resource warnings
        // TODO: Implement proper font optimization with actual usage tracking
        // console.log('Font optimization disabled - using standard font loading');
        
        // Optimize font display for existing font links
        document.querySelectorAll('link[href*="fonts.googleapis.com"]').forEach(link => {
            link.setAttribute('media', 'print');
            link.setAttribute('onload', "this.media='all'");
        });
    }
    
    /**
     * Service Worker Setup
     */
    setupServiceWorker() {
        const isLocalhost = ['localhost', '127.0.0.1'].includes(location.hostname);
        if ('serviceWorker' in navigator && !isLocalhost) {
            window.addEventListener('load', () => {
                navigator.serviceWorker.register('/static/service-worker.js')
                    .then(registration => {
                        // console.log('SW registered: ', registration);
                        setInterval(() => { registration.update(); }, 60000);
                    })
                    .catch(() => {/* non-fatal */});
            });
        }
    }
    
    /**
     * Intersection Observers for Performance
     */
    setupIntersectionObservers() {
        // Observe components for performance optimization
        const componentObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.optimizeComponent(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        // Observe wellness cards and other components
        document.querySelectorAll('.wellness-card, .feature-card, .stat-card').forEach(component => {
            componentObserver.observe(component);
        });
    }
    
    /**
     * Performance Issue Monitoring
     */
    monitorPerformanceIssues() {
        // Monitor for slow loading resources
        const resourceObserver = new PerformanceObserver((list) => {
            list.getEntries().forEach(entry => {
                if (entry.duration > 3000) { // 3 seconds threshold
                    this.reportSlowResource(entry);
                }
            });
        });
        resourceObserver.observe({ entryTypes: ['resource'] });
        
        // Monitor for layout shifts
        const layoutShiftObserver = new PerformanceObserver((list) => {
            list.getEntries().forEach(entry => {
                if (entry.value > 0.1) { // CLS threshold
                    this.reportLayoutShift(entry);
                }
            });
        });
        layoutShiftObserver.observe({ entryTypes: ['layout-shift'] });
    }
    
    /**
     * Utility Methods
     */
    preloadResource(href, as) {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = href;
        link.as = as;
        document.head.appendChild(link);
    }
    
    loadImage(img) {
        const src = img.dataset.src;
        if (src) {
            img.src = src;
            img.removeAttribute('data-src');
            img.classList.remove('lazy');
        }
    }
    
    supportsWebP() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }
    
    convertImagesToWebP() {
        // Disabled WebP conversion to prevent 404 errors
        // TODO: Add WebP versions of images or implement proper fallback
        // console.log('WebP conversion disabled - using original image formats');
    }
    
    isAboveTheFold(element) {
        const rect = element.getBoundingClientRect();
        return rect.top < window.innerHeight;
    }
    
    handleImageError(img) {
        // Fallback to original format or placeholder
        if (img.src.includes('.webp')) {
            img.src = img.src.replace('.webp', '.png');
        } else {
            img.src = '/static/images/placeholder.svg';
        }
    }
    
    setupComponentLazyLoading() {
        // Lazy load non-critical components
        const components = document.querySelectorAll('[data-lazy-component]');
        const componentObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadComponent(entry.target);
                    componentObserver.unobserve(entry.target);
                }
            });
        });
        
        components.forEach(component => {
            componentObserver.observe(component);
        });
    }
    
    loadComponent(component) {
        const componentType = component.dataset.lazyComponent;
        // Load component based on type
        switch (componentType) {
            case 'chart':
                this.loadChartComponent(component);
                break;
            case 'table':
                this.loadTableComponent(component);
                break;
            case 'form':
                this.loadFormComponent(component);
                break;
        }
    }
    
    optimizeComponent(component) {
        // Apply performance optimizations to components
        // Only use will-change during actual animations
        const animationHandler = () => {
            component.style.willChange = 'transform';
            component.addEventListener('transitionend', () => {
                component.style.willChange = 'auto';
            }, { once: true });
        };
        
        // Apply on hover/focus for better performance
        component.addEventListener('mouseenter', animationHandler);
        component.addEventListener('focus', animationHandler);
    }
    
    prefetchLikelyResources() {
        // Prefetch resources that are likely to be needed
        const likelyResources = [
            '/dashboard',
            '/expenses',
            '/reports'
        ];
        
        // Prefetch after page load
        const isLocalhost = ['localhost', '127.0.0.1'].includes(location.hostname);
        if (!isLocalhost) {
            window.addEventListener('load', () => {
                setTimeout(() => {
                    likelyResources.forEach(resource => {
                        const link = document.createElement('link');
                        link.rel = 'prefetch';
                        link.href = resource;
                        document.head.appendChild(link);
                    });
                }, 2000);
            });
        }
    }
    
    measureTimeToInteractive() {
        // Measure time to interactive using Long Task API
        if ('PerformanceObserver' in window && PerformanceObserver.supportedEntryTypes.includes('longtask')) {
            let lastLongTask = 0;
            const longTaskObserver = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                entries.forEach(entry => {
                    lastLongTask = entry.startTime + entry.duration;
                });
            });
            longTaskObserver.observe({ entryTypes: ['longtask'] });
            
            // Estimate TTI after page load
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const tti = Math.max(lastLongTask, performance.timing.domInteractive - performance.timing.navigationStart);
                    this.performanceMetrics.timeToInteractive = tti;
                    this.logPerformanceMetric('TTI', tti);
                }, 5000); // Wait 5 seconds after load
            });
        }
    }
    
    logPerformanceMetric(name, value) {
        // console.log(`Performance Metric - ${name}: ${value}ms`);
        
        // Send to analytics if available
        if (window.gtag) {
            gtag('event', 'performance_metric', {
                metric_name: name,
                metric_value: value
            });
        }
    }
    
    reportSlowResource(entry) {
        // console.warn('Slow resource detected:', entry.name, entry.duration);
        
        // Send to error tracking
        if (window.Sentry) {
            Sentry.captureMessage('Slow resource detected', {
                level: 'warning',
                extra: {
                    name: entry.name,
                    duration: entry.duration,
                    entryType: entry.entryType
                }
            });
        }
    }
    
    reportLayoutShift(entry) {
        // console.warn('Layout shift detected:', entry.value);
        
        // Send to error tracking
        if (window.Sentry) {
            Sentry.captureMessage('Layout shift detected', {
                level: 'warning',
                extra: {
                    value: entry.value,
                    sources: entry.sources
                }
            });
        }
    }
    
    /**
     * Component Loading Methods
     */
    loadChartComponent(container) {
        // Placeholder for chart component
        // TODO: Implement when charts.js is available
        // console.log('Chart component requested for:', container);
        container.innerHTML = '<div class="skeleton" style="height: 300px; border-radius: 8px;"></div>';
    }
    
    loadTableComponent(container) {
        // Skip API call on landing page - not needed
        if (window.location.pathname === '/' || !window.location.pathname.includes('/dashboard')) {
            return;
        }
        
        // Load table data and render
        fetch('/api/data/table')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Failed to load table data');
                }
                return response.json();
            })
            .then(data => {
                this.renderTable(container, data);
            })
            .catch(error => {
                // console.error('Error loading table data:', error);
                container.innerHTML = '<p class="text-gray-500">Unable to load data</p>';
            });
    }
    
    loadFormComponent(container) {
        // Initialize form with basic validation
        const forms = container.querySelectorAll('form');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                // Basic validation
                const inputs = form.querySelectorAll('input[required]');
                let valid = true;
                inputs.forEach(input => {
                    if (!input.value.trim()) {
                        valid = false;
                        input.classList.add('error');
                    } else {
                        input.classList.remove('error');
                    }
                });
                if (!valid) {
                    e.preventDefault();
                }
            });
        });
    }
    
    renderTable(container, data) {
        // Render table with data
        const table = document.createElement('table');
        table.className = 'wellness-table';
        
        // Build table HTML
        let tableHTML = '<thead><tr>';
        Object.keys(data[0] || {}).forEach(key => {
            tableHTML += `<th>${key}</th>`;
        });
        tableHTML += '</tr></thead><tbody>';
        
        data.forEach(row => {
            tableHTML += '<tr>';
            Object.values(row).forEach(value => {
                tableHTML += `<td>${value}</td>`;
            });
            tableHTML += '</tr>';
        });
        tableHTML += '</tbody>';
        
        table.innerHTML = tableHTML;
        container.appendChild(table);
    }
    
    /**
     * Public API
     */
    getPerformanceMetrics() {
        return this.performanceMetrics;
    }
    
    optimizePage() {
        // Run all optimizations
        this.optimizeCriticalCSS();
        this.setupLazyLoading();
        this.optimizeImages();
        this.setupResourcePreloading();
    }
    
    preloadPage(url) {
        // Preload a specific page
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = url;
        document.head.appendChild(link);
    }
}

// Initialize performance optimization
const coraPerformance = new CORAPerformance();

// Export for use in other modules
window.CORAPerformance = coraPerformance;

// Auto-optimize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    coraPerformance.optimizePage();
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (typeof coraPerformance !== 'undefined' && coraPerformance.cleanup) {
        coraPerformance.cleanup();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CORAPerformance;
} 