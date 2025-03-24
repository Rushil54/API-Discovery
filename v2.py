import requests
import time
from collections import deque

API_URL = "http://35.200.185.69:8000/v2/autocomplete"
MAX_WAIT = 2  # Adjust based on rate limits

def fetch_suggestions(prefix):
    """Fetch autocomplete suggestions for a given prefix from v2 API."""
    try:
        response = requests.get(API_URL, params={"query": prefix}, timeout=3)
        if response.status_code == 200:
            return response.json().get("results", [])
        elif response.status_code == 429:  # Rate limit exceeded
            print(f"Rate limited! Sleeping for {MAX_WAIT} seconds...")
            time.sleep(MAX_WAIT)
            return fetch_suggestions(prefix)  # Retry after wait
        else:
            print(f"Failed: {response.status_code} - {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return []

def bfs_autocomplete():
    """Breadth-first search for extracting all possible names from autocomplete."""
    discovered = set()
    queue = deque([chr(i) for i in range(97, 123)])  # Start with 'a' to 'z'
    
    while queue:
        prefix = queue.popleft()
        if prefix in discovered:
            continue
        
        suggestions = fetch_suggestions(prefix)
        discovered.update(suggestions)
        
        # If the response hits the max limit, expand search further
        if len(suggestions) >= 12:  # v2 seems to have a max of 12 results
            queue.extend([name for name in suggestions if name not in discovered])
        
        time.sleep(0.5)  # Short pause to reduce API load
    
    return discovered

if __name__ == "__main__":
    all_names = bfs_autocomplete()
    
    # Save results to a file
    with open("v2.txt", "w") as f:
        for name in sorted(all_names):
            f.write(name + "\n")

    print(f"Extracted {len(all_names)} names. Results saved to 'v2.txt'.")
