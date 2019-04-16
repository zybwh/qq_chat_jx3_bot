from .GameConfig import *

QIYU_LIST = {
    'hong_fu_qi_tian': {
        "display_name": '鸿运当头',
        "description": "江湖快马飞报！[CQ:at,qq={0}]侠士签到时洪福降临，不经意间出发奇遇【鸿运当头】！签到时获得额外奖励。",
        "chance": 0.1,
        "cooldown": 0,
        "reward": {"money": DALIY_MONEY_REWARD, "weiwang": DALIY_REWARD_MIN, "banggong": DALIY_REWARD_MIN}
    },
    'luan_shi_wu_ji': {
        "display_name": '乱世舞姬',
        "description": "江湖快马飞报！[CQ:at,qq={0}]侠士表演惊艳绝伦，不经意间触发奇遇【乱世舞姬】！倾城独立世所稀，乱世舞起影凌乱！",
        "chance": 0.01,
        "cooldown": 1 * 60 * 60,
        "reward": {"money": 200, "energy": 100}
    },
    'hu_xiao_shan_lin': {
        "display_name": '虎啸山林',
        "description": "江湖快马飞报！[CQ:at,qq={0}]侠士正在浴血奋战，不经意间触发奇遇【虎啸山林】！正所谓十年磨一剑，不漏其锋芒。只待剑鞘出，斩尽敌首颅。",
        "chance": 0.05,
        "cooldown": 2 * 60 * 60,
        "reward": {"weiwang": 5000}
    },
    'hu_you_cang_sheng': {
        "display_name": '护佑苍生',
        "description": "江湖快马飞报！[CQ:at,qq={0}]侠士尽心保护他人，不经意间触发奇遇【护佑苍生】！苍生天下系于一心，此份重担能否一肩担起，与其共勉！",
        "chance": 0.05,
        "cooldown": 2 * 60 * 60,
        "reward": {"weiwang": 5000}
    },
    'fu_yao_jiu_tian': {
        "display_name": '扶摇九天',
        "description": "江湖快马飞报！[CQ:at,qq={0}]侠士轻功盖世，触发奇遇【扶摇九天】！正是御风行千里，扶摇红尘巅",
        "chance": 0.01,
        "cooldown": 1 * 60 * 60,
        "reward": {"money": 200, "energy": 100}
    },
    'cha_guan_qi_yuan': {
        "display_name": '茶馆奇缘',
        "description": "江湖快马飞报！[CQ:at,qq={0}]侠士正在茶馆闲坐，不经意间触发奇遇【茶馆奇缘】！正是：叱咤江湖，不见美人顾怀。茶馆闲坐，却遇等闲是非！",
        "chance": 0.05,
        "cooldown": 2 * 60 * 60,
        "require": {'money': 10000},
        "reward": {"money": 1000, "banggong": 5000}
    },
    'qing_feng_bu_wang': {
        "display_name": "清风捕王",
        "description": "江湖快马飞报！[CQ:at,qq={0}]侠士正在行侠江湖，不经意间触发奇遇【清风捕王】！",
        "chance": 0.05,
        "cooldown": 0,
        "reward": {"money": 500, "weiwang": 5000}
    },
    'san_shan_si_hai': {
        "display_name": "三山四海",
        "description": "江湖快马飞报！[CQ:at,qq={0}]侠士福至心灵，不经意间触发奇遇【三山四海】！正是：翻遍三山捣四海，行尽天涯觅真金。",
        "chance": 0.01,
        "cooldown": 2 * 60 * 60,
        "reward": {"money": 1000}
    },
    'yin_yang_liang_jie': {
        "display_name": "阴阳两界",
        "description": "江湖快马飞报！[CQ:at,qq={0}]侠士福缘非浅，触发奇遇【阴阳两界】，此千古奇缘将开启怎样的奇妙际遇，令人神往！",
        "chance": 0.05,
        "cooldown": 24 * 60 * 60,
        "require": {"pvp_gear_point": 3000, "pve_gear_point": 3000},
        "reward": {"money": 500, "weiwang": 5000}
    }
}

def convert_old_qiyu_to_new_list(old_qiyu):
    return {'unknown': old_qiyu}

class Jx3Qiyu(object):
    _name = ''
    _display_name = ''
    _description = ''
    _chance = 0
    _cooldown = 0
    _reward = {}
    _require = {}

    def __init__(self, name, data):
        self._name = name
        self._display_name = data['display_name']
        self._description = data['description']
        self._chance = data['chance']
        self._cooldown = data['cooldown']
        self._reward = data['reward']
        self._require = data.get('require', {})
    
