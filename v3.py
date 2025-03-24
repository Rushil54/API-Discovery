import requests
import time
from collections import deque

API_URL = "http://35.200.185.69:8000/v3/autocomplete"
MAX_WAIT = 2  # Start with 2 seconds for rate limit handling

def fetch_suggestions(prefix, retries=3):
    """Fetch autocomplete suggestions for a given prefix from v3 API."""
    global MAX_WAIT
    for attempt in range(retries):
        try:
            response = requests.get(API_URL, params={"query": prefix}, timeout=3)
            if response.status_code == 200:
                return response.json().get("results", [])
            elif response.status_code == 429:  # Rate limit exceeded
                wait_time = MAX_WAIT * (2 ** attempt)  # Exponential backoff
                print(f"Rate limited! Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"Failed: {response.status_code} - {response.text}")
                return []
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
    return []

def bfs_autocomplete():
    """Breadth-first search to extract all possible names from v3 autocomplete."""
    discovered = set()
    queue = deque([chr(i) for i in range(97, 123)])  # Start with 'a' to 'z'
    
    while queue:
        prefix = queue.popleft()
        if prefix in discovered:
            continue
        
        suggestions = fetch_suggestions(prefix)
        discovered.update(suggestions)
        
        # If max results (15 for v3) are returned, explore further
        if len(suggestions) >= 15:
            queue.extend([name for name in suggestions if name not in discovered])
        
        time.sleep(0.5)  # Reduce API load
    
    return discovered

if __name__ == "__main__":
    all_names = bfs_autocomplete()
    
    # Save results to a file
    with open("v3.txt", "w") as f:
        for name in sorted(all_names):
            f.write(name + "\n")

    print(f"Extracted {len(all_names)} names. Results saved to 'v3.txt'.")
