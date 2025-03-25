import asyncio
import aiohttp
import csv

BASE_URL = 'https://hacker-news.firebaseio.com/v0'
OUTPUT_CSV = 'show_launch_hn_data.csv'
CONCURRENT_REQUESTS = 50

def is_show_or_launch(title):
    title = title.lower()
    return title.startswith('show hn') or title.startswith('launch hn')

async def fetch_item(session, item_id):
    url = f'{BASE_URL}/item/{item_id}.json'
    try:
        async with session.get(url, timeout=5) as resp:
            if resp.status == 200:
                return await resp.json()
    except Exception:
        return None

async def get_max_item_id(session):
    url = f'{BASE_URL}/maxitem.json'
    async with session.get(url, timeout=5) as resp:
        return await resp.json()

async def scrape(target_count=10_000):
    rows = []
    all_keys = set()

    conn = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS)
    async with aiohttp.ClientSession(connector=conn) as session:
        max_id = await get_max_item_id(session)
        candidate_ids = range(max_id, 0, -1)

        sem = asyncio.Semaphore(CONCURRENT_REQUESTS)

        async def process(item_id):
            async with sem:
                item = await fetch_item(session, item_id)
                if not item or 'title' not in item or 'score' not in item:
                    return None
                if not is_show_or_launch(item['title']):
                    return None
                item['open_source'] = 'open source' in item['title'].lower()
                return item

        tasks = []
        for item_id in candidate_ids:
            if len(rows) >= target_count:
                break
            tasks.append(process(item_id))

            if len(tasks) >= CONCURRENT_REQUESTS * 10:
                results = await asyncio.gather(*tasks)
                for item in results:
                    if item:
                        rows.append(item)
                        all_keys.update(item.keys())
                        if len(rows) >= target_count:
                            break
                tasks = []

    # Write CSV
    if not rows:
        print("No matching posts found.")
        return

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(all_keys))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} posts to {OUTPUT_CSV}")

if __name__ == '__main__':
    asyncio.run(scrape())
