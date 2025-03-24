import requests
import time
from collections import deque

API_URL = "http://35.200.185.69:8000/{}/autocomplete"
MAX_DEPTH = 3  # Go up to 3-letter prefixes
WAIT_TIME = 0.5  # Rate limit delay

def fetch_suggestions(prefix, version="v1"):
    """Fetch autocomplete suggestions for a given prefix."""
    url = API_URL.format(version)
    params = {"query": prefix}
    
    try:
        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            return response.json().get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return []

def bfs_autocomplete(version="v1"):
    """Perform a BFS to extract all possible names from the autocomplete system."""
    discovered = set()
    queue = deque([chr(i) for i in range(97, 123)])  # Start with 'a' to 'z'

    while queue:
        prefix = queue.popleft()
        if prefix in discovered or len(prefix) > MAX_DEPTH:
            continue

        suggestions = fetch_suggestions(prefix, version)
        discovered.update(suggestions)

        # If the API returns max results, explore deeper
        if len(suggestions) >= 10:
            queue.extend([prefix + chr(i) for i in range(97, 123)])  # Add 'aa', 'ab', ..., 'zz'

        time.sleep(WAIT_TIME)  # Avoid rate limits

    return discovered

def save_results_to_file(results, filename="v1.txt"):
    """Save the extracted results to a text file."""
    with open(filename, "w", encoding="utf-8") as file:
        for name in sorted(results):
            file.write(name + "\n")
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    all_names = bfs_autocomplete("v1")
    save_results_to_file(all_names)
