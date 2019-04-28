import random
import logging
import os
import json
import copy
import time
import datetime
import math

import aiofiles
import aiohttp

from nonebot import get_bot, scheduler

from .Jx3Class import *
from .Jx3User import *
from .Jx3Faction import *
from .Jx3Qiyu import *
from .Jx3Item import *
from .Jx3Dungeon import *
from .GameConfig import *
from .Utils import *

class Jx3Handler(object):

    class data_handler(object):
        def __init__(self, read_only: bool=False, return_list: bool=False, async_func=False):
            self.read_only = read_only
            self.return_list = return_list
            self.async_func = async_func

        def __call__(self, func):
            async def wrapper(jx3Handler, *args, **kwargs) -> str:
                try:
                    if self.async_func:
                        return_val = await func(jx3Handler, *args, **kwargs)
                    else:
                        return_val = func(jx3Handler, *args, **kwargs)

                    is_qiyu = await jx3Handler.do_qiyu()

                    if is_qiyu or not self.read_only:
                        await jx3Handler._save_data()

                    return return_val
                except Exception as e:
                    logging.exception(e)
                    jx3Handler._read_data()
                    return [] if self.return_list else ""

            return wrapper

    json_file_path = ""

    _jx3_users = {}
    _today = 0
    _jx3_faction = copy.deepcopy(faction_daily_dict)
    _lover_pending = {}
    _jail_list = {}
    _group_info = {}
    _jjc_data = {
        'season': 1,
        'day': 1,
        'last_season_data': {},
        'current_season_data': {},
        'get_last_season_reward': []
    }
    _wanted_list = {}
    _rob_protect = {}
    _dungeon_status = {}
    _qiyu_status = {}

    _jx3_daily_info = []

    def __init__(self, qq_group, DATABASE_PATH):
        self._qq_group = qq_group

        self.json_dir_path = os.path.join(DATABASE_PATH, str(qq_group))
        self.json_file_path = os.path.join(self.json_dir_path, 'data.json')

        self._read_data()

    async def reset_daily_count_and_start_scheduler(self):
        await self._reset_daily_count()
        @scheduler.scheduled_job('cron', hour='7')
        async def _():
            try:
                self._reset_daily_count()
            except Exception as e:
                logging.exception(e)

    @data_handler(async_func=True)
    async def _reset_daily_count(self):
        yday = time.localtime(time.time() - DALIY_REFRESH_OFFSET).tm_yday
        if yday != self._today:
            self._today = yday

            for v in self._jx3_users.values():
                v['daily_count'] = copy.deepcopy(daily_dict)
                v['today'] = self._today

            async with aiohttp.ClientSession().get('http://www.jx3tong.com/?m=api&c=daily&a=daily_list') as response:
                jx3_daily_details = json.loads(await response.text())
                self._jx3_daily_info = jx3_daily_details['activity_data']

            big_war = ""
            battle_field = ""
            for activity in self._jx3_daily_info:
                for act in activity['activity_list']:
                    if '大战·' in act['title']:
                        big_war = act['title'].split('大战·')[1]
                    if '战场-' in act['title']:
                        battle_field = act['title'].split('战场-')[1]

            msg = (
                f"日常刷新啦\n"
                f"今日剑三大战本：{big_war}, 战场：{battle_field}"
            )
            await get_bot().send_group_msg(group_id=int(self._qq_group), message=msg)

            self._jjc_data['day'] += 1
            if self._jjc_data['day'] > JJC_DAYS_PER_SEASON:
                self._jjc_data['day'] = 1
                self._jjc_data['season'] += 1
                self._jjc_data['last_season_data'] = copy.deepcopy(self._jjc_data['current_season_data'])
                self._jjc_data['current_season_data'] = {}
                self._jjc_data['get_last_season_reward'] = []

                returnMsg = f"名剑大会赛季{self._jjc_data['season']-1}已结束！赛季排行榜："

                rank_list = sorted(self._jjc_data['last_season_data'], key=lambda x: self._jjc_data['last_season_data'][x]['score'], reverse=True)
                list_len = len(rank_list)
                for i in range(5):
                    if i < list_len and self._jjc_data['last_season_data'][rank_list[i]]['score'] != 0:
                        qq_nickname = await get_group_nickname(self._qq_group, rank_list[i])
                        score = self._jjc_data['last_season_data'][rank_list[i]]['score']
                        returnMsg += (
                            f"\n{i + 1}. {qq_nickname} "
                            f"分数：{score} 段位：{min(score // 100, MAX_JJC_RANK)}"
                        )
                    else:
                        break
                await get_bot().send_group_msg(group_id=int(self._qq_group), message=returnMsg)

    async def _save_data(self):
        try:
            if not os.path.exists(self.json_dir_path):
                os.makedirs(self.json_dir_path)

            json_file_path = os.path.join(self.json_dir_path, 'data.json')
            json_file_path_old = os.path.join(self.json_dir_path, 'data.json.old')
            json_file_path_old_2 = os.path.join(self.json_dir_path, 'data.json.old2')

            if os.path.exists(json_file_path_old):
                if os.path.exists(json_file_path_old_2):
                    os.remove(json_file_path_old_2)
                os.rename(json_file_path_old, json_file_path_old_2)

            if os.path.exists(json_file_path):
                if os.path.exists(json_file_path_old):
                    os.remove(json_file_path_old)
                os.rename(json_file_path, json_file_path_old)

            async with aiofiles.open(json_file_path, 'w', encoding='utf-8') as f:
                data = self._dump_data()
                await f.write(json.dumps(data))
        except Exception as e:
            logging.exception(e)

    def _read_data(self):
        try:
            game_data = {}
            if os.path.exists(self.json_file_path):
                with open(self.json_file_path, 'r', encoding='utf-8') as f:
                    game_data = json.loads(f.readline())

            self._qiyu_status = game_data.get('qiyu', {})

            self._load_user_data(game_data.get('jx3_users', {}))
            self._load_equipment(game_data.get('equipment', {}))
            self._load_daily_count(game_data.get('daily_action_count', {}))

            self._jx3_faction = game_data.get('jx3_faction', self._jx3_faction)
            self._lover_pending = game_data.get('lover_pending', {})
            self._jail_list = game_data.get('jail_list', {})
            self._today = game_data.get('today', 0)
            self._group_info = game_data.get('group_info', {})
            self._jjc_data = game_data.get('jjc_data', self._jjc_data)
            self._wanted_list = game_data.get('wanted_list', {})
            self._rob_protect = game_data.get('rob_protect', {})
            self._jx3_daily_info = game_data.get('jx3_daily_info', [])
            self._dungeon_status = game_data.get('dungeon_status', {})
        except Exception as e:
            logging.exception(e)

    def _load_user_data(self, user_data):
        try:
            for k, v in user_data.items():
                val = copy.deepcopy(v)
                if isinstance(val['class_id'], int):
                    val['class_id'] = OLD_CLASS_LIST_TO_NEW_LIST[val['class_id']]
                if isinstance(val['faction_id'], int):
                    val['faction_id'] = OLD_FACTION_LIST[val['faction_id']]
                if isinstance(val['qiyu'], int):
                    val['qiyu'] = {'unknown': val['qiyu']}

                self._jx3_users[str(k)] = val
                if str(k) not in self._qiyu_status:
                    self._qiyu_status[str(k)] = {'pending_qiyu': "", 'cd': {}, 'has_qiyu_in_same_command': False}
        except Exception as e:
            logging.exception(e)

    def _load_equipment(self, equipment_data):
        if equipment_data != {}:
            for k, v in equipment_data.items():
                if k in self._jx3_users:
                    self._jx3_users[k]['equipment'] = copy.deepcopy(v)

    def _load_daily_count(self, daily_count_data):
        if daily_count_data == {}:
            return
        sorted_list = sorted(daily_count_data['daily_action_count'].items, key=lambda x: int(x[0]), reverse=True)
        day, count_list = sorted_list.items()[0]
        for k, v in count_list.items():
            if k in self._jx3_users:
                self._jx3_users[k]['day'] = day
                self._jx3_users[k]['daily_count'] = copy.deepcopy(v)

    def _dump_data(self):
        try:
            data = {
                "jx3_users": self._jx3_users,
                "jx3_faction": self._jx3_faction,
                "lover_pending": self._lover_pending,
                "jail_list": self._jail_list,
                "today": self._today,
                "group_info": self._group_info,
                "jjc_data": self._jjc_data,
                "wanted_list": self._wanted_list,
                "rob_protect": self._rob_protect,
                "dungeon_status": self._dungeon_status,
                "jx3_daily_info": self._jx3_daily_info,
                "qiyu":self._qiyu_status
            }
            return data
        except Exception as e:
            logging.exception(e)

            
    @data_handler()
    def add_speech_count(self, qq_account: str, msg: str):
        self._jx3_users[qq_account]['daily_count']['speech_count'] += 1

        if self._jx3_users[qq_account]['daily_count']['speech_energy_gain'] < DALIY_MAX_SPEECH_ENERGY_GAIN:
            self._jx3_users[qq_account]['daily_count']['speech_energy_gain'] += SPEECH_ENERGY_GAIN
            self._jx3_users[qq_account]['energy'] += SPEECH_ENERGY_GAIN
        
        if qq_account not in self._qiyu_status:
            self._qiyu_status[qq_account] = {'pending_qiyu': '', 'cd': {}}
        
        self._qiyu_status[qq_account]['pending_qiyu'] = 'luan_shi_wu_ji' if '[CQ:image,file=' in msg else 'fu_yao_jiu_tian' 

    @data_handler()
    def register(self, qq_account: str):
        if qq_account in self._jx3_users:
            return f"[CQ:at,qq={qq_account}] 注册失败！你已经注册过了。"
        else:
            self._jx3_users[qq_account] = {
                'class_id': 'da_xia',
                'faction_id': 'zhong_li',
                'faction_join_time': None,
                'weiwang': 0,
                'banggong': 0,
                'money': 0,
                'energy': 0,
                'achievement': {},
                'lover': '',
                'lover_time': None,
                'qiyu': {},
                'register_time': time.time(),
                'bag': {},
                'equipment': copy.deepcopy(default_equipment),
                'today': self._today,
                'daily_count': copy.deepcopy(daily_dict),
                'qiandao_count': 0
            }
            return (
                f"注册成功！\n"
                f"[CQ:at,qq={qq_account}]\n"
                f"注册时间：{time.strftime('%Y-%m-%d', time.localtime(self._jx3_users[qq_account]['register_time']))}"
            )

    def is_user_register(self, qq_account: str):
        return qq_account in self._jx3_users

    @data_handler(read_only=True, async_func=True)
    async def get_info(self, qq_account: str):
        lover_name = await get_group_nickname(self._qq_group, self._jx3_users[qq_account]['lover']) if self._jx3_users[qq_account]['lover'] != "" else ""
        return (
            f"[CQ:at,qq={qq_account}]\n"
            f"情缘:\t\t{lover_name}\n"
            f"门派:\t\t{CLASS_LIST[self._jx3_users[qq_account]['class_id']]}\n"
            f"阵营:\t\t{FACTION_LIST[self._jx3_users[qq_account]['faction_id']]}\n"
            f"威望:\t\t{self._jx3_users[qq_account]['weiwang']}\n"
            f"帮贡:\t\t{self._jx3_users[qq_account]['banggong']}\n"
            f"金钱:\t\t{self._jx3_users[qq_account]['money']}G\n"
            f"体力:\t\t{self._jx3_users[qq_account]['energy']}\n"
            f"签到状态:\t{'已签到' if self._jx3_users[qq_account]['daily_count']['qiandao'] else '未签到'}\n"
            f"奇遇:\t\t{get_qiyu_count(self._jx3_users[qq_account])}\n"
            f"今日发言:\t{self._jx3_users[qq_account]['daily_count']['speech_count']}"
        )

    @data_handler()
    def qiandao(self, qq_account: str):

        val = self._jx3_users[qq_account]

        if self._jx3_users[qq_account]['daily_count']['qiandao']:
            returnMsg = f"[CQ:at,qq={qq_account}]今天已经签到过了!"
        else:
            banggong_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)
            weiwang_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)

            self._jx3_users[qq_account]['weiwang'] += weiwang_reward
            self._jx3_users[qq_account]['banggong'] += banggong_reward
            self._jx3_users[qq_account]['money'] += DALIY_MONEY_REWARD
            self._jx3_users[qq_account]['energy'] += DALIY_ENERGY_REWARD

            self._jx3_users[qq_account]['qiandao_count'] += 1

            self._jx3_users[qq_account]['daily_count']['qiandao'] = True

            returnMsg = (
                f"[CQ:at,qq={qq_account}] 签到成功！累积签到次数：{self._jx3_users[qq_account]['qiandao_count']} "
                f"签到奖励: 威望+{weiwang_reward} 帮贡+{banggong_reward} 金钱+{DALIY_MONEY_REWARD} 体力+{DALIY_ENERGY_REWARD}"
            )

            faction_reward =  self._jx3_faction[self._jx3_users[qq_account]['faction_id']]['yesterday_reward']

            if faction_reward != 0:
                self._weiwang += faction_reward
                returnMsg += f"\n获得昨日阵营奖励：威望+{faction_reward}"

            if self._jjc_data['last_season_data'] != {} and qq_account not in self._jjc_data['get_last_season_reward']:
                self._jjc_data['get_last_season_reward'].append(qq_account)
                rank = self._jjc_data['last_season_data'][qq_account]['score'] // 100

                rank_list = sorted(self._jjc_data['last_season_data'], key=lambda x: self._jjc_data['last_season_data'][x]['score'], reverse=True)
                rank_msg = ""
                i = 0
                modifier = 1
                for k in rank_list:
                    i += 1
                    if qq_account == k:
                        rank_msg = f"\n上赛季名剑大会成绩： 分数：{self._jjc_data['last_season_data'][k]['score']}，段位：{rank}，排名：{i}。"
                        if i == 1:
                            modifier = 2
                            rank_msg += "由于上赛季排名为第1，获得2倍奖励。"
                        elif i >= 2 and i <= 3:
                            modifier = 1.5
                            rank_msg += f"由于上赛季排名前3，获得{modifier}倍奖励。"


                jjc_weiwang_reward = rank * JJC_SEASON_PER_RANK_WEIWANG_REWARD
                jjc_money_reward = rank * JJC_SEASON_PER_RANK_MONEY_REWARD

                self._jx3_users[qq_account]['weiwang'] += int(jjc_weiwang_reward * modifier)
                self._jx3_users[qq_account]['money'] += int(jjc_money_reward * modifier)

                returnMsg += f"{rank_msg}\n获得上赛季名剑大会排行奖励：威望+{jjc_weiwang_reward} 金钱+{jjc_money_reward}"
                
                self._qiyu_status[qq_account]['pending_qiyu'] = 'hong_fu_qi_tian'

        return returnMsg

    @data_handler()
    def add_lover(self, fromQQ: str, toQQ: str):
        returnMsg = ""

        fromQQ_stat = self._jx3_users[fromQQ]
        toQQ_stat = self._jx3_users[toQQ]

        if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in fromQQ_stat['bag']:
            return "[CQ:at,qq={0}] 绑定情缘需要消耗1个{1}。\n你并没有此物品，请先购买。".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
        else:
            if fromQQ_stat['lover'] == toQQ:
                return f"[CQ:at,qq={fromQQ}] 你们已经绑定过啦！还想乱撒狗粮？".format()
            elif fromQQ_stat['lover'] != "":
                return f"[CQ:at,qq={fromQQ}]  想什么呢？你就不怕[CQ:at,qq={fromQQ_stat['lover']}]打你吗？"
            elif toQQ_stat['lover'] != "":
                return f"[CQ:at,qq={fromQQ}] 人家已经有情缘啦，你是想上818吗？"
            elif toQQ in self._lover_pending and self._lover_pending[toQQ] != fromQQ:
                return f"[CQ:at,qq={fromQQ}] 已经有人向[CQ:at,qq={toQQ}]求情缘啦，你是不是再考虑一下？"
            else:
                pendingList = [k for k, v in self._lover_pending.items() if v == fromQQ]
                for p in pendingList:
                    self._lover_pending.pop(p)
                self._lover_pending[toQQ] = fromQQ
                return f"[CQ:at,qq={fromQQ}] [CQ:at,qq={toQQ}] 希望与你绑定情缘，请输入 同意 或者 拒绝。"

    @data_handler(return_list=True, async_func=True)
    async def accept_lover(self, toQQ: str):
        returnMsg = []

        if toQQ in self._lover_pending.keys():
            fromQQ = self._lover_pending.pop(toQQ)

            if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in self._jx3_users[fromQQ]['bag'].keys():
                returnMsg.append(f"[CQ:at,qq={fromQQ}] 虽然人家同意了但是你并没有1个{get_item_display_name(LOVE_ITEM_REQUIRED)}。")
            else:
                self._jx3_users[fromQQ]['lover'] = toQQ
                self._jx3_users[fromQQ]['lover_time'] = time.time()
                self._jx3_users[toQQ]['lover'] = fromQQ
                self._jx3_users[toQQ]['lover_time'] = time.time()
                if LOVE_ITEM_REQUIRED != "":
                    self._jx3_users[fromQQ]['bag'][LOVE_ITEM_REQUIRED] -= 1
                    if self._jx3_users[fromQQ]['bag'][LOVE_ITEM_REQUIRED] == 0:
                        self._jx3_users[fromQQ]['bag'].pop(LOVE_ITEM_REQUIRED)

                    fromQQ_nickname = await get_group_nickname(self._qq_group, fromQQ)
                    toQQ_nickname = await get_group_nickname(self._qq_group, toQQ)

                    for m in ITEM_LIST[LOVE_ITEM_REQUIRED].get('firework', []):
                        returnMsg.append(m.format(fromQQ_nickname, toQQ_nickname))

                returnMsg.append((
                    f"[CQ:at,qq={fromQQ}] 与 [CQ:at,qq={toQQ}]，喜今日嘉礼初成，良缘遂缔。诗咏关雎，雅歌麟趾。瑞叶五世其昌，祥开二南之化。"
                    "同心同德，宜室宜家。相敬如宾，永谐鱼水之欢。互助精诚，共盟鸳鸯之誓"
                ))

        return returnMsg

    @data_handler()
    def reject_lover(self, toQQ: str):
        returnMsg = ""
        if toQQ in self._lover_pending:
            fromQQ = self._lover_pending.pop(toQQ)
            returnMsg = f"[CQ:at,qq={fromQQ}] 落花有意，流水无情， [CQ:at,qq={toQQ}]婉拒了你的请求。"

        return returnMsg

    def _is_in_jailed(self, qq_account: str):
        if qq_account in self._jail_list:
            if time.time() - self._jail_list[qq_account] < JAIL_DURATION:
                return f"[CQ:at,qq={qq_account}] 老实点，你还要在监狱里蹲{get_remaining_time_string(JAIL_DURATION, self._jail_list[qq_account])}。"
            else:
                self._jail_list.pop(qq_account)
        return ""

    @data_handler()
    def ya_biao(self, qq_account: str):
        returnMsg = ""

        val = self._jx3_users[qq_account]
        if val['faction_id'] == 'zhong_li' and not NO_FACTION_ALLOW_YA_BIAO:
            return f"[CQ:at,qq={qq_account}] 中立阵营无法押镖。"
        elif val['energy'] < YA_BIAO_ENERGY_REQUIRED:
            return f"[CQ:at,qq={qq_account}] 体力不足！无法押镖。"
        else:
            jail_status = self._is_in_jailed(qq_account)
            if jail_status != "":
                return jail_status
            else:
                if self._jx3_users[qq_account]['daily_count']['ya_biao'] < MAX_DALIY_YA_BIAO_COUNT:
                    reward = random.randint(DALIY_YA_BIAO_REWARD_MIN, DALIY_YA_BIAO_REWARD_MAX)
                    self._jx3_users[qq_account]['weiwang'] += reward
                    self._jx3_users[qq_account]['energy'] -= YA_BIAO_ENERGY_REQUIRED
                    self._jx3_users[qq_account]['money'] += DALIY_YA_BIAO_MONEY_REWARD
                    self._jx3_users[qq_account]['daily_count']["ya_biao"] += 1

                    self._jx3_faction[self._jx3_users[qq_account]['faction_id']]['faction_point'] += YA_BIAO_FACTION_POINT_GAIN

                    self._qiyu_status[qq_account]['pending_qiyu'] = 'hu_you_cang_sheng'

                    return (
                        f"[CQ:at,qq={qq_account}] 押镖成功！"
                        f"体力-{YA_BIAO_ENERGY_REQUIRED} 威望+{reward} 金钱+{DALIY_YA_BIAO_MONEY_REWARD}"
                    )
                else:
                    return f"[CQ:at,qq={qq_account}] 一天最多押镖{MAX_DALIY_YA_BIAO_COUNT}次。你已经押了{MAX_DALIY_YA_BIAO_COUNT}趟啦，明天再来吧。"

    @data_handler(read_only=True)
    def check_bag(self, qq_account):
        if self._jx3_users[qq_account]['bag'] == {}:
            itemMsg = "\n空空如也"
        else:
            itemMsg = ""
            for k, v in self._jx3_users[qq_account]['bag'].items():
                itemMsg += f"\n{get_item_display_name(k)} x {v}"

        return f"[CQ:at,qq={qq_account}] 的背包：{itemMsg}"


    @data_handler()
    def join_faction(self, qq_account: str, faction: str):
        if faction in FACTION_LIST.values():
            qq_stat = self._jx3_users[qq_account]
            qq_faction_str = FACTION_LIST[qq_stat['faction_id']]
            if faction == qq_faction_str:
                return f"[CQ:at,qq={qq_account}] 你已经加入了 {faction}。"
            elif qq_stat['faction_id'] != 'zhong_li':
                return f"[CQ:at,qq={qq_account}] 你已经加入了 {qq_faction_str}，{faction} 并不想接受你的申请。"
            else:
                remain_time = get_remaining_time_string(FACTION_REJOIN_CD_SECS, qq_stat['faction_join_time'])
                if remain_time != "":
                    return f"[CQ:at,qq={qq_account}] 由于不久前才退出阵营，你需要等待{remain_time}之后才能重新加入。"
                else:
                    self._jx3_users[qq_account]['faction_id'] = convert_display_name_to_faction_id(faction)
                    self._jx3_users[qq_account]['faction_join_time'] = time.time()
                    return f"[CQ:at,qq={qq_account}] 成功加入 {faction}。"

    @data_handler()
    def quit_faction(self, qq_account: str):
        qq_stat = self._jx3_users[qq_account]
        if qq_stat['faction_id'] == 'zhong_li':
            return f"[CQ:at,qq={qq_account}] 你并没有加入任何阵营。"
        else:
            pre_faction_id = qq_stat['faction_id']
            self._jx3_users[qq_account]['faction_id'] = "zhong_li"
            self._jx3_users[qq_account]['faction_join_time'] = time.time()
            if FACTION_QUIT_EMPTY_WEIWANG:
                self._jx3_users[qq_account]['weiwang'] = 0
            return f"[CQ:at,qq={qq_account}] 退出了江湖纷争，脱离了 {FACTION_LIST[pre_faction_id]}。"

    @data_handler()
    def transfer_faction(self, qq_account: str):
        qq_stat = self._jx3_users[qq_account]
        if qq_stat['faction_id'] == 'zhong_li':
            return f"[CQ:at,qq={qq_account}] 你并没有加入任何阵营。"
        elif qq_stat['weiwang'] < FACTION_TRANSFER_WEIWANG_COST:
            return f"[CQ:at,qq={qq_account}] 转换阵营需要消耗{FACTION_TRANSFER_WEIWANG_COST}威望，当前威望不足。"
        else:
            remain_time = get_remaining_time_string(FACTION_REJOIN_CD_SECS, qq_stat['faction_join_time'])
            if remain_time != "":
               return f"[CQ:at,qq={qq_account}] 由于不久前才更改阵营，你需要等待{remain_time}之后才能更改。"
            else:
                pre_faction_id = qq_stat['faction_id']
                new_faction_id = 'e_ren' if pre_faction_id == 'hao_qi' else 'hao_qi'
                self._jx3_users[qq_account]['faction_id'] = new_faction_id
                self._jx3_users[qq_account]['faction_join_time'] = time.time()
                return (
                    f"[CQ:at,qq={qq_account}] 通过地下交易，"
                    f"花费了{FACTION_TRANSFER_WEIWANG_COST}威望，成功地脱离了 {FACTION_LIST[pre_faction_id]}，"
                    f"加入了 {FACTION_LIST[new_faction_id]}。"
                )

    @data_handler(return_list=True, async_func=True)
    async def rob(self, fromQQ: str, toQQ: str) -> list:
        returnMsg = []

        fromQQ_stat = self._jx3_users[fromQQ]
        toQQ_stat = self._jx3_users[toQQ]

        if 'rob' not in fromQQ_stat['daily_count']:
            fromQQ_stat['daily_count']['rob'] = {'weiwang': 0, 'money': 0, 'last_rob_time': None}

        if fromQQ_stat['faction_id'] == 'zhong_li':
            returnMsg.append(f"[CQ:at,qq={fromQQ}] 中立阵营无法打劫，请先加入阵营。")
        elif toQQ_stat['faction_id'] == 'zhong_li':
            returnMsg.append(f"[CQ:at,qq={fromQQ}] 对方是中立阵营，无法打劫。")
        elif fromQQ_stat['faction_id'] == toQQ_stat['faction_id'] and ROB_SAME_FACTION_PROTECTION:
            returnMsg.append(f"[CQ:at,qq={fromQQ}] 同阵营无法打劫！")
        elif toQQ in self._rob_protect and ROB_PROTECT_COUNT != 0 and self._rob_protect[toQQ]['count'] >= ROB_PROTECT_COUNT and (time.time() - self._rob_protect[toQQ]['rob_time']) <= ROB_PROTECT_DURATION:
            remain_msg = get_remaining_time_string(ROB_PROTECT_DURATION, self._rob_protect[toQQ]['rob_time'])
            returnMsg.append(f"[CQ:at,qq={fromQQ}] 对方最近被打劫太多次啦，已经受到了神之护佑。剩余时间：{remain_msg}")
        else:
            jail_status = self._is_in_jailed(fromQQ)

            if jail_status != "":
                returnMsg.append(jail_status)
            elif toQQ in self._jail_list and time.time() - self._jail_list[toQQ] < JAIL_DURATION:
                returnMsg.append(f"[CQ:at,qq={fromQQ}] 对方在监狱里蹲着呢，你这是要劫狱吗？")
            elif fromQQ_stat['energy'] < ROB_ENERGY_COST:
                returnMsg.append(f"[CQ:at,qq={fromQQ}] 体力不足！无法打劫。")
            elif fromQQ_stat['daily_count']['rob']['last_rob_time'] != None and time.time() - fromQQ_stat['daily_count']['rob']['last_rob_time'] < ROB_LOSE_COOLDOWN:
                remain_msg = get_remaining_time_string(ROB_LOSE_COOLDOWN, fromQQ_stat['daily_count']['rob']['last_rob_time'])
                returnMsg.append(f"[CQ:at,qq={fromQQ}] 你还需要恢复{remain_msg}")
            else:
                if fromQQ in self._jail_list:
                    self._jail_list.pop(fromQQ)

                fromQQ_battle_stat = {
                    'qq_account': fromQQ,
                    'equipment': copy.deepcopy(fromQQ_stat['equipment'])
                }
                toQQ_battle_stat = {
                    'qq_account': toQQ,
                    'equipment': copy.deepcopy(toQQ_stat['equipment'])
                }

                battle_result = self._calculate_battle(fromQQ_battle_stat, toQQ_battle_stat, 'pvp')

                winner = battle_result['winner']
                loser = battle_result['loser']
                success_chance = battle_result['success_chance']

                weiwang_amount = int(self._jx3_users[loser]['weiwang'] * random.uniform(ROB_GAIN_FACTOR_MIN, ROB_GAIN_FACTOR_MAX))
                money_amount = int(self._jx3_users[loser]['money'] * random.uniform(ROB_GAIN_FACTOR_MIN, ROB_GAIN_FACTOR_MAX))

                if loser == toQQ:

                    if fromQQ_stat['daily_count']['rob']['weiwang'] < ROB_DALIY_MAX_WEIWANG_GAIN:
                        weiwang_gain = min(weiwang_amount, ROB_DALIY_MAX_WEIWANG_GAIN - fromQQ_stat['daily_count']['rob']['weiwang'])
                    else:
                        weiwang_gain = 0

                    if loser not in self._rob_protect:
                        self._rob_protect[loser] = {"count": 0, "rob_time": None}

                    if fromQQ_stat['daily_count']['rob']['money'] < ROB_DALIY_MAX_MONEY_GAIN and self._rob_protect[loser]['count'] <= ROB_PROTECT_NO_LOST_COUNT:
                        money_gain = min(money_amount, ROB_DALIY_MAX_MONEY_GAIN - fromQQ_stat['daily_count']['rob']['money'])
                    else:
                        money_gain = 0

                    if weiwang_gain != 0 or money_gain != 0:
                        self._jx3_users[fromQQ]['energy'] -= ROB_ENERGY_COST
                        energy_cost = ROB_ENERGY_COST
                    else:
                        energy_cost = 0

                    self._jx3_users[winner]['weiwang'] += weiwang_gain
                    fromQQ_stat['daily_count']['rob']['weiwang'] += weiwang_gain

                    self._jx3_users[winner]['money'] += money_gain
                    fromQQ_stat['daily_count']['rob']['money'] += money_gain

                    if loser not in self._rob_protect:
                        self._rob_protect[loser] = {'count': 0, 'rob_time': None}

                    if money_gain != 0:
                        self._rob_protect[loser]['count'] += 1
                        self._rob_protect[loser]['rob_time'] = time.time()

                    if ROB_LOST_WEIWANG and self._rob_protect[loser]['count'] <= ROB_PROTECT_NO_LOST_COUNT:
                        weiwang_lost = weiwang_gain
                    else:
                        weiwang_lost = 0

                    if ROB_LOST_MONEY and self._rob_protect[loser]['count'] <= ROB_PROTECT_NO_LOST_COUNT:
                        money_lost = money_gain
                    else:
                        money_lost = 0

                    self._jx3_users[loser]['weiwang'] -= weiwang_lost
                    self._jx3_users[loser]['money'] -= money_lost

                    fromQQ_nickname = await get_group_nickname(self._qq_group, fromQQ)
                    toQQ_nickname = await get_group_nickname(self._qq_group, toQQ)
                    returnMsg.append(
                        (
                            f"打劫成功！成功率：{success_chance}%\n"
                            f"[CQ:at,qq={fromQQ}] 在野外打劫了 [CQ:at,qq={toQQ}]\n"
                            f"{fromQQ_nickname} 威望+{weiwang_gain} 金钱+{money_gain} 体力-{energy_cost}\n"
                            f"{toQQ_nickname} 威望-{weiwang_lost} 金钱-{money_lost}"
                        )
                    )
                    wanted_chance = ROB_WIN_WANTED_CHANCE if energy_cost != 0 else 0

                    if energy_cost != 0:
                        self._jx3_faction[fromQQ_stat['faction_id']]['point'] += ROB_FACTION_POINT_GAIN
                        self._qiyu_status[fromQQ]['pending_qiyu'] = 'hu_xiao_shan_lin'
                        self._qiyu_status[toQQ]['pending_qiyu'] = 'yin_yang_liang_jie'

                else:
                    fromQQ_stat['daily_count']['rob']['last_rob_time'] = time.time()
                    remain_msg = get_remaining_time_string(ROB_LOSE_COOLDOWN, time.time())

                    if fromQQ_stat['daily_count']['rob']['weiwang'] < ROB_DALIY_MAX_WEIWANG_GAIN or fromQQ_stat['daily_count']['money'] < ROB_DALIY_MAX_MONEY_GAIN:
                        self._jx3_users[fromQQ]['energy'] -= ROB_ENERGY_COST
                        energy_cost = ROB_ENERGY_COST
                    else:
                        energy_cost = 0

                    returnMsg.append(
                        (
                            f"打劫失败！成功率：{success_chance}%\n"
                            f"[CQ:at,qq={fromQQ}] 在野外打劫 [CQ:at,qq={toQQ}] 时被反杀，需要休息{remain_msg}。体力-{energy_cost}"
                        )
                    )
                    wanted_chance = ROB_LOSE_WANTED_CHANCE if energy_cost != 0 else 0

                rand = random.uniform(0, 1)
                logging.info("wanted chance: {0} rand: {1}".format(wanted_chance, rand))
                if rand <= wanted_chance:
                    returnMsg.append(self._put_wanted_internal(fromQQ, ROB_WANTED_REWARD))

        return returnMsg

    @data_handler(async_func=True)
    async def practise(self, fromQQ: str, toQQ: str) -> str:
        returnMsg = ""

        fromQQ_stat = self._jx3_users[fromQQ]
        toQQ_stat = self._jx3_users[toQQ]

        if fromQQ_stat['faction_id'] == 'zhong_li':
            returnMsg = f"[CQ:at,qq={fromQQ}] 中立阵营无法切磋，请先加入阵营。"
        elif toQQ_stat['faction_id'] == 'zhong_li':
            returnMsg = f"[CQ:at,qq={fromQQ}] 对方是中立阵营，无法切磋。"
        elif fromQQ_stat['faction_id'] != toQQ_stat['faction_id'] and ROB_SAME_FACTION_PROTECTION:
            returnMsg = f"[CQ:at,qq={fromQQ}] 不同阵营无法切磋！"
        else:
            jail_status = self._is_in_jailed(fromQQ)
            if jail_status != "":
                returnMsg = jail_status
            elif toQQ in self._jail_list and time.time() - self._jail_list[toQQ] < JAIL_DURATION:
                    returnMsg = f"[CQ:at,qq={fromQQ}] 对方在监狱里蹲着呢，没法跟你切磋。"
            elif self._jx3_users[fromQQ]['energy'] < PRACTISE_ENERGY_COST:
                returnMsg = f"[CQ:at,qq={fromQQ}] 体力不足！需要消耗{PRACTISE_ENERGY_COST}体力。"
            else:
                if fromQQ in self._jail_list:
                    self._jail_list.pop(fromQQ)

                fromQQ_battle_stat = {
                    'qq_account': fromQQ,
                    'equipment': copy.deepcopy(fromQQ_stat['equipment'])
                }
                toQQ_battle_stat = {
                    'qq_account': toQQ,
                    'equipment': copy.deepcopy(toQQ_stat['equipment'])
                }

                battle_result = self._calculate_battle(fromQQ_battle_stat, toQQ_battle_stat, 'pvp')

                winner = battle_result['winner']
                loser = battle_result['loser']
                success_chance = battle_result['success_chance']

                if 'practise' not in fromQQ_stat['daily_count']:
                    fromQQ_stat['daily_count']['practise'] = {'weiwang': 0}
                if 'practise' not in toQQ_stat['daily_count']:
                    toQQ_stat['daily_count']['practise'] = {'weiwang': 0}

                weiwang_amount = random.randint(PRACTISE_WEIWANG_GAIN_MIN, PRACTISE_WEIWANG_GAIN_MAX)

                if self._jx3_users[winner]['daily_count']['practise']['weiwang'] < DALIY_PRACITSE_WEIWANG_GAIN:
                    winner_weiwang_gain = min(weiwang_amount, DALIY_PRACITSE_WEIWANG_GAIN - self._jx3_users[winner]['daily_count']['practise']['weiwang'])
                else:
                    winner_weiwang_gain = 0

                if winner_weiwang_gain != 0 and self._jx3_users[loser]['daily_count']['practise']['weiwang'] < DALIY_PRACITSE_WEIWANG_GAIN:
                    loser_weiwang_gain = min(int(weiwang_amount * PRACTISE_LOSER_GAIN_PERCENTAGE), DALIY_PRACITSE_WEIWANG_GAIN - self._jx3_users[loser]['daily_count']['practise']['weiwang'])
                else:
                    loser_weiwang_gain = 0

                if (winner_weiwang_gain != 0 and winner == fromQQ) or (loser_weiwang_gain != 0 and loser == fromQQ):
                    energy_cost = PRACTISE_ENERGY_COST
                else:
                    energy_cost = 0

                self._jx3_users[fromQQ]['energy'] -= energy_cost

                self._jx3_users[winner]['weiwang'] += winner_weiwang_gain
                self._jx3_users[winner]['daily_count']['practise']['weiwang'] += winner_weiwang_gain
                self._jx3_users[loser]['weiwang'] += loser_weiwang_gain
                self._jx3_users[loser]['daily_count']['practise']['weiwang'] += loser_weiwang_gain

                if energy_cost != 0:
                    self._jx3_faction[fromQQ_stat['faction_id']]['point'] += PRACTISE_FACTION_POINT_GAIN

                winner_nickname = await get_group_nickname(self._qq_group, winner)
                loser_nickname = await get_group_nickname(self._qq_group, loser)

                returnMsg = (
                    f"[CQ:at,qq={0}]与[CQ:at,qq={1}]进行了切磋。"
                    f"{winner_nickname} 战胜了 {loser_nickname}，成功率{success_chance}%。\n"
                    f"{winner_nickname} 威望+{winner_weiwang_gain} {'体力-{0}'.format(energy_cost) if winner == fromQQ else ''}\n"
                    f"{loser_nickname} 威望+{loser_weiwang_gain} {'体力-{0}'.format(energy_cost) if loser == fromQQ else ''}"
                )

        return returnMsg

    @data_handler(return_list=True, async_func=True)
    async def jjc(self, qq_account: str) -> list:
        returnMsg = []

        qq_account_stat = self._jx3_users[qq_account]

        if qq_account not in self._jjc_data['current_season_data']:
            self._jjc_data['current_season_data'][qq_account] = {'score': 0, 'last_time': None, 'win': 0, 'lose': 0}

        jail_status = self._is_in_jailed(qq_account)
        if jail_status != "":
            returnMsg.append(jail_status)
        elif self._jx3_users[qq_account]['energy'] < JJC_ENERGY_COST:
            returnMsg.append(f"[CQ:at,qq={qq_account}] 体力不足！需要消耗{1}体力。")
        else:
            remain_time = get_remaining_time_string(JJC_COOLDOWN, self._jjc_data['current_season_data'][qq_account]['last_time'])
            if remain_time != "":
                returnMsg.append(f"[CQ:at,qq={qq_account}] 你刚排过名剑大会了，请过{remain_time}之后再来吧。")
            else:
                jjc_stat = self._jjc_data['current_season_data'][qq_account]

                rank = min(MAX_JJC_RANK, jjc_stat['score'] // 100)

                available_list = list(set(self._jx3_users.keys()) - set([qq_account]))
                random_person = available_list[random.randint(0, len(available_list) - 1)]
                random_person_stat = self._jx3_users[random_person]

                if random_person not in self._jjc_data['current_season_data']:
                    self._jjc_data['current_season_data'][random_person] = {'score': 0, 'last_time': None, 'win': 0, 'lose': 0}
                random_person_jjc_stat = self._jjc_data['current_season_data'][random_person]

                random_person_rank = random_person_jjc_stat['score'] // 100

                fromQQ_modifier = 1
                toQQ_modifier = 1
                if rank >= 0 and random_person_rank >= 0:
                    if rank > random_person_rank:
                        toQQ_modifier = 1 + JJC_GEAR_MODIFIER * int(rank - random_person_rank)
                    elif rank < random_person_rank:
                        fromQQ_modifier = 1 + JJC_GEAR_MODIFIER * int(random_person_rank - rank)

                logging.info(
                    (
                        f"fromqq: {qq_account} score: {jjc_stat['score']} rank: {rank} modifier: {fromQQ_modifier}; "
                        f"toqq: {random_person} score: {random_person_jjc_stat['score']} rank: {random_person_rank} modifier: {toQQ_modifier}"
                    )
                )

                random_person_nickname = await get_group_nickname(self._qq_group, random_person)
                returnMsg.append(
                    (
                        f"[CQ:at,qq={qq_account}] 加入名剑大会排位。\n"
                        f"你的名剑大会分数：{jjc_stat['score']} 段位：{rank}段。"
                        f"匹配到的对手是 {random_person_nickname}，名剑大会分数：{random_person_jjc_stat['score']} 段位：{random_person_rank}段"
                    )
                )

                fromQQ_battle_stat = {
                    'qq_account': qq_account,
                    'equipment': copy.deepcopy(qq_account_stat['equipment']),
                    'modifier': fromQQ_modifier
                }
                toQQ_battle_stat = {
                    'qq_account': random_person,
                    'equipment': copy.deepcopy(random_person_stat['equipment']),
                    'modifier': toQQ_modifier
                }

                battle_result = self._calculate_battle(fromQQ_battle_stat, toQQ_battle_stat, 'pvp')

                winner = battle_result['winner']
                loser = battle_result['loser']
                success_chance = battle_result['success_chance']

                self._jx3_users[qq_account]['energy'] -= JJC_ENERGY_COST

                qq_account_nickname = await get_group_nickname(self._qq_group, qq_account)

                if winner == qq_account:

                    if 'jjc' in qq_account_stat['daily_count'] and qq_account_stat['daily_count']['jjc']['win'] < DALIY_JJC_DOUBLE_REWARD_COUNT:
                        reward_modifier = 2
                    else:
                        reward_modifier = 1

                    weiwang_reward = int(random.randint(JJC_REWARD_WEIWANG_MIN, JJC_REWARD_WEIWANG_MAX) * (1 + JJC_REWARD_RANK_MODIFIER * rank)  * reward_modifier)

                    self._jx3_users[qq_account]['weiwang'] += weiwang_reward

                    if rank < random_person_rank:
                        score_reward = int(JJC_REWARD_RANK * (random_person_rank - rank) * reward_modifier)
                        score_lost = JJC_REWARD_RANK
                    else:
                        score_reward = JJC_REWARD_RANK * reward_modifier
                        score_lost = 0

                    double_msg = " (每日{1}场双倍奖励加成中：{0}/{1})".format(qq_account_stat['daily_count']['jjc']['win'] + 1, DALIY_JJC_DOUBLE_REWARD_COUNT) if reward_modifier == 2 else ""

                    self._jjc_data['current_season_data'][qq_account]['score'] += score_reward
                    self._jjc_data['current_season_data'][qq_account]['last_time'] = time.time()

                    if self._jjc_data['current_season_data'][random_person]['score'] < JJC_REWARD_RANK:
                        score_lost = 0

                    self._jjc_data['current_season_data'][random_person]['score'] -= score_lost
                    self._jjc_data['current_season_data'][qq_account]['win'] += 1
                    qq_account_stat['daily_count']['jjc']['win'] += 1
                    self._jjc_data['current_season_data'][random_person]['lose'] += 1

                    new_rank = self._jjc_data['current_season_data'][qq_account]['score'] // 100
                    rank_msg = "\n段位变更为：{0}".format(new_rank) if new_rank != rank else ""

                    returnMsg.append(
                        (
                            f"[CQ:at,qq={qq_account}] 战斗结果：胜利！成功率：{success_chance}%\n"
                            f"{qq_account_nickname} 威望+{weiwang_reward} 分数+{score_reward} 体力-{JJC_ENERGY_COST}{double_msg} "
                            f"{random_person_nickname} 分数-{score_lost}\n"
                            f"{rank_msg}"
                        )
                    )
                else:
                    if rank < random_person_rank:
                        score_reward = JJC_REWARD_RANK
                        score_lost = 0
                    elif rank > random_person_rank:
                        score_reward = int(JJC_REWARD_RANK * (rank - random_person_rank))
                        score_lost = JJC_REWARD_RANK
                    else:
                        score_reward = JJC_REWARD_RANK
                        score_lost = 0

                    if self._jjc_data['current_season_data'][qq_account]['score'] < JJC_REWARD_RANK:
                        score_lost = 0
                    self._jjc_data['current_season_data'][qq_account]['score'] -= score_lost

                    self._jjc_data['current_season_data'][qq_account]['last_time'] = time.time()
                    self._jjc_data['current_season_data'][random_person]['score'] += score_reward

                    self._jjc_data['current_season_data'][random_person]['win'] += 1
                    self._jjc_data['current_season_data'][qq_account]['lose'] += 1

                    new_rank = self._jjc_data['current_season_data'][random_person]['score'] // 100
                    rank_msg = "\n段位变更为：{0}".format(new_rank) if new_rank != random_person_rank else ""

                    returnMsg.append(
                        (
                            f"[CQ:at,qq={qq_account}] 战斗结果：失败！成功率：{success_chance}%\n"
                            f"{qq_account_nickname} 分数-{score_lost} 体力-{JJC_ENERGY_COST} "
                            f"{random_person_nickname} 分数+{score_reward}"
                            f"{rank_msg}"
                        )
                    )

        return returnMsg

    @data_handler()
    def catch_hun_hun(self, qq_account: str) -> str:
        returnMsg = ""

        jail_status = self._is_in_jailed(qq_account)
        if jail_status != "":
            returnMsg = jail_status
        elif self._jx3_users[qq_account]['daily_count']['cha_guan']['current_quest'] == "cha_guan_hun_hun":
            if self._jx3_users[qq_account]['bag'].get('hun_hun_zheng_ming', 0) >= 3:
                returnMsg = f"[CQ:at,qq={qq_account}] 你已经抓了太多混混啦，休息一下吧。"
            else:
                qq_stat = {
                    'qq_account': qq_account,
                    'equipment': copy.deepcopy(self._jx3_users[qq_account]['equipment']),
                }
                hun_hun_stat = {
                    'qq_account': 'hun_hun',
                    'equipment': copy.deepcopy(NPC_LIST['hun_hun']['equipment'])
                }
                battle_result = self._calculate_battle(qq_stat, hun_hun_stat, 'pve')
                winner = battle_result['winner']
                loser = battle_result['loser']
                success_chance = battle_result['success_chance']

                if winner == qq_account:
                    reward_chance = NPC_LIST["hun_hun"]['reward_chance']
                    reward_list = NPC_LIST["hun_hun"]['reward']

                    rewardMsg = ""
                    for k, v in reward_list.items():
                        if k in self._jx3_users[qq_account]:
                            rand = random.uniform(0, 1)
                            if rand <= reward_chance:
                                self._jx3_users[qq_account][k] += v
                                rewardMsg = f"{USER_STAT_DISPLAY[k]}+{v} "

                    if 'hun_hun_zheng_ming' not in self._jx3_users[qq_account]['bag']:
                        self._jx3_users[qq_account]['bag']['hun_hun_zheng_ming'] = 0
                    self._jx3_users[qq_account]['bag']['hun_hun_zheng_ming'] += 1
                    rewardMsg += f"{get_item_display_name('hun_hun_zheng_ming')}+1"

                    returnMsg = (
                        f"[CQ:at,qq={qq_account}] 抓捕混混成功！成功率：{success_chance}%\n"
                        f"获得奖励：{rewardMsg}"
                    )
                else:
                    returnMsg = f"[CQ:at,qq={qq_account}] 抓捕失败，成功率：{success_chance}%"

        return returnMsg

    def _modify_item_in_bag(self, qq_account, item_name, amount):
        if item_name not in self._jx3_users[qq_account]['bag']:
            self._jx3_users[qq_account]['bag'][item_name] = 0
        self._jx3_users[qq_account]['bag'][item_name] += amount

        if self._jx3_users[qq_account]['bag'][item_name] == 0:
            self._jx3_users[qq_account]['bag'].pop(item_name)

    @data_handler()
    def buy_item(self, qq_account, item_display_name, item_amount):
        returnMsg = ""

        item = get_item_id_by_display_name(item_display_name)
        if item != "" and item_amount > 0:
            if 'cost' not in ITEM_LIST[item]:
                returnMsg = f"[CQ:at,qq={qq_account}] {item_display_name} 不可购买。"
            else:
                qq_stat = self._jx3_users[qq_account]

                cost_list = ITEM_LIST[item]['cost']
                can_afford = True
                for k, v in cost_list.items():
                    can_afford = can_afford and (k in qq_stat and qq_stat[k] >= v * item_amount)

                if can_afford:
                    self._modify_item_in_bag(qq_account, item, item_amount)

                    returnMsg = (
                        f"[CQ:at,qq={qq_account}] 购买成功！\n"
                        f"{item_display_name}+{item_amount} "
                    )

                    for k, v in cost_list.items():
                        if k in qq_stat:
                            self._jx3_users[qq_account][k] -= v * item_amount
                            returnMsg += "{0}-{1} ".format(USER_STAT_DISPLAY[k], v * item_amount)
                else:
                    returnMsg = (
                        f"[CQ:at,qq={qq_account}] 购买失败！\n"
                        f"购买1个 {item_display_name} 需要:{print_item_cost(item)}"
                    )

        return returnMsg

    @data_handler(return_list=True, async_func=True)
    async def use_item(self, qq_account: str, item_display_name: str, item_amount: int=1, toQQ: str=""):
        returnMsg = []

        item = get_item_id_by_display_name(item_display_name)

        if item != None and item_amount > 0:
            if 'firework' in ITEM_LIST[item] and toQQ == "":
                returnMsg.append(f"[CQ:at,qq={qq_account}] {item_display_name} 需要使用对象。")
            elif 'firework' in ITEM_LIST[item] and toQQ == qq_account:
                returnMsg.append(f"[CQ:at,qq={qq_account}] 不能对自己使用{item_display_name}。")
            elif 'effect' not in ITEM_LIST[item] and 'firework' not in ITEM_LIST[item]:
                returnMsg.append(f"[CQ:at,qq={qq_account}] {item_display_name} 不可使用。")
            else:
                qq_stat = self._jx3_users[qq_account]

                if item not in self._jx3_users[qq_account]['bag']:
                    returnMsg.append(f"[CQ:at,qq={qq_account}] 你并没有{item_display_name}，无法使用。")
                elif self._jx3_users[qq_account]['bag'][item] < item_amount:
                    returnMsg.append(f"[CQ:at,qq={qq_account}] 你并没有那么多 {item_display_name}。")
                else:
                    item_used = True

                    if 'firework' in ITEM_LIST[item]:
                        for m in ITEM_LIST[LOVE_ITEM_REQUIRED].get('firework', []):
                            returnMsg.append(m.format(qq_account, toQQ))
                    else:
                        effect_list = ITEM_LIST[item]['effect']

                        msg = f"[CQ:at,qq={qq_account}] 使用 {item_display_name} x {item_amount}"
                        for k, v in effect_list.items():
                            if k in qq_stat:
                                self._jx3_users[qq_account][k] += v * item_amount
                                msg += f"\n{USER_STAT_DISPLAY[k]}+{v * item_amount}"
                            elif k == 'attack_count':
                                if qq_account in self._group_info:
                                    leader = qq_account
                                else:
                                    leader = self._get_leader_by_member(qq_account)

                                if leader != "" and leader in self._dungeon_status:
                                    self._dungeon_status[leader]['attack_count'][qq_account]['available_attack'] += v * item_amount
                                    msg += f"\n攻击次数+{v * item_amount}"
                                else:
                                    msg = f"[CQ:at,qq={qq_account}] 你不在副本里，无法使用。"
                                    item_used = False
                            else:
                                if k == 'pve_weapon':
                                    self._jx3_users[qq_account]['equipment']['weapon']['pve'] += v * item_amount
                                    msg += f"\n武器pve伤害+{v * item_amount}"
                                elif k == 'pvp_weapon':
                                    self._jx3_users[qq_account]['equipment']['weapon']['pvp'] += v * item_amount
                                    msg += f"\n武器pvp伤害+{v * item_amount}"
                                elif k == 'pve_armor':
                                    self._jx3_users[qq_account]['equipment']['armor']['pve'] += v * item_amount
                                    msg += f"\n防具pve血量+{v * item_amount}"
                                elif k == 'pvp_armor':
                                    self._jx3_users[qq_account]['equipment']['armor']['pvp'] += v * item_amount
                                    msg += f"\n防具pvp血量+{v * item_amount}"

                        returnMsg.append(msg)

                    if item_used:
                        self._modify_item_in_bag(qq_account, item, 0 - item_amount)

        return returnMsg

    @data_handler(read_only=True)
    def shop_list(self, qq_account):
        returnMsg = (
            f"[CQ:at,qq={qq_account}]\n"
            f"---------杂货商---------\n"
            f"---货真价实，童叟无欺---"
        )
        for item in ITEM_LIST.values():
            if 'cost' in item:
                returnMsg += f"\n*【{item['display_name']}】"
                for k, v in item['cost'].items():
                    returnMsg += f"-- {USER_STAT_DISPLAY[k]}：{v}"

        return returnMsg

    def _get_wa_bao_reward(self):
        max_index = 0
        wa_bao_items = {}
        for item_name in random.sample(ITEM_LIST.keys(), len(ITEM_LIST)):
            if ITEM_LIST[item_name]['rank'] != 0:
                new_max_index = max_index + pow(ITEM_LIST[item_name]['rank'], WA_BAO_RARE_FACTOR)
                wa_bao_items[item_name] = {'min': max_index, 'max': new_max_index}
                max_index = new_max_index

        rand_index = random.uniform(0, max_index)
        logging.info("wa_bao items: {1} rand index: {0}".format(rand_index, wa_bao_items))
        for item_name, min_max in wa_bao_items.items():
            if rand_index >= min_max['min'] and rand_index < min_max['max']:
                return item_name
        return ""

    @data_handler()
    def wa_bao(self, qq_account):
        returnMsg = ""

        val = self._jx3_users[qq_account]
        if val['energy'] < WA_BAO_ENERGY_REQUIRED:
            returnMsg = f"[CQ:at,qq={qq_account}] 体力不足！无法挖宝。"
        else:
            jail_status = self._is_in_jailed(qq_account)
            if jail_status != "":
                returnMsg = jail_status
            else:
                if qq_account in self._jail_list:
                    self._jail_list.pop(qq_account)

                if val['daily_count']["wa_bao"]['count'] < MAX_DALIY_WA_BAO_COUNT:
                    remain_time = get_remaining_time_string(WA_BAO_COOLDOWN, val['daily_count']["wa_bao"]['last_time'])
                    if remain_time != "":
                        returnMsg = f"[CQ:at,qq={qq_account}] 大侠你刚刚挖完宝藏，身体有些疲惫，请过{remain_time}之后再挖。"
                    else:
                        reward_item_name = self._get_wa_bao_reward()
                        self._jx3_users[qq_account]['daily_count']["wa_bao"]['count'] += 1
                        self._jx3_users[qq_account]['daily_count']["wa_bao"]['last_time'] = time.time()

                        self._jx3_users[qq_account]['energy'] -= WA_BAO_ENERGY_REQUIRED

                        returnMsg = (
                            f"[CQ:at,qq={qq_account}]\n"
                            f"今日挖宝次数：{self._jx3_users[qq_account]['daily_count']['wa_bao']['count']}/{MAX_DALIY_WA_BAO_COUNT}"
                        )

                        if reward_item_name == "":
                            returnMsg += "\n你一铲子下去，什么也没挖到。"
                        else:
                            self._modify_item_in_bag(qq_account, reward_item_name, 1)
                            returnMsg += f"\n你一铲子下去，挖到了一个神秘的东西: {get_item_display_name(reward_item_name)}+1 体力-{WA_BAO_ENERGY_REQUIRED}"
                            self._qiyu_status[qq_account]['pending_qiyu'] = 'san_shan_si_hai'
                else:
                    returnMsg = f"[CQ:at,qq={0}] 一天最多挖宝{MAX_DALIY_WA_BAO_COUNT}次。你已经挖了{MAX_DALIY_WA_BAO_COUNT}次啦，今天休息休息吧。"

        return returnMsg

    def _calculate_gear_point(self, equipment):
        weapon = equipment['weapon']
        armor = equipment['armor']
        return {'pve': weapon['pve'] * 30 + armor['pve'] * 10, 'pvp': weapon['pvp'] * 30 + armor['pvp'] * 10}

    @data_handler(read_only=True)
    def get_equipment_info(self, qq_account):
        val = self._jx3_users[qq_account]['equipment']
        gear_point = self._calculate_gear_point(val)
        returnMsg = (
            f"[CQ:at,qq={qq_account}] 装备信息：\n"
            f"pve评分：{gear_point['pve']} pvp评分：{gear_point['pvp']}\n"
            f"武器：{val['weapon']['display_name']} 伤害：\n"
            f"pve：{val['weapon']['pve']} pvp：{val['weapon']['pvp']}\n"
            f"防具：{val['armor']['display_name']} 血量：\n"
            f"pve：{val['armor']['pve']} pvp：{val['armor']['pvp']}"
        )

        return returnMsg

    @data_handler()
    def change_weapon_name(self, qq_account: str, name: str):
        self._jx3_users[qq_account]['equipment']['weapon']['display_name'] = name
        returnMsg = f"[CQ:at,qq={qq_account}] 的武器已更名为 {name}"

        return returnMsg

    @data_handler()
    def change_armor_name(self, qq_account: str, name: str):
        self._jx3_users[qq_account]['equipment']['armor']['display_name'] = name
        returnMsg = f"[CQ:at,qq={qq_account}] 的防具已更名为 {name}"

        return returnMsg

    def _get_faction_count(self):
        retval = {
            'zhong_li': 0,
            'e_ren': 0,
            'hao_qi': 0
        }
        for key, value in self._jx3_users.items():
            retval[value['faction_id']] += 1
        return retval

    @data_handler(read_only=True)
    def get_faction_info(self):
        retval = self._get_faction_count()
        strong_faction = "浩气强势" if retval['hao_qi'] > retval['e_ren'] else "恶人强势" if retval['e_ren'] > retval['hao_qi'] else "势均力敌"
        returnMsg = (
            f"本群阵营信息\n"
            f"本群为{strong_faction}群\n"
            f"恶人谷人数:\t{retval['e_ren']} 今日阵营点数：{self._jx3_faction['e_ren']['faction_point']}\n"
            f"浩气盟人数:\t{retval['hao_qi']} 今日阵营点数：{self._jx3_faction['hao_qi']['faction_point']}\n"
            f"中立人数:\t{retval['zhong_li']}"
        )

        return returnMsg

    @data_handler(read_only=True, async_func=True)
    async def get_pve_gear_point_rank(self):
        returnMsg = "本群pve装备排行榜"

        pve_gear_point_list = {k: self._calculate_gear_point(v['equipment'])['pve'] for k, v in self._jx3_users.items()}
        rank_list = sorted(pve_gear_point_list, key=pve_gear_point_list.get, reverse=True)
        list_len = len(rank_list)
        for i in range(10):
            if i < list_len:
                qq_nickname = await get_group_nickname(self._qq_group, rank_list[i])
                returnMsg += f"\n{i + 1}. {qq_nickname} {pve_gear_point_list.get(rank_list[i])}"
            else:
                break

        return returnMsg

    @data_handler(read_only=True, async_func=True)
    async def get_pvp_gear_point_rank(self):
        returnMsg = "本群pvp装备排行榜"

        pvp_gear_point_list = {k: self._calculate_gear_point(v['equipment'])['pvp'] for k, v in self._jx3_users.items()}
        rank_list = rank_list = sorted(pvp_gear_point_list, key=pvp_gear_point_list.get, reverse=True)
        list_len = len(rank_list)
        for i in range(10):
            if i < list_len:
                qq_nickname = await get_group_nickname(self._qq_group, rank_list[i])
                returnMsg += f"\n{i + 1}. {qq_nickname} {pvp_gear_point_list.get(rank_list[i])}"
            else:
                break

        return returnMsg

    @data_handler(read_only=True, async_func=True)
    async def get_money_rank(self):
        returnMsg = "本群土豪排行榜"

        rank_list = sorted(self._jx3_users, key=lambda x: self._jx3_users[x]['money'], reverse=True)
        list_len = len(rank_list)
        for i in range(10):
            if i < list_len and self._jx3_users[rank_list[i]]['money'] != 0:
                qq_nickname = await get_group_nickname(self._qq_group, rank_list[i])
                returnMsg += f"\n{i + 1}. {qq_nickname} {self._jx3_users[rank_list[i]]['money']}"
            else:
                break

        return returnMsg

    @data_handler(read_only=True, async_func=True)
    async def get_speech_rank(self):
        returnMsg = "本群今日聊天排行榜"

        rank_list = sorted(self._jx3_users, key=lambda x: self._jx3_users[x]['daily_count']['speech_count'], reverse=True)
        list_len = len(rank_list)
        for i in range(10):
            if i < list_len and self._jx3_users[rank_list[i]]['daily_count']['speech_count'] != 0:
                qq_nickname = await get_group_nickname(self._qq_group, rank_list[i])
                returnMsg += f"\n{i + 1}. {qq_nickname} {self._jx3_users[rank_list[i]]['daily_count']['speech_count']}"
            else:
                break

        return returnMsg

    @data_handler(read_only=True, async_func=True)
    async def get_qiyu_rank(self):
        returnMsg = "本群奇遇排行榜"

        rank_list = sorted(self._jx3_users, key=lambda x: get_qiyu_count(self._jx3_users[x]), reverse=True)
        list_len = len(rank_list)
        for i in range(10):
            if i < list_len and get_qiyu_count(self._jx3_users[rank_list[i]]) != 0:
                qq_nickname = await get_group_nickname(self._qq_group, rank_list[i])
                returnMsg += f"\n{i + 1}. {qq_nickname} {get_qiyu_count(self._jx3_users[rank_list[i]])}"
            else:
                break

        return returnMsg

    @data_handler(read_only=True, async_func=True)
    async def get_weiwang_rank(self):
        returnMsg = "本群威望排行榜"

        rank_list = sorted(self._jx3_users, key=lambda x: self._jx3_users[x]['weiwang'], reverse=True)
        list_len = len(rank_list)
        for i in range(10):
            if i < list_len and self._jx3_users[rank_list[i]]['weiwang'] != 0:
                qq_nickname = await get_group_nickname(self._qq_group, rank_list[i])
                returnMsg += f"\n{i + 1}. {qq_nickname} {self._jx3_users[rank_list[i]]['weiwang']}"
            else:
                break

        return returnMsg

    @data_handler(read_only=True, async_func=True)
    async def get_jjc_rank(self):

        returnMsg = f"名剑大会排名榜 赛季：{self._jjc_data['season']} 天数：{self._jjc_data['day']}"

        rank_list = sorted(self._jjc_data['current_season_data'], key=lambda x: self._jjc_data['current_season_data'][x]['score'], reverse=True)
        list_len = len(rank_list)
        for i in range(10):
            if i < list_len and self._jjc_data['current_season_data'][rank_list[i]]['score'] != 0:
                qq_nickname = await get_group_nickname(self._qq_group, rank_list[i])
                score = self._jjc_data['current_season_data'][rank_list[i]]['score']
                returnMsg += (
                    f"\n{i + 1}. {qq_nickname} "
                    f"分数：{score} 段位：{min(score // 100, MAX_JJC_RANK)}"
                )
            else:
                break

        return returnMsg

    @data_handler(read_only=True, async_func=True)
    async def get_wanted_list(self):
        msg_list = ""
        rank_list = sorted(self._wanted_list, key=lambda x: self._wanted_list[x]['reward'], reverse=True)
        index = 1
        for k in rank_list:
            if time.time() - self._wanted_list[k]['wanted_time'] < WANTED_DURATION:
                remain_time_msg = get_remaining_time_string(WANTED_DURATION, self._wanted_list[k]['wanted_time'])
                qq_nickname = await get_group_nickname(self._qq_group, k)
                msg_list += f"\n{index}. {qq_nickname} {self._wanted_list[k]['reward']}金 {remain_time_msg}"
                index += 1

        if msg_list == "":
            msg_list = "\n暂无悬赏"

        return "本群悬赏榜" + msg_list

    def _put_wanted_internal(self, toQQ_str, money_amount):
        if toQQ_str in self._wanted_list:
            if time.time() - self._wanted_list[toQQ_str]['wanted_time'] > WANTED_DURATION:
                self._wanted_list[toQQ_str]['reward'] = money_amount
            else:
                self._wanted_list[toQQ_str]['reward'] += money_amount

            self._wanted_list[toQQ_str]['wanted_time'] = time.time()
        else:
            self._wanted_list[toQQ_str] = {'reward': money_amount, 'wanted_time': time.time(), 'failed_try': {}}

        return (
            f"江湖恩怨一朝清，惟望群侠多援手。现有人愿付{money_amount}金对[CQ:at,qq={toQQ_str}]进行悬赏，"
            f"总赏金已达{self._wanted_list[toQQ_str]['reward']}金，众侠士切勿错过。"
        )

    @data_handler(return_list=True)
    def put_wanted(self, fromQQ: str, toQQ: str) -> [str]:
        returnMsg = []

        if self._jx3_users[fromQQ]['money'] < WANTED_MONEY_REWARD:
            returnMsg.append(f"[CQ:at,qq={fromQQ}] 金钱不足，无法悬赏。")
        elif self._jx3_users[toQQ]['daily_count']['jailed'] >= JAIL_TIMES_PROTECTION:
            returnMsg.append(f"[CQ:at,qq={fromQQ}] 对方今天已经被抓进去{JAIL_TIMES_PROTECTION}次了，无法悬赏。")
        else:
            self._jx3_users[fromQQ]['money'] -= WANTED_MONEY_REWARD

            returnMsg.append(f"[CQ:at,qq={fromQQ}] 悬赏成功！\n金钱-{WANTED_MONEY_REWARD}")
            returnMsg.append(self._put_wanted_internal(toQQ, WANTED_MONEY_REWARD))

        return returnMsg

    @data_handler(async_func=True)
    async def catch_wanted(self, fromQQ: str, toQQ: str) -> str:
        returnMsg = ""

        jail_status = self._is_in_jailed(fromQQ)

        if jail_status != "":
            returnMsg = jail_status
        elif toQQ in self._jail_list and time.time() - self._jail_list[toQQ] < JAIL_DURATION:
                returnMsg = f"[CQ:at,qq={fromQQ}] 对方在监狱里蹲着呢，你这是要劫狱吗？"
        elif toQQ in self._wanted_list and time.time() - self._wanted_list[toQQ]['wanted_time'] < WANTED_DURATION:

            if 'failed_try' in self._wanted_list[toQQ] and fromQQ in self._wanted_list[toQQ]['failed_try'] and time.time() - self._wanted_list[toQQ]['failed_try'][fromQQ] < WANTED_COOLDOWN:
                remain_time_msg = get_remaining_time_string(WANTED_DURATION, self._wanted_list[toQQ_str]['failed_try'][fromQQ])
                returnMsg = f"[CQ:at,qq={fromQQ}] 你已经尝试过抓捕了，奈何技艺不佳。请锻炼{remain_time_msg}后再来挑战！"
            elif self._jx3_users[fromQQ]['energy'] < WANTED_ENERGY_COST:
                returnMsg = f"[CQ:at,qq={fromQQ}] 体力不足！需要消耗{WANTED_ENERGY_COST}体力。"
            else:
                fromQQ_battle_stat = {
                    'qq_account': fromQQ,
                    'equipment': copy.deepcopy(self._jx3_users[fromQQ]['equipment'])
                }
                toQQ_battle_stat = {
                    'qq_account': toQQ,
                    'equipment': copy.deepcopy(self._jx3_users[toQQ]['equipment'])
                }
                battle_result = self._calculate_battle(fromQQ_battle_stat, toQQ_battle_stat, 'pvp')
                winner = battle_result['winner']
                loser = battle_result['loser']
                success_chance = battle_result['success_chance']

                self._jx3_users[fromQQ]['energy'] -= WANTED_ENERGY_COST

                if winner == fromQQ:
                    reward = int(0.9 * self._wanted_list[toQQ]['reward'])
                    self._jx3_users[fromQQ]['money'] += reward
                    self._wanted_list.pop(toQQ)
                    self._jail_list[toQQ] = time.time()

                    self._jx3_users[toQQ]['daily_count']['jailed'] += 1

                    fromQQ_nickname = await get_group_nickname(self._qq_group, fromQQ)
                    toQQ_nickname = await get_group_nickname(self._qq_group, toQQ)

                    returnMsg = (
                        f"{toQQ_nickname}在时限内被{fromQQ_nickname}成功抓捕，悬赏解除。成功率：{success_chance}%\n"
                        f"[CQ:at,qq={fromQQ}] 获得：金钱+{reward}金 体力-{WANTED_ENERGY_COST}"
                    )

                    self._qiyu_status[fromQQ]['pending_qiyu'] = 'qing_feng_bu_wang'
                    self._qiyu_status[toQQ]['pending_qiyu'] = 'yin_yang_liang_jie'
                else:
                    if 'failed_try' not in self._wanted_list[toQQ]:
                        self._wanted_list[toQQ]['failed_try'] = {}
                    self._wanted_list[toQQ]['failed_try'][fromQQ] = time.time()
                    returnMsg = f"[CQ:at,qq={fromQQ}] 抓捕失败，成功率：{success_chance}% 体力-{WANTED_ENERGY_COST}"

        return returnMsg

    @data_handler()
    def get_cha_guan_quest(self, qq_account: str):
        daliy_stat = self._jx3_users[qq_account]['daily_count']['cha_guan']

        jail_status = self._is_in_jailed(qq_account)

        if jail_status != "":
            returnMsg = jail_status
        else:
            if len(daliy_stat['complete_quest']) >= len(CHA_GUAN_QUEST_INFO):
                returnMsg = f"[CQ:at,qq={qq_account}] 你已经完成了{len(CHA_GUAN_QUEST_INFO)}个茶馆任务啦，明天再来吧。"
            elif self._jx3_users[qq_account]['energy'] < CHA_GUAN_ENERGY_COST:
                returnMsg = f"[CQ:at,qq={qq_account}] 体力不足！需要消耗{CHA_GUAN_ENERGY_COST}体力。"
            elif daliy_stat['current_quest'] != "":
                returnMsg = f"[CQ:at,qq={qq_account}] 你已经接了一个任务啦。\n当前任务：{CHA_GUAN_QUEST_INFO[daliy_stat['current_quest']]['display_name']}"
            else:
                remain_quest = list(set(CHA_GUAN_QUEST_INFO.keys()) - set(daliy_stat['complete_quest']))

                quest_name = remain_quest[random.randint(0, len(remain_quest) - 1)]

                self._jx3_users[qq_account]['daily_count']['cha_guan']['current_quest'] = quest_name
                quest = CHA_GUAN_QUEST_INFO[quest_name]

                rewardMsg = ""
                for k, v in quest['reward'].items():
                    rewardMsg += f"{USER_STAT_DISPLAY[k]}+{v} "

                requireMsg = ""
                for k, v in quest['require'].items():
                    requireMsg += f"{get_item_display_name(k)}x{v} "
                requireMsg += f"体力：{CHA_GUAN_ENERGY_COST}"

                returnMsg = (
                    f"[CQ:at,qq={qq_account}] 茶馆任务({len(daliy_stat['complete_quest']) + 1}/{len(CHA_GUAN_QUEST_INFO.keys())})\n"
                    f"{quest['display_name']}\n"
                    f"{quest['description']}\n"
                    f"需求：{requireMsg}\n"
                    f"奖励：{rewardMsg}"
                )

        return returnMsg

    @data_handler(return_list=True)
    def complete_cha_guan_quest(self, qq_account):
        returnMsg = []
        jail_status = self._is_in_jailed(qq_account)
        if jail_status != "":
            returnMsg.append(jail_status)
        else:
            if self._jx3_users[qq_account]['daily_count']['cha_guan']['current_quest'] != "":

                daliy_stat = self._jx3_users[qq_account]['daily_count']['cha_guan']
                quest = CHA_GUAN_QUEST_INFO[daliy_stat['current_quest']]

                if self._jx3_users[qq_account]['energy'] < CHA_GUAN_ENERGY_COST:
                    returnMsg.append(f"[CQ:at,qq={qq_account}] 体力不足！需要消耗{CHA_GUAN_ENERGY_COST}体力。")
                else:
                    has_require = True
                    for k, v in quest['require'].items():
                        has_require = has_require and k in self._jx3_users[qq_account]['bag'] and self._jx3_users[qq_account]['bag'][k] >= v

                    if has_require:
                        itemMsg = ""

                        for k, v in quest['require'].items():
                            self._jx3_users[qq_account]['bag'][k] -= v
                            if self._jx3_users[qq_account]['bag'][k] == 0:
                                self._jx3_users[qq_account]['bag'].pop(k)
                            itemMsg += f"{get_item_display_name(k)}-{v} "

                        self._jx3_users[qq_account]['energy'] -= CHA_GUAN_ENERGY_COST
                        self._jx3_users[qq_account]['daily_count']['cha_guan']['complete_quest'].append(daliy_stat['current_quest'])
                        self._jx3_users[qq_account]['daily_count']['cha_guan']['current_quest'] = ""

                        rewardMsg = ""
                        for k, v in quest['reward'].items():
                            if k in self._jx3_users[qq_account]:
                                self._jx3_users[qq_account][k] += v
                                rewardMsg += f"{USER_STAT_DISPLAY[k]}+{v} "

                        returnMsg.append(
                            (
                                f"[CQ:at,qq={qq_account}] 茶馆任务完成！"
                                f"{len(self._jx3_users[qq_account]['daily_count']['cha_guan']['complete_quest'])}/{len(CHA_GUAN_QUEST_INFO)}\n"
                                f"消耗任务物品：{itemMsg}\n"
                                f"体力-{CHA_GUAN_ENERGY_COST}\n"
                                f"获得奖励：{rewardMsg}"
                            )
                        )

                        self._qiyu_status[qq_account]['pending_qiyu'] = 'cha_guan_qi_yuan'

                        if len(self._jx3_users[qq_account]['daily_count']['cha_guan']['complete_quest']) == len(CHA_GUAN_QUEST_INFO):
                            banggong_reward = random.randint(CHA_GUAN_FINAL_REWARD_BANGGONG_MIN, CHA_GUAN_FINAL_REWARD_BANGGONG_MAX)
                            self._jx3_users[qq_account]['banggong'] += banggong_reward
                            self._jx3_users[qq_account]['money'] += CHA_GUAN_FINAL_REWARD_MONEY
                            returnMsg.append(
                                    f"[CQ:at,qq={qq_account}] 已完成今日全部茶馆任务，获得额外奖励：帮贡+{banggong_reward} 金钱+{CHA_GUAN_FINAL_REWARD_MONEY}"
                            )

                    else:
                        returnMsg.append(f"[CQ:at,qq={qq_account}] 任务物品不足！")

        return returnMsg

    async def do_qiyu(self):
        has_qiyu = False
        print(self._qiyu_status)
        pending_qiyu_list = [k for k, v in self._qiyu_status.items() if v['pending_qiyu'] != ""]

        for qq_account in pending_qiyu_list:
            qiyu_name = self._qiyu_status[qq_account]['pending_qiyu']
            qiyu = QIYU_LIST[qiyu_name]

            if self._qiyu_status[qq_account].get('has_qiyu_in_same_command', False):
                logging.info("this qq has qiyu already in same command, ignoring")
                self._qiyu_status[qq_account]['has_qiyu_in_same_command'] = False
                self._qiyu_status[qq_account]['pending_qiyu'] = ""
                continue

            if time.time() - self._qiyu_status[qq_account]['cd'].get(qiyu_name, 0) < qiyu['cooldown']:
                logging.info('qi yu in cd!')
                self._qiyu_status[qq_account]['pending_qiyu'] = ""
                continue

            require_meet = True
            if 'require' in qiyu:
                for key, val in qiyu['require'].items():
                    if key in self._jx3_users[qq_account]:
                        require_meet = require_meet and (self._jx3_users[qq_account][key] >= val)
                        requireMsg += f"{key}: {self._jx3_users[qq_account][key]} > {val}; "

            if not require_meet:
                logging.info(f"qiyu require not met! qq: {qq_account} require: {requireMsg}")
            else:
                rand = random.uniform(0, 1)

                if rand > qiyu['chance']:
                    logging.info(f"No qiyu qq: {qq_account} chance: {rand} > {qiyu['chance']}")
                else:
                    rewardMsg = ""
                    for k, v in qiyu['reward'].items():
                        if k in self._jx3_users[qq_account]:
                            self._jx3_users[qq_account][k] += v
                            rewardMsg += f"\n{USER_STAT_DISPLAY[k]}+{v}"

                    if qiyu_name not in self._jx3_users[qq_account]['qiyu']:
                        self._jx3_users[qq_account]['qiyu'][qiyu_name] = 0

                    self._jx3_users[qq_account]['qiyu'][qiyu_name] += 1

                    self._qiyu_status[qq_account]['cd'][qiyu_name] = time.time()
                    self._qiyu_status[qq_account]['has_qiyu_in_same_command'] = True

                    returnMsg = (
                        f"{qiyu['description'].format(qq_account)}\n"
                        f"获得奖励：{rewardMsg}"
                    )

                    await get_bot().send_group_msg(group_id=int(self._qq_group), message=returnMsg)
                    has_qiyu = True

                    logging.info(f"qiyu! qq: {qq_account} qiyu_name: {qiyu_name} success_chance: {rand} < {qiyu['chance']}")
                
                self._qiyu_status[qq_account]['pending_qiyu'] = ""

        return has_qiyu

    @data_handler(read_only=True)
    def get_jjc_info(self, qq_account: str):
        if qq_account not in self._jjc_data['current_season_data']:
            self._jjc_data['current_season_data'][qq_account] = {'score': 0, 'last_time': None, 'win': 0, 'lose': 0}

        jjc_status = self._jjc_data['current_season_data'][qq_account]

        total_match = jjc_status['win'] + jjc_status['lose']
        win_chance = int(jjc_status['win'] * 100 / total_match) if total_match > 0 else 100

        returnMsg = (
            f"[CQ:at,qq={qq_account}] 第{self._jjc_data['season']}赛季名剑大会分数："
            f"{jjc_status['score']} 段位：{jjc_status['score'] // 100} "
            f"胜负：{jjc_status['win']}/{total_match} 胜率：{win_chance}%"
        )

        return returnMsg

    @data_handler()
    def join_class(self, qq_account: str, class_display_name):
        if self._jx3_users[qq_account]['class_id'] != 'da_xia':
            returnMsg = f"[CQ:at,qq={qq_account}] 你已经加入了门派{CLASS_LIST[self._jx3_users[qq_account]['class_id']]}！"
        elif class_display_name in CLASS_LIST.values():
            self._jx3_users[qq_account]['class_id'] = get_class_id_by_display_name(class_display_name)
            returnMsg = f"[CQ:at,qq={qq_account}] 加入门派{class_display_name}！"

        return returnMsg

    @data_handler()
    def remove_lover(self, qq_account):
        if self._jx3_users[qq_account]['lover'] == "":
            returnMsg = f"[CQ:at,qq={qq_account}] 你没有情缘，别乱用。"
        else:
            lover = self._jx3_users[qq_account]['lover']
            love_time = time.time() - self._jx3_users[qq_account]['lover_time']
            self._jx3_users[qq_account]['lover_time'] = None
            self._jx3_users[qq_account]['lover'] = ""
            self._jx3_users[lover]['lover_time'] = None
            self._jx3_users[lover]['lover'] = ""
            returnMsg = f"[CQ:at,qq={qq_account}] 决定去寻找新的旅程。"

        return returnMsg

    def _get_leader_by_member(self, qq_account_str):
        for k, v in self._group_info.items():
            if qq_account_str in v['member_list']:
                return k
        return ""

    @data_handler(async_func=True)
    async def create_group(self, qq_account: str):
        if qq_account in self._group_info:
            returnMsg = f"[CQ:at,qq={qq_account}] 你已经创建了一个队伍了！"
        else:
            find_leader = self._get_leader_by_member(qq_account)
            if find_leader != "":
                leader_nickname = await get_group_nickname(self._qq_group, find_leader)
                returnMsg = "[CQ:at,qq={qq_account}] 你已经加入了 {leader_nickname} 的队伍！"
            else:
                self._group_info[qq_account] = {
                    'member_list': [qq_account],
                    'create_time': time.time()
                }
                returnMsg = (
                    f"[CQ:at,qq={qq_account}] 创建队伍成功！请让队友输入【加入队伍[CQ:at,qq={qq_account}]】加入队伍。\n"
                    f"进入副本后此队伍无法被加入，请确认人数正确后再进入副本。"
                )

        return returnMsg

    @data_handler(async_func=True)
    async def join_group(self, qq_account: str, leader: str):
        if qq_account in self._group_info:
            returnMsg = f"[CQ:at,qq={qq_account}] 你已经创建了一个队伍，不能加入其他人的队伍，输入【退出队伍】退出当前队伍。"
        elif leader not in self._group_info:
            returnMsg = f"[CQ:at,qq={qq_account}] 队伍不存在。"
        elif leader in self._dungeon_status:
            leader_nickname = await get_group_nickname(self._qq_group, leader)
            returnMsg = f"[CQ:at,qq={qq_account}] {leader_nickname} 的队伍正在副本里，无法加入。"
        elif len(self._group_info[leader]['member_list']) >= MAX_GROUP_MEMBER:
            returnMsg = f"[CQ:at,qq={qq_account}] 队伍已满，无法加入。"
        else:
            find_leader = self._get_leader_by_member(qq_account)
            if find_leader != "":
                leader_nickname = await get_group_nickname(self._qq_group, find_leader)
                returnMsg = f"[CQ:at,qq={qq_account}] 你已经加入了 {1} 的队伍，输入【退出队伍】退出当前队伍"
            else:
                self._group_info[leader]['member_list'].append(qq_account)
                leader_nickname = await get_group_nickname(self._qq_group, leader)
                returnMsg = f"[CQ:at,qq={qq_account}] 成功加入 {leader_nickname} 的队伍。"

        return returnMsg

    @data_handler(read_only=True, async_func=True)
    async def get_group_info(self, qq_account: str) -> str:
        if qq_account in self._group_info:
            leader = qq_account
        else:
            leader = self._get_leader_by_member(qq_account)

        if leader == "":
            returnMsg = f"[CQ:at,qq={qq_account}] 你没有加入任何队伍。"
        else:

            returnMsg = f"[CQ:at,qq={qq_account}] 当前队伍信息："
            if self._group_info[leader]['member_list'] != []:
                for member in self._group_info[leader]['member_list']:
                    member_nickname = await get_group_nickname(self._qq_group, member)
                    pve_gear_point = self._calculate_gear_point(self._jx3_users[member]['equipment'])['pve']
                    returnMsg += (
                        f"\n{member_nickname} "
                        f"pve装分：{pve_gear_point} {'(队长) ' if member == leader else ''}"
                    )

        return returnMsg

    @data_handler(async_func=True)
    async def get_group_list(self, qq_account: str) -> str:
        returnMsg = f"[CQ:at,qq={qq_account}] 当前存在的队伍有："
        index = 0
        for k, v in self._group_info.items():
            index += 1
            nickname = await get_group_nickname(self._qq_group, k)
            returnMsg += f"\n{index}. 队长：{nickname} 人数：{len(v['member_list'])}"

        return returnMsg

    @data_handler(async_func=True)
    async def quit_group(self, qq_account: str) -> str:
        if qq_account not in self._group_info:
            leader = self._get_leader_by_member(qq_account)
            if leader == "":
                returnMsg = f"[CQ:at,qq={qq_account}] 你不在任何队伍里。"
            else:
                self._group_info[leader]['member_list'].remove(qq_account)
                leader_nickname = await get_group_nickname(self._qq_group, leader)
                returnMsg = f"[CQ:at,qq={qq_account}] 你离开了 {leader_nickname} 的队伍。"
        else:
            self._group_info.pop(qq_account)
            if qq_account in self._dungeon_status:
                self._dungeon_status.pop(qq_account)
            returnMsg = f"[CQ:at,qq={qq_account}] 你的队伍解散了。"

        return returnMsg

    @data_handler()
    def kick_group(self, fromQQ: str, toQQ: str) -> str:
        if fromQQ not in self._group_info:
            returnMsg = f"[CQ:at,qq={fromQQ}] 你不是队长，无法使用此命令。"
        else:
            if toQQ not in self._group_info[fromQQ]:
                returnMsg = f"[CQ:at,qq={fromQQ}] 对方不在你的队里。"
            else:
                self._group_info[fromQQ]['member_list'].remove(toQQ)
                returnMsg = f"[CQ:at,qq={toQQ}] 被[CQ:at,qq={fromQQ}] 踢出了队伍。"

        return returnMsg

    @data_handler(read_only=True)
    def list_dungeon(self, qq_account: str) -> str:
        returnMsg = f"[CQ:at,qq={qq_account}] 副本列表："
        val = self._jx3_users[qq_account]

        if 'dungeon' not in val['daily_count']:
            self._jx3_users[qq_account]['daily_count']['dungeon'] = {}

        gear_point = self._calculate_gear_point(val['equipment'])
        dungeon_list = sorted(DUNGEON_LIST, key=lambda x: DUNGEON_LIST[x]['max_pve_reward_gain'])
        index = 0
        for k in dungeon_list:
            index += 1
            has_cd = k in val['daily_count']['dungeon'] and val['daily_count']['dungeon'][k] == True
            has_reward = gear_point['pve'] <= DUNGEON_LIST[k]['max_pve_reward_gain']
            can_enter = gear_point['pve'] >= DUNGEON_LIST[k].get('min_pve_reward_enter', 0)
            can_enter_msg = "有cd" if has_cd else "可进入" if can_enter else "不可进入"
            has_reward_msg = "无boss奖励" if not has_reward else "有boss奖励" if can_enter else "装分不足"
            returnMsg += f"\n{index}. {DUNGEON_LIST[k]['display_name']} {can_enter_msg} {has_reward_msg}"

        return returnMsg

    @data_handler(return_list=True)
    def start_dungeon(self, qq_account, dungeon_name) -> list:
        returnMsg = []

        dungeon_id = get_dungeon_id_by_display_name(dungeon_name)

        if 'dungeon' not in self._jx3_users[qq_account]['daily_count']:
            self._jx3_users[qq_account]['daily_count']['dungeon'] = {}

        val = self._jx3_users[qq_account]

        if dungeon_id != "":
            if qq_account not in self._group_info:
                leader = self._get_leader_by_member(qq_account)
                if leader == "":
                    returnMsg.append(f"[CQ:at,qq={qq_account}] 必须创建队伍才能进入副本。")
                else:
                    returnMsg.append(f"[CQ:at,qq={qq_account}] 你不是队长！无法使用此命令。")
            elif qq_account in self._dungeon_status:
                returnMsg.append(f"[CQ:at,qq={qq_account}] 你已经在副本里了。")
            else:
                leader = qq_account
                group = self._group_info[leader]

                has_cd = False
                cd_msg = ""
                has_energy = True
                energy_msg = ""

                has_cd = []
                no_energy = []
                pve_gear_point_too_high = []
                pve_gear_point_too_low = []

                for m in group['member_list']:
                    val = self._jx3_users[m]
                    if val['daily_count']['dungeon'].get(dungeon_id, False) == True:
                        has_cd.append(m)
                    else:
                        pve_gear_point = self._calculate_gear_point(val['equipment'])['pve']

                        if pve_gear_point >= DUNGEON_LIST[dungeon_id]['max_pve_reward_gain'] and val['daily_count']['dungeon'].get(dungeon_id, True):
                                pve_gear_point_too_high.append(m)
                                self._jx3_users[m]['daily_count']['dungeon'][dungeon_id] = False
                        elif pve_gear_point < DUNGEON_LIST[dungeon_id].get('min_pve_reward_enter', 0):
                            pve_gear_point_too_low.append(m)
                        elif val['energy'] < DUNGEON_ENERGY_REQUIRED:
                            no_energy.append(m)

                if len(has_cd) > 0:
                    returnMsg.append(f"队伍中{' '.join(['[CQ:at,qq={}]'.format(m) for m in has_cd])}有此副本cd，无法进入。")
                elif len(pve_gear_point_too_high) > 0:
                    returnMsg.append(
                        (
                            f"队伍中{' '.join(['[CQ:at,qq={}]'.format(m) for m in pve_gear_point_too_high])}pve装备太厉害啦，"
                            f"已经不能获得boss奖励了，仅可获得通关奖励且不消耗体力。如果确定还要进本的话，请再次输入 进入副本{DUNGEON_LIST[dungeon_id]['display_name']}"
                        )
                    )
                elif len(pve_gear_point_too_low) > 0:
                    returnMsg.append(
                        (
                            f"队伍中{' '.join(['[CQ:at,qq={}]'.format(m) for m in pve_gear_point_too_low])}"
                            f"装分未满副本要求({DUNGEON_LIST[dungeon_id].get('min_pve_reward_enter', 0)})，无法进入。"
                        )
                    )
                elif len(no_energy) > 0:
                    returnMsg.append(f"队伍中{' '.join(['[CQ:at,qq={}]'.format(m) for m in no_energy])}体力不足({DUNGEON_ENERGY_REQUIRED})，无法进入。")
                else:
                    self._dungeon_status[leader] = copy.deepcopy(DUNGEON_LIST[dungeon_id])
                    self._dungeon_status[leader]['boss_detail'] = []
                    self._dungeon_status[leader]['attack_count'] = {}
                    self._dungeon_status[leader]['no_reward'] = copy.deepcopy(pve_gear_point_too_high)

                    for boss_id in self._dungeon_status[leader]['boss']:
                        boss = copy.deepcopy(NPC_LIST[boss_id])
                        boss['remain_hp'] = boss['equipment']['armor']['pve']
                        self._dungeon_status[leader]['boss_detail'].append(boss)

                    energy_msg = ""

                    for m in group['member_list']:
                        self._jx3_users[m]['daily_count']['dungeon'][dungeon_id] = True
                        if m not in pve_gear_point_too_high:
                            self._jx3_users[m]['energy'] -= DUNGEON_ENERGY_REQUIRED
                            energy_msg += "[CQ:at,qq={0}] ".format(m)
                    returnMsg.append(f"[CQ:at,qq={qq_account}] 进入副本 {dungeon_name} 成功！{energy_msg}体力-{DUNGEON_ENERGY_REQUIRED}")

                    boss = self._dungeon_status[leader]['boss_detail'][0]
                    returnMsg.append(
                        (
                            f"boss战：{boss['display_name']} (1/{len(self._dungeon_status[leader]['boss_detail'])}\n"
                            f"请输入每位队员输入【攻击boss】开始战斗。"
                        )
                    )

        return returnMsg

    @data_handler(read_only=True, async_func=True)
    async def get_current_boss_info(self, qq_account: str) -> str:
        if qq_account in self._group_info:
            leader = qq_account
        else:
            leader = self._get_leader_by_member(qq_account)

        dungeon = self._dungeon_status.get(leader, {})

        if dungeon != {} and leader != "":
            current_boss = dungeon['boss_detail'][0]
            rank_list = sorted(dungeon['attack_count'].keys(), key=lambda x: dungeon['attack_count'][x]['damage'], reverse=True)
            list_len = len(rank_list)
            damage_msg = ""
            for i in range(MAX_GROUP_MEMBER):
                if i < list_len:
                    nickname = await get_group_nickname(self._qq_group, int(rank_list[i]))
                    damage_msg += (
                        f"\n{i + 1}. {nickname} 伤害：{dungeon['attack_count'][rank_list[i]]['damage']}"
                        f" 次数：{dungeon['attack_count'][rank_list[i]]['success_attack_count']}/{dungeon['attack_count'][rank_list[i]]['total_attack_count']}"
                    )
                else:
                    break

            current_boss_index = len(dungeon['boss']) - len(dungeon['boss_detail']) + 1
            boss_gear_point = self._calculate_gear_point(current_boss['equipment'])['pve']
            returnMsg = (
                f"[CQ:at,qq={qq_account}] 当前副本：{dungeon['display_name']} "
                f"当前boss：{current_boss['display_name']} {current_boss_index}/{len(dungeon['boss'])}\n"
                f"血量：{current_boss['remain_hp']}/{current_boss['equipment']['armor']['pve']} pve装分：{boss_gear_point}\n"
                f"伤害排行榜：{damage_msg}"
            )

        return returnMsg

    @data_handler(read_only=True)
    def get_dungeon_info(self, qq_account: str, dungeon_name: str) -> str:
        dungeon_id = get_dungeon_id_by_display_name(dungeon_name)

        if dungeon_id != "":
            dungeon = DUNGEON_LIST[dungeon_id]
            boss_msg = ""
            for boss_id in dungeon['boss']:
                boss = NPC_LIST[boss_id]
                boss_gear_point = self._calculate_gear_point(boss['equipment'])['pve']
                boss_msg += f"\nboss: {boss['display_name']} 装分：{boss_gear_point}"

            reward_msg = " ".join([f"{USER_STAT_DISPLAY[k]}+{v}" for k, v in dungeon['reward'].items()])
            returnMsg = (
                f"[CQ:at,qq={qq_account}] 【{dungeon['display_name']}】副本信息："
                f"{boss_msg}\n"
                f"副本装分区间：{dungeon['min_pve_reward_enter']} ~ {dungeon['max_pve_reward_gain']}\n"
                f"体力要求：{DUNGEON_ENERGY_REQUIRED} 通关奖励：{reward_msg}"
            )

        return returnMsg

    def _get_hp_range(self, buff, fromQQ_equipment, fromQQ_stat, gear_mode):
        max_hp = buff.get('max_hp', 1) * fromQQ_equipment['armor'][gear_mode]
        min_hp = buff.get('min_hp', 0) * fromQQ_equipment['armor'][gear_mode]

        return fromQQ_stat.get('remain_hp', fromQQ_equipment['armor'][gear_mode]) >= min_hp \
            and fromQQ_stat.get('remain_hp', fromQQ_equipment['armor'][gear_mode]) <= max_hp

    def _apply_skill_internal(self, buff, equipment, stat, gear_mode):
        if 'max_count' in buff and buff.get('count', -1) >= 0:
            equipment['weapon'][gear_mode] = int(equipment['weapon'][gear_mode] * (1 + buff['weapon'] * buff['count']))
            description = buff['description'].format(buff['count'], buff['max_count'])
        elif 'money' in buff:
            if 'reward' not in stat:
                stat['reward'] = {'money': 0}
            stat['reward']['money'] += buff['money']
            stat['hp_recover'] = 'hp_recover'
            description = buff['description']
        elif 'hp_recover' in buff :
            stat['hp_recover'] = 'hp_recover'
            description = buff['description']
        elif 'attack_count' in buff:
            stat['available_attack_modifier'] = buff['attack_count']
            description = buff['description']
        else:
            equipment['weapon'][gear_mode] = int(equipment['weapon'][gear_mode] * buff['weapon'])
            description = buff['description']

        return description

    def _apply_skill_self(self, buff_list, equipment, stat, gear_mode):
        for buff in random.sample(buff_list, len(buff_list)):
            rand = random.uniform(0, 1)

            if rand <= buff['chance'] and self._get_hp_range(buff, equipment, stat, gear_mode):
                description = self._apply_skill_internal(buff, equipment, stat, gear_mode)
                buff_msg = "\n{0}使出了招数：{1}。{2}".format(stat['display_name'], buff['display_name'], description)

                return buff_msg
        return ""

    def _apply_skill_other(self, buff_list, fromQQ_equipment, fromQQ_stat, toQQ_equipment, toQQ_stat, gear_mode):
        for buff in random.sample(buff_list, len(buff_list)):
            rand = random.uniform(0, 1)

            if rand <= buff['chance'] and self._get_hp_range(buff, fromQQ_equipment, fromQQ_stat, gear_mode):
                description = self._apply_skill_internal(buff, toQQ_equipment, toQQ_stat, gear_mode)
                buff_msg = "\n{0}使出了招数：{1}。{2}".format(fromQQ_stat['display_name'], buff['display_name'], description)

                return buff_msg
        return ""

    def _calculate_skill(self, fromQQ_stat: dict, toQQ_stat: dict, gear_mode: str) -> None:
        fromQQ_buff = fromQQ_stat.get('buff', [])
        fromQQ_debuff = fromQQ_stat.get('debuff', [])
        fromQQ_equipment = fromQQ_stat['equipment']

        toQQ_buff = toQQ_stat.get('buff', [])
        toQQ_debuff = toQQ_stat.get('debuff', [])
        toQQ_equipment = toQQ_stat['equipment']

        buff_msg = ""

        buff_msg += self._apply_skill_self(fromQQ_buff, fromQQ_equipment, fromQQ_stat, gear_mode)
        buff_msg += self._apply_skill_self(toQQ_buff, toQQ_equipment, toQQ_stat, gear_mode)
        buff_msg += self._apply_skill_other(fromQQ_debuff, fromQQ_equipment, fromQQ_stat, toQQ_equipment, toQQ_stat, gear_mode)
        buff_msg += self._apply_skill_other(toQQ_debuff, toQQ_equipment, toQQ_stat, fromQQ_equipment, fromQQ_stat, gear_mode)

        return buff_msg

    def _calculate_battle(self, fromQQ_stat: dict, toQQ_stat: dict, gear_mode: str) -> dict:
        buff_msg = self._calculate_skill(fromQQ_stat, toQQ_stat, gear_mode)

        toQQ_equipment = toQQ_stat['equipment']
        toQQ_modifier = toQQ_equipment.get('modifier', 1)
        toQQ_gear_point = self._calculate_gear_point(toQQ_equipment)[gear_mode] * toQQ_modifier
        toQQ_armor = toQQ_equipment['armor'][gear_mode] * toQQ_modifier

        fromQQ_equipment = fromQQ_stat['equipment']
        fromQQ_modifier = fromQQ_equipment.get('modifier', 1)
        fromQQ_gear_point = self._calculate_gear_point(fromQQ_equipment)[gear_mode] * fromQQ_modifier
        fromQQ_weapon = fromQQ_equipment['weapon'][gear_mode] * fromQQ_modifier

        random_base = random.uniform(0.4, 0.5)
        success_chance = random_base + 0.25 * ((fromQQ_gear_point - toQQ_gear_point) / float(toQQ_gear_point)) + 0.25 * float(fromQQ_weapon) / float(toQQ_armor)

        logging.info(
            (
                f"success_chance: {random_base} + "
                f"0.25 * {(fromQQ_gear_point - toQQ_gear_point) / float(toQQ_gear_point)} + "
                f"0.25 * {float(fromQQ_weapon) / float(toQQ_armor)}"
            )
        )

        chance = random.uniform(0, 1)
        logging.info("chance: {0}, success_chance: {1}".format(chance, success_chance))
        if chance <= success_chance:
            winner = fromQQ_stat['qq_account']
            loser = toQQ_stat['qq_account']
        else:
            winner = toQQ_stat['qq_account']
            loser = fromQQ_stat['qq_account']

        return {'winner': winner, 'loser': loser, 'success_chance': int(math.floor(success_chance * 100)), 'damage': fromQQ_weapon, 'buff_msg': buff_msg}

    @data_handler(return_list=True, async_func=True)
    async def attack_boss(self, qq_account: str) -> list:
        returnMsg = []

        if qq_account in self._group_info:
            leader = qq_account
        else:
            leader = self._get_leader_by_member(qq_account)

        dungeon = self._dungeon_status.get(leader, {})

        if dungeon != {} and leader != "":
            current_boss = dungeon['boss_detail'][0]

            if qq_account not in dungeon['attack_count']:
                dungeon['attack_count'][qq_account] = {
                    'remain_hp': self._jx3_users[qq_account]['equipment']['armor']['pve'],
                    'damage': 0,
                    'available_attack': DUNGEON_MAX_ATTACK_COUNT,
                    'last_attack_time': time.time(),
                    'total_attack_count': 0,
                    'success_attack_count': 0
                }

            if dungeon['attack_count'][qq_account]['available_attack'] < DUNGEON_MAX_ATTACK_COUNT:
                count = int(math.floor((time.time() - dungeon['attack_count'][qq_account]['last_attack_time']) / float(DUNGEON_ATTACK_COOLDOWN)))
                min_count = min(count, DUNGEON_MAX_ATTACK_COUNT - dungeon['attack_count'][qq_account]['available_attack'])
                dungeon['attack_count'][qq_account]['available_attack'] += min_count
                if min_count > 0:
                    dungeon['attack_count'][qq_account]['last_attack_time'] += min_count * DUNGEON_ATTACK_COOLDOWN

            if dungeon['attack_count'][qq_account]['available_attack'] >= DUNGEON_MAX_ATTACK_COUNT:
                dungeon['attack_count'][qq_account]['last_attack_time'] = time.time()

            if dungeon['attack_count'][qq_account]['available_attack'] < 1:
                remain_time_string = get_remaining_time_string(
                    DUNGEON_ATTACK_COOLDOWN * (1 - dungeon['attack_count'][qq_account]['available_attack']),
                    dungeon['attack_count'][qq_account]['last_attack_time']
                )
                returnMsg.append(f"[CQ:at,qq={qq_account}] 你没有攻击次数啦，还需要等待{remain_time_string}。")
            else:
                # nickname = await get_group_nickname(self._qq_group, qq_account)
                qq_stat = {
                    'qq_account': qq_account,
                    # 'display_name': nickname,
                    'equipment': copy.deepcopy(self._jx3_users[qq_account]['equipment']),
                    'remain_hp': dungeon['attack_count'][qq_account]
                }
                boss_stat = {
                    'qq_account': 'boss',
                    'display_name': current_boss['display_name'],
                    'equipment': copy.deepcopy(current_boss['equipment']),
                    'buff': current_boss.get('buff', []),
                    'debuff': current_boss.get('debuff', []),
                    'remain_hp': current_boss['remain_hp']
                }

                battle_result = self._calculate_battle(qq_stat, boss_stat, 'pve')

                winner = battle_result['winner']
                loser = battle_result['loser']
                success_chance = battle_result['success_chance']
                damage = battle_result['damage']
                buff_msg = battle_result['buff_msg']

                dungeon['attack_count'][qq_account]['total_attack_count'] += 1

                battle_msg = (
                    f"[CQ:at,qq={qq_account}] 你对{current_boss['display_name']}发起了攻击。"
                )

                boss_max_hp = current_boss['equipment']['armor']['pve']

                if loser == qq_account:
                    dungeon['attack_count'][qq_account]['available_attack'] -= 1 + qq_stat.get('available_attack_modifier', 0)
                    battle_msg += (
                        f"剩余攻击次数：{dungeon['attack_count'][qq_account]['available_attack']}/{DUNGEON_MAX_ATTACK_COUNT}"
                        f"{buff_msg}"
                        f"\n攻击失败！成功率：{success_chance}%。"
                        f"{current_boss['display_name']}血量：{current_boss['remain_hp']}/{boss_max_hp}"
                    )
                else:
                    dungeon['attack_count'][qq_account]['damage'] += damage
                    dungeon['attack_count'][qq_account]['available_attack'] -= 1 + qq_stat.get('available_attack_modifier', 0)
                    dungeon['attack_count'][qq_account]['success_attack_count'] += 1
                    dungeon['attack_count'][qq_account]['remain_hp'] += min(qq_stat.get('recover_hp', 0), self._jx3_users[qq_account]['equipment']['armor']['pve'] - qq_stat.get('recover_hp', 0))
                    current_boss['remain_hp'] += min(boss_stat.get('recover_hp', 0), boss_max_hp - boss_stat.get('recover_hp', 0))
                    current_boss['remain_hp'] -= min(damage, current_boss['remain_hp'])

                    if 'buff' in current_boss:
                        for buff in current_boss['buff']:
                            if buff.get('increase_type', '') == 'lose' and 'count' in buff and 'max_count' in buff:
                                buff['count'] += 1 if buff['count'] < buff['max_count'] else 0

                    battle_msg += (
                        f"剩余攻击次数：{dungeon['attack_count'][qq_account]['available_attack']}/{DUNGEON_MAX_ATTACK_COUNT}"
                        f"{buff_msg}"
                        f"\n攻击成功！成功率：{success_chance}%，"
                        f"造成伤害：{damage}。"
                        f"{current_boss['display_name']}血量：{current_boss['remain_hp']}/{boss_max_hp}"
                    )

                returnMsg.append(battle_msg)

                if current_boss['remain_hp'] <= 0:
                    reward_member_msg = ""
                    reward_msg = ""

                    for k, v in current_boss['reward'].items():
                        for m in self._group_info[leader]['member_list']:
                            if k in self._jx3_users[m] and m not in dungeon['no_reward']:
                                self._jx3_users[m][k] += v
                                reward_member_msg += f"[CQ:at,qq={m}] "
                                reward_msg = "获得奖励：{0}+{1} ".format(USER_STAT_DISPLAY[k], v)

                    item_reward_msg = ""
                    for k, v in current_boss['reward_item'].items():
                        for m in self._group_info[leader]['member_list']:
                            if m not in dungeon['no_reward']:
                                rand = random.uniform(0, 1)
                                if rand <= v:
                                    if k not in self._jx3_users[m]['bag']:
                                        self._jx3_users[m]['bag'][k] = 0
                                    self._jx3_users[m]['bag'][k] += 1
                                    item_reward_msg += f"\n[CQ:at,qq={m}] 获得额外奖励：{get_item_display_name(k)} x 1 概率：{int(v * 100)}%"

                    mvp = sorted(dungeon['attack_count'].keys(), key=lambda x: dungeon['attack_count'][x]['damage'], reverse=True)

                    mvp_qq = mvp[0]
                    mvp_reward_msg = ""
                    if 'mvp_reward' in dungeon and mvp_qq not in dungeon['no_reward']:
                        mvp_reward_msg = "mvp奖励加成："
                        for k, v in dungeon['mvp_reward'].items():
                            if k in self._jx3_users[mvp_qq]:
                                self._jx3_users[mvp_qq][k] += v
                                mvp_reward_msg += f"{USER_STAT_DISPLAY[k]}+{v} "

                    returnMsg.append(
                        (
                            f"{current_boss['display_name']}成功被击倒！{reward_msg}{item_reward_msg}\n"
                            f"mvp：[CQ:at,qq={mvp_qq}] 伤害：{dungeon['attack_count'][mvp_qq]['damage']} "
                            f"攻击次数：{dungeon['attack_count'][mvp_qq]['success_attack_count']}/{dungeon['attack_count'][mvp_qq]['total_attack_count']}"
                            f"\n{mvp_reward_msg}"
                        )
                    )

                    for k, v in dungeon['attack_count'].items():
                        dungeon['attack_count'][k] = {
                            'remain_hp': self._jx3_users[qq_account]['equipment']['armor']['pve'],
                            'damage': 0,
                            'available_attack': DUNGEON_MAX_ATTACK_COUNT,
                            'last_attack_time': time.time(),
                            'total_attack_count': 0,
                            'success_attack_count': 0
                        }

                    dungeon['boss_detail'].pop(0)

                    if len(dungeon['boss_detail']) > 0:
                        next_boss =  dungeon['boss_detail'][0]
                        boss_index = len(dungeon['boss']) - len(dungeon['boss_detail']) + 1
                        returnMsg.append(
                            (
                                f"boss战：{next_boss['display_name']} "
                                f"{boss_index}/{len(dungeon['boss'])}\n"
                                f"请输入每位队员输入【攻击boss】开始战斗。"
                            )
                        )
                    else:
                        reward_msg = ""
                        for k, v in dungeon['reward'].items():
                            for m in self._group_info[leader]['member_list']:
                                if k in self._jx3_users[m]:
                                    self._jx3_users[m][k] += v
                            reward_msg += "{0} + {1} ".format(USER_STAT_DISPLAY[k], v)

                        returnMsg.append(f"副本已结束！恭喜通关{dungeon['display_name']}！全员获得通关奖励：{reward_msg}")

                        returnMsg.append("队伍已解散。")
                        self._group_info.pop(leader)
                        self._dungeon_status.pop(leader)

        return returnMsg

    @data_handler(read_only=True)
    def get_jx3_daily_info(self, qq_account: str) -> str:
        big_war = ""
        battle_field = ""
        for activity in self._jx3_daily_info:
            for act in activity['activity_list']:
                if '大战·' in act['title']:
                    big_war = act['title'].split('大战·')[1]
                if '战场-' in act['title']:
                    battle_field = act['title'].split('战场-')[1]

        returnMsg = f"[CQ:at,qq={qq_account}]本日剑三大战本：{big_war}, 战场：{battle_field}。"

        weekday = datetime.datetime.today().weekday()
        if weekday == 1 or weekday == 3:
            returnMsg += "本日有阵营小攻防。"

        return returnMsg