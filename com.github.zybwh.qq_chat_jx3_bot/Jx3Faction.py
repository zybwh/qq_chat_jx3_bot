# -*- coding:gbk -*-

import sys
reload(sys)
sys.setdefaultencoding('gbk')

FACTION_LIST = {
    'zhong_li': '中立',
    'e_ren': '恶人谷',
    'hao_qi': '浩气盟'
}

OLD_FACTION_LIST = [
    'zhong_li',
    'e_ren',
    'hao_qi'
]

def convert_old_faction_id_to_new_faction_id(old_id):
    if old_id in OLD_FACTION_LIST:
        return old_id
    return OLD_FACTION_LIST[old_id]

def convert_display_name_to_faction_id(display_name):
    if display_name in FACTION_LIST.values():
        return FACTION_LIST.keys()[FACTION_LIST.values().index(display_name)]
    return ""

class Jx3Faction(object):
    _name = ''
    _display_name = ''
    _member_list = []
    _today = 0
    _today_score = 0
    _yesterday_score_reward = 0
    
    def __init__(self, name, display_name):
        self._name = name
        self._display_name = display_name
    
    def dump_data(self):
        return self._name
    
    def get_display_name(self):
        return self._display_name
    
    def is_zhong_li(self):
        return self._name == 'zhong_li'
    
    def reset_daliy_count(self, yday):
        if yday != self._today and not self.is_zhong_li():
            self._today = yday
            self._yesterday_score_reward = self._today_score / len(self._member_list)
            self._today_score = 0
    
    def score_gain(self, score_gain):
        _today_score += score_gain
    
    def get_yesterday_faction_reward(self):
        return _yesterday_score_reward
    
    def is_member(self, qq_account_str):
        return qq_account_str in self._member_list
    
    def add_member(self, qq_acount_str):
        self._member_list.append(qq_acount_str)

    def remove_member(self, qq_acount_str):
        self._member_list.remove(qq_acount_str)