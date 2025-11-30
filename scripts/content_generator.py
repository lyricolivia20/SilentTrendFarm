#!/usr/bin/env python3
"""
Content Generator - Creates SEO-optimized articles using OpenAI
with automatic affiliate link injection and schema-ready structure.
"""
import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path

load_dotenv()

# Affiliate configuration - loaded from env or defaults
AMAZON_TAG = os.getenv("AMAZON_AFFILIATE_TAG", "youraffiliate-20")
CLICKBANK_ID = os.getenv("CLICKBANK_ID", "yourclickbank")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    prompt = f"""Write a comprehensive, SEO-optimized blog post about: "{trend_topic}"

Requirements:
- Length: 800-1200 words
- Tone: Informative, engaging, trustworthy
- If it's a product, write a review. Otherwise, write an informative guide.

Structure (use these exact H2 headings):
## Introduction
Brief intro explaining what this is and why it's trending.

## Key Features and Benefits
List 4-6 main features/benefits with brief explanations.

## Pros and Cons
Create a balanced pros/cons list.

## Buying Guide
What to look for when purchasing, price ranges, where to buy.
Include a call-to-action with [Amazon Link] placeholder.

## Frequently Asked Questions
3-4 common questions with answers.

## Conclusion
Summary and final recommendation with [Amazon Link] placeholder.

Output as JSON:
{{
  "title": "SEO-friendly title (50-60 chars)",
  "description": "Meta description (150-160 chars)",
  "tags": ["tag1", "tag2", "tag3"],
  "content": "Full markdown content with H2 sections",
  "products": [
    {{"name": "Product Name", "asin": "B08XXXXX" or null}}
  ]
}}"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are an expert content writer specializing in SEO-optimized product reviews and trend articles. Always output valid JSON."},
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
            "title": f"Complete Guide to {trend_topic} in {datetime.now().year}",
            "description": f"Discover everything about {trend_topic}. Our comprehensive guide covers features, pros/cons, and where to buy.",
            "tags": [slugify(trend_topic), "review", "guide"],
            "content": raw_content,
            "products": []
        }
    
    # Generate slug
    slug = slugify(data["title"])
    
    # Process affiliate links in content
    content = inject_affiliate_links(data.get("content", ""), trend_topic)
    
    # Build affiliate links array
    search_url = f"https://www.amazon.com/s?k={trend_topic.replace(' ', '+')}&tag={AMAZON_TAG}"
    affiliate_links = [
        {"text": "Shop on Amazon", "url": search_url}
    ]
    
    # Add specific product links if ASINs provided
    for product in data.get("products", []):
        if product.get("asin"):
            affiliate_links.append({
                "text": f"Buy {product['name']}",
                "url": f"https://www.amazon.com/dp/{product['asin']}?tag={AMAZON_TAG}"
            })
    
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
    
    return slug, full_content

def generate_and_save(trend_topic: str, output_dir: str = None) -> str:
    """
    Generate content and save to file.
    
    Args:
        trend_topic: Topic to write about
        output_dir: Directory to save the markdown file
    
    Returns:
        Path to the generated file
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "src" / "content" / "posts"
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    slug, content = generate_content(trend_topic)
    
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
        slug, content = generate_content(args.topic, model=args.model)
        print(json.dumps({"slug": slug, "content": content}))
    else:
        filepath = generate_and_save(args.topic, args.output)
        print(f"Generated: {filepath}")
