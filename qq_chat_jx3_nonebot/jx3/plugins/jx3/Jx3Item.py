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

class Jx3Item(object):
    _name = ''
    _display_name = ''
    _rank = 0
    _cost = {}
    _effect = {}
    _firework = []

    def __init__(self, name, data):
        self._name = name
        self._display_name = data['display_name']
        self._rank = data['rank']
        self._cost = data.get('cost', {})
        self._effect = data.get('effect', {})
        self._firework = data.get('firework', [])
    
    def is_firework(self):
        return self._firework != []
    
    def use_item(self, user, amount, toQQ, group):
        if self._firework != []:
            return self.use_firework(user.get_qq_account_str(), toQQ, group)
        returnMsg = "[CQ:at,qq={0}]\n使用 {1} x {2}\n"
        for stat, v in self._effect.items():
            if stat in USER_STAT_DISPLAY:
                if stat == 'weiwang':
                    user.modify_weiwang(v * item_amount)
                elif stat == 'banggong':
                    user.modify_banggong(v * item_amount)
                elif stat == 'money':
                    user.modify_money(v * item_amount)
                elif stat == 'energy':
                    user.modify_energy(v * item_amount)
                returnMsg += "{0}+{1} ".format(USER_STAT_DISPLAY[stat], v * item_amount)
            elif k == 'pve_weapon':
                self.equipment[qq_account_str]['weapon']['pve'] += v * item_amount
                returnMsg += "\n武器pve伤害+{0}".format(v * item_amount)
                self._update_gear_point(qq_account_str)
            elif k == 'pvp_weapon':
                self.equipment[qq_account_str]['weapon']['pvp'] += v * item_amount
                returnMsg += "\n武器pvp伤害+{0}".format(v * item_amount)
                self._update_gear_point(qq_account_str)
            elif k == 'pve_armor':
                self.equipment[qq_account_str]['armor']['pve'] += v * item_amount
                returnMsg += "\n防具pve血量+{0}".format(v * item_amount)
                self._update_gear_point(qq_account_str)
            elif k == 'pvp_armor':
                self.equipment[qq_account_str]['armor']['pvp'] += v * item_amount
                returnMsg += "\n防具pvp血量+{0}".format(v * item_amount)
                self._update_gear_point(qq_account_str)
        return returnMsg

    def use_firework(self, fromQQ, toQQ, group):
        import CQSDK
        for msg in self._firework:
            if msg != "" and group != "":
                "hahahah"
        return ""