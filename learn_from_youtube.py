#!/usr/bin/env python3
"""
YouTube Learning Plugin for OpenClaw
Downloads video metadata, transcripts, and extracts knowledge

Author: D3n14l0f53rv1c3
"""

import os
import sys
import json
import subprocess
import re
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
    except Exception as e:
        print(f"Error downloading video info: {e}")
        return None

def get_transcript(url):
    """
    Download video transcript using youtube-transcript-api
    Returns transcript text and language
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        
        # Extract video ID
        if "v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in url:
            video_id = url.split("youtu.be/")[-1].split("?")[0]
        else:
            video_id = url.split("/")[-1]
        
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        
        # Try to get transcript (manual first, then auto-generated)
        transcript_obj = None
        language = None
        
        # Priority: manual English > auto English > manual German > auto German
        for lang in ['en', 'de']:
            try:
                transcript_obj = transcript_list.find_transcript([lang])
                language = lang
                break
            except:
                try:
                    transcript_obj = transcript_list.find_generated_transcript([lang])
                    language = f"a.{lang}"
                    break
                except:
                    continue
        
        if transcript_obj:
            result = transcript_obj.fetch()
            # Extract text from snippets
            text = ' '.join([snippet.text for snippet in result.snippets])
            # Clean up (remove music markers, etc.)
            text = re.sub(r'\[.*?\]', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text, language
        
        return None, None
        
    except ImportError:
        print("youtube-transcript-api not installed, falling back to yt-dlp")
        return get_transcript_ytdlp(url)
    except Exception as e:
        print(f"Error getting transcript: {e}")
        return None, None

def get_transcript_ytdlp(url):
    """Fallback: Download transcript using yt-dlp"""
    output_dir = KNOWLEDGE_DIR / "transcripts"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        "yt-dlp",
        "--write-auto-subs",
        "--write-subs",
        "--sub-lang", "en,de",
        "--skip-download",
        "--sub-format", "vtt",
        "-o", str(output_dir / "%(id)s.%(ext)s"),
        url
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, timeout=60)
        
        # Find the downloaded subtitle file
        if "v=" in url:
            video_id = url.split("v=")[-1].split("&")[0]
        else:
            video_id = url.split("/")[-1]
        
        for lang in ["en", "de", "a.en", "a.de"]:
            vtt_file = output_dir / f"{video_id}.{lang}.vtt"
            if vtt_file.exists():
                return parse_vtt(vtt_file), lang
        
        vtt_file = output_dir / f"{video_id}.vtt"
        if vtt_file.exists():
            return parse_vtt(vtt_file), "unknown"
        
        return None, None
    except Exception as e:
        print(f"Error downloading transcript: {e}")
        return None, None

def parse_vtt(vtt_path):
    """Parse VTT subtitle file and extract clean text"""
    text = []
    try:
        with open(vtt_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove WEBVTT header
        content = re.sub(r'^WEBVTT.*\n', '', content, flags=re.MULTILINE)
        
        # Remove timestamps
        content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}.*\n', '', content)
        
        # Remove tags
        content = re.sub(r'<[^>]+>', '', content)
        
        # Remove duplicate lines
        lines = content.strip().split('\n')
        prev_line = ""
        for line in lines:
            line = line.strip()
            if line and line != prev_line and not line.startswith('NOTE'):
                text.append(line)
                prev_line = line
        
        return ' '.join(text)
    except Exception as e:
        print(f"Error parsing VTT: {e}")
        return None

def extract_topics(video_info, transcript_text=None):
    """Extract topics from video metadata and transcript"""
    topics = []
    if not video_info:
        return topics
    
    title = video_info.get("title", "").lower()
    description = video_info.get("description", "") or ""
    description = description.lower()
    tags = video_info.get("tags", []) or []
    text = f"{title} {description} {' '.join(str(t) for t in tags)}"
    
    if transcript_text:
        text += f" {transcript_text.lower()}"
    
    # Topic categories
    categories = {
        "security": ["hack", "security", "pentest", "wifi", "bluetooth", "sdr",
                     "aircrack", "kismet", "hashcat", "exploit", "vulnerability",
                     "cve", "ransomware", "malware", "phishing", "network", "cyber"],
        "ai": ["machine learning", "ai", "neural", "llm", "gpt", "transformer",
               "deep learning", "nlp", "computer vision", "reinforcement", "ai"],
        "dev": ["python", "javascript", "rust", "golang", "arduino", "esp32",
                "programming", "coding", "api", "framework", "software"],
        "hardware": ["esp32", "arduino", "raspberry", "sdr", "lora", "meshtastic",
                     "embedded", "iot", "sensor", "electronics"],
        "finance": ["trading", "crypto", "bitcoin", "stock", "market", "investment"],
        "science": ["research", "paper", "study", "experiment", "physics", "chemistry"],
    }
    
    for category, keywords in categories.items():
        for kw in keywords:
            if kw in text:
                topics.append(f"{category}:{kw}")
    
    return list(set(topics))

def save_learning(url, video_info, transcript_text, transcript_lang, topics):
    """Save learning to knowledge base"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    video_id = video_info.get("id", timestamp)
    
    learning = {
        "timestamp": timestamp,
        "url": url,
        "video_id": video_id,
        "title": video_info.get("title", "Unknown"),
        "channel": video_info.get("uploader", "Unknown"),
        "duration": video_info.get("duration", 0),
        "topics": topics,
        "description": (video_info.get("description", "") or "")[:500],
        "transcript_language": transcript_lang,
        "has_transcript": transcript_text is not None,
        "transcript_length": len(transcript_text) if transcript_text else 0
    }
    
    # Save JSON
    json_file = KNOWLEDGE_DIR / f"learning_{timestamp}.json"
    with open(json_file, "w") as f:
        json.dump(learning, f, indent=2)
    
    # Save Markdown with full transcript
    md_file = KNOWLEDGE_DIR / f"learning_{timestamp}.md"
    with open(md_file, "w") as f:
        f.write(f"# {video_info.get('title', 'Unknown')}\n\n")
        f.write(f"**URL:** {url}\n\n")
        f.write(f"**Channel:** {video_info.get('uploader', 'Unknown')}\n\n")
        f.write(f"**Duration:** {video_info.get('duration', 0)}s ({video_info.get('duration', 0)//60}m)\n\n")
        f.write(f"**Topics:** {', '.join(topics)}\n\n")
        f.write(f"**Transcript:** {transcript_lang or 'N/A'} ({len(transcript_text) if transcript_text else 0} chars)\n\n")
        
        desc = video_info.get("description", "") or ""
        if desc:
            f.write(f"## Description\n\n{desc[:1000]}...\n\n")
        
        if transcript_text:
            f.write(f"## Transcript\n\n")
            # Format in paragraphs
            words = transcript_text.split()
            for i in range(0, len(words), 100):
                paragraph = ' '.join(words[i:i+100])
                f.write(f"{paragraph}\n\n")
    
    # Save transcript separately
    if transcript_text:
        transcript_file = KNOWLEDGE_DIR / "transcripts" / f"{video_id}.txt"
        with open(transcript_file, "w") as f:
            f.write(transcript_text)
    
    return json_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 learn_from_youtube.py <youtube_url>")
        print("\nFeatures:")
        print("  - Downloads video metadata")
        print("  - Extracts auto-generated or manual subtitles")
        print("  - Identifies topics from content")
        print("  - Saves to knowledge base")
        print("\nExample:")
        print("  python3 learn_from_youtube.py 'https://www.youtube.com/watch?v=VIDEO_ID'")
        sys.exit(1)
    
    url = sys.argv[1]
    
    print(f"=== YOUTUBE LEARNING ===")
    print(f"URL: {url}")
    
    # Download video info
    print("\n[1/4] Downloading video metadata...")
    video_info = download_video_info(url)
    if not video_info:
        print("Failed to download video info")
        sys.exit(1)
    
    print(f"Title: {video_info.get('title', 'Unknown')}")
    print(f"Channel: {video_info.get('uploader', 'Unknown')}")
    print(f"Duration: {video_info.get('duration', 0)}s")
    
    # Get transcript
    print("\n[2/4] Extracting transcript...")
    transcript_text, transcript_lang = get_transcript(url)
    
    if transcript_text:
        print(f"✓ Transcript extracted ({len(transcript_text)} chars, language: {transcript_lang})")
    else:
        print("✗ No transcript available")
    
    # Extract topics
    print("\n[3/4] Extracting topics...")
    topics = extract_topics(video_info, transcript_text)
    print(f"Topics: {topics}")
    
    # Save learning
    print("\n[4/4] Saving to knowledge base...")
    output_file = save_learning(url, video_info, transcript_text, transcript_lang, topics)
    print(f"✓ Saved: {output_file}")
    
    print("\n=== LEARNING COMPLETE ===")
    
    # Show transcript preview
    if transcript_text:
        print(f"\nTranscript preview:\n{transcript_text[:300]}...")

if __name__ == "__main__":
    main()
