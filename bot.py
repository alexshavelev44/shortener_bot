from dotenv import load_dotenv
import os
import asyncio
import aiohttp
import telepot.aio
from telepot.aio.loop import MessageLoop


BITLY_URL = 'https://api-ssl.bitly.com/v4/{}'
WELCOME_MSG = """
Hey!

🔹 Send long url https://www.chelseafc.com/en 
   receive short http://bit.ly/2FUgzLf

🔹 Send short url bit.ly/2FUgzLf 
   receive clicks count  
"""

CLICKS_COUNT = "🔹 Clicks count = {}"


def get_headers(token):
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer {}'.format(token)}
    return headers


async def shorten_url(token, link):
    url = BITLY_URL.format('shorten')
    headers = get_headers(token)
    async with aiohttp.ClientSession() as session:
        res = await session.post(url=url, headers=headers, json={'long_url': link})
        if res.status in (200, 201):
            bitly_data = await res.json()
            print(bitly_data)
            return bitly_data['link']


async def get_clicks_count(token, link):
    url = BITLY_URL.format('bitlinks/{}/clicks/summary'.format(link))
    headers = get_headers(token)
    async with aiohttp.ClientSession() as session:
        res = await session.get(url=url, headers=headers, json={'long_url': link})
        print(res.status)
        if res.status == 200:
            bitly_data = await res.json()
            print(bitly_data)
            return bitly_data['total_clicks']


## https://github.com/nickoala/telepot/blob/master/examples/simple/skeletona.py

async def handle(msg):

    text = msg['text']
    if text == '/start':
        response = WELCOME_MSG
    else:
        # if user but whole link http://bit.ly/2DISR2l we will cut htts:// off
        if text.startswith('http://bit.ly/'):
            text = text[6:]
        clicks_count = await get_clicks_count(BITLY_TOKEN, text)
        if isinstance(clicks_count, int):
            response = CLICKS_COUNT.format(clicks_count)
        else:
            if not text.startswith('https://'):
                text = 'https://' + text
            short_link = await shorten_url(BITLY_TOKEN, text)
            print(short_link)
            if short_link:
                response = short_link
            else:
                response = 'bad url'

    print(msg)

    user_id = msg['from']['id']

    await bot.sendMessage(user_id, response, disable_web_page_preview=True)


load_dotenv()
BITLY_TOKEN = os.getenv("TOKEN")
BOT_TOKEN = os.getenv("TG_TOKEN")
bot = telepot.aio.Bot(BOT_TOKEN)
loop = asyncio.get_event_loop()

loop.create_task(MessageLoop(bot, handle).run_forever())
print('Listening ...')

loop.run_forever()





