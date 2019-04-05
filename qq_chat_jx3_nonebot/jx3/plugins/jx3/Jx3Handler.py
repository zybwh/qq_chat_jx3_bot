import random
import logging
import os

from .Jx3Class import *
from .Jx3User import *
from .Jx3Faction import *
from .Jx3Qiyu import *
from .Jx3Item import *
from .GameConfig import *
from .Utils import *

class Jx3Handler(object):

    _jx3_users = {}
    _jjc_data = {
        'season': 1,
        'day': 1
    }
    _jjc_history = {}
    
    def __init__(self, qq_group, DATABASE_PATH):
        self._qq_group = qq_group

        json_file_path = os.path.join(DATABASE_PATH, str(qq_group), 'data.json')
        game_data = {}
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as f:
                game_data = json.loads(f.readline())

        self.read_data(game_data)

    def read_data(self, game_data):
        try:
            self._load_user_data(game_data.get('jx3_users', {}))
            self._load_equipment(game_data.get('equipment', {}))
            self._load_daily_count(game_data.get('daily_action_count', {}))
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
        except Exception as e:
            logging.exception(e)
    
    def _load_equipment(self, equipment_data):
        if equipment_data != {}:
            for k, v in equipment_data['equipment'].items():
                if k in self['jx3_users']:
                    self['jx3_users'][k]['equipment'] = copy.deepcopy(v)
    
    def _load_daily_count(self, daily_count_data):
        sorted_list = sorted(daily_count_data['daily_action_count'].items, key=lambda x: int(x[0]), reverse=True)
        day, count_list = sorted_list.items()[0]
        for k, v in count_list.items():
            if k in self._jx3_users['jx3_users']:
                self._jx3_users['jx3_users'][k]['day'] = day
                self._jx3_users['jx3_users'][k]['daily_count'] = copy.deepcopy(v)
    
    def dump_data(self):
        try:
            data = {
                "jx3_users": self._jx3_users
            }
            return data
        except Exception as e:
            logging.exception(e)
    
    def add_speech_count(self, qq_account: str):
        try:
            self._jx3_users[qq_account]['daily_count']['speech_count'] += 1

            if self._jx3_users[qq_account]['daily_count']['speech_energy_gain'] < DALIY_MAX_SPEECH_ENERGY_GAIN:
                self._jx3_users[qq_account]['daily_count']['speech_energy_gain'] += SPEECH_ENERGY_GAIN
                self._jx3_users[qq_account]['energy'] += SPEECH_ENERGY_GAIN
        except Exception as e:
            logging.exception(e)

    def register(self, qq_account: str):
        returnMsg = ""

        try:
            if qq_account in self._jx3_users:
                returnMsg = "[CQ:at,qq={0}] 注册失败！你已经注册过了。".format(qq_account)
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
                    'daily_count': copy.deepcopy(daily_dict)
                }
                returnMsg = "注册成功！\n[CQ:at,qq={0}]\n注册时间：{1}".format(
                    qq_account,
                    time.strftime('%Y-%m-%d', time.localtime(self._jx3_users[qq_account].register_time))
                )
        except Exception as e:
            logging.exception(e)
        
        return returnMsg

    def is_user_register(self, qq_account: str):
        return qq_account in self._jx3_users
    
    def get_lover(self, qq_account):
        try:
            return self._jx3_users[qq_account].get_lover()
        except Exception as e:
            logging.exception(e)

    async def get_info(self, qq_account: str):
        returnMsg = ""
        try:
            returnMsg = "[CQ:at,qq={0}]\n情缘:\t\t{1}\n门派:\t\t{2}\n阵营:\t\t{3}\n威望:\t\t{4}\n帮贡:\t\t{5}\n金钱:\t\t{6}G\n体力:\t\t{7}\n签到状态:\t{8}\n奇遇:\t\t{9}\n今日发言:\t{10}".format(
                qq_account,
                await get_group_nickname(self._qq_group, self._jx3_users[qq_account]['lover']) if self._jx3_users[qq_account]['lover'] != "" else "",
                CLASS_LIST[self._jx3_users[qq_account]],
                FACTION_LIST[self._jx3_users[qq_account]],
                self._jx3_users[qq_account]['weiwang'],
                self._jx3_users[qq_account]['banggong'],
                self._jx3_users[qq_account]['money'],
                self._jx3_users[qq_account]['energy'],
                '已签到' if self._jx3_users[qq_account]['daily_count']['qiandao'] else '未签到',
                get_qiyu_count(self._jx3_users[qq_account]),
                self._jx3_users[qq_account]['daily_count']['speech_count'])
            returnMsg
        except Exception as e:
            logging.exception(e)
        
        return returnMsg
    
    def qiandao(self, qq_account):
        returnMsg = ""
        try:
            qq_account_str = str(qq_account)
            val = self._jx3_users[qq_account_str]

            if val.has_qiandao():
                returnMsg = "[CQ:at,qq={0}]今天已经签到过了!".format(qq_account)
            else:
                banggong_reward = random.randint(daily_REWARD_MIN, daily_REWARD_MAX)
                weiwang_reward = random.randint(daily_REWARD_MIN, daily_REWARD_MAX)

                returnMsg = val.qiandao(weiwang_reward, banggong_reward, daily_MONEY_REWARD, daily_ENERGY_REWARD)
        except Exception as e:
            logging.exception(e)
        
        return returnMsg
    
    def add_lover(self, fromQQ: str, toQQ: str):
        returnMsg = []

        try:
            fromQQ_stat = self.jx3_users[fromQQ]
            toQQ_stat = self.jx3_users[toQQ]

            if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in fromQQ_stat['bag'].keys():
                returnMsg = "[CQ:at,qq={0}] 绑定情缘需要消耗1个{1}。\n你并没有此物品，请先购买。".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
            else:
                if str(fromQQ_stat['lover']) == str(toQQ):
                    returnMsg = "[CQ:at,qq={0}] 你们已经绑定过啦！还想乱撒狗粮？".format(fromQQ)
                elif fromQQ_stat['lover'] != 0:
                    returnMsg = "[CQ:at,qq={0}]  想什么呢？你就不怕[CQ:at,qq={1}]打你吗？".format(fromQQ, fromQQ_stat['lover'])
                elif toQQ_stat['lover'] != 0:
                    returnMsg = "[CQ:at,qq={0}] 人家已经有情缘啦，你是想上818吗？".format(fromQQ)
                elif toQQ in self.lover_pending and self.lover_pending[str(toQQ)] != fromQQ:
                    returnMsg = "[CQ:at,qq={0}] 已经有人向[CQ:at,qq={1}]求情缘啦，你是不是再考虑一下？".format(fromQQ, toQQ)
                else:
                    pendingList = [k for k, v in self.lover_pending.items() if v == fromQQ]
                    for p in pendingList:
                        self.lover_pending.pop(p)
                    self.lover_pending[str(toQQ)] = fromQQ
                    returnMsg = "[CQ:at,qq={1}]\n[CQ:at,qq={0}] 希望与你绑定情缘，请输入 同意 或者 拒绝。".format(fromQQ, toQQ)
        except Exception as e:
            logging.exception(e)
        
        return returnMsg