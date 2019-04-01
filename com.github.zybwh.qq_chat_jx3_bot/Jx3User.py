import Utils
import Jx3Item

import time
import copy

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
    'jjc': {'score': 0, 'last_time': None, 'win': 0, 'lose': 0}
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

    _achievement = {}

    _lover = ""
    _lover_time = None

    _qiyu = {}

    _energy = 0
    register_time = None
    
    _qiandao_count = 0

    _bag = {}

    _today = 0

    _daliy_count = {}

    _equipment = {}

    def __init__(self, data={})
        if data == {}:
            return
        self._qq_account_str = data['qq_account_str']
        self._class_ptr = Utils.get_key_or_return_default(data, 'class_ptr', None)
        self._faction_ptr = Utils.get_key_or_return_default(data, 'faction_ptr', None)
        self._faction_join_time = Utils.get_key_or_return_default(data, 'faction_join_time', None)

        self._weiwang = Utils.get_key_or_return_default(data, 'weiwang', 0)
        self._banggong = Utils.get_key_or_return_default(data, 'banggong', 0)
        self._money = Utils.get_key_or_return_default(data, 'money', 0)
        self._energy = Utils.get_key_or_return_default(data, 'energy', 0)

        self._achievement = Utils.get_key_or_return_default(data, 'achievement', {})
        
        self._lover = Utils.get_key_or_return_default(data, 'lover', "")
        self._lover_time = Utils.get_key_or_return_default(data, 'lover_time', None)

        self._qiyu = Utils.get_key_or_return_default(data, 'qiyu', {})
        self.register_time = Utils.get_key_or_return_default(data, 'register_time', time.time())
        self._qiandao_count = Utils.get_key_or_return_default(data, 'qiandao_count', 0)

        self._bag = Utils.get_key_or_return_default(data, 'bag', {})
        self._equipment = Utils.get_key_or_return_default(data, 'equipment', copy.deepcopy(default_equipment))

    def dump_data(self):
        return {
            'qq_account_str': self._qq_account_str,
            'class_ptr': self._class_ptr.dump_data(),
            'faction_ptr': self._faction_ptr.dump_data(),
            'faction_join_time': self._faction_join_time,
            'weiwang': self._weiwang,
            'banggong': self._banggong,
            'money': self._money,
            'energy': self._energy,
            'achievement': self._achievement,
            'lover': self._lover,
            'lover_time': self._lover_time,
            'qiyu': {k: v['count'] for k, v in self_qiyu.items()},
            'register_time': self._register_time,
            'bag': {k, v['count'] for k, v in self._bag.items()},
            'equipment': self._equipment
        }
    
    def get_info(self, qq_group):
        return "[CQ:at,qq={0}]\n情缘:\t\t{1}\n门派:\t\t{2}\n阵营:\t\t{3}\n威望:\t\t{4}\n帮贡:\t\t{5}\n金钱:\t\t{6}G\n体力:\t{7}\n签到状态:\t{8}\n奇遇:\t\t{9}\n今日发言:\t{10}".format(
            self._qq_account_str,
            "" if self._lover == 0 else Utils.get_group_nick_name(int(qq_group), int(self._lover)),
            self._class_ptr.get_display_name(),
            self._faction_ptr.get_display_name(),
            self._weiwang,
            self._banggong,
            self._money,
            self._energy,
            self._daliy_count['qiandao'],
            0,
            self._daliy_count['speech_count'])
    
    def qiandao(self, weiwang_reward, banggong_reward, money_reward, energy_gain):
        self._weiwang += weiwang_reward
        self._banggong += banggong_reward
        self._energy += energy_gain
        self._money += money_reward
        
        self._qiandao_count += 1

        self._daliy_count['qiandao'] = True
        returnMsg = "[CQ:at,qq={0}] 签到成功！签到奖励: 威望+{1} 帮贡+{2} 金钱+{3} 体力+{4}".format(
            qq_account,
            weiwang_reward,
            banggong_reward,
            money_reward,
            energy_gain)
        
        faction_reward = self._faction_ptr.get_yesterday_faction_reward()

        if faction_reward != 0:
            self._weiwang += faction_reward
            returnMsg += "\n获得昨日阵营奖励：威望+{0}".format(faction_reward)
        
        return returnMsg
    
    def has_qiandao(self):
        return self._daliy_count['qiandao']

    def add_speech_count(self, speech_energy_gain, max_speech_energy_gain):
        self._daliy_count['speech_count'] += 1

        if self._daliy_count['speech_energy_gain'] < max_speech_energy_gain:
            self._daliy_count['speech_energy_gain'] += speech_energy_gain
            self._energy += speech_energy_gain
    
    def addd_lover(self, lover_str):
        self._lover = lover_str
        self._lover_time = time.time()
    
    def display_bag(self):
        returnMsg = ""
        for item, amount in self._bag.items():
            returnMsg += "\n{0} x {1}".format(item.get_display_name(), amount)
        
        if returnMsg == "":
            returnMsg = "\n空空如也"
        return returnMsg
    
    def check_item(self, item):
        return item in self.bag
    
    def use_item(self, item, amount):
        returnMsg = item.use_item(self, amount)
        self.bag[item] -= amount
        if self.bag[item] == 0:
            self.bag.pop(item)
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
        return weapon['pve'] * 50 + armor['pve'] * 20
    
    def get_pvp_gear_point(self):
        weapon = equipment['weapon']
        armor = equipment['armor']
        return weapon['pvp'] * 50 + armor['pvp'] * 10
    


