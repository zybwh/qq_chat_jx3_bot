import aiohttp
import aiofiles
import nonebot
import os
import time
import logging
import json
import random

from bs4 import BeautifulSoup

DATABASE_PATH = os.path.join(os.getcwd(), 'data')
tieba_data_json = os.path.join(DATABASE_PATH, 'tieba_data.json')
tieba_data = {'shu_dong': {}, "818": {}, 'other': {}}
last_update_time = 0
NEED_REFREST_TIME = 30 * 60
is_retriving = False

DISPLAY_NAME = {
    'shu_dong': '树洞',
    '818': '818',
    'other': '帖子'
}

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
            if int(i.find(class_='threadlist_rep_num').text) > 0:
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
                    page_list = BeautifulSoup(data, 'html.parser').find_all(class_='j_thread_list')
                    t3 = time.time()
                    extra_from_one_page(page_list)
                    logging.info(f"time for request: {t2-t1} bs: {t3-t2} parsing: {time.time()-t3}")
            i += 1
        except Exception as e:
            logging.exception(e)

@nonebot.on_command('818')
async def do_818(session):
    await get_tieba_info(session, '818')

@nonebot.on_command('树洞')
async def do_shu_dong(session):
    await get_tieba_info(session, 'shu_dong')

@nonebot.on_command('随机帖子')
async def do_shu_dong(session):
    await get_tieba_info(session, 'other')

@nonebot.on_natural_language(keywords={'818'})
async def natural_818(session):
    print('HAHAHHA')
    return nonebot.IntentCommand(100, '818')

@nonebot.on_natural_language(keywords={'树洞'})
async def natural_shu_dong(session):
    return nonebot.IntentCommand(100, '树洞')

async def get_tieba_info(session, msg_type):
    global last_update_time, is_retriving
    user_id = str(session.ctx.get('user_id', ''))
    raw_message = session.ctx.get('raw_message')

    msg_count = 5
    num = 200
    random_id = 0

    if '更多' in raw_message:
        msg_count = 10
    
    if '最新' in raw_message:
        num = 0

    if '随机' in raw_message and len(tieba_data[msg_type]) > 0:
        msg_count = 1
        random_id = random.randint(0, len(tieba_data[msg_type]) - 1)

    if tieba_data[msg_type] == {} or time.time() - last_update_time > NEED_REFREST_TIME:
        await session.send(f"[CQ:at,qq={user_id}] 正在获取贴吧关于【{DISPLAY_NAME[msg_type]}】的最新信息，请稍后")
        await get_some_tieba_data()

    msg = f"[CQ:at,qq={user_id}] 您要的{DISPLAY_NAME[msg_type]}在这里："

    if random_id != 0:
        key = list(tieba_data[msg_type].keys())[random_id]
        msg += f"\n{key} {tieba_data[msg_type][key]['name']} {tieba_data[msg_type][key]['num']}"
    else:
        count = 0
        for k in sorted(tieba_data[msg_type].keys(), key=lambda x: tieba_data[msg_type][x]['last_update_time']):
            if tieba_data[msg_type][k]['num'] < num:
                continue
            msg += f"\n{k} {tieba_data[msg_type][k]['name']} {tieba_data[msg_type][k]['num']}"
            count += 1
            if count >= msg_count:
                break

    await session.finish(msg)

async def get_some_tieba_data():
    await get_tieba_data_internal(5)

@nonebot.scheduler.scheduled_job('cron', hour='*')
async def _():
    await get_tieba_data_internal(50)
    

async def get_tieba_data_internal(num):
    global last_update_time, is_retriving

    if is_retriving:
        last_update_time = time.time()
        return
    
    is_retriving = True

    t1 = time.time()
    try:
        await search_n_pages(num)
        async with aiofiles.open(tieba_data_json, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(tieba_data))
        last_update_time = time.time()
    except Exception as e:
        logging.exception(e)
    t2 = time.time()
    logging.info(f"tieba job complete in {t2 - t1} seconds")

    is_retriving = False