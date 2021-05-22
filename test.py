import aiohttp
import asyncio
import scrap


# async def fetch(session: aiohttp.ClientSession, url: str):
#     async with session.get(url) as response:
#         return await response.text()


# async def main():
#     async with aiohttp.ClientSession() as client:
#         tasks = [asyncio.create_task(fetch(client, "http://python.org")) for _ in range(3)]
#         results = await asyncio.gather(*tasks)

#         print(results)
#         # result = await fetch(client, "http://python.org")
#         # print(result[:15])

# loop = asyncio.get_event_loop()
# loop.run_until_complete(main())
async def main():
    urls = ["https://g1.globo.com/educacao/", "https://g1.globo.com/economia/"]
    async with aiohttp.ClientSession() as session:
        tasks = asyncio.create_task(scrap.GetLatestG1News(session, urls))
        await tasks

    for _ in tasks.result():
        print("Request done")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())