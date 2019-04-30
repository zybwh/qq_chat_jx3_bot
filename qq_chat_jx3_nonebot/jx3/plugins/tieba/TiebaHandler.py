import aiohttp
import aiofiles
import nonebot
import os
import time
import logging
import json

from bs4 import BeautifulSoup

DATABASE_PATH = os.path.join(os.getcwd(), 'data')
tieba_data_json = os.path.join(DATABASE_PATH, 'tieba_data.json')
tieba_data = {'shu_dong': {}, "818": {}, 'other': {}}

if not os.path.exists(DATABASE_PATH):
    os.makedirs(DATABASE_PATH)

try:
    if os.path.exists(tieba_data_json):
        with open(tieba_data_json, 'r', encoding='utf-8') as f:
            tieba_data = json.loads(f.readline())
except Exception as e:
    logging.exception(e)

template_url = 'https://tieba.baidu.com/f?kw=%E5%89%91%E7%BD%913&fr=index&fp=0&ie=utf-8&pn={}'

def extra_from_one_page(page_list):
    for i in page_list:
        try:
            if int(i.find(class_='threadlist_rep_num').text) > 200:
                field = ""

                if '树洞' in i.find(class_='threadlist_title').text:
                    field = 'shu_dong'
                elif '818' in i.find(class_='threadlist_title').text:
                    field = '818'
                else:
                    field = 'other'

                name = i.find(class_='threadlist_title').text.strip('\n')
                address = f"https://tieba.baidu.com{i.find(class_='threadlist_title').a['href']}"
                num = int(i.find(class_='threadlist_rep_num').text)

                logging.info(f"{address} {name} {num}")

                if address not in tieba_data[field]:
                    tieba_data[field][address] = {
                        'name': name,
                        'num': num,
                        'last_update_time': time.time()
                    }
                else:
                    tieba_data[field][address]['num'] = num
                    tieba_data[field][address]['last_update_time'] = time.time()

        except:
            pass

async def search_n_pages(n):
    i = 0
    while i < n:
        time.sleep(0.2)
        try:
            logging.info(f'getting from data tieba... page: {i}')
            target_url = template_url.format(50*i)

            t1 = time.time()
            async with aiohttp.ClientSession() as session:
                async with session.get(target_url) as response:
                    data = await response.text()
                    t2 = time.time()
                    print(f'one page time: {t2 - t1}')
                    page_list = BeautifulSoup(data, 'html.parser').find_all(class_='j_thread_list')
                    t3 = time.time()
                    print(f'bs time: {t3 - t2}')

                    extra_from_one_page(page_list)
                    print(f'parse time: {time.time() - t3}')

            i += 1
        except Exception as e:
            logging.exception(e)

@nonebot.scheduler.scheduled_job('cron', hour='*')
async def _():
    t1 = time.time()
    try:
        await search_n_pages(100)
        async with aiofiles.open(tieba_data_json, 'w', encoding='utf-8') as f:
            data = {}
            for k, v in tieba_data.items():
                data[k] = {addr: v[addr] for addr in sorted(v.keys(), key=lambda x: v[x]['last_update_time'], reverse=True)}
            await f.write(json.dumps(data))
    except Exception as e:
        logging.exception(e)
    t2 = time.time()
    logging.info(f"tieba job complete in {t2 - t1} seconds")
    print(f"tieba job complete in {t2 - t1} seconds")
