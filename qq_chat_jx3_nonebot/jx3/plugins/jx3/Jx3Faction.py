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

faction_daily_dict = {
    'zhong_li': {
        'faction_point': 0,
        'yesterday_reward': 0
    },
    'hao_qi': {
        'faction_point': 0,
        'yesterday_reward': 0
    },
    'e_ren': {
        'faction_point': 0,
        'yesterday_reward': 0
    }
}

def get_faction_id(fid):
    if isinstance(fid, str) and fid in OLD_FACTION_LIST:
        return fid
    return OLD_FACTION_LIST[fid]

def convert_display_name_to_faction_id(display_name):
    for k, v in FACTION_LIST.items():
        if v == display_name:
            return k
    return ""
