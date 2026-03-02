#!/usr/bin/env python3
"""
YouTube Learning Plugin for OpenClaw Agents
Downloads, transcribes, and extracts knowledge from YouTube videos

Author: D3n14l0f53rv1c3
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path.home() / "knowledge" / "youtube_learning"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

def download_video_info(url):
    """Download video metadata without downloading the video"""
    cmd = ["yt-dlp", "--dump-json", "--no-download", url]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return json.loads(result.stdout)
        return None
    except Exception:
        return None

def download_transcript(url):
    """Download video transcript if available"""
    output_dir = KNOWLEDGE_DIR / "transcripts"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "yt-dlp",
        "--write-auto-sub",
        "--sub-lang", "en,de",
        "--skip-download",
        "-o", str(output_dir / "%(title)s.%(ext)s"),
        url
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=60)
        return True
    except Exception:
        return False

def extract_topics(video_info):
    """Extract topics from video metadata"""
    topics = []
    if not video_info:
        return topics
    
    title = video_info.get("title", "").lower()
    description = video_info.get("description", "").lower()
    tags = video_info.get("tags", [])
    text = f"{title} {description} {' '.join(tags)}"
    
    # Topic categories
    categories = {
        "security": ["hack", "security", "pentest", "wifi", "bluetooth", "sdr", 
                     "aircrack", "kismet", "hashcat", "exploit", "vulnerability"],
        "dev": ["python", "javascript", "rust", "golang", "arduino", "esp32"],
        "hardware": ["esp32", "arduino", "raspberry", "sdr", "lora", "meshtastic"],
        "ai": ["machine learning", "ai", "neural", "llm", "gpt", "transformer"],
        "finance": ["trading", "crypto", "bitcoin", "stock", "market"],
    }
    
    for category, keywords in categories.items():
        for kw in keywords:
            if kw in text:
                topics.append(f"{category}:{kw}")
    
    return list(set(topics))

def save_learning(url, video_info, topics):
    """Save learning to knowledge base"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    learning = {
        "timestamp": timestamp,
        "url": url,
        "title": video_info.get("title", "Unknown"),
        "channel": video_info.get("uploader", "Unknown"),
        "duration": video_info.get("duration", 0),
        "topics": topics,
        "description": video_info.get("description", "")[:500],
    }
    
    # Save JSON
    json_file = KNOWLEDGE_DIR / f"learning_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(learning, f, indent=2)
    
    # Save Markdown
    md_file = KNOWLEDGE_DIR / f"learning_{timestamp}.md"
    with open(md_file, "w") as f:
        f.write(f"# YouTube Learning - {timestamp}\n\n")
        f.write(f"**URL:** {url}\n\n")
        f.write(f"**Title:** {learning['title']}\n\n")
        f.write(f"**Channel:** {learning['channel']}\n\n")
        f.write(f"**Duration:** {learning['duration']}s\n\n")
        f.write(f"**Topics:** {', '.join(topics)}\n\n")
        f.write(f"**Description:**\n\n{learning['description']}\n")
    
    return json_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 learn_from_youtube.py <youtube_url>")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print(f"=== YOUTUBE LEARNING ===")
    print(f"URL: {url}")
    
    video_info = download_video_info(url)
    if not video_info:
        print("Failed to download video info")
        sys.exit(1)
    
    print(f"Title: {video_info.get('title', 'Unknown')}")
    print(f"Channel: {video_info.get('uploader', 'Unknown')}")
    print(f"Duration: {video_info.get('duration', 0)}s")
    
    topics = extract_topics(video_info)
    print(f"Topics: {topics}")
    
    output_file = save_learning(url, video_info, topics)
    print(f"Saved: {output_file}")
    
    if download_transcript(url):
        print("Transcript downloaded")
    
    print("=== LEARNING COMPLETE ===")

if __name__ == "__main__":
    main()
