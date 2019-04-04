import time
import copy

from .Utils import *

daliy_dict = {
    'qiandao': False,
    'speech_count': 0,
    'ya_biao': 0,
    'wa_bao': {'count': 0, 'last_time': None},
    'jailed': 0,
    'cha_guan': {'complete_quest': [], 'current_quest': ""},
    "speech_energy_gain": 0,
    'rob': {'weiwang': 0, 'money': 0, 'last_rob_time': None},
    'practise': {'weiwang': 0},
    'jjc': {'score': 0, 'last_time': None, 'win': 0, 'lose': 0},
    'dungeon': {},
    'item_usage': {}
}

default_equipment = {
    'weapon': {"display_name": "大侠剑", 'pvp': 10, 'pve': 10}, 
    'armor': {"display_name": "大侠衣", 'pvp': 100, 'pve': 100}
}

class Jx3User(object):

    _qq_account_str = ""
    _class_ptr = None
    _faction_ptr = None
    _faction_join_time = None

    _weiwang = 0
    _money = 0
    _banggong = 0
    _energy = 0

    _achievement = {}

    _lover = ""
    _lover_time = None

    _qiyu = {}

    register_time = None    
    _qiandao_count = 0

    _today = 0
    _daliy_count = {}

    _bag = {}
    _equipment = {}

    def __init__(self, data={}):
        if data == {}:
            return
        self._qq_account_str = data['qq_account_str']
        self._class_ptr = data.get('class_ptr')
        self._faction_ptr = data.get('faction_ptr')
        self._faction_join_time = data.get('faction_join_time')

        self._weiwang = data.get('weiwang', 0)
        self._banggong = data.get('banggong', 0)
        self._money = data.get('money', 0)
        self._energy = data.get('energy', 0)

        self._achievement = data.get('achievement', {})
        
        self._lover = data.get('lover', "")
        self._lover_time = data.get('lover_time')

        self._qiyu = data.get('qiyu', {})
        self.register_time = data.get('register_time', time.time())
        self._qiandao_count = data.get('qiandao_count', 0)

        self._bag = data.get('bag', {})
        self._equipment = data.get('equipment', copy.deepcopy(default_equipment))

        self._today = data.get('today', 0)
        self._daliy_count = data.get('daliy_count', copy.deepcopy(daliy_dict))

    def dump_data(self):
        return {
            'qq_account_str': self._qq_account_str,
            'class_id': self._class_ptr.dump_data(),
            'faction_id': self._faction_ptr.dump_data(),
            'faction_join_time': self._faction_join_time,
            'weiwang': self._weiwang,
            'banggong': self._banggong,
            'money': self._money,
            'energy': self._energy,
            'achievement': self._achievement,
            'lover': self._lover,
            'lover_time': self._lover_time,
            'qiyu': {k: v['count'] for k, v in self._qiyu.items()},
            'register_time': self.register_time,
            'bag': {k: v['count'] for k, v in self._bag.items()},
            'equipment': self._equipment,
            'today': self._today,
            'daliy_count': self._daliy_count
        }
    
    def get_info(self, lover_nickname):
        return "[CQ:at,qq={0}]\n情缘:\t\t{1}\n门派:\t\t{2}\n阵营:\t\t{3}\n威望:\t\t{4}\n帮贡:\t\t{5}\n金钱:\t\t{6}G\n体力:\t\t{7}\n签到状态:\t{8}\n奇遇:\t\t{9}\n今日发言:\t{10}".format(
            self._qq_account_str,
            lover_nickname,
            self._class_ptr.get_display_name(),
            self._faction_ptr.get_display_name(),
            self._weiwang,
            self._banggong,
            self._money,
            self._energy,
            '已签到' if self._daliy_count['qiandao'] else '未签到',
            0,
            self._daliy_count['speech_count'])
    
    def qiandao(self, weiwang_reward, banggong_reward, money_reward, energy_gain):
        self.modify_weiwang(weiwang_reward)
        self.modify_banggong(banggong_reward)
        self.modify_money(money_reward)
        self.modify_energy(energy_gain)
        
        self._qiandao_count += 1

        self._daliy_count['qiandao'] = True
        returnMsg = "[CQ:at,qq={0}] 签到成功！签到奖励: 威望+{1} 帮贡+{2} 金钱+{3} 体力+{4}".format(
            self._qq_account_str,
            weiwang_reward,
            banggong_reward,
            money_reward,
            energy_gain)
        
        faction_reward = self._faction_ptr.get_yesterday_faction_reward()

        if faction_reward != 0:
            self._weiwang += faction_reward
            returnMsg += "\n获得昨日阵营奖励：威望+{0}".format(faction_reward)
        
        return returnMsg
    
    def modify_weiwang(self, weiwang_reward):
        self._weiwang += int(weiwang_reward)
    
    def modify_banggong(self, banggong_reward):
        self._banggong += int(banggong_reward)
    
    def modify_money(self, money_reward):
        self._money += int(money_reward)
    
    def modify_energy(self, energy_reward):
        self._energy += int(energy_reward)

    def has_qiandao(self):
        return self._daliy_count['qiandao']
    
    def has_energy(self, energy_require):
        return self._energy >= energy_require

    def add_speech_count(self, speech_energy_gain, max_speech_energy_gain):
        self._daliy_count['speech_count'] += 1

        if self._daliy_count['speech_energy_gain'] < max_speech_energy_gain:
            self._daliy_count['speech_energy_gain'] += speech_energy_gain
            self.modify_energy(speech_energy_gain)
    
    def can_ya_biao(self, daliy_max_ya_biao_count):
        return self._daliy_count['ya_biao'] < daliy_max_ya_biao_count

    def ya_biao(self, weiwang_reward, money_reward, energy_cost):
        self.modify_weiwang(weiwang_reward)
        self.modify_money(money_reward)
        self.modify_energy(0 - energy_cost)
        self._daliy_count['ya_biao'] += 1

    def get_faction(self):
        return self._faction_ptr
    
    def get_faction_join_time(self):
        return self._faction_join_time
    
    def get_lover(self):
        return self._lover
    
    def get_qq_account_str(self):
        return self._qq_account_str
    
    def addd_lover(self, lover_str):
        self._lover = lover_str
        self._lover_time = time.time()

    def join_faction(self, faction_ptr):
        self._faction_ptr.remove_member(self._qq_account_str)
        self._faction_ptr = faction_ptr
        self._faction_ptr.add_member(self._qq_account_str)
        self._faction_join_time = time.time()
    
    def display_bag(self):
        returnMsg = ""
        for item_name, v in self._bag.items():
            if v['amount'] != 0:
                returnMsg += "\n{0} x {1}".format(v['object'].get_display_name(), v['amount'])
        
        if returnMsg == "":
            returnMsg = "\n空空如也"
        return returnMsg
    
    def check_item(self, item_name):
        return item_name in self.bag

    def use_item(self, item_name, amount=1, toQQ="", qq_group=""):
        returnMsg = self._bag[item_name]['object'].use_item(self, amount, toQQ, qq_group)
        self._bag[item_name]['amount'] -= amount
        if self._bag[item_name]['amount'] == 0:
            self.bag.pop(item_name)
        return returnMsg
    
    def buy_item(self, item, amount):
        if item not in self.bag:
            self.bag[item] = 0
        returnMsg = item(self, amount)
        self.bag[item] += amount
        return returnMsg
    
    def reset_daliy_count(self, yday, keep_jjc_data=False):
        return_dict = {}
        if yday != self._today:
            new_daliy = copy.deepcopy(daliy_dict)
            if keep_jjc_data:
                new_daliy['jjc'] = copy.deepcopy(self._daliy_count['jjc'])
            else:
                return_dict = copy.deepcopy(self._daliy_count['jjc'])
            self._daliy_count = new_daliy
            self._today = yday
        
        return return_dict

    def get_pve_gear_point(self):
        weapon = equipment['weapon']
        armor = equipment['armor']
        return weapon['pve'] * 50 + armor['pve'] * 10
    
    def get_pvp_gear_point(self):
        weapon = equipment['weapon']
        armor = equipment['armor']
        return weapon['pvp'] * 50 + armor['pvp'] * 10
    


