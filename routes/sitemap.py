"""
XML Sitemap Generation for SEO
Provides dynamic sitemap with all pages and priority settings
"""
from fastapi import APIRouter, Response
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

router = APIRouter()

# Define pages with their priorities and change frequencies
PAGES = [
    # High Priority Pages
    {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
    {"loc": "/features", "priority": "0.9", "changefreq": "monthly"},
    {"loc": "/pricing", "priority": "0.9", "changefreq": "monthly"},
    {"loc": "/how-it-works", "priority": "0.8", "changefreq": "monthly"},
    
    # User Pages
    {"loc": "/signup", "priority": "0.8", "changefreq": "yearly"},
    {"loc": "/login", "priority": "0.7", "changefreq": "yearly"},
    
    # Content Pages
    {"loc": "/reviews", "priority": "0.7", "changefreq": "weekly"},
    {"loc": "/contact", "priority": "0.6", "changefreq": "monthly"},
    {"loc": "/blog", "priority": "0.7", "changefreq": "weekly"},
    {"loc": "/about", "priority": "0.6", "changefreq": "monthly"},
    
    # Legal Pages
    {"loc": "/privacy", "priority": "0.5", "changefreq": "yearly"},
    {"loc": "/terms", "priority": "0.5", "changefreq": "yearly"},
    {"loc": "/security", "priority": "0.5", "changefreq": "yearly"},
    
    # Location-Specific Pages (for local SEO)
    {"loc": "/texas-contractors", "priority": "0.8", "changefreq": "monthly"},
    {"loc": "/florida-construction-software", "priority": "0.8", "changefreq": "monthly"},
    {"loc": "/california-contractor-tools", "priority": "0.8", "changefreq": "monthly"},
    {"loc": "/new-york-construction-profit-tracking", "priority": "0.8", "changefreq": "monthly"},
    
    # Feature-Specific Pages (for keyword targeting)
    {"loc": "/real-time-profit-tracking", "priority": "0.9", "changefreq": "monthly"},
    {"loc": "/voice-input-construction", "priority": "0.9", "changefreq": "monthly"},
    {"loc": "/ai-budget-alerts", "priority": "0.9", "changefreq": "monthly"},
    {"loc": "/mobile-job-costing", "priority": "0.9", "changefreq": "monthly"},
]

@router.get("/sitemap.xml", response_class=Response)
async def generate_sitemap():
    """Generate XML sitemap for search engines"""
    
    # Create root element
    urlset = ET.Element("urlset")
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Current timestamp
    lastmod = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    # Add each page to sitemap
    for page in PAGES:
        url = ET.SubElement(urlset, "url")
        
        # Location
        loc = ET.SubElement(url, "loc")
        loc.text = f"https://coraai.tech{page['loc']}"
        
        # Last modified
        lastmod_elem = ET.SubElement(url, "lastmod")
        lastmod_elem.text = lastmod
        
        # Change frequency
        changefreq = ET.SubElement(url, "changefreq")
        changefreq.text = page["changefreq"]
        
        # Priority
        priority = ET.SubElement(url, "priority")
        priority.text = page["priority"]
    
    # Convert to string
    xml_string = ET.tostring(urlset, encoding='unicode')
    
    # Add XML declaration
    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_string
    
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={
            "Cache-Control": "public, max-age=3600"  # Cache for 1 hour
        }
    )

@router.get("/robots.txt", response_class=Response)
async def robots_txt():
    """Generate robots.txt file"""
    content = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /dashboard/
Disallow: /static/js/
Disallow: /static/css/

# Sitemap location
Sitemap: https://coraai.tech/sitemap.xml

# Crawl delay for respectful crawling
Crawl-delay: 1
"""
    return Response(
        content=content,
        media_type="text/plain",
        headers={
            "Cache-Control": "public, max-age=86400"  # Cache for 1 day
        }
    )