import requests
import threading
from queue import Queue
from urllib.parse import urljoin


WORDLIST_PATH = "app/scanner/web/wordlists/common_dirs.txt"

THREADS = 10


def load_wordlist():

    with open(WORDLIST_PATH, "r") as f:
        return [line.strip() for line in f.readlines()]


def worker(target, queue, results):

    while not queue.empty():

        directory = queue.get()

        url = urljoin(target + "/", directory)

        try:

            r = requests.get(url, timeout=4)

            if r.status_code in [200, 301, 302, 403]:

                results.append({
                    "path": "/" + directory,
                    "status": r.status_code
                })

        except Exception:
            pass

        queue.task_done()


def scan_directories(target):

    words = load_wordlist()

    queue = Queue()

    results = []

    for word in words:
        queue.put(word)

    threads = []

    for _ in range(THREADS):

        t = threading.Thread(target=worker, args=(target, queue, results))
        t.daemon = True
        t.start()

        threads.append(t)

    queue.join()

    return {
        "success": True,
        "directories_found": results,
        "total_found": len(results)
    }