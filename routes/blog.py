"""
Blog Routes for Content Marketing
Handles blog posts targeting high-value keywords
"""
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse
import os

router = APIRouter()
# Use centralized templates from app.state.templates set in app.py

# Blog post data (in production, this would come from a database)
BLOG_POSTS = [
    {
        "slug": "5-budget-killers-every-contractor-misses",
        "title": "5 Budget Killers Every Contractor Misses",
        "meta_description": "Discover the hidden expenses that destroy construction profits and how to catch them before they cost you thousands.",
        "author": "CORA Team",
        "date": "2025-08-01",
        "read_time": "7 min read",
        "category": "Profit Management",
        "featured": True,
        "excerpt": "Small expenses compound into massive losses. Here are the 5 most common budget killers that contractors miss until it's too late.",
        "keywords": "construction budget overrun, hidden construction costs, contractor profit loss"
    },
    {
        "slug": "real-time-tracking-saved-my-construction-business",
        "title": "How Real-Time Tracking Saved My Construction Business",
        "meta_description": "A contractor's story of how switching from spreadsheets to real-time profit tracking prevented bankruptcy and increased margins by 30%.",
        "author": "Mike Thompson",
        "date": "2025-07-28",
        "read_time": "5 min read",
        "category": "Success Stories",
        "featured": True,
        "excerpt": "I was losing $3-5k per job and didn't know why. Here's how real-time tracking changed everything.",
        "keywords": "construction success story, real-time job costing, construction profit tracking"
    },
    {
        "slug": "voice-input-construction-game-changer",
        "title": "Why Voice Input is a Game-Changer for Construction",
        "meta_description": "Track expenses with muddy hands, while driving, or on a noisy job site. Voice input solves the #1 reason contractors miss expenses.",
        "author": "CORA Team",
        "date": "2025-07-25",
        "read_time": "6 min read",
        "category": "Technology",
        "featured": False,
        "excerpt": "Can't use your phone with gloves on? Hands covered in concrete? Voice input lets you track expenses instantly, anywhere.",
        "keywords": "voice input construction, hands-free expense tracking, construction technology"
    },
    {
        "slug": "construction-cash-flow-crisis-solutions",
        "title": "Construction Cash Flow Crisis? Here's Your Survival Guide",
        "meta_description": "Practical solutions for contractors facing cash flow problems. Learn how to predict, prevent, and manage cash flow crises.",
        "author": "CORA Team",
        "date": "2025-07-20",
        "read_time": "10 min read",
        "category": "Financial Management",
        "featured": False,
        "excerpt": "When cash flow dries up, your business dies. Here's how to see problems coming and fix them before disaster strikes.",
        "keywords": "construction cash flow, contractor financial crisis, cash flow management"
    }
]

@router.get("/blog", response_class=HTMLResponse)
async def blog_index(request: Request):
    """Blog index page showing all posts"""
    return request.app.state.templates.TemplateResponse("blog/index.html", {
        "request": request,
        "posts": BLOG_POSTS,
        "title": "Construction Business Blog | CORA",
        "description": "Expert insights on construction profit tracking, cash flow management, and technology for contractors.",
        "keywords": "construction blog, contractor tips, construction management"
    })

@router.get("/blog/{slug}", response_class=HTMLResponse)
async def blog_post(request: Request, slug: str):
    """Individual blog post page"""
    # Find the post
    post = next((p for p in BLOG_POSTS if p["slug"] == slug), None)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    
    # Get related posts (in production, this would be smarter)
    related_posts = [p for p in BLOG_POSTS if p["slug"] != slug][:3]
    
    return request.app.state.templates.TemplateResponse(f"blog/{slug}.html", {
        "request": request,
        "post": post,
        "related_posts": related_posts,
        "title": f"{post['title']} | CORA Blog",
        "description": post["meta_description"],
        "keywords": post["keywords"]
    })

@router.get("/blog/category/{category}", response_class=HTMLResponse)
async def blog_category(request: Request, category: str):
    """Blog posts by category"""
    # Filter posts by category
    category_posts = [p for p in BLOG_POSTS if p["category"].lower().replace(" ", "-") == category.lower()]
    
    if not category_posts:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return request.app.state.templates.TemplateResponse("blog/category.html", {
        "request": request,
        "posts": category_posts,
        "category": category.replace("-", " ").title(),
        "title": f"{category.replace('-', ' ').title()} | CORA Blog",
        "description": f"Read our latest articles about {category.replace('-', ' ')} for construction contractors.",
        "keywords": f"construction {category.replace('-', ' ')}, contractor {category.replace('-', ' ')}"
    })