#!/usr/bin/env python3
"""
Content Generator - Creates SEO-optimized articles using OpenAI
with automatic affiliate link injection and schema-ready structure.
"""
import os
import re
import json
import hashlib
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

load_dotenv()

# Affiliate configuration - loaded from env or defaults
AMAZON_TAG = os.getenv("AMAZON_AFFILIATE_TAG", "youraffiliate-20")
CLICKBANK_ID = os.getenv("CLICKBANK_ID", "yourclickbank")

# Link cloaking - use internal redirects to mask affiliate URLs
USE_LINK_CLOAKING = os.getenv("USE_LINK_CLOAKING", "true").lower() == "true"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def cloak_affiliate_link(url: str, link_text: str) -> str:
    """
    Generate a cloaked internal redirect URL for affiliate links.
    This makes links look like internal pages: /go/product-name
    """
    if not USE_LINK_CLOAKING:
        return url
    
    # Create a clean slug from the link text
    slug = re.sub(r'[^\w\s-]', '', link_text.lower())
    slug = re.sub(r'[-\s]+', '-', slug).strip('-')
    
    # Use hash suffix for uniqueness
    url_hash = hashlib.md5(url.encode()).hexdigest()[:6]
    
    return f"/go/{slug}-{url_hash}"

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug."""
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    return slug.strip('-')

def inject_affiliate_links(content: str, topic: str) -> str:
    """
    Post-process content to inject affiliate links.
    Scans for Amazon URLs and product mentions, adds tracking tags.
    """
    # Add affiliate tag to any Amazon URLs
    amazon_pattern = r'(https?://(?:www\.)?amazon\.com/[^\s\)]+)'
    def add_amazon_tag(match):
        url = match.group(1)
        if '?' in url:
            if 'tag=' not in url:
                return f"{url}&tag={AMAZON_TAG}"
            return url
        return f"{url}?tag={AMAZON_TAG}"
    
    content = re.sub(amazon_pattern, add_amazon_tag, content)
    
    # Replace placeholder links
    content = content.replace('[Amazon Link]', f'https://www.amazon.com/s?k={topic.replace(" ", "+")}&tag={AMAZON_TAG}')
    content = content.replace('[ClickBank Link]', f'https://{CLICKBANK_ID}.clickbank.net')
    
    return content

def generate_content(trend_topic: str, model: str = "gpt-4"):
    """
    Generate a blog post about the trending topic using OpenAI.
    
    Args:
        trend_topic: The topic to write about
        model: OpenAI model to use (gpt-4, gpt-4-turbo, gpt-3.5-turbo)
    
    Returns:
        Tuple of (slug, full_markdown_content)
    """
    prompt = f"""Write a technical, evergreen article about: "{trend_topic}"

TARGET AUDIENCE: Developers, AI enthusiasts, automation builders, tech-savvy creators

CRITICAL TONE GUIDELINES:
- Write for a technical audience who values substance over hype
- Use a slightly informal, developer-friendly tone (like Hacker News or dev.to)
- Include specific technical details, use cases, and practical examples
- NEVER use time-sensitive language like "this year", "2024", "2025", "recently", "new", "latest", "trending"
- NEVER use clickbait phrases like "BEST EVER", "YOU WON'T BELIEVE", "MUST-HAVE", "GAME-CHANGER"
- Be honest about limitations, learning curves, and pricing
- Include code snippets or command examples where relevant (use markdown code blocks)
- The article should read like it's from an established tech publication

Requirements:
- Length: 1000-1500 words
- Tone: Technical, practical, no-nonsense
- NO dates, NO year references, NO hype language
- Include specific tool names, features, and use cases
- Mention pricing tiers where relevant (free tier, pro pricing, etc.)

Structure (use these H2 headings):
## The Signal
What this is, why it matters, and who should care. Cut straight to the point.

## Key Features
List 5-7 specific features or capabilities with brief technical explanations.
Use bullet points with bold feature names.

## Use Cases
3-4 practical scenarios where this tool/approach excels.
Include specific workflows or integrations.

## Limitations & Trade-offs
Honest assessment of downsides, learning curve, pricing concerns.
What alternatives exist and when to use them instead.

## Getting Started
Quick-start guide or key steps to begin.
Include a code snippet or command if applicable.

## The Verdict
Who this is for, who should skip it, and key takeaways.

Output as JSON:
{{
  "title": "Clear, technical title - NO year, NO 'best', NO clickbait (50-60 chars)",
  "description": "Technical meta description for developers/creators (150-160 chars)",
  "tags": ["ai-tools", "automation", "python", etc - use lowercase with hyphens],
  "content": "Full markdown content with H2 sections and code blocks where relevant",
  "products": [
    {{"name": "Tool/Product Name", "asin": "B08XXXXX" or null, "url": "https://tool-website.com" or null}}
  ]
}}"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a senior technical writer at a developer-focused publication. You write for an audience of developers, AI enthusiasts, and automation builders. Your tone is technical but accessible, like Hacker News or dev.to. You include specific details, code examples, and honest assessments. NEVER use dates, years, 'new', 'latest', 'trending', or hype language. Your content is evergreen and practical. Always output valid JSON."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=3000,
        temperature=0.7
    )

    raw_content = response.choices[0].message.content.strip()
    
    # Extract JSON from response (handle markdown code blocks)
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_content)
    if json_match:
        raw_content = json_match.group(1)
    
    # Parse JSON
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        # Fallback if not valid JSON
        data = {
            "title": f"A Complete Guide to {trend_topic}",
            "description": f"Everything you need to know about {trend_topic}. Our comprehensive guide covers features, pros/cons, and buying advice.",
            "tags": [slugify(trend_topic), "guide"],
            "content": raw_content,
            "products": []
        }
    
    # Generate slug
    slug = slugify(data["title"])
    
    # Process affiliate links in content
    content = inject_affiliate_links(data.get("content", ""), trend_topic)
    
    # Build affiliate links array with optional cloaking
    search_url = f"https://www.amazon.com/s?k={quote_plus(trend_topic)}&tag={AMAZON_TAG}"
    
    # Store both display URL and actual URL for redirect generation
    affiliate_links = []
    redirect_map = {}  # For generating redirect rules
    
    main_link_text = "View Options"
    cloaked_url = cloak_affiliate_link(search_url, main_link_text)
    affiliate_links.append({"text": main_link_text, "url": cloaked_url})
    redirect_map[cloaked_url] = search_url
    
    # Add specific product links if ASINs provided
    for product in data.get("products", []):
        if product.get("asin"):
            product_url = f"https://www.amazon.com/dp/{product['asin']}?tag={AMAZON_TAG}"
            link_text = f"Check {product['name']}"
            cloaked = cloak_affiliate_link(product_url, link_text)
            affiliate_links.append({"text": link_text, "url": cloaked})
            redirect_map[cloaked] = product_url
    
    # Build frontmatter
    tags_yaml = "\n".join([f'  - "{tag}"' for tag in data.get("tags", [])])
    links_yaml = "\n".join([f'  - text: "{link["text"]}"\n    url: "{link["url"]}"' for link in affiliate_links])
    
    frontmatter = f"""---
title: "{data['title']}"
description: "{data['description']}"
pubDate: {datetime.now().strftime('%Y-%m-%d')}
updatedDate: {datetime.now().strftime('%Y-%m-%d')}
heroImage: /images/placeholder.jpg
tags:
{tags_yaml}
affiliateLinks:
{links_yaml}
---

"""
    
    full_content = frontmatter + content
    
    return slug, full_content, redirect_map

def save_redirect_map(redirect_map: dict, project_root: Path = None):
    """Save redirect map to JSON file for Netlify redirects generation."""
    if project_root is None:
        project_root = Path(__file__).parent.parent
    
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    
    redirects_file = data_dir / "redirects.json"
    
    # Load existing redirects and merge
    existing = {}
    if redirects_file.exists():
        existing = json.loads(redirects_file.read_text(encoding="utf-8"))
    
    existing.update(redirect_map)
    
    redirects_file.write_text(json.dumps(existing, indent=2), encoding="utf-8")
    
    # Also generate the _redirects file for Netlify
    public_dir = project_root / "public"
    public_dir.mkdir(exist_ok=True)
    
    lines = [
        "# Affiliate link redirects - auto-generated",
        "# Do not edit manually",
        ""
    ]
    for cloaked_path, actual_url in existing.items():
        lines.append(f"{cloaked_path}  {actual_url}  302")
    
    (public_dir / "_redirects").write_text("\n".join(lines), encoding="utf-8")

def generate_and_save(trend_topic: str, output_dir: str = None) -> str:
    """
    Generate content and save to file.
    
    Args:
        trend_topic: Topic to write about
        output_dir: Directory to save the markdown file
    
    Returns:
        Path to the generated file
    """
    project_root = Path(__file__).parent.parent
    
    if output_dir is None:
        output_dir = project_root / "src" / "content" / "posts"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    slug, content, redirect_map = generate_content(trend_topic)
    
    # Save redirect map for link cloaking
    if redirect_map:
        save_redirect_map(redirect_map, project_root)
    
    # Ensure unique filename
    filepath = output_dir / f"{slug}.md"
    if filepath.exists():
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filepath = output_dir / f"{slug}-{timestamp}.md"
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    
    return str(filepath)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate SEO content for a topic")
    parser.add_argument("topic", nargs="?", default="Wireless Earbuds", help="Topic to write about")
    parser.add_argument("--model", default="gpt-4", help="OpenAI model to use")
    parser.add_argument("--output", "-o", help="Output directory for markdown file")
    parser.add_argument("--json", action="store_true", help="Output as JSON instead of saving file")
    args = parser.parse_args()
    
    if args.json:
        slug, content, redirects = generate_content(args.topic, model=args.model)
        print(json.dumps({"slug": slug, "content": content, "redirects": redirects}))
    else:
        filepath = generate_and_save(args.topic, args.output)
        print(f"Generated: {filepath}")
