CLASS_LIST = {
    'da_xia': '无门派',
    'tian_ce': '天策',
    'chun_yang': '纯阳',
    'shao_lin': '少林',
    'qi_xiu': '七秀',
    'wan_hua': '万花',
    'cang_jian': '藏剑',
    'wu_du': '五毒',
    'tang_men': '唐门',
    'ming_jiao': '明教',
    'gai_bang': '丐帮',
    'cang_yun': '苍云',
    'chang_ge': '长歌',
    'ba_dao': '霸刀',
    'peng_lai': '蓬莱'
}

OLD_CLASS_LIST_TO_NEW_LIST = [
    'da_xia',
    'tian_ce',
    'chun_yang',
    'shao_lin',
    'qi_xiu',
    'wan_hua',
    'cang_jian',
    'wu_du',
    'tang_men',
    'ming_jiao',
    'gai_bang',
    'cang_yun',
    'chang_ge',
    'ba_dao',
    'peng_lai'
]

def get_class_id(cid):
    if isinstance(cid, str) and cid in OLD_CLASS_LIST_TO_NEW_LIST:
        return cid
    return OLD_CLASS_LIST_TO_NEW_LIST[cid]

def get_class_id_by_display_name(display_name):
    for k, v in CLASS_LIST.items():
        if v == display_name:
            return k
    return ""
