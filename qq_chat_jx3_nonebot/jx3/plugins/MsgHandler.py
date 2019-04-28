import os
import json
import logging
import datetime
import pytz

DATABASE_PATH = os.path.join(os.getcwd(), 'data')
GROUP_DATA_JSON_FILE = os.path.join(DATABASE_PATH, 'jx3_group.json')
LOG_FILE_NAME = os.path.join(DATABASE_PATH, 'bot.log')

logging.basicConfig(
    level       = logging.INFO,
    format      = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt     = '%Y-%m-%d %H:%M:%S',
    filename    = LOG_FILE_NAME,
    filemode    = 'w+'
)

import aiofiles

from nonebot import on_command, CommandSession, get_bot, scheduler, on_natural_language, NLPSession, IntentCommand, Message, permission

from .jx3.GameConfig import *
from .jx3.Jx3Handler import *

group_data = {}
active_group = []

BOT_START = False

bot = get_bot()

@bot.server_app.before_serving
async def start():
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

        @scheduler.scheduled_job('cron', hour='0')
        async def _():
            try:
                os.rename(LOG_FILE_NAME, os.path.join(DATABASE_PATH, f"{datetime.date.today().strftime('%Y-%m-%d')}.log"))
            except Exception as e:
                logging.exception(e)

    except Exception as e:
        logging.exception(e)

class check_user_register(object):
    def __init__(self, need_register: bool=True):
        self.need_register = need_register

    def __call__(self, func):
        async def wrapper(session: CommandSession):
            global BOT_START
            if not BOT_START:
                return
            return_val = False
            try:
                group_id = str(session.ctx.get('group_id', ''))
                user_id = str(session.ctx.get('user_id', ''))

                if group_id != '' and (not self.need_register or group_data[group_id].is_user_register(user_id)):
                    return_val = True

            except Exception as e:
                logging.exception(e)

            if return_val:
                await func(session, group_id, user_id)

        return wrapper

def check_to_qq_is_self_or_not_register(group_id, user_id, toQQ, self_msg='该指令无法对自己使用，'):
    if toQQ == '':
        return ""
    elif toQQ == user_id:
        return f"[CQ:at,qq={user_id}] {self_msg}"
    elif not group_data[group_id].is_user_register(toQQ):
        return f"[CQ:at,qq={user_id}] 对方尚未注册。"
    return ""

@bot.on_message('group')
async def handle_group_message(ctx):
    global BOT_START
    group_id = str(ctx.get('group_id', ''))
    user_id = str(ctx.get('user_id', ''))

    if group_id != '' and BOT_START:
        if group_id not in active_group:
            active_group.append(group_id)
            group_data[group_id] = Jx3Handler(int(group_id), DATABASE_PATH)
            async with aiofiles.open(GROUP_DATA_JSON_FILE, 'w') as f:
                await f.write(json.dumps(active_group))

        if group_data[group_id].is_user_register(user_id):
            await group_data[group_id].add_speech_count(user_id, ctx.get('raw_message'))

@on_command('test', permission=permission.SUPERUSER)
async def test(session: CommandSession):
    async with aiohttp.ClientSession().get('http://www.jx3tong.com/?m=api&c=daily&a=daily_list') as response:
        big_war_detail = json.loads(await response.text())

@on_command('开启', permission=permission.SUPERUSER)
async def start_bot(session: CommandSession):
    global BOT_START
    for group in active_group:
        try:
            await bot.send_group_msg(group_id=int(group), message=f'神小隐上线啦！更新日志请查看帮助手册：{HELP_URL}')
            await group_data[str(group)].reset_daily_count_and_start_scheduler()
        except Exception as e:
            logging.exception(e)
            pass
    BOT_START = True

    await session.finish()

@on_command('关闭', permission=permission.SUPERUSER)
async def stop_bot(session: CommandSession):
    global BOT_START
    for group in active_group:
        await bot.send_group_msg(group_id=group, message='神小隐[离线，有事请留言]')
    BOT_START = False
    for v in group_data.values():
        await v._save_data()
    await session.finish()

@on_command('剑三日常', only_to_me=False)
@check_user_register(need_register=False)
async def get_jx3_daily_info(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = group_data[group_id].get_jx3_daily_info(user_id)
    await session.finish(returnMsg)

@on_command('注册', only_to_me=False)
@check_user_register(need_register=False)
async def register(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].register(user_id)
    await session.finish(returnMsg)

@on_command('指令', aliases=['帮助', '使用手册'], only_to_me=False)
@check_user_register(need_register=False)
async def help(session: CommandSession, group_id: str="", user_id: str=""):
    await session.finish(f"神小隐说明：{HELP_URL}")

@on_command('查看阵营', aliases=['阵营信息'], only_to_me=False)
@check_user_register(need_register=False)
async def get_faction_info(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_faction_info()
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
    returnMsg = await group_data[group_id].get_equipment_info(user_id)
    await session.finish(returnMsg)

@on_command('查看名剑大会', only_to_me=False)
@check_user_register()
async def get_jjc_info(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_jjc_info(user_id)
    await session.finish(returnMsg)

@on_command('签到', only_to_me=False)
@check_user_register()
async def qiandao(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].qiandao(user_id)
    await session.finish(returnMsg)

@on_natural_language(keywords={'绑定情缘'}, only_to_me=False)
async def _(session: NLPSession):
    toQQ = [s['data']['qq'] for s in Message(session.msg.strip()) if s.get('type', '') == 'at']
    if len(toQQ) == 1 and toQQ[0] != '':
        toQQ = toQQ[0]
        return IntentCommand(100, '///jx3_handler_add_lover///', current_arg=toQQ)
    return None

@on_command('///jx3_handler_add_lover///')
@check_user_register()
async def add_lover(session: CommandSession, group_id: str="", user_id: str=""):
    toQQ = str(session.current_arg_text)
    returnMsg = check_to_qq_is_self_or_not_register(group_id, user_id, toQQ, "为什么要和自己绑定情缘？你也太惨了吧。")
    if returnMsg == "":
        returnMsg = await group_data[group_id].add_lover(user_id, toQQ)
    await session.finish(returnMsg)

@on_command('同意', only_to_me=False)
@check_user_register()
async def accept_lover(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].accept_lover(user_id)
    for msg in returnMsg:
        await session.send(msg)
    await session.finish(returnMsg)

@on_command('拒绝', only_to_me=False)
@check_user_register()
async def reject_lover(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].reject_lover(user_id)
    await session.finish(returnMsg)

@on_command('押镖', only_to_me=False)
@check_user_register()
async def ya_biao(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].ya_biao(user_id)
    await session.finish(returnMsg)

@on_command('背包', only_to_me=False)
@check_user_register()
async def check_bag(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].check_bag(user_id)
    await session.finish(returnMsg)

@on_natural_language(keywords={'加入阵营'}, only_to_me=False)
async def _(session: NLPSession):
    split_msg = session.msg.strip().split('加入阵营')
    if len(split_msg) == 2 and split_msg[0] == '' and split_msg[1] != '':
        return IntentCommand(100, '///jx3_handler_join_faction///', current_arg=split_msg[1])
    return None

@on_command('///jx3_handler_join_faction///')
@check_user_register()
async def join_faction(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].join_faction(user_id, session.current_arg_text)
    await session.finish(returnMsg)

@on_command('退出阵营', only_to_me=False)
@check_user_register()
async def quit_faction(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].quit_faction(user_id)
    await session.finish(returnMsg)

@on_command('转换阵营', only_to_me=False)
@check_user_register()
async def transfer_faction(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].transfer_faction(user_id)
    await session.finish(returnMsg)

@on_natural_language(keywords={'打劫'}, only_to_me=False)
async def _(session: NLPSession):
    toQQ = [s['data']['qq'] for s in Message(session.msg.strip()) if s.get('type', '') == 'at']
    if len(toQQ) == 1 and toQQ[0] != '':
        toQQ = toQQ[0]
        return IntentCommand(100, '///jx3_handler_rob///', current_arg=toQQ)
    return None

@on_command('///jx3_handler_rob///')
@check_user_register()
async def rob(session: CommandSession, group_id: str="", user_id: str=""):
    toQQ = str(session.current_arg_text)
    returnMsg = check_to_qq_is_self_or_not_register(group_id, user_id, toQQ, "为什么要打劫自己？")
    if returnMsg == "":
        returnMsgList = await group_data[group_id].rob(user_id, toQQ)
        for msg in returnMsgList:
            await session.send(msg)
    await session.finish(returnMsg)

@on_natural_language(keywords={'切磋'}, only_to_me=False)
async def _(session: NLPSession):
    toQQ = [s['data']['qq'] for s in Message(session.msg.strip()) if s.get('type', '') == 'at']
    if len(toQQ) == 1 and toQQ[0] != '':
        toQQ = toQQ[0]
        return IntentCommand(100, '///jx3_handler_practise///', current_arg=toQQ)
    return None

@on_command('///jx3_handler_practise///')
@check_user_register()
async def practise(session: CommandSession, group_id: str="", user_id: str=""):
    toQQ = str(session.current_arg_text)
    returnMsg = check_to_qq_is_self_or_not_register(group_id, user_id, toQQ, "这个世界里没有左右互搏。")
    if returnMsg == "":
        returnMsg = await group_data[group_id].practise(user_id, toQQ)
    await session.finish(returnMsg)

@on_natural_language(keywords={'购买'}, only_to_me=False)
async def _(session: NLPSession):
    msg_list = session.msg.strip().split("购买")
    if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "":
        msg_list_2 = msg_list[1].split("*")
        item_amount = int(msg_list_2[1]) if len(msg_list_2) == 2 and msg_list_2[1] != "" else 1

        return IntentCommand(100, '///jx3_handler_buy_item///', args={'item': msg_list_2[0], 'item_amount': item_amount})
    return None

@on_command('///jx3_handler_buy_item///', only_to_me=False)
@check_user_register()
async def buy_item(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].buy_item(user_id, session.args.get('item', ''), session.args.get('item_amount', 1))
    await session.finish(returnMsg)

@on_natural_language(keywords={'使用'}, only_to_me=False)
async def _(session: NLPSession):
    msg = ""
    toQQ = ""
    for s in Message(session.msg.strip()):
        if s.get('type', '') == 'text' and s.get('data', {}).get('text', '') != '':
            msg = s['data']['text']
        if s.get('type', '') == 'at' and s.get('data', {}).get('qq', '') != '' and toQQ == '':
            toQQ = str(s['data']['qq'])
    if msg != "":
        msg_list = msg.split("使用")
        if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "":
            msg_list_2 = msg_list[1].split("*")
            item_amount = int(msg_list_2[1]) if toQQ =="" and len(msg_list_2) == 2 and msg_list_2[1] != "" else 1

            return IntentCommand(100, '///jx3_handler_use_item///', args={'item': msg_list_2[0], 'item_amount': item_amount, 'toQQ': toQQ})
    return None

@on_command('///jx3_handler_use_item///', only_to_me=False)
@check_user_register()
async def use_item(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].use_item(user_id,
        session.args.get('item', ''),
        session.args.get('item_amount', 1),
        session.args.get('toQQ', ''))
    for msg in returnMsg:
        await session.send(msg)
    await session.finish()

@on_command('商店', only_to_me=False)
@check_user_register()
async def shop_list(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].shop_list(user_id)
    await session.finish(returnMsg)

@on_command('挖宝', only_to_me=False)
@check_user_register()
async def wa_bao(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].wa_bao(user_id)
    await session.finish(returnMsg)

@on_natural_language(keywords={'武器更名'}, only_to_me=False)
async def _(session: NLPSession):
    split_msg = session.msg.strip().split('武器更名')
    if len(split_msg) == 2 and split_msg[0] == '' and split_msg[1] != '':
        return IntentCommand(100, '///jx3_handler_change_weapon_name///', current_arg=split_msg[1])
    return None

@on_command('///jx3_handler_change_weapon_name///')
@check_user_register()
async def change_weapon_name(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].change_weapon_name(user_id, session.current_arg_text)
    await session.finish(returnMsg)

@on_natural_language(keywords={'防具更名'}, only_to_me=False)
async def _(session: NLPSession):
    split_msg = session.msg.strip().split('防具更名')
    if len(split_msg) == 2 and split_msg[0] == '' and split_msg[1] != '':
        return IntentCommand(100, '///jx3_handler_change_armor_name///', current_arg=split_msg[1])
    return None

@on_command('///jx3_handler_change_armor_name///')
@check_user_register()
async def change_armor_name(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].change_armor_name(user_id, session.current_arg_text)
    await session.finish(returnMsg)

@on_natural_language(keywords={'悬赏'}, only_to_me=False)
async def _(session: NLPSession):
    toQQ = [s['data']['qq'] for s in Message(session.msg.strip()) if s.get('type', '') == 'at']
    if len(toQQ) == 1 and toQQ[0] != '':
        toQQ = toQQ[0]
        return IntentCommand(100, '///jx3_handler_put_wanted///', current_arg=toQQ)
    return None

@on_command('///jx3_handler_put_wanted///')
@check_user_register()
async def put_wanted(session: CommandSession, group_id: str="", user_id: str=""):
    toQQ = str(session.current_arg_text)
    returnMsg = check_to_qq_is_self_or_not_register(group_id, user_id, toQQ, "为什么要悬赏自己？")
    if returnMsg == "":
        returnMsgList = await group_data[group_id].put_wanted(user_id, toQQ)
        for msg in returnMsgList:
            await session.send(msg)
    await session.finish(returnMsg)

@on_natural_language(keywords={'抓捕'}, only_to_me=False)
async def _(session: NLPSession):
    toQQ = [s['data']['qq'] for s in Message(session.msg.strip()) if s.get('type', '') == 'at']
    if len(toQQ) == 1 and toQQ[0] != '':
        toQQ = toQQ[0]
        return IntentCommand(100, '///jx3_handler_catch_wanted///', current_arg=toQQ)
    return None

@on_command('///jx3_handler_catch_wanted///')
@check_user_register()
async def catch_wanted(session: CommandSession, group_id: str="", user_id: str=""):
    toQQ = str(session.current_arg_text)
    returnMsg = check_to_qq_is_self_or_not_register(group_id, user_id, toQQ, "就算你有悬赏，也不能抓捕自己啊。")
    if returnMsg == "":
        returnMsg = await group_data[group_id].catch_wanted(user_id, toQQ)
    await session.finish(returnMsg)

@on_command('茶馆', only_to_me=False)
@check_user_register()
async def get_cha_guan_quest(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_cha_guan_quest(user_id)
    await session.finish(returnMsg)

@on_command('交任务', only_to_me=False)
@check_user_register()
async def complete_cha_guan_quest(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].complete_cha_guan_quest(user_id)
    for msg in returnMsg:
        await session.send(msg)
    await session.finish()

@on_command('抓捕混混', only_to_me=False)
@check_user_register()
async def catch_hun_hun(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].catch_hun_hun(user_id)
    await session.finish(returnMsg)

@on_command('参加名剑大会', only_to_me=False)
@check_user_register()
async def jjc(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].jjc(user_id)
    for msg in returnMsg:
        await session.send(msg)
    await session.finish()

@on_natural_language(keywords={'加入门派'}, only_to_me=False)
async def _(session: NLPSession):
    split_msg = session.msg.strip().split('加入门派')
    if len(split_msg) == 2 and split_msg[0] == '' and split_msg[1] != '':
        return IntentCommand(100, '///jx3_handler_join_class///', current_arg=split_msg[1])
    return None

@on_command('///jx3_handler_join_class///')
@check_user_register()
async def join_class(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].join_class(user_id, session.current_arg_text)
    await session.finish(returnMsg)

@on_command('挥泪斩情丝', only_to_me=False)
@check_user_register()
async def remove_lover(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].remove_lover(user_id)
    await session.finish(returnMsg)

@on_command('创建队伍', only_to_me=False)
@check_user_register()
async def create_group(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].create_group(user_id)
    await session.finish(returnMsg)

@on_natural_language(keywords={'加入队伍'}, only_to_me=False)
async def _(session: NLPSession):
    toQQ = [s['data']['qq'] for s in Message(session.msg.strip()) if s.get('type', '') == 'at']
    if len(toQQ) == 1 and toQQ[0] != '':
        toQQ = toQQ[0]
        return IntentCommand(100, '///jx3_handler_join_group///', current_arg=toQQ)
    return None

@on_command('///jx3_handler_join_group///')
@check_user_register()
async def join_group(session: CommandSession, group_id: str="", user_id: str=""):
    toQQ = str(session.current_arg_text)
    returnMsg = check_to_qq_is_self_or_not_register(group_id, user_id, toQQ, "无法加入自己的队伍。")
    if returnMsg == "":
        returnMsg = await group_data[group_id].join_group(user_id, toQQ)
    await session.finish(returnMsg)

@on_command('查看队伍', only_to_me=False)
@check_user_register()
async def get_group_info(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_group_info(user_id)
    await session.finish(returnMsg)

@on_command('队伍列表', only_to_me=False)
@check_user_register()
async def get_group_list(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_group_list(user_id)
    await session.finish(returnMsg)

@on_command('退出队伍', only_to_me=False)
@check_user_register()
async def quit_group(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].quit_group(user_id)
    await session.finish(returnMsg)

@on_command('副本列表', only_to_me=False)
@check_user_register()
async def list_dungeon(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].list_dungeon(user_id)
    await session.finish(returnMsg)

@on_natural_language(keywords={'查看副本'}, only_to_me=False)
async def _(session: NLPSession):
    split_msg = session.msg.strip().split('查看副本')
    if len(split_msg) == 2 and split_msg[0] == '' and split_msg[1] != '':
        return IntentCommand(100, '///jx3_handler_get_dungeon_info///', current_arg=split_msg[1])
    return None

@on_command('///jx3_handler_get_dungeon_info///')
@check_user_register()
async def get_dungeon_info(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_dungeon_info(user_id, session.current_arg_text)
    await session.finish(returnMsg)

@on_natural_language(keywords={'进入副本'}, only_to_me=False)
async def _(session: NLPSession):
    split_msg = session.msg.strip().split('进入副本')
    if len(split_msg) == 2 and split_msg[0] == '' and split_msg[1] != '':
        return IntentCommand(100, '///jx3_handler_start_dungeon///', current_arg=split_msg[1])
    return None

@on_command('///jx3_handler_start_dungeon///')
@check_user_register()
async def start_dungeon(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].start_dungeon(user_id, session.current_arg_text)
    for msg in returnMsg:
        await session.send(msg)
    await session.finish()

@on_command('攻击boss', only_to_me=False)
@check_user_register()
async def attack_boss(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].attack_boss(user_id)
    for msg in returnMsg:
        await session.send(msg)
    await session.finish()

@on_command('查看boss', only_to_me=False)
@check_user_register()
async def get_current_boss_info(session: CommandSession, group_id: str="", user_id: str=""):
    returnMsg = await group_data[group_id].get_current_boss_info(user_id)
    await session.finish(returnMsg)

@on_command('设置闹钟', only_to_me=False)
async def add_scheduler(session: CommandSession):
    group_id = str(session.ctx.get('group_id', ''))
    user_id = str(session.ctx.get('user_id', ''))

    raw_message = session.ctx.get('raw_message')
    time = int(session.current_arg)

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
    stripped_msg = session.msg_text.strip().split("设置闹钟")

    if len(stripped_msg) == 2 and stripped_msg[0] == '' and stripped_msg[1] != '':
        try:
            time = int(stripped_msg[1])
        except ValueError:
            pass
        else:
            return IntentCommand(100, '设置闹钟', current_arg=time)

    return None
