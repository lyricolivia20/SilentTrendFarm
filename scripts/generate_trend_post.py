#!/usr/bin/env python3
"""
Main automation script - Fetches trending topic and generates a new post.
This is the entry point for the GitHub Actions workflow.
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from trend_fetcher import select_best_topic, get_trending_topics
from content_generator import generate_and_save

def log(message: str):
    """Print timestamped log message."""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")

def main():
    """Main entry point for the automation."""
    log("Starting SilentTrendFarm content generation...")
    
    # Step 1: Fetch trending topic
    log("Fetching trending topics...")
    try:
        # First try with niche filter
        topic = select_best_topic(filter_niche=True)
        log(f"Selected topic (niche-filtered): {topic}")
    except Exception as e:
        log(f"Warning: Niche filter failed ({e}), trying without filter...")
        try:
            topic = select_best_topic(filter_niche=False)
            log(f"Selected topic (unfiltered): {topic}")
        except Exception as e2:
            log(f"Error fetching trends: {e2}")
            topic = "Best Tech Gadgets 2025"
            log(f"Using fallback topic: {topic}")
    
    # Step 2: Generate content
    log(f"Generating content for: {topic}")
    try:
        filepath = generate_and_save(topic)
        log(f"Content saved to: {filepath}")
    except Exception as e:
        log(f"Error generating content: {e}")
        sys.exit(1)
    
    # Step 3: Verify the file was created
    if not Path(filepath).exists():
        log(f"Error: Generated file not found at {filepath}")
        sys.exit(1)
    
    log("Content generation complete!")
    
    # Output for GitHub Actions
    print(f"::set-output name=topic::{topic}")
    print(f"::set-output name=filepath::{filepath}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
