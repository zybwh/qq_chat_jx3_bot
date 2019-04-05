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

def get_faction_id(fid):
    if isinstance(fid, str) and fid in OLD_FACTION_LIST:
        return fid
    return OLD_FACTION_LIST[fid]

def convert_display_name_to_faction_id(display_name):
    if display_name in FACTION_LIST.values():
        return FACTION_LIST.keys()[FACTION_LIST.values().index(display_name)]
    return ""
