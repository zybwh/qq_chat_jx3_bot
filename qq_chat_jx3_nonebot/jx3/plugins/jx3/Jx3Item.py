ITEM_LIST = {
    "zhen_cheng_zhi_xin": {
        "display_name": "真橙之心",
        "rank": 2, 
        "cost": {"money": 999},
        'firework': [
            "    [CQ:face,id=145][CQ:face,id=145]    [CQ:face,id=145][CQ:face,id=145]    \n[CQ:face,id=145]         [CQ:face,id=145]         [CQ:face,id=145]\n    [CQ:face,id=145]                [CQ:face,id=145]\n          [CQ:face,id=145]    [CQ:face,id=145]\n               [CQ:face,id=145]",
            "“江湖飞马来报！[CQ:at,qq={0}] 侠士对 [CQ:at,qq={1}] 侠士使用了传说中的【真橙之心】！以此向天下宣告其爱慕之心，奉日月以为盟，昭天地以为鉴，啸山河以为证，敬鬼神以为凭。从此山高不阻其志，涧深不断其行，流年不毁其意，风霜不掩其情。纵然前路荆棘遍野，亦将坦然无惧仗剑随行。今生今世，不离不弃，永生永世，相许相从！”"
        ]
    },
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

USER_STAT_DISPLAY = {
    'banggong': '',
    'weiwang': '',
    'money': '',
    'energy': ''
}

def load_item_data(data, item_list):
    return {k: {'object': item_list[k], 'count': v} for k, v in data.items()}

def get_item_display_name(item_name):
    return ITEM_LIST[item_name]['display_name'] if item_name in ITEM_LIST else ""