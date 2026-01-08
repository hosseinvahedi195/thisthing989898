#!/usr/bin/env python3
"""
Research LinkedIn posts about data privacy regulations and generate blog content.
Follows directives/linkedin_data_privacy_research.md
"""

from apify_client import ApifyClient
from dotenv import load_dotenv
import os
import json
import google.generativeai as genai
from datetime import datetime

# Load environment variables
load_dotenv()

# Initialize APIs
apify_token = os.getenv('APIFY_API_TOKEN')
gemini_key = os.getenv('GEMINI_API_KEY')

if not apify_token:
    raise ValueError("APIFY_API_TOKEN not found in .env")
if not gemini_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

apify_client = ApifyClient(apify_token)
genai.configure(api_key=gemini_key)

print("=" * 80)
print("LinkedIn Data Privacy Research - Starting")
print("=" * 80)

# Step 1: Define search queries for LinkedIn posts
search_queries = [
    "HIPAA compliance data privacy healthcare",
    "PIPEDA data protection Canada privacy",
    "FIPPA privacy act information protection",
    "client data privacy on-premise hosting",
    "data sovereignty client controlled servers",
    "healthcare data privacy regulations compliance",
    "private practice data security HIPAA",
    "patient data privacy best practices",
    "secure client data hosting solutions",
    "privacy regulations healthcare technology"
]

print(f"\n[1/4] Searching LinkedIn for posts about data privacy...")
print(f"       Using {len(search_queries)} targeted search queries")

# Step 2: Scrape LinkedIn using Google Search (since direct LinkedIn scraping requires login)
# We'll use Google Search to find LinkedIn posts
run_input = {
    "queries": "\n".join([
        f'site:linkedin.com/posts/ OR site:linkedin.com/pulse/ "{query}"' 
        for query in search_queries
    ]),
    "maxPagesPerQuery": 1,
    "resultsPerPage": 10,  # Get more results to filter for top engagement
    "countryCode": "us",
    "languageCode": "en",
}

print(f"       Executing Apify Google Search Scraper...")

# Run the scraper
run = apify_client.actor("apify/google-search-scraper").call(run_input=run_input)

print(f"       ✓ Scraper completed. Dataset ID: {run['defaultDatasetId']}")

# Step 3: Fetch and process results
print(f"\n[2/4] Processing scraped data...")

all_posts = []
for item in apify_client.dataset(run["defaultDatasetId"]).iterate_items():
    organic_results = item.get('organicResults', [])
    for result in organic_results:
        # Extract relevant information
        post = {
            'title': result.get('title', ''),
            'url': result.get('url', ''),
            'description': result.get('description', ''),
            'query': item.get('searchQuery', {}).get('term', '')
        }
        all_posts.append(post)

print(f"       ✓ Found {len(all_posts)} LinkedIn posts")

# Save raw research data
research_file = '.tmp/privacy_research.json'
with open(research_file, 'w') as f:
    json.dump(all_posts, f, indent=2)

print(f"       ✓ Saved raw data to {research_file}")

# Step 4: Generate blog content using Gemini
print(f"\n[3/4] Generating blog content with Gemini AI...")

# Prepare research summary for AI
research_summary = "\n\n".join([
    f"Post {i+1}:\nTitle: {post['title']}\nDescription: {post['description']}\nURL: {post['url']}"
    for i, post in enumerate(all_posts[:15])  # Use top 15 for context
])

prompt = f"""You are a professional content writer creating a blog post about client data privacy for a business automation consultancy website.

Based on the following LinkedIn research about data privacy regulations and solutions, write a comprehensive, professional blog post.

RESEARCH DATA:
{research_summary}

REQUIREMENTS:
1. **Tone**: Spartan, professional, and human-like. Write like you're explaining to a business owner, not a lawyer.
2. **Style**: Accessible and clear. Avoid heavy jargon. If you use a technical term, explain it briefly.
3. **Content Focus**:
   - Address major data privacy regulations: HIPAA (healthcare), PIPEDA (Canada), FIPPA (information protection)
   - Explain what these regulations mean for businesses in practical terms
   - Provide solutions: on-premise hosting, client-controlled servers, data sovereignty
   - Include actionable advice businesses can implement

4. **Structure**: 
   - Engaging introduction that states why this matters
   - 3-4 main sections covering regulations and solutions
   - Practical takeaways
   - Strong conclusion

5. **Length**: 800-1200 words
6. **Voice**: Direct, confident, helpful. Avoid being preachy or alarmist.

Do NOT include a title or meta description - just the body content. Use HTML tags for structure: <p>, <h2>, <h3>, <div class="highlight-box"> for important callouts.

Write the blog post now:"""

# Generate content
model = genai.GenerativeModel('gemini-2.0-flash-exp')
response = model.generate_content(prompt)

blog_content = response.text

# Save blog content
content_file = '.tmp/blog_content.txt'
with open(content_file, 'w') as f:
    f.write(blog_content)

print(f"       ✓ Generated {len(blog_content)} characters of content")
print(f"       ✓ Saved to {content_file}")

# Step 5: Display preview
print(f"\n[4/4] Content Preview:")
print("=" * 80)
print(blog_content[:500] + "...\n")
print("=" * 80)

print(f"\n✅ Research and content generation complete!")
print(f"\nNext steps:")
print(f"  1. Review content in: {content_file}")
print(f"  2. Review research in: {research_file}")
print(f"  3. Create HTML blog file with this content")
