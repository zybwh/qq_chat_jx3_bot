import random
import logging

from .Jx3Class import *
from .Jx3User import *
from .Jx3Faction import *
from .Jx3Qiyu import *
from .Jx3Item import *
from .GameConfig import *


class Jx3Handler(object):

    _jx3_class = {}
    _jx3_users = {}
    _jx3_faction = {}
    _jx3_qiyu = {}
    _jx3_item = {}
    _jjc_data = {
        'season': 1,
        'day': 1
    }
    _jjc_history = {}
    
    def __init__(self, qq_group, game_data={}):
        self._qq_group = qq_group
        self._init_game_data()

        if game_data != {}:
            self.read_data(game_data)

    def _init_game_data(self):
        self._init_class_data()
        self._init_faction_data()
        self._init_qiyu_data()
        self._init_item_data()

    def _init_class_data(self):
        for k, v in CLASS_LIST.items():
            self._jx3_class[k] = Jx3Class(k, v)
    
    def _init_faction_data(self):
        for k, v in FACTION_LIST.items():
            self._jx3_faction[k] = Jx3Faction(k, v)
    
    def _init_qiyu_data(self):
        for k, v in QIYU_LIST.items():
            self._jx3_qiyu[k] = Jx3Qiyu(k, v)
    
    def _init_item_data(self):
        for k, v in ITEM_LIST.items():
            self._jx3_item[k] = Jx3Item(k, v)
    
    def _load_user_data(self, user_data):
        try:
            for k, v in user_data.items():
                val = copy.deepcopy(v)
                data = {
                    'qq_account_str': str(k),
                    'class_ptr': self._jx3_class[get_class_id(val['class_id'])],
                    'faction_ptr': self._jx3_faction[get_faction_id(val['faction_id'])],
                    'faction_join_time': val['faction_join_time'],
                    'weiwang': val['weiwang'],
                    'banggong': val['banggong'],
                    'money': val['money'],
                    'energy': val['energy'],
                    # 'achievement': convert_old_achievement_to_new(v['achievement']),
                    'lover': val['lover'],
                    'lover_time': val['lover_time'],
                    'qiyu': convert_old_qiyu_to_new_list(val['qiyu']),
                    'register_time': val['register_time'],
                    'bag': load_item_data(val['bag'], self._jx3_item),
                    'equipment': val['equipment'],
                }
                if 'today' in val:
                    data['today'] = val['today']
                if 'daliy_count' in val:
                    data['daliy_count'] = val['daliy_count']

                self._jx3_users[k] = Jx3User(data)
        except Exception as e:
            logging.exception(e)

    def read_data(self, game_data):
        try:
            if 'equipment' in game_data:
                for k, v in game_data['equipment'].items():
                    if k in game_data['jx3_users']:
                        game_data['jx3_users'][k]['equipment'] = v
            
            self._load_user_data(game_data.get('jx3_users', {}))
        except Exception as e:
            logging.exception(e)
    
    def dump_data(self):
        try:
            data = {
                "jx3_users": {k: v.dump_data() for k, v in self._jx3_users.items()}
            }
            return data
        except Exception as e:
            logging.exception(e)
    
    def add_speech_count(self, qq_account):
        try:
            self._jx3_users[str(qq_account)].add_speech_count(SPEECH_ENERGY_GAIN, DALIY_MAX_SPEECH_ENERGY_GAIN)
        except Exception as e:
            logging.exception(e)
    
    def register(self, qq_account):
        returnMsg = []
        qq_account_str = str(qq_account)

        try:
            if qq_account_str in self._jx3_users:
                returnMsg.append("[CQ:at,qq={0}] 注册失败！你已经注册过了。".format(qq_account))
            else:
                data = {
                    'qq_account_str': qq_account_str,
                    'class_ptr': self._jx3_class['da_xia'],
                    'faction_ptr': self._jx3_faction['zhong_li']
                }
                self._jx3_users[qq_account_str] = Jx3User(data)
                returnMsg.append("注册成功！\n[CQ:at,qq={0}]\n注册时间：{1}".format(
                    qq_account,
                    time.strftime('%Y-%m-%d', time.localtime(self._jx3_users[qq_account_str].register_time))
                ))
        except Exception as e:
            logging.exception(e)
        
        return returnMsg

    def is_user_register(self, qq_account):
        return str(qq_account) in self._jx3_users
    
    def get_lover(self, qq_account):
        try:
            return self._jx3_users[str(qq_account)].get_lover()
        except Exception as e:
            logging.exception(e)

    def get_info(self, qq_account, lover_nickname):
        returnMsg = []
        try:
            returnMsg.append(self._jx3_users[str(qq_account)].get_info(lover_nickname))
        except Exception as e:
            logging.exception(e)
        
        return returnMsg
    
    def qiandao(self, qq_account):
        returnMsg = []
        try:
            qq_account_str = str(qq_account)
            val = self._jx3_users[qq_account_str]

            if val.has_qiandao():
                returnMsg.append("[CQ:at,qq={0}]今天已经签到过了!".format(qq_account))
            else:
                banggong_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)
                weiwang_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)

                returnMsg.append(val.qiandao(weiwang_reward, banggong_reward, DALIY_MONEY_REWARD, DALIY_ENERGY_REWARD))
        except Exception as e:
            logging.exception(e)
        
        return returnMsg