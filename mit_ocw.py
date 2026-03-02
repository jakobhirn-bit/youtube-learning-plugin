#!/usr/bin/env python3
"""
MIT OpenCourseWare Integration
Access free MIT course materials

Author: D3n14l0f53rv1c3
"""

import os
import sys
import json
import urllib.request
import urllib.parse
from datetime import datetime
from pathlib import Path

KNOWLEDGE_DIR = Path.home() / "knowledge" / "mit_courses"
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

# MIT OCW API endpoint (they have a REST API)
OCW_API = "https://ocw.mit.edu/api"

def search_courses(query, limit=10):
    """
    Search MIT OCW courses
    
    Note: MIT OCW doesn't have a public API, but we can search
    their course catalog via web scraping or use their RSS feeds
    """
    # For now, return popular courses in key areas
    courses = {
        "computer science": [
            {"id": "6.0001", "title": "Introduction to Computer Science and Programming", "url": "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/"},
            {"id": "6.0002", "title": "Introduction to Computational Thinking and Data Science", "url": "https://ocw.mit.edu/courses/6-0002-introduction-to-computational-thinking-and-data-science-spring-2016/"},
            {"id": "6.006", "title": "Introduction to Algorithms", "url": "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/"},
            {"id": "6.034", "title": "Artificial Intelligence", "url": "https://ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/"},
        ],
        "security": [
            {"id": "6.858", "title": "Computer Systems Security", "url": "https://ocw.mit.edu/courses/6-858-computer-systems-security-fall-2014/"},
            {"id": "6.857", "title": "Network and Computer Security", "url": "https://ocw.mit.edu/courses/6-857-network-and-computer-security-spring-2014/"},
        ],
        "ai": [
            {"id": "6.034", "title": "Artificial Intelligence", "url": "https://ocw.mit.edu/courses/6-034-artificial-intelligence-fall-2010/"},
            {"id": "6.036", "title": "Introduction to Machine Learning", "url": "https://ocw.mit.edu/courses/6-036-introduction-to-machine-learning-spring-2022/"},
            {"id": "6.864", "title": "Advanced Natural Language Processing", "url": "https://ocw.mit.edu/courses/6-864-advanced-natural-language-processing-fall-2005/"},
        ],
        "networks": [
            {"id": "6.029", "title": "Computer Networks", "url": "https://ocw.mit.edu/courses/6-029-computer-networks-spring-2018/"},
            {"id": "6.829", "title": "Computer Networks", "url": "https://ocw.mit.edu/courses/6-829-computer-networks-fall-2017/"},
        ],
        "electronics": [
            {"id": "6.002", "title": "Circuits and Electronics", "url": "https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/"},
            {"id": "6.003", "title": "Signals and Systems", "url": "https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/"},
        ],
        "mathematics": [
            {"id": "18.06", "title": "Linear Algebra", "url": "https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/"},
            {"id": "18.02", "title": "Multivariable Calculus", "url": "https://ocw.mit.edu/courses/18-02sc-multivariable-calculus-fall-2010/"},
            {"id": "6.042", "title": "Mathematics for Computer Science", "url": "https://ocw.mit.edu/courses/6-042j-mathematics-for-computer-science-spring-2015/"},
        ],
    }
    
    query_lower = query.lower()
    results = []
    
    for topic, course_list in courses.items():
        if topic in query_lower or query_lower in topic:
            results.extend(course_list[:limit])
    
    if not results:
        # Search by title
        for topic, course_list in courses.items():
            for course in course_list:
                if query_lower in course["title"].lower():
                    results.append(course)
    
    return results[:limit]

def get_course_info(course_id):
    """
    Get detailed information about a specific course
    
    Note: This would require web scraping in production
    """
    return {
        "id": course_id,
        "url": f"https://ocw.mit.edu/courses/{course_id}",
        "status": "Course information requires web scraping"
    }

def save_course(course, topics=None):
    """Save course to knowledge base"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    # Save JSON
    json_file = KNOWLEDGE_DIR / f"course_{course.get('id', timestamp)}.json"
    with open(json_file, "w") as f:
        json.dump(course, f, indent=2)
    
    # Save Markdown
    md_file = KNOWLEDGE_DIR / f"course_{course.get('id', timestamp)}.md"
    with open(md_file, "w") as f:
        f.write(f"# {course.get('title', 'Unknown Course')}\n\n")
        f.write(f"**Course ID:** {course.get('id', 'Unknown')}\n\n")
        f.write(f"**URL:** {course.get('url', 'N/A')}\n\n")
        
        if topics:
            f.write(f"**Topics:** {', '.join(topics)}\n\n")
        
        f.write(f"## Resources\n\n")
        f.write(f"- Course Materials: {course.get('url', 'N/A')}\n")
    
    return json_file

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 mit_ocw.py <command>")
        print("\nCommands:")
        print("  search <query>       - Search for courses")
        print("  list <topic>         - List courses by topic")
        print("\nTopics:")
        print("  computer science, security, ai, networks, electronics, mathematics")
        print("\nExamples:")
        print("  python3 mit_ocw.py search \"machine learning\"")
        print("  python3 mit_ocw.py list security")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "search":
        query = " ".join(sys.argv[2:])
        print(f"=== SEARCHING MIT OCW ===")
        print(f"Query: {query}")
        print()
        
        courses = search_courses(query)
        
        if not courses:
            print("No courses found")
            print("\nTry topics: computer science, security, ai, networks, electronics, mathematics")
            sys.exit(0)
        
        print(f"Found {len(courses)} courses:\n")
        for i, course in enumerate(courses, 1):
            print(f"{i}. {course['title']}")
            print(f"   ID: {course['id']}")
            print(f"   URL: {course['url']}")
            print()
        
        # Save first course
        if courses:
            save_course(courses[0])
            print("Saved first course to knowledge base")
    
    elif command == "list":
        topic = sys.argv[2] if len(sys.argv) > 2 else "computer science"
        print(f"=== MIT OCW COURSES: {topic.upper()} ===\n")
        
        courses = search_courses(topic, limit=20)
        
        for i, course in enumerate(courses, 1):
            print(f"{i}. {course['title']}")
            print(f"   {course['url']}")
            print()
    
    else:
        # Treat as search
        query = " ".join(sys.argv[1:])
        courses = search_courses(query)
        
        for i, course in enumerate(courses[:5], 1):
            print(f"{i}. {course['title']}")
            print(f"   {course['url']}")

if __name__ == "__main__":
    main()
