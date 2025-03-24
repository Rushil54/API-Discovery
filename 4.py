import requests
import time
import threading
from queue import Queue

API_URL = "http://35.200.185.69:8000/{}/autocomplete"
MAX_DEPTH = 4  # Search up to 4-letter prefixes
THREADS = 3    # Reduce to avoid rate limits
WAIT_TIME = 1  # Ensure at least 1 second between requests
RETRY_LIMIT = 3  # Retry failed requests with exponential backoff

def fetch_suggestions(prefix, version="v1"):
    """Fetch autocomplete suggestions with retry and exponential backoff on 429."""
    url = API_URL.format(version)
    params = {"query": prefix}
    wait = 2  # Initial wait for backoff

    for attempt in range(RETRY_LIMIT):
        try:
            response = requests.get(url, params=params, timeout=5)

            if response.status_code == 200:
                return response.json().get("results", [])
            elif response.status_code == 429:
                print(f"Rate limited! Retrying in {wait} seconds...")
                time.sleep(wait)
                wait *= 2  # Exponential backoff (2s → 4s → 8s)
            else:
                print(f"Warning: {prefix} → HTTP {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            print(f"Request failed (attempt {attempt+1}): {e}")
            time.sleep(wait)
            wait *= 2  # Exponential backoff for errors

    return []

def worker(queue, discovered, visited, version):
    """Thread worker to process API requests while respecting rate limits."""
    while not queue.empty():
        prefix = queue.get()
        if prefix in visited or len(prefix) > MAX_DEPTH:
            queue.task_done()
            continue

        visited.add(prefix)
        suggestions = fetch_suggestions(prefix, version)
        discovered.update(suggestions)

        if suggestions:
            for i in range(97, 123):  # 'a' to 'z'
                new_prefix = prefix + chr(i)
                if new_prefix not in visited:
                    queue.put(new_prefix)

        queue.task_done()
        time.sleep(WAIT_TIME)  # Prevent hitting rate limits

def bfs_autocomplete(version="v1"):
    """Perform a BFS with controlled parallel threads to extract names."""
    discovered = set()
    visited = set()
    queue = Queue()

    # Start with 'a' to 'z'
    for i in range(97, 123):
        queue.put(chr(i))

    # Create worker threads
    threads = []
    for _ in range(THREADS):
        t = threading.Thread(target=worker, args=(queue, discovered, visited, version))
        t.start()
        threads.append(t)

    queue.join()  # Wait for all workers to finish

    return discovered

def save_results_to_file(results, filename="v1.txt"):
    """Save the extracted results to a text file."""
    with open(filename, "w", encoding="utf-8") as file:
        for name in sorted(results):
            file.write(name + "\n")
    print(f"Results saved to {filename}")

if __name__ == "__main__":
    start_time = time.time()
    all_names = bfs_autocomplete("v1")
    save_results_to_file(all_names)
    print(f"Total names found: {len(all_names)}")
    print(f"Time taken: {time.time() - start_time:.2f} seconds")
