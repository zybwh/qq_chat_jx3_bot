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

from nonebot import on_command, CommandSession, get_bot, scheduler, on_natural_language, NLPSession, IntentCommand, Message, MessageSegment

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

class check_user_register(object):
    def __init__(self, need_register: bool=True):
        self.need_register = need_register
    
    def __call__(self, func):
        async def wrapper(session: CommandSession):
            return_val = False
            try:
                group_id = str(session.ctx.get('group_id', ''))
                user_id = str(session.ctx.get('user_id', ''))
                print(session.cmd.name)
                if group_id != '':
                    if group_id not in active_group:
                        active_group.append(group_id)
                        group_data[group_id] = Jx3Handler(int(group_id), DATABASE_PATH)
                        async with aiofiles.open(GROUP_DATA_JSON_FILE, 'w') as f:
                            await f.write(json.dumps(active_group))
                    
                    if group_data[group_id].is_user_register(user_id):
                        group_data[group_id].add_speech_count(user_id)
                    
                    if not self.need_register or group_data[group_id].is_user_register(user_id):
                        return_val = True

            except Exception as e:
                logging.exception(e)
            finally:
                if return_val:
                    await func(session, group_id, user_id)

        return wrapper


@bot.on_message('group')
async def handle_group_message(ctx):
    pass
    # try:
    #     group_id = str(ctx.get('group_id', ''))
    #     if group_id != '' and group_id not in active_group:
    #         active_group.append(group_id)
    #         group_data[group_id] = Jx3Handler(int(group_id), DATABASE_PATH)

    #         async with aiofiles.open(GROUP_DATA_JSON_FILE, 'w') as f:
    #             await f.write(json.dumps(active_group))

    #     user_id = str(ctx.get('user_id', ''))
    #     if user_id != '' and group_data[group_id].is_user_register(user_id):
    #         group_data[group_id].add_speech_count(user_id)

    # except Exception as e:
    #     print(e)
    #     logging.exception(e)

@on_command('注册', only_to_me=False)
@check_user_register(need_register=False)
async def register(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = group_data[group_id].register(user_id)
    await session.finish(returnMsg)

@on_command('指令', aliases=['帮助', '使用手册'], only_to_me=False)
@check_user_register(need_register=False)
async def help(session: CommandSession, group_id: str="", user_id: str=""):
    await session.finish("神小隐说明：{0}".format(HELP_URL))

@on_command('查看阵营', aliases=['阵营信息'], only_to_me=False)
@check_user_register(need_register=False)
async def get_faction_info(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = group_data[group_id].get_faction_info()
    await session.finish(returnMsg)

@on_command('查看悬赏', aliases=['悬赏排行'], only_to_me=False)
@check_user_register(need_register=False)
async def get_wanted_list(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_wanted_list()
    await session.finish(returnMsg)

@on_command('名剑大会排行', only_to_me=False)
@check_user_register(need_register=False)
async def get_jjc_rank(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_jjc_rank()
    await session.finish(returnMsg)

@on_command('pve装分排行', aliases=['Pve装分排行', 'PVE装分排行'], only_to_me=False)
@check_user_register(need_register=False)
async def get_pve_gear_point_rank(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_pve_gear_point_rank()
    await session.finish(returnMsg)

@on_command('pvp装分排行', aliases=['Pvp装分排行', 'PVP装分排行'], only_to_me=False)
@check_user_register(need_register=False)
async def get_pvp_gear_point_rank(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_pvp_gear_point_rank()
    await session.finish(returnMsg)

@on_command('土豪排行', aliases=['金钱排行', '财富排行'], only_to_me=False)
@check_user_register(need_register=False)
async def get_money_rank(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_money_rank()
    await session.finish(returnMsg)

@on_command('聊天排行', aliases=['水群排行'], only_to_me=False)
@check_user_register(need_register=False)
async def get_speech_rank(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_speech_rank()
    print(returnMsg)
    await session.finish(returnMsg)

@on_command('奇遇排行', only_to_me=False)
@check_user_register(need_register=False)
async def get_qiyu_rank(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_qiyu_rank()
    await session.finish(returnMsg)

@on_command('威望排行', only_to_me=False)
@check_user_register(need_register=False)
async def get_weiwang_rank(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_weiwang_rank()
    await session.finish(returnMsg)

@on_command('查看', only_to_me=False)
@check_user_register()
async def get_info(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_info(user_id)
    await session.finish(returnMsg)

@on_command('查看装备', aliases=['装备信息'], only_to_me=False)
@check_user_register()
async def get_equipment_info(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = group_data[group_id].get_equipment_info(user_id)
    await session.finish(returnMsg)

@on_command('查看名剑大会', only_to_me=False)
@check_user_register()
async def get_jjc_info(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = group_data[group_id].get_jjc_info(user_id)
    await session.finish(returnMsg)

@on_command('签到', only_to_me=False)
@check_user_register()
async def qiandao(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = group_data[group_id].qiandao(user_id)
    await session.finish(returnMsg)

@on_natural_language(keywords={'绑定情缘'}, only_to_me=False)
async def _(session: NLPSession):
    toQQ = [s['data']['qq'] for s in Message(session.msg) if s.get('type', '') == 'at']
    print(toQQ)

    if len(toQQ) == 1 and toQQ[0] != '':
        toQQ = toQQ[0]
        return IntentCommand(100, '绑定情缘', current_arg=toQQ)

    return None

@on_command('绑定情缘', only_to_me=False)
@check_user_register()
async def add_lover(session: CommandSession, group_id: str="", user_id: str=""):
    toQQ = str(session.current_arg_text)
    if toQQ == user_id:
        returnMsg = f"[CQ:at,qq={user_id}] 为什么要和自己绑定情缘？你也太惨了吧。"
    elif not group_data[group_id].is_user_register(toQQ):
        returnMsg = f"[CQ:at,qq={user_id}] 对方尚未注册。"
    else:
        returnMsg = group_data[group_id].add_lover(user_id, toQQ)
    await session.finish(returnMsg)

@on_command('设置闹钟', only_to_me=False)
async def add_scheduler(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))
    user_id = str(session.ctx.get('user_id', ''))

    print(session.current_arg_text)
    raw_message = session.ctx.get('raw_message')
    time = int(raw_message.split("设置闹钟 ")[1])

    time = 10
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
            session.state
        except ValueError:
            pass
        else:
            return IntentCommand(100, '设置闹钟', current_arg=time)
    
    return None