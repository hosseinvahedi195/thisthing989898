from apify_client import ApifyClient
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()

# Initialize the ApifyClient with your API token
apify_token = os.getenv('APIFY_API_TOKEN')
if not apify_token:
    # Fallback/Debug if env var is missing or named differently
    print("Warning: APIFY_API_TOKEN not found in .env, checking for other keys...")
    # In the viewed .env file, it was APIFY_API_TOKEN
    
client = ApifyClient(apify_token)

# Prepare the Actor input
run_input = {
    "queries": "\n".join([
        "site:linkedin.com/posts/ OR site:linkedin.com/pulse/ \"Future of AI Automation 2026\"",
        "site:linkedin.com/posts/ OR site:linkedin.com/pulse/ \"Low-Code Solutions Scale Better\"",
        "site:linkedin.com/posts/ OR site:linkedin.com/pulse/ \"Signs You Need Systems Automation\""
    ]),
    "maxPagesPerQuery": 1,
    "resultsPerPage": 3,
    "countryCode": "us",
    "languageCode": "en",
}

print("Starting Google Search Scraper for LinkedIn posts...")

# Run the Actor and wait for it to finish
# Actor ID for Google Search Scraper: apify/google-search-scraper
run = client.actor("apify/google-search-scraper").call(run_input=run_input)

print(f"Scraper finished. Dataset ID: {run['defaultDatasetId']}")

# Fetch and print Actor results from the run's dataset (if there are any)
results = []
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    results.append(item)

# Save results to a file for review
with open('research_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Saved {len(results)} results to research_results.json")

# Print a summary
for item in results:
    query = item.get('searchQuery', {}).get('term', 'Unknown Query')
    organic_results = item.get('organicResults', [])
    suggested_results = item.get('suggestedResults', [])
    all_results = organic_results + suggested_results
    
    print(f"\n--- Results for: {query} ---")
    for res in all_results[:3]: # Top 3
        print(f"Title: {res.get('title')}")
        print(f"Link: {res.get('url')}")
        print(f"Snippet: {res.get('description')}\n")
