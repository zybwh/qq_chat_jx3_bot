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
    
    def reset_daliy_count(self, yday):
        if yday != self._today and self._name != 'zhong_li':
            self._today = yday
            self._yesterday_score_reward = self._today_score / len(self._member_list)
            self._today_score = 0
    
    def get_yesterday_faction_reward(self):
        return _yesterday_score_reward