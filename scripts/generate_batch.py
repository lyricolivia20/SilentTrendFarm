#!/usr/bin/env python3
"""
Batch content generator - Creates multiple SEO-optimized posts with affiliate links.
"""
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from content_generator import generate_and_save

# Hot trend topics with affiliate integration
TOPICS = [
    "Cloud GPUs for AI Training: RunPod vs Lambda vs Vast.ai",
    "Flux LoRA Fine-Tuning on RunPod: A Complete Setup Guide",
    "Jasper AI vs ChatGPT for Affiliate Marketing Content",
    "Building an AI Content Pipeline: From Idea to Published Post",
]

# All affiliates to embed
AFFILIATES = ["runpod", "bluehost", "codecademy", "jasper", "creatify"]

def main():
    print(f"Generating {len(TOPICS)} posts with affiliates: {', '.join(AFFILIATES)}\n")
    
    generated = []
    for i, topic in enumerate(TOPICS, 1):
        print(f"[{i}/{len(TOPICS)}] Generating: {topic}")
        try:
            filepath = generate_and_save(topic, affiliates=AFFILIATES)
            generated.append(filepath)
            print(f"  ✓ Saved: {filepath}\n")
        except Exception as e:
            print(f"  ✗ Error: {e}\n")
    
    print(f"\n{'='*50}")
    print(f"Generated {len(generated)}/{len(TOPICS)} posts:")
    for path in generated:
        print(f"  - {path}")

if __name__ == "__main__":
    main()
