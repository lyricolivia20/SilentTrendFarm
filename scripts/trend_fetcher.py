#!/usr/bin/env python3
"""
Trend Fetcher - Fetches trending AI/tech topics from multiple sources
with niche filtering and history tracking to avoid repeats.
"""
import os
import json
import requests
from pathlib import Path
from datetime import datetime
from pytrends.request import TrendReq

# AI/Tech focused keywords for trend discovery
AI_TECH_KEYWORDS = [
    # AI & ML
    "AI", "artificial intelligence", "machine learning", "GPT", "LLM",
    "ChatGPT", "Claude", "Gemini", "Llama", "Mistral", "neural network",
    "deep learning", "transformer", "diffusion", "stable diffusion",
    "midjourney", "DALL-E", "AI art", "AI video", "AI music",
    
    # Automation & Dev Tools
    "automation", "n8n", "zapier", "make.com", "workflow",
    "Python", "JavaScript", "API", "GitHub", "VS Code", "Cursor",
    "Copilot", "code assistant", "developer tools", "devops",
    
    # SaaS & Productivity
    "Notion", "Obsidian", "Canva", "Figma", "productivity",
    "SaaS", "no-code", "low-code", "Airtable", "Supabase",
    
    # Hardware & Tech
    "GPU", "NVIDIA", "AMD", "Apple", "M3", "M4", "MacBook",
    "smart home", "IoT", "Raspberry Pi", "Arduino"
]

# Seed topics for AI/tech content (evergreen fallbacks)
AI_TECH_SEED_TOPICS = [
    "AI Writing Tools for Content Creators",
    "Python Automation Scripts for Developers",
    "No-Code AI Tools for Beginners",
    "Best AI Image Generators",
    "Workflow Automation with n8n",
    "AI Coding Assistants Compared",
    "Local LLM Setup Guide",
    "AI Tools for Video Editing",
    "Notion AI Features",
    "GitHub Copilot Alternatives",
    "AI Voice Cloning Tools",
    "Stable Diffusion Workflows",
    "AI Research Paper Summarizers",
    "Smart Home Automation Ideas",
    "AI-Powered SEO Tools"
]

HISTORY_FILE = Path(__file__).parent / "topic_history.json"

def load_history():
    """Load previously used topics to avoid repeats."""
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"topics": [], "last_updated": None}

def save_history(history):
    """Save topic history."""
    history["last_updated"] = datetime.now().isoformat()
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def is_ai_tech_relevant(topic: str) -> bool:
    """Check if topic matches AI/tech keywords."""
    topic_lower = topic.lower()
    return any(kw.lower() in topic_lower for kw in AI_TECH_KEYWORDS)

def get_trending_topics(filter_niche: bool = False, max_results: int = 10):
    """
    Fetch trending topics from Google Trends.
    
    Args:
        filter_niche: If True, only return topics matching NICHES
        max_results: Maximum number of topics to return
    
    Returns:
        List of trending topics with momentum scores
    """
    pytrends = TrendReq(hl='en-US', tz=360)
    history = load_history()
    used_topics = set(history.get("topics", []))
    
    results = []
    
    # Get today's trending searches
    try:
        trending_df = pytrends.trending_searches(pn='united_states')
        if not trending_df.empty:
            for idx, row in trending_df.iterrows():
                topic = row[0]
                if topic in used_topics:
                    continue
                if filter_niche and not is_ai_tech_relevant(topic):
                    continue
                results.append({
                    "topic": topic,
                    "source": "trending_now",
                    "rank": idx + 1
                })
                if len(results) >= max_results:
                    break
    except Exception as e:
        print(f"Warning: Could not fetch trending searches: {e}")
    
    # If not enough results, try related queries for AI/tech keywords
    if len(results) < max_results and filter_niche:
        ai_keywords = ["AI tools", "Python automation", "ChatGPT", "machine learning", "workflow automation"]
        for keyword in ai_keywords:
            try:
                pytrends.build_payload([keyword], timeframe='now 7-d')
                related = pytrends.related_queries()
                if keyword in related and related[keyword]['rising'] is not None:
                    rising_df = related[keyword]['rising']
                    for idx, row in rising_df.head(3).iterrows():
                        topic = row['query']
                        if topic not in used_topics:
                            results.append({
                                "topic": topic,
                                "source": f"rising_{keyword.replace(' ', '_')}",
                                "rank": idx + 1
                            })
            except:
                continue
            if len(results) >= max_results:
                break
    
    # Fallback to curated AI/tech seed topics if nothing found
    if not results:
        import random
        available_seeds = [t for t in AI_TECH_SEED_TOPICS if t not in used_topics]
        if available_seeds:
            selected = random.choice(available_seeds)
            results.append({"topic": selected, "source": "seed_topic", "rank": 0})
        else:
            # All seeds used, pick random one anyway
            results.append({"topic": random.choice(AI_TECH_SEED_TOPICS), "source": "seed_topic_repeat", "rank": 0})
    
    return results

def select_best_topic(filter_niche: bool = True) -> str:
    """
    Select the best trending topic and record it in history.
    
    Returns:
        The selected topic string
    """
    topics = get_trending_topics(filter_niche=filter_niche)
    
    if not topics:
        import random
        return random.choice(AI_TECH_SEED_TOPICS)
    
    # Select the top result
    selected = topics[0]["topic"]
    
    # Update history
    history = load_history()
    history["topics"].append(selected)
    # Keep only last 100 topics
    history["topics"] = history["topics"][-100:]
    save_history(history)
    
    return selected

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch trending topics")
    parser.add_argument("--list", action="store_true", help="List multiple topics")
    parser.add_argument("--no-filter", action="store_true", help="Don't filter by niche")
    parser.add_argument("--count", type=int, default=10, help="Number of topics to list")
    args = parser.parse_args()
    
    if args.list:
        topics = get_trending_topics(filter_niche=not args.no_filter, max_results=args.count)
        print(json.dumps({"topics": topics}, indent=2))
    else:
        trend = select_best_topic(filter_niche=not args.no_filter)
        print(json.dumps({"trend": trend}))
