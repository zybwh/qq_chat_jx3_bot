import os
import json
import logging

logging.basicConfig(
    level       = logging.INFO,
    format      = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt     = '%Y-%m-%d %H:%M:%S',
    filename    = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bot.log'),
    filemode    = 'w+'
)

import aiofiles

from nonebot import on_command, CommandSession, get_bot

from .jx3.GameConfig import *
from .jx3.Jx3Handler import *

group_data = {}
active_group = []

bot = get_bot()

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'data')
GROUP_DATA_JSON_FILE = os.path.join(DATABASE_PATH, 'jx3_group.json')

try:
    if not os.path.exists(DATABASE_PATH):
        os.makedirs(DATABASE_PATH)

    if os.path.exists(GROUP_DATA_JSON_FILE):
        with open(GROUP_DATA_JSON_FILE, 'r') as f:
            group_file_data = json.loads(f.readline())
            for group in group_file_data:
                active_group.append(group)
                group_data[str(group)] = Jx3Handler(int(group), DATABASE_PATH)

            print(group_data)
    print('load group complete')
except Exception as e:
    logging.exception(e)


@bot.on_message('group')
async def handle_group_message(ctx):
    try:
        group_id = ctx.get('group_id')
        if group_id != None and group_id not in active_group:
            active_group.append(group_id)
            group_data[str(group_id)] = Jx3Handler(int(group_id))

            async with aiofiles.open(GROUP_DATA_JSON_FILE, 'w') as f:
                await f.write(json.dumps(active_group))

        user_id = ctx.get('user_id')
        if user_id != None and group_data[str(group_id)].is_user_register(user_id):
            group_data[str(group_id)].add_speech_count(user_id)
            data = group_data[str(group_id)].dump_data()
            await _write_game_data(group_id, data)

    except Exception as e:
        print(e)
        logging.exception(e)

async def _write_game_data(qq_group, data):
    try:
        json_file_dir = os.path.join(DATABASE_PATH, str(qq_group))
        if not os.path.exists(json_file_dir):
            os.makedirs(json_file_dir)

        json_file_path = os.path.join(json_file_dir, 'data.json')
        json_file_path_old = os.path.join(json_file_dir, 'data.json.old')
        json_file_path_old_2 = os.path.join(json_file_dir, 'data.json.old2')

        if os.path.exists(json_file_path_old):
            if os.path.exists(json_file_path_old_2):
                os.remove(json_file_path_old_2)
            os.rename(json_file_path_old, json_file_path_old_2)
                
        if os.path.exists(json_file_path):
            if os.path.exists(json_file_path_old):
                os.remove(json_file_path_old)
            os.rename(json_file_path, json_file_path_old)

        async with aiofiles.open(json_file_path, 'w') as f:
            await f.write(json.dumps(data))
    except Exception as e:
        logging.exception(e)

async def get_group_nickname(ctx, group_id, qq_id):
    info = await bot.get_group_member_info(group_id=int(group_id), user_id=int(qq_id))
    ctx['lover_nickname'] = info['card'] if info['card'] != "" else info['nickname']

@on_command('注册', only_to_me=False)
async def register(session: CommandSession):
    group_id = session.ctx.get('group_id')
    print(session.ctx)
    if group_id != None:
        returnMsg = group_data[str(group_id)].register(session.ctx.get('user_id'))

        data = group_data[str(group_id)].dump_data()
        await _write_game_data(group_id, data)
        for msg in returnMsg:
            await session.finish(msg)

@on_command('指令', aliases=['帮助', '使用手册'], only_to_me=False)
async def help(session: CommandSession):
    group_id = session.ctx.get('group_id')
    await session.finish("神小隐说明：{0}".format(HELP_URL))

@on_command('查看', only_to_me=False)
async def get_info(session: CommandSession):
    group_id = session.ctx.get('group_id')
    if group_id != None:
        user_id = session.ctx.get('user_id')
        if group_data[str(group_id)].is_user_register(user_id):
            returnMsg = await group_data[str(group_id)].get_info(user_id)
            for msg in returnMsg:
                await session.finish(msg)

@on_command('签到', only_to_me=False)
async def qiandao(session: CommandSession):
    group_id = session.ctx.get('group_id')
    if group_id != None:
        user_id = session.ctx.get('user_id')
        if group_data[str(group_id)].is_user_register(user_id):
            returnMsg = group_data[str(group_id)].qiandao(user_id)
            
            data = group_data[str(group_id)].dump_data()
            await _write_game_data(group_id, data)
            for msg in returnMsg:
                await session.finish(msg)