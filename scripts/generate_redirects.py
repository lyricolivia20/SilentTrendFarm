#!/usr/bin/env python3
"""
Generate Netlify _redirects file for affiliate link cloaking.
Scans all markdown posts for affiliate links and creates redirect rules.
"""
import os
import re
import json
from pathlib import Path

def extract_affiliate_links(content_dir: Path) -> dict:
    """
    Extract all affiliate links from markdown frontmatter.
    Returns a dict mapping cloaked URLs to actual affiliate URLs.
    """
    redirects = {}
    
    for md_file in content_dir.glob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        
        # Extract frontmatter
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        if not frontmatter_match:
            continue
        
        frontmatter = frontmatter_match.group(1)
        
        # Find affiliateLinks section
        links_match = re.search(r'affiliateLinks:\s*\n((?:\s+-.*\n?)+)', frontmatter)
        if not links_match:
            continue
        
        links_section = links_match.group(1)
        
        # Parse each link entry
        current_text = None
        current_url = None
        
        for line in links_section.split('\n'):
            text_match = re.search(r'text:\s*["\']?([^"\']+)["\']?', line)
            url_match = re.search(r'url:\s*["\']?([^"\']+)["\']?', line)
            
            if text_match:
                current_text = text_match.group(1)
            if url_match:
                current_url = url_match.group(1)
            
            # If we have both, check if it's a cloaked URL
            if current_text and current_url:
                if current_url.startswith('/go/'):
                    # This is a cloaked URL - we need to find the actual URL
                    # For now, store it; actual URL will be in a separate data file
                    pass
                current_text = None
                current_url = None
    
    return redirects

def load_redirect_map(data_file: Path) -> dict:
    """Load the redirect map from the data file."""
    if data_file.exists():
        return json.loads(data_file.read_text(encoding="utf-8"))
    return {}

def generate_redirects_file(output_dir: Path, redirect_map: dict):
    """
    Generate Netlify _redirects file.
    Format: /go/slug  https://actual-url.com  302
    """
    redirects_file = output_dir / "_redirects"
    
    lines = [
        "# Affiliate link redirects - auto-generated",
        "# Do not edit manually",
        ""
    ]
    
    for cloaked_path, actual_url in redirect_map.items():
        # Use 302 (temporary) redirect to avoid caching issues
        lines.append(f"{cloaked_path}  {actual_url}  302")
    
    redirects_file.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated {len(redirect_map)} redirects to {redirects_file}")

def main():
    project_root = Path(__file__).parent.parent
    content_dir = project_root / "src" / "content" / "posts"
    public_dir = project_root / "public"
    data_file = project_root / "data" / "redirects.json"
    
    # Ensure public dir exists
    public_dir.mkdir(exist_ok=True)
    
    # Load existing redirect map
    redirect_map = load_redirect_map(data_file)
    
    if redirect_map:
        generate_redirects_file(public_dir, redirect_map)
    else:
        print("No redirect map found. Run content generator first.")

if __name__ == "__main__":
    main()
