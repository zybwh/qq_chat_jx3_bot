import Utils

ITEM_LIST = {
    "zhen_cheng_zhi_xin": {"display_name": "真橙之心", "rank": 2, "cost": {"money": 999}},
    "hai_shi_shan_meng": {"display_name": "海誓山盟", "rank": 1, "cost": {"money": 9999}},
    "jin_zhuan": {"display_name": "金砖", "rank": 5, "effect": {"money": 50}},
    "jin_ye_zi": {"display_name": "金叶子", "rank": 6, "effect": {"money": 10}},
    "zhuan_shen_can": {"display_name": "转神餐", "rank": 5, "effect": {"energy": 5}, "cost": {"money": 100}},
    "jia_zhuan_shen_can": {"display_name": "佳·转神餐", "rank": 3, "effect": {"energy": 30}, "cost": {"money": 500}},
    "rong_ding": {"display_name": "熔锭", "rank": 3, "effect": {'pve_weapon': 5}, "cost": {"banggong": 5000}},
    "mo_shi": {"display_name": "磨石", "rank": 3, "effect": {'pvp_weapon': 5}, "cost": {"weiwang": 5000}},
    "ran": {"display_name": "绣", "rank": 0, "effect": {'pve_armor': 10}},
    "xiu": {"display_name": "绣", "rank": 4, "effect": {'pve_armor': 10}, "cost": {"banggong": 2000}},
    "yin": {"display_name": "印", "rank": 4, "effect": {'pvp_armor': 10}, "cost": {"weiwang": 2000}},
    "sui_rou": {"display_name": "碎肉", "rank": 4, "cost": {"money": 10}},
    "cu_bu": {"display_name": "粗布", "rank": 4, "cost": {"money": 10}},
    "gan_cao": {"display_name": "甘草", "rank": 4, "cost": {"money": 10}},
    "hong_tong": {"display_name": "红铜", "rank": 4, "cost": {"money": 10}},
    "hun_hun_zheng_ming": {"display_name": "混混抓捕证明", "rank": 0}
}

def load_item_data(data, item_list):
    return {k: {'object': item_list[k], 'count': v} for k, v in data.items()}

def Jx3Item(object):
    _name = ''
    _display_name = ''
    _rank = 0
    _cost = {}
    _effect = {}

    def __init__(self, name, data):
        self._name = name
        self._display_name = data['display_name']
        self._rank = data['rank']
        self._cost = Utils.get_key_or_return_default(data, 'cost', {})
        self._effect = Utils.get_key_or_return_default(data, 'effect', {})