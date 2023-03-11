import time
import asyncio
import aiohttp
import lxml.html


async def send_request(session, link):
    try:
        async with session.request('GET', link, timeout=aiohttp.ClientTimeout(total=1)) as response:
            if response.status == 200:
                html = await response.text()
                root = lxml.html.fromstring(html)
                title = root.find('.//title').text
                if "TorrServer" in title:
                    if html.lower().find("matrix") != -1:
                        return link
    except:
        return None


async def process_chunk(chunk):
    valid_links = set()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for item in chunk:
            link = 'http://' + item
            task = asyncio.create_task(send_request(session, link))
            tasks.append(task)
        results = await asyncio.gather(*tasks, return_exceptions=False)
        for result in results:
            if result is not None:
                valid_links.add(result)
    return valid_links


async def main():
    start_time = time.perf_counter()
    CHUNK_SIZE = 1200
    valid_links = set()
    total_links_processed = 0
    with open('ip.txt') as f:
        chunk = []
        for line in f:
            if line.startswith("open"):
                data = line.strip().split(" ")
                line = data[3] + ':' + data[2]
                chunk.append(line)
            if len(chunk) == CHUNK_SIZE:
                links = await process_chunk(chunk)
                valid_links.update(links)
                total_links_processed += CHUNK_SIZE
                write_final(links)
                chunk = []
        if chunk:
            links = await process_chunk(chunk)
            valid_links.update(links)
            total_links_processed += len(chunk)
            write_final(links)
    end_time = time.perf_counter()
    print(f"Total links processed: {total_links_processed}")
    print(f"Total valid links: {len(valid_links)}")
    #print(f"Total time taken: {end_time - start_time:0.2f} seconds")


def write_final(links):
    with open('final.txt', 'a') as final:
        for link in links:
            final.write(link + '\n')


if __name__ == '__main__':
    file = open("final.txt", "w")
    asyncio.run(main())
