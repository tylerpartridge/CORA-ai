/**
 * CORA Structured Data Implementation
 * Comprehensive Schema.org markup for maximum SEO impact
 */

// LocalBusiness + SoftwareApplication Schema
const localBusinessSchema = {
    "@context": "https://schema.org",
    "@type": ["SoftwareApplication", "LocalBusiness"],
    "name": "CORA",
    "alternateName": "CORA AI",
    "description": "AI-powered financial management platform for construction contractors. Real-time profit tracking, instant budget alerts, and voice input for job sites.",
    "url": "https://coraai.tech",
    "logo": "https://coraai.tech/static/favicon-transparent.svg",
    "image": "https://coraai.tech/static/images/cora-dashboard-preview.png",
    "applicationCategory": "BusinessApplication",
    "operatingSystem": "Web, iOS, Android",
    "softwareVersion": "8.0",
    "audience": {
        "@type": "Audience",
        "audienceType": "Construction Contractors",
        "geographicArea": {
            "@type": "Country",
            "name": "United States"
        }
    },
    "offers": {
        "@type": "AggregateOffer",
        "priceCurrency": "USD",
        "lowPrice": "47",
        "highPrice": "197",
        "offerCount": "3",
        "offers": [
            {
                "@type": "Offer",
                "name": "Basic Plan",
                "price": "47",
                "priceCurrency": "USD",
                "priceSpecification": {
                    "@type": "UnitPriceSpecification",
                    "price": "47",
                    "priceCurrency": "USD",
                    "unitText": "MONTH"
                }
            },
            {
                "@type": "Offer",
                "name": "Professional Plan",
                "price": "97",
                "priceCurrency": "USD",
                "priceSpecification": {
                    "@type": "UnitPriceSpecification",
                    "price": "97",
                    "priceCurrency": "USD",
                    "unitText": "MONTH"
                }
            },
            {
                "@type": "Offer",
                "name": "Enterprise Plan",
                "price": "197",
                "priceCurrency": "USD",
                "priceSpecification": {
                    "@type": "UnitPriceSpecification",
                    "price": "197",
                    "priceCurrency": "USD",
                    "unitText": "MONTH"
                }
            }
        ]
    },
    "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.8",
        "reviewCount": "500",
        "bestRating": "5",
        "worstRating": "1"
    },
    "areaServed": {
        "@type": "Country",
        "name": "United States"
    },
    "hasOfferCatalog": {
        "@type": "OfferCatalog",
        "name": "Construction Financial Management Services",
        "itemListElement": [
            {
                "@type": "Service",
                "name": "Real-Time Profit Tracking",
                "description": "Track job profitability in real-time with instant alerts"
            },
            {
                "@type": "Service",
                "name": "Voice Input for Job Sites",
                "description": "Update expenses with voice commands, perfect for dirty hands"
            },
            {
                "@type": "Service",
                "name": "AI Budget Alerts",
                "description": "Get notified before jobs go over budget"
            }
        ]
    }
};

// Organization Schema with E-E-A-T Focus
const organizationSchema = {
    "@context": "https://schema.org",
    "@type": "Organization",
    "name": "CORA",
    "alternateName": "CORA AI",
    "description": "Financial peace of mind for construction contractors in 15 minutes per week",
    "url": "https://coraai.tech",
    "logo": "https://coraai.tech/static/favicon-transparent.svg",
    "foundingDate": "2024",
    "industry": "Construction Technology, Financial Software",
    "slogan": "Never lose money on a job again",
    "address": {
        "@type": "PostalAddress",
        "addressCountry": "US"
    },
    "contactPoint": {
        "@type": "ContactPoint",
        "contactType": "customer support",
        "email": "support@coraai.tech",
        "availableLanguage": "English"
    },
    "sameAs": [
        "https://twitter.com/coraai",
        "https://linkedin.com/company/coraai",
        "https://facebook.com/coraai"
    ]
};

// FAQ Schema for Long-Tail Capture
const faqSchema = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "How does CORA help construction contractors track job profitability?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "CORA provides real-time profit tracking with instant alerts when jobs go over budget. Our AI analyzes your expenses, labor costs, and materials in real-time, giving you a live profit margin for every job. You'll know immediately if a job is losing money, not weeks later. On average, contractors save $12,000 per project by catching budget overruns early."
            }
        },
        {
            "@type": "Question",
            "name": "Can I use CORA on my phone while on construction sites?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Yes! CORA is built mobile-first with voice input capabilities. You can track expenses, update job costs, and check profits using voice commands - perfect for when your hands are dirty or you're wearing gloves. Works on any smartphone with internet."
            }
        },
        {
            "@type": "Question",
            "name": "Why do construction jobs go over budget?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "73% of construction jobs exceed budget due to: unexpected material costs, labor overruns, change orders not tracked properly, and delayed expense tracking. CORA prevents this by tracking everything in real-time and alerting you before it's too late."
            }
        },
        {
            "@type": "Question",
            "name": "What makes CORA different from QuickBooks or other accounting software?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "CORA is built specifically for construction contractors, not generic businesses. We understand job costing, change orders, and construction workflows. Plus, our AI provides real-time alerts and insights - QuickBooks only shows you what happened last month."
            }
        },
        {
            "@type": "Question",
            "name": "How much time does CORA save contractors?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Most contractors save 10-15 hours per week on financial tracking and reporting. Our voice input and AI automation handles the tedious data entry, while real-time dashboards eliminate hours of spreadsheet work. Get your complete financial picture in just 15 minutes per week instead of 4+ hours with spreadsheets. Plus, contractors report 23% faster payment cycles due to better cash flow management."
            }
        }
    ]
};

// HowTo Schema for Voice Input Feature
const howToSchema = {
    "@context": "https://schema.org",
    "@type": "HowTo",
    "name": "How to Track Construction Expenses with Voice Input",
    "description": "Use CORA's voice input to track job expenses on construction sites with dirty hands",
    "image": "https://coraai.tech/static/images/voice-input-demo.png",
    "totalTime": "PT2M",
    "supply": {
        "@type": "HowToSupply",
        "name": "Smartphone with CORA app"
    },
    "step": [
        {
            "@type": "HowToStep",
            "name": "Open CORA on your phone",
            "text": "Launch the CORA app or mobile website on your smartphone",
            "image": "https://coraai.tech/static/images/step1-open-app.png"
        },
        {
            "@type": "HowToStep",
            "name": "Tap the microphone button",
            "text": "Press the large orange microphone button on any screen",
            "image": "https://coraai.tech/static/images/step2-tap-mic.png"
        },
        {
            "@type": "HowToStep",
            "name": "Speak your expense",
            "text": "Say something like 'Spent 47 dollars on lumber at Home Depot for the Johnson job'",
            "image": "https://coraai.tech/static/images/step3-speak.png"
        },
        {
            "@type": "HowToStep",
            "name": "Confirm and save",
            "text": "CORA will categorize the expense and assign it to the correct job automatically",
            "image": "https://coraai.tech/static/images/step4-confirm.png"
        }
    ]
};

// Product Schema for Software Features
const productSchema = {
    "@context": "https://schema.org",
    "@type": "Product",
    "name": "CORA Construction Financial Management",
    "description": "AI-powered profit tracking and financial management for construction contractors",
    "brand": {
        "@type": "Brand",
        "name": "CORA"
    },
    "offers": {
        "@type": "AggregateOffer",
        "priceCurrency": "USD",
        "lowPrice": "47",
        "highPrice": "197",
        "availability": "https://schema.org/InStock"
    },
    "review": [
        {
            "@type": "Review",
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": "5",
                "bestRating": "5"
            },
            "author": {
                "@type": "Person",
                "name": "Mike Johnson",
                "jobTitle": "General Contractor"
            },
            "reviewBody": "CORA saved my business. I was losing money on jobs and didn't know until it was too late. Now I get alerts in real-time and can fix problems before they cost me thousands."
        },
        {
            "@type": "Review",
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": "5",
                "bestRating": "5"
            },
            "author": {
                "@type": "Person",
                "name": "Sarah Martinez",
                "jobTitle": "Construction Business Owner"
            },
            "reviewBody": "The voice input is a game-changer. I can track expenses right from the job site without taking off my gloves. Worth every penny."
        }
    ]
};

// Function to inject structured data into page
function injectStructuredData() {
    // Remove any existing structured data
    const existingScripts = document.querySelectorAll('script[type="application/ld+json"]');
    existingScripts.forEach(script => script.remove());
    
    // Determine which schemas to include based on page
    const schemas = [];
    const path = window.location.pathname;
    
    // Always include organization schema
    schemas.push(organizationSchema);
    
    // Page-specific schemas
    if (path === '/' || path === '/index.html') {
        schemas.push(localBusinessSchema);
        schemas.push(faqSchema);
        schemas.push(productSchema);
    } else if (path.includes('pricing')) {
        schemas.push(localBusinessSchema);
        schemas.push(productSchema);
    } else if (path.includes('features')) {
        schemas.push(localBusinessSchema);
        schemas.push(howToSchema);
    } else if (path.includes('how-it-works')) {
        schemas.push(howToSchema);
        schemas.push(faqSchema);
    }
    
    // Inject schemas
    schemas.forEach(schema => {
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.textContent = JSON.stringify(schema);
        document.head.appendChild(script);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', injectStructuredData);

// Export for use in other modules
window.CORAStructuredData = {
    localBusinessSchema,
    organizationSchema,
    faqSchema,
    howToSchema,
    productSchema,
    injectStructuredData
};