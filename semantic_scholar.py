#!/usr/bin/env python3
"""
Semantic Scholar API Integration
Search and retrieve academic papers

Author: D3n14l0f53rv1c3
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path.home() / "knowledge" / "papers"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

API_BASE = "https://api.semanticscholar.org/graph/v1"

def search_papers(query, limit=10, year_range=None, fields=None):
    """
    Search for papers on Semantic Scholar
    
    Args:
        query: Search query string
        limit: Maximum number of results (default 10)
        year_range: Tuple of (start_year, end_year) or None
        fields: List of fields to return
    
    Returns:
        List of paper dictionaries
    """
    if fields is None:
        fields = ["paperId", "title", "authors", "year", "abstract", 
                  "url", "venue", "publicationDate", "citationCount"]
    
    params = {
        "query": query,
        "limit": limit,
        "fields": ",".join(fields)
    }
    
    if year_range:
        params["year"] = f"{year_range[0]}-{year_range[1]}"
    
    url = f"{API_BASE}/paper/search?{urllib.parse.urlencode(params)}"
    
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "OpenClaw Learning System")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode())
            return data.get("data", [])
    except Exception as e:
        print(f"Error searching papers: {e}")
        return []

def get_paper(paper_id, fields=None):
    """
    Get detailed information about a specific paper
    
    Args:
        paper_id: Semantic Scholar paper ID
        fields: List of fields to return
    
    Returns:
        Paper dictionary
    """
    if fields is None:
        fields = ["paperId", "title", "authors", "year", "abstract",
                  "url", "venue", "publicationDate", "citationCount",
                  "references", "citations", "embedding"]
    
    url = f"{API_BASE}/paper/{paper_id}?fields={','.join(fields)}"
    
    try:
        req = urllib.request.Request(url)
        req.add_header("User-Agent", "OpenClaw Learning System")
        
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error getting paper: {e}")
        return None

def get_recent_papers(query, days=30, limit=10):
    """
    Get papers published in the last N days
    
    Args:
        query: Search query
        days: Number of days to look back
        limit: Maximum results
    
    Returns:
        List of recent papers
    """
    from datetime import datetime, timedelta
    
    # Semantic Scholar doesn't have a direct "recent" filter
    # We search and filter by date
    papers = search_papers(query, limit=limit*2)  # Get more to filter
    
    recent = []
    cutoff_date = datetime.now() - timedelta(days=days)
    
    for paper in papers:
        pub_date = paper.get("publicationDate")
        if pub_date:
            try:
                paper_date = datetime.strptime(pub_date[:10], "%Y-%m-%d")
                if paper_date >= cutoff_date:
                    recent.append(paper)
            except:
                pass
        
        if len(recent) >= limit:
            break
    
    return recent

def save_paper(paper, topics=None):
    """Save paper to knowledge base"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    paper_id = paper.get("paperId", "unknown")
    
    # Save JSON
    json_file = KNOWLEDGE_DIR / f"paper_{paper_id}.json"
    with open(json_file, "w") as f:
        json.dump(paper, f, indent=2)
    
    # Save Markdown
    md_file = KNOWLEDGE_DIR / f"paper_{paper_id}.md"
    with open(md_file, "w") as f:
        f.write(f"# {paper.get('title', 'Unknown Title')}\n\n")
        f.write(f"**Paper ID:** {paper_id}\n\n")
        f.write(f"**Year:** {paper.get('year', 'N/A')}\n\n")
        
        authors = paper.get("authors", [])
        if authors:
            author_names = [a.get("name", "Unknown") for a in authors]
            f.write(f"**Authors:** {', '.join(author_names)}\n\n")
        
        f.write(f"**Venue:** {paper.get('venue', 'N/A')}\n\n")
        f.write(f"**Citations:** {paper.get('citationCount', 0)}\n\n")
        f.write(f"**URL:** {paper.get('url', 'N/A')}\n\n")
        
        if topics:
            f.write(f"**Topics:** {', '.join(topics)}\n\n")
        
        abstract = paper.get("abstract")
        if abstract:
            f.write(f"## Abstract\n\n{abstract}\n\n")
    
    return json_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 semantic_scholar.py <query>")
        print("\nCommands:")
        print("  search <query>       - Search for papers")
        print("  recent <query>       - Get recent papers (last 30 days)")
        print("  paper <paper_id>     - Get paper details")
        print("\nOptions:")
        print("  --limit N            - Limit results to N papers")
        print("  --year START-END     - Filter by year range")
        print("\nExamples:")
        print("  python3 semantic_scholar.py search \"machine learning security\"")
        print("  python3 semantic_scholar.py recent \"wifi vulnerabilities\" --limit 5")
        print("  python3 semantic_scholar.py paper 649def34f8fa52c3e0e7")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # Parse options
    limit = 10
    year_range = None
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--limit" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
            i += 2
        elif sys.argv[i] == "--year" and i + 1 < len(sys.argv):
            years = sys.argv[i + 1].split("-")
            year_range = (int(years[0]), int(years[1]))
            i += 2
        else:
            i += 1
    
    if command == "search":
        query = " ".join(sys.argv[2:]).split("--")[0].strip()
        print(f"=== SEARCHING PAPERS ===")
        print(f"Query: {query}")
        print(f"Limit: {limit}")
        if year_range:
            print(f"Year range: {year_range[0]}-{year_range[1]}")
        print()
        
        papers = search_papers(query, limit=limit, year_range=year_range)
        
        if not papers:
            print("No papers found")
            sys.exit(0)
        
        print(f"Found {len(papers)} papers:\n")
        for i, paper in enumerate(papers, 1):
            print(f"{i}. {paper.get('title', 'Unknown')}")
            print(f"   Year: {paper.get('year', 'N/A')} | Citations: {paper.get('citationCount', 0)}")
            print(f"   ID: {paper.get('paperId', 'unknown')}")
            print()
        
        # Save first paper
        if papers:
            save_paper(papers[0], topics=[query])
            print(f"Saved first paper to knowledge base")
    
    elif command == "recent":
        query = " ".join(sys.argv[2:]).split("--")[0].strip()
        print(f"=== RECENT PAPERS (LAST 30 DAYS) ===")
        print(f"Query: {query}")
        print()
        
        papers = get_recent_papers(query, days=30, limit=limit)
        
        if not papers:
            print("No recent papers found")
            sys.exit(0)
        
        print(f"Found {len(papers)} recent papers:\n")
        for i, paper in enumerate(papers, 1):
            pub_date = paper.get("publicationDate", "Unknown")
            print(f"{i}. {paper.get('title', 'Unknown')}")
            print(f"   Published: {pub_date}")
            print(f"   ID: {paper.get('paperId', 'unknown')}")
            print()
    
    elif command == "paper":
        paper_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not paper_id:
            print("Error: Paper ID required")
            sys.exit(1)
        
        print(f"=== GETTING PAPER ===")
        print(f"Paper ID: {paper_id}")
        print()
        
        paper = get_paper(paper_id)
        if not paper:
            print("Paper not found")
            sys.exit(1)
        
        print(f"Title: {paper.get('title', 'Unknown')}")
        print(f"Year: {paper.get('year', 'N/A')}")
        print(f"Venue: {paper.get('venue', 'N/A')}")
        print(f"Citations: {paper.get('citationCount', 0)}")
        print()
        
        if paper.get('abstract'):
            print(f"Abstract:\n{paper['abstract'][:500]}...")
        
        save_paper(paper)
        print(f"\nSaved to knowledge base")
    
    else:
        # Treat as search query
        query = " ".join(sys.argv[1:])
        print(f"=== SEARCHING PAPERS ===")
        print(f"Query: {query}")
        print()
        
        papers = search_papers(query, limit=limit)
        
        for i, paper in enumerate(papers[:5], 1):
            print(f"{i}. {paper.get('title', 'Unknown')}")
            print(f"   Year: {paper.get('year', 'N/A')}")
        
        if papers:
            save_paper(papers[0])

if __name__ == "__main__":
    main()
