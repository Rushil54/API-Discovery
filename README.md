# API-Discovery
Technical Assignment - Ivy homes

Autocomplete API Exploration

1️. API Details
Base URL: http://35.200.185.69:8000/v1/autocomplete
Query Parameter: query (e.g., ?query=a)
Response Format: JSON { "results": ["Name1", "Name2", ...] }
Maximum Results Per Query: 10–15 (depends on version)
Different Versions: v1, v2, v3

v1: No digits in results

v2: Names can start with digits

v3: Supports special characters (like -, .), but only inside the name, not as first character

2️. Findings & Limitations
Prefix-based search → The API returns results based on input prefixes.
Depth limitation → Querying "a" gives up to 10–15 results, but not all names.
Rate-Limited (HTTP 429) → Sending too many requests results in a Too Many Requests error.
Timeout Issues (HTTP 408 / 503) → Some long queries fail due to connection timeouts.
Doesn't support capital letters → Only lowercase queries return results.
Special character behavior → - and . appear in results, but cannot be used as the first character.

3️. Optimization Strategies Used
Multi-threading (3 threads max) → Balances speed & rate limits.
Exponential Backoff for Rate Limits → Waits 2s → 4s → 8s on HTTP 429 errors.
Breadth-First Search (BFS) Expansion → Queries go deeper (a → aa, ab, ac...).
File Storage → Extracted names are saved in autocomplete_results.txt.
Query Limits Avoidance → 1 request per second to avoid getting blocked.

4️. How to Run the Code
Install Python 3 & required libraries:

pip install requests

Run the script:

python 4.py

Results will be saved in:

v1.txt
