import os
import json
import logging
import datetime
import pytz

logging.basicConfig(
    level       = logging.INFO,
    format      = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt     = '%Y-%m-%d %H:%M:%S',
    filename    = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'bot.log'),
    filemode    = 'w+'
)

import aiofiles

from nonebot import on_command, CommandSession, get_bot, scheduler, on_natural_language, NLPSession, IntentCommand

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
        group_id = str(ctx.get('group_id', ''))
        if group_id != '' and group_id not in active_group:
            active_group.append(group_id)
            group_data[group_id] = Jx3Handler(int(group_id), DATABASE_PATH)

            async with aiofiles.open(GROUP_DATA_JSON_FILE, 'w') as f:
                await f.write(json.dumps(active_group))

        user_id = str(ctx.get('user_id', ''))
        if user_id != '' and group_data[group_id].is_user_register(user_id):
            group_data[group_id].add_speech_count(user_id)
        
        if '设置闹钟' in ctx.get('raw_message'):
            split_msg = ctx.get('raw_message').split('设置闹钟')
            ctx['raw_message'] = ' '.join(['设置闹钟', split_msg[1]])

            # data = group_data[group_id].dump_data()
            # await _write_game_data(group_id, data)

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
    group_id = str(session.ctx.get('group_id', ''))
    user_id = str(session.ctx.get('user_id', ''))

    print(session.ctx)
    if group_id != None:
        returnMsg = group_data[group_id].register(user_id)
        await session.finish(returnMsg)

@on_command('指令', aliases=['帮助', '使用手册'], only_to_me=False)
async def help(session: CommandSession):
    group_id = session.ctx.get('group_id')
    await session.finish("神小隐说明：{0}".format(HELP_URL))

@on_command('查看', only_to_me=False)
async def get_info(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))
    user_id = str(session.ctx.get('user_id', ''))

    if group_id != "" and group_data[group_id].is_user_register(user_id):
        returnMsg = await group_data[group_id].get_info(user_id)
        await session.finish(returnMsg)

@on_command('查看装备', aliases=['装备信息'], only_to_me=False)
async def get_equipment_info(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))
    user_id = str(session.ctx.get('user_id', ''))

    if group_id != "" and group_data[group_id].is_user_register(user_id):
        returnMsg = group_data[group_id].get_equipment_info(user_id)
        await session.finish(returnMsg)

@on_command('查看阵营', only_to_me=False)
async def get_faction_info(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))

    if group_id != "":
        returnMsg = group_data[group_id].get_faction_info()
        await session.finish(returnMsg)

@on_command('查看悬赏', aliases=['悬赏排行'], only_to_me=False)
async def get_wanted_list(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))

    if group_id != "":
        returnMsg = await group_data[group_id].get_wanted_list()
        await session.finish(returnMsg)

@on_command('查看名剑大会', only_to_me=False)
async def get_equipment_info(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))
    user_id = str(session.ctx.get('user_id', ''))

    if group_id != "" and group_data[group_id].is_user_register(user_id):
        returnMsg = group_data[group_id].get_jjc_info(user_id)
        await session.finish(returnMsg)

@on_command('名剑大会排行', only_to_me=False)
async def get_equipment_info(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))

    if group_id != "":
        returnMsg = await group_data[group_id].get_jjc_rank()
        await session.finish(returnMsg)

@on_command('pve装分排行', aliases=['Pve装分排行', 'PVE装分排行'], only_to_me=False)
async def get_pve_gear_point_rank(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))

    if group_id != "":
        returnMsg = await group_data[group_id].get_pve_gear_point_rank()
        await session.finish(returnMsg)

@on_command('pvp装分排行', aliases=['Pvp装分排行', 'PVP装分排行'], only_to_me=False)
async def get_pvp_gear_point_rank(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))

    if group_id != "":
        returnMsg = await group_data[group_id].get_pvp_gear_point_rank()
        await session.finish(returnMsg)

@on_command('土豪排行', aliases=['金钱排行', '财富排行'], only_to_me=False)
async def get_money_rank(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))

    if group_id != "":
        returnMsg = await group_data[group_id].get_money_rank()
        await session.finish(returnMsg)

@on_command('聊天排行', aliases=['水群排行'], only_to_me=False)
async def get_speech_rank(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))

    if group_id != "":
        returnMsg = await group_data[group_id].get_speech_rank()
        await session.finish(returnMsg)

@on_command('奇遇排行', only_to_me=False)
async def get_qiyu_rank(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))

    if group_id != "":
        returnMsg = await group_data[group_id].get_qiyu_rank()
        await session.finish(returnMsg)

@on_command('威望排行', only_to_me=False)
async def get_weiwang_rank(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))

    if group_id != "":
        returnMsg = await group_data[group_id].get_weiwang_rank()
        await session.finish(returnMsg)

@on_command('签到', only_to_me=False)
async def qiandao(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))
    user_id = str(session.ctx.get('user_id', ''))

    if group_id != "" and group_data[group_id].is_user_register(user_id):
        returnMsg = group_data[group_id].qiandao(user_id)
        await session.finish(returnMsg)

@on_command('设置闹钟', only_to_me=False)
async def add_scheduler(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))
    user_id = str(session.ctx.get('user_id', ''))

    print(session.ctx)
    raw_message = session.ctx.get('raw_message')
    time = int(raw_message.split("设置闹钟 ")[1])

    time = session.state['time']
    print(time)
    print(datetime.datetime.now() + datetime.timedelta(seconds=time))
    await bot.send_group_msg(group_id=int(group_id),
        message=f'[CQ:at,qq={user_id}] 设置闹钟成功！倒计时{time}秒')

    @scheduler.scheduled_job('date', run_date=datetime.datetime.now(pytz.timezone('Asia/Shanghai')) + datetime.timedelta(seconds=time))
    async def _():
        try:
            await bot.send_group_msg(group_id=int(group_id),
                message=f'[CQ:at,qq={user_id}] 闹钟响啦！')
        except Exception as e:
            logging.exception(e)

@on_natural_language(keywords={'设置闹钟'}, only_to_me=False)
async def _(session: NLPSession):
    print(session.msg_text)
    stripped_msg = session.msg_text.strip().split("设置闹钟")

    if len(stripped_msg) == 2 and stripped_msg[0] == '' and stripped_msg[1] != '':
        print(stripped_msg)
        try:
            time = int(stripped_msg[1])
        except ValueError:
            pass
        else:
            return IntentCommand(100, '设置闹钟')
    
    return None