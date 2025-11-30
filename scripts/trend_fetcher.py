#!/usr/bin/env python3
"""
Trend Fetcher - Fetches trending topics from Google Trends
with niche filtering and history tracking to avoid repeats.
"""
import os
import json
from pathlib import Path
from datetime import datetime
from pytrends.request import TrendReq

# Configurable niches to filter trends
NICHES = [
    "tech", "gadgets", "electronics", "smartphone", "laptop", "tablet",
    "fitness", "health", "wellness", "workout", "gym",
    "home", "kitchen", "appliances", "furniture",
    "gaming", "console", "pc", "video game",
    "fashion", "clothing", "shoes", "accessories",
    "beauty", "skincare", "makeup", "cosmetics"
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

def is_niche_relevant(topic: str) -> bool:
    """Check if topic matches configured niches."""
    topic_lower = topic.lower()
    return any(niche in topic_lower for niche in NICHES)

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
                if filter_niche and not is_niche_relevant(topic):
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
    
    # If not enough results, try related queries for niche keywords
    if len(results) < max_results and filter_niche:
        for niche in NICHES[:5]:  # Try first 5 niches
            try:
                pytrends.build_payload([niche], timeframe='now 7-d')
                related = pytrends.related_queries()
                if niche in related and related[niche]['rising'] is not None:
                    rising_df = related[niche]['rising']
                    for idx, row in rising_df.head(3).iterrows():
                        topic = row['query']
                        if topic not in used_topics:
                            results.append({
                                "topic": topic,
                                "source": f"rising_{niche}",
                                "rank": idx + 1
                            })
            except:
                continue
            if len(results) >= max_results:
                break
    
    # Fallback topics if nothing found
    if not results:
        fallbacks = [
            "Wireless Earbuds 2025",
            "Smart Home Devices",
            "Fitness Tracker Watch",
            "Portable Charger",
            "Robot Vacuum Cleaner"
        ]
        for fb in fallbacks:
            if fb not in used_topics:
                results.append({"topic": fb, "source": "fallback", "rank": 0})
                break
    
    return results

def select_best_topic(filter_niche: bool = True) -> str:
    """
    Select the best trending topic and record it in history.
    
    Returns:
        The selected topic string
    """
    topics = get_trending_topics(filter_niche=filter_niche)
    
    if not topics:
        return "Best Tech Gadgets 2025"
    
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
