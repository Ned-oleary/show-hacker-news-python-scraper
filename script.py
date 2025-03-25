from concurrent.futures import ThreadPoolExecutor
import requests
import csv
import time

BASE_URL = 'https://hacker-news.firebaseio.com/v0'
OUTPUT_CSV = 'show_launch_hn_data.csv'

# the HN API requires that you fetch by ID like this
def fetch_item(item_id):
    try:
        resp = requests.get(f'{BASE_URL}/item/{item_id}.json', timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except:
        try:
            time.sleep(5)
            resp = requests.get(f'{BASE_URL}/item/{item_id}.json', timeout=5)
            if resp.status_code == 200:
                return resp.json()
        except:
            print("Failed on item " + item_id)
    return None

# this is really the only way to get the most recent posts
def get_max_item_id():
    resp = requests.get(f'{BASE_URL}/maxitem.json')
    if resp.status_code == 200:
        return resp.json() # actually returns an int, fwiw
    return None

def is_show_or_launch(title):
    title = title.lower()
    return title.startswith('show hn') or title.startswith('launch hn')


def scrape(target_count=1000):
    max_item_id = get_max_item_id()
    candidate_ids = list(range(max_item_id, max_item_id - 100000, -1))

    rows = []

    def process_id(item_id):
        item = fetch_item(item_id)
        if not item or 'title' not in item or 'score' not in item:
            return None
        title = item['title']
        if not is_show_or_launch(title):
            return None
        print(title)
        item['open_source'] = 'open source' in title.lower()
        return item

    with ThreadPoolExecutor(max_workers=10) as executor:
        for item in executor.map(process_id, candidate_ids):
            if item:
                rows.append(item)
                if len(rows) >= target_count:
                    break

    if not rows:
        print("No matching posts found.")
        return

    all_keys = set()
    for row in rows:
        all_keys.update(row.keys())
    fieldnames = list(all_keys)

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} posts to {OUTPUT_CSV}")



if __name__ == '__main__':
    scrape()