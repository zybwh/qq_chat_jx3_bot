# -*- coding:gbk -*-

import sys
reload(sys)
sys.setdefaultencoding('gbk')

import os
import logging
import time
import math

logging.basicConfig(
    level       = logging.INFO,
    format      = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt     = '%Y-%m-%d %H:%M:%S',
    filename    = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'CQHandler.log'),
    filemode    = 'w+'
)

import json
import copy
import random

from threading import Lock

DATABASE_PATH = os.path.join('data', 'app', 'com.github.zybwh.qq_chat_jx3_bot')
OLD_DATABASE_PATH = os.path.join('data', 'app', 'com.github.qq_chat_jx3_bot')

DATA_JSON_FILE = os.path.join(DATABASE_PATH, 'jx3.json')
DATA_JSON_FILE_OLD = os.path.join(DATABASE_PATH, 'jx3.json.old')
DATA_JSON_FILE_OLD_2 = os.path.join(DATABASE_PATH, 'jx3.json.old2')

LOVE_ITEM_REQUIRED = "zhen_cheng_zhi_xin"

MAX_GROUP_MEMBER = 4

DALIY_REFRESH_OFFSET = 7 * 60 * 60
DALIY_COUNT_SAVE_DAY = 3
DALIY_REWARD_MIN = 1000
DALIY_REWARD_MAX = 3000
DALIY_ENERGY_REWARD = 500
DALIY_MONEY_REWARD = 100

DALIY_MAX_SPEECH_ENERGY_GAIN = 500
SPEECH_ENERGY_GAIN = 5

YA_BIAO_ENERGY_REQUIRED = 50
MAX_DALIY_YA_BIAO_COUNT = 3
DALIY_YA_BIAO_REWARD_MIN = 1000
DALIY_YA_BIAO_REWARD_MAX = 3000
DALIY_YA_BIAO_MONEY_REWARD = 50
YA_BIAO_FACTION_POINT_GAIN = 1000

WA_BAO_ENERGY_REQUIRED = 50
MAX_DALIY_WA_BAO_COUNT = 10
WA_BAO_COOLDOWN = 10 * 60
WA_BAO_RARE_FACTOR = 2

MAX_DALIY_CHA_GUAN_COUNT = 5
CHA_GUAN_ENERGY_COST = 30

FACTION_REJOIN_CD_SECS = 24 * 60 * 60
FACTION_TRANSFER_WEIWANG_COST = 5000
FACTION_QUIT_EMPTY_WEIWANG = True
NO_FACTION_ALLOW_YA_BIAO = False

ROB_ENERGY_COST = 30
ROB_PROTECT_COUNT = 2
ROB_PROTECT_DURATION = 30 * 60
ROB_LOSE_COOLDOWN = 10 * 60
ROB_SAME_FACTION_PROTECTION = True
ROB_GAIN_FACTOR_MIN = 0.05
ROB_GAIN_FACTOR_MAX = 0.1
ROB_LOST_MONEY = True
ROB_LOST_WEIWANG = True
ROB_PROTECT_NO_LOST_COUNT = 3
ROB_DALIY_MAX_WEIWANG_GAIN = 5000
ROB_DALIY_MAX_MONEY_GAIN = 300
ROB_WIN_WANTED_CHANCE = 0.1
ROB_LOSE_WANTED_CHANCE = 0.05
ROB_WANTED_REWARD = 200
ROB_FACTION_POINT_GAIN = 100

PRACTISE_ENERGY_COST = 50
DALIY_PRACITSE_WEIWANG_GAIN = 5000
PRACTISE_LOSER_GAIN_PERCENTAGE = 0.5
PRACTISE_WEIWANG_GAIN_MIN = 800
PRACTISE_WEIWANG_GAIN_MAX = 1200
PRACTISE_FACTION_POINT_GAIN = 50

WANTED_MONEY_REWARD = 1000
WANTED_DURATION = 24 * 60 * 60
WANTED_COOLDOWN = 10 * 60
WANTED_ENERGY_COST = 50

JAIL_DURATION = 1 * 60 * 60
JAIL_TIMES_PROTECTION = 2

JJC_ENERGY_COST = 20
JJC_REWARD_WEIWANG_MIN = 100
JJC_REWARD_WEIWANG_MAX = 150
JJC_REWARD_RANK = 10
JJC_COOLDOWN = 10 * 60
JJC_GEAR_MODIFIER = 0.5
JJC_RANK_DIFF_PROTECTION = 2
JJC_REWARD_RANK_MODIFIER = 0.1
DALIY_JJC_DOUBLE_REWARD_COUNT = 5
JJC_DAYS_PER_SEASON = 7
MAX_JJC_RANK = 14
JJC_SEASON_PER_RANK_WEIWANG_REWARD = 1000
JJC_SEASON_PER_RANK_MONEY_REWARD = 100

DUNGEON_MAX_ATTACK_COUNT = 5
DUNGEON_ATTACK_COOLDOWN = 10 * 60
DUNGEON_ENERGY_REQUIRED = 100


FACTION_DISPLAY_NAME = ['中立', '恶人谷', '浩气盟']
FACTION_NAME_ID = ['zhongli', 'eren', 'haoqi']

ITEM_LIST = [
    {"name": "zhen_cheng_zhi_xin", "display_name": "真橙之心", "rank": 2, "cost": {"money": 999}},
    {"name": "hai_shi_shan_meng", "display_name": "海誓山盟", "rank": 1, "cost": {"money": 9999}},
    {"name": "jin_zhuan", "display_name": "金砖", "rank": 5, "effect": {"money": 50}},
    {"name": "jin_ye_zi", "display_name": "金叶子", "rank": 6, "effect": {"money": 10}},
    {"name": "zhuan_shen_can", "display_name": "转神餐", "rank": 5, "effect": {"energy": 5}, "cost": {"money": 100}},
    {"name": "jia_zhuan_shen_can", "display_name": "佳·转神餐", "rank": 3, "effect": {"energy": 30}, "cost": {"money": 500}},
    {"name": "rong_ding", "display_name": "熔锭", "rank": 3, "effect": {'pve_weapon': 5}, "cost": {"banggong": 5000}},
    {"name": "mo_shi", "display_name": "磨石", "rank": 3, "effect": {'pvp_weapon': 5}, "cost": {"weiwang": 5000}},
    {"name": "ran", "display_name": "绣", "rank": 4, "effect": {'pve_armor': 10}, "cost": {"banggong": 2000}},
    {"name": "yin", "display_name": "印", "rank": 4, "effect": {'pvp_armor': 10}, "cost": {"weiwang": 2000}},
    {"name": "sui_rou", "display_name": "碎肉", "rank": 4, "cost": {"money": 10}},
    {"name": "cu_bu", "display_name": "粗布", "rank": 4, "cost": {"money": 10}},
    {"name": "gan_cao", "display_name": "甘草", "rank": 4, "cost": {"money": 10}},
    {"name": "hong_tong", "display_name": "红铜", "rank": 4, "cost": {"money": 10}},
    {"name": "hun_hun_zheng_ming", "display_name": "混混抓捕证明", "rank": 0},
    {"name": "tuan_yuan_yan", "display_name": "团圆宴", "rank": 2, "effect": {'attack_count': 5}, "cost": {"money": 500}}
]

CHA_GUAN_QUEST_INFO = {
    "cha_guan_sui_rou": {"display_name": "茶馆：碎肉",
                            "description": "需要提交一份碎肉，可在商店购买。",
                            "require": {"sui_rou": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_cu_bu": {"display_name": "茶馆：粗布",
                            "description": "需要提交一份粗布，可在商店购买。",
                            "require": {"cu_bu": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_gan_cao": {"display_name": "茶馆：甘草",
                            "description": "需要提交一份甘草，可在商店购买。",
                            "require": {"gan_cao": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_hong_tong": {"display_name": "茶馆：红铜",
                            "description": "需要提交一份红铜，可在商店购买。",
                            "require": {"hong_tong": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_hun_hun": {"display_name": "茶馆：抓捕混混",
                            "description": "抓捕混混三个。使用指令 抓捕混混",
                            "require": {"hun_hun_zheng_ming": 3},
                            "reward": {"money": 50, "banggong": 500}}
}

NPC_LIST = {
    "hun_hun": {
        "display_name": "熊痴",
        "equipment": {'weapon': {"display_name": "混混棍", 'pvp': 0, 'pve': 10},
                        'armor': {"display_name": "混混衣", 'pvp': 0, 'pve': 50}},
        "reward": {"money": 50},
        "reward_chance": 0.5
    },
    'xiong_chi': {
        "display_name": "熊痴",
        "equipment": {'weapon': {"display_name": "熊痴拳套", 'pvp': 0, 'pve': 100},
                        'armor': {"display_name": "熊痴衣", 'pvp': 0, 'pve': 500}},
        "reward": {
            "money": 50,
            "banggong": 2000,
        },
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.2,
            "ran": 0.2
        }
    },
    'deng_wen_feng': {
        "display_name": "邓文峰",
        "equipment": {'weapon': {"display_name": "“邓文峰枪", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "邓文峰衣", 'pvp': 0, 'pve': 1500}},
        "reward": {
            "money": 100,
            "banggong": 5000,
        },
        "buff": [
            {
                "display_name": "邓家阵法",
                "description": "自身武器攻击+50%",
                "weapon": 1.5,
                "chance": 0.1,
            },
            {
                "display_name": "邓家将",
                "description": "自身武器攻击+20%",
                "weapon": 1.2,
                "chance": 0.3
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.6,
            "ran": 1
        }
    },
    'shang_zhong_yong': {
        "display_name": "商仲永",
        "equipment": {'weapon': {"display_name": "“商仲永扇", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "商仲永衣", 'pvp': 0, 'pve': 3000}},
        "reward": {
            "money": 200,
            "banggong": 10000,
        },
        "buff": [
            {
                "display_name": "木人阵攻击",
                "description": "自身武器攻击+50%",
                "weapon": 1.5,
                "chance": 0.1,
            }
        ],
        "debuff": [
            {
                "display_name": "八卦阵防御",
                "description": "敌方武器攻击-50%",
                "weapon": 0.5,
                "chance": 0.2,
            },
            {
                "display_name": "天雷阵防御",
                "description": "敌方武器攻击-20%",
                "weapon": 0.8,
                "chance": 0.4
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 1,
            "ran": 1,
            "jia_zhuan_shen_can": 1,
            "zhen_cheng_zhi_xin": 0.1
        }
    },
    'fang_ji_chang': {
        "display_name": "方季常",
        "equipment": {'weapon': {"display_name": "方季常剑", 'pvp': 0, 'pve': 100},
                        'armor': {"display_name": "方季常衣", 'pvp': 0, 'pve': 1000}},
        "reward": {
            "money": 50,
            "banggong": 2000,
        },
        "buff": [
            {
                "display_name": "毒气蔓延",
                "description": "每次受到攻击时自身武器攻击+10%，现在已叠{0}层，最高{1}层",
                "weapon": 0.1,
                "chance": 1,
                'increase_type': 'win',
                'count': 0,
                'max_count':10
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.2,
            "ran": 0.2
        }
    },
    'ping_san_zhi': {
        "display_name": "平三指",
        "equipment": {'weapon': {"display_name": "平三指剑", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "平三指衣", 'pvp': 0, 'pve': 3000}},
        "reward": {
            "money": 100,
            "banggong": 5000,
        },
        "debuff": [
            {
                "display_name": "毒液喷射",
                "description": "对方攻击-100%",
                "weapon": 0,
                "chance": 0.25,
            },
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.6,
            "ran": 1
        }
    },
    'si_tu_yi_yi': {
        "display_name": "司徒一一",
        "equipment": {'weapon': {"display_name": "司徒一一剑", 'pvp': 0, 'pve': 300},
                        'armor': {"display_name": "司徒一一衣", 'pvp': 0, 'pve': 5000}},
        "reward": {
            "money": 200,
            "banggong": 10000,
        },
        "buff": [
            {
                "display_name": "巨龙横扫",
                "description": "自身武器攻击+50%",
                "weapon": 1.5,
                "chance": 0.2,
            }
        ],
        "debuff": [
            {
                "display_name": "巨龙吐息",
                "description": "敌方需要消耗额外1次攻击次数",
                "weapon": 1,
                "chance": 1,
                'attack_count': 1,
                'hp': 0.3
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 1,
            "ran": 2,
            "jia_zhuan_shen_can": 1,
            "zhen_cheng_zhi_xin": 0.2
        }
    },
    'feng_du': {
        "display_name": "冯度",
        "equipment": {'weapon': {"display_name": "冯度剑", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "冯度衣", 'pvp': 0, 'pve': 2000}},
        "reward": {
            "money": 50,
            "banggong": 2000,
        },
        "buff": [
            {
                "display_name": "跪地求饶",
                "description": "自身回血50，奖励金钱+10",
                "hp_recover": 50,
                "money": 10,
                "chance": 0.2,
                "hp": 0.25
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.2,
            "ran": 0.2
        }
    },
    'wang_yan_zhi': {
        "display_name": "王彦直",
        "equipment": {'weapon': {"display_name": "王彦直剑", 'pvp': 0, 'pve': 300},
                        'armor': {"display_name": "王彦直衣", 'pvp': 0, 'pve': 5000}},
        "reward": {
            "money": 100,
            "banggong": 5000,
        },
        "buff": [
            {
                "display_name": "碎星辰",
                "description": "每次受到攻击时自身武器攻击+20%，现在已叠{0}层，最高{1}层",
                "weapon": 0.2,
                "chance": 1,
                'increase_type': 'win',
                'count': 0,
                'max_count':10
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.6,
            "ran": 1,
            "tuan_yuan_yan": 0.4
        }
    },
    'gui_ying_xiao_ci_lang': {
        "display_name": "鬼影小次郎",
        "equipment": {'weapon': {"display_name": "鬼影小次郎剑", 'pvp': 0, 'pve': 400},
                        'armor': {"display_name": "鬼影小次郎衣", 'pvp': 0, 'pve': 8000}},
        "reward": {
            "money": 200,
            "banggong": 10000,
        },
        "buff": [
            {
                "display_name": "一闪",
                "description": "自身武器攻击+20%",
                "weapon": 1.2,
                "chance": 0.4,
            }
        ],
        "debuff": [
            {
                "display_name": "真·天珠·一闪",
                "description": "敌方需要消耗额外1次攻击次数",
                "chance": 0.5,
                'attack_count': 1,
                'hp': 0.5
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 1,
            "ran": 2,
            "jia_zhuan_shen_can": 1,
            "zhen_cheng_zhi_xin": 0.2
        }
    }
}

QIYU_LIST = {
    'hong_fu_qi_tian': {"description": "江湖快马飞报！[CQ:at,qq={0}]侠士鸿运当头！签到时获得额外奖励。",
                        "chance": 0.1,
                        "cooldown": 0,
                        "reward": {"money": DALIY_MONEY_REWARD, "weiwang": DALIY_REWARD_MIN, "banggong": DALIY_REWARD_MIN}},
    'luan_shi_wu_ji': {"description": "江湖快马飞报！[CQ:at,qq={0}]侠士表演惊艳绝伦，不经意间触发奇遇【乱世舞姬】！倾城独立世所稀，乱世舞起影凌乱！",
                        "chance": 0.01,
                        "cooldown": 1 * 60 * 60,
                        "reward": {"money": 200, "energy": 100}},
    'hu_xiao_shan_lin': {"description": "江湖快马飞报！[CQ:at,qq={0}]侠士正在浴血奋战，不经意间触发奇遇【虎啸山林】！正所谓十年磨一剑，不漏其锋芒。只待剑鞘出，斩尽敌首颅。",
                        "chance": 0.05,
                        "cooldown": 2 * 60 * 60,
                        "reward": {"weiwang": 5000}},
    'hu_you_cang_sheng': {"description": "江湖快马飞报！[CQ:at,qq={0}]侠士尽心保护他人，不经意间触发奇遇【护佑苍生】！苍生天下系于一心，此份重担能否一肩担起，与其共勉！",
                        "chance": 0.05,
                        "cooldown": 2 * 60 * 60,
                        "reward": {"weiwang": 5000}},
    'fu_yao_jiu_tian': {"description": "江湖快马飞报！[CQ:at,qq={0}]侠士轻功盖世，触发奇遇【扶摇九天】！正是御风行千里，扶摇红尘巅",
                        "chance": 0.01,
                        "cooldown": 1 * 60 * 60,
                        "reward": {"money": 200, "energy": 100}},
    'cha_guan_qi_yuan': {"description": "江湖快马飞报！[CQ:at,qq={0}]侠士正在茶馆闲坐，不经意间触发奇遇【茶馆奇缘】！正是：叱咤江湖，不见美人顾怀。茶馆闲坐，却遇等闲是非！",
                        "chance": 0.05,
                        "cooldown": 2 * 60 * 60,
                        "require": {'money': 10000},
                        "reward": {"money": 1000, "banggong": 5000}},
    'qing_feng_bu_wang': {"description": "江湖快马飞报！[CQ:at,qq={0}]侠士正在行侠江湖，不经意间触发奇遇【清风捕王】！",
                        "chance": 0.05,
                        "cooldown": 0,
                        "reward": {"money": 500, "weiwang": 5000}},
    'san_shan_si_hai': {"description": "江湖快马飞报！[CQ:at,qq={0}]侠士福至心灵，不经意间触发奇遇【三山四海】！正是：翻遍三山捣四海，行尽天涯觅真金。",
                        "chance": 0.01,
                        "cooldown": 2 * 60 * 60,
                        "reward": {"money": 1000}},
    'yin_yang_liang_jie': {"description": "江湖快马飞报！[CQ:at,qq={0}]侠士福缘非浅，触发奇遇【阴阳两界】，此千古奇缘将开启怎样的奇妙际遇，令人神往！",
                        "chance": 0.05,
                        "cooldown": 24 * 60 * 60,
                        "require": {"pvp_gear_point": 3000, "pve_gear_point": 3000},
                        "reward": {"money": 500, "weiwang": 5000}},
}

DUNGEON_LIST = {
    'san_cai_zhen': {
        "display_name": "三才阵",
        "max_pve_reward_gain": 12000,
        "boss": ['xiong_chi', 'deng_wen_feng', 'shang_zhong_yong'],
        "reward": {
            "banggong": 1000
        }
    },
    'tian_gong_fang': {
        "display_name": "天工坊",
        "max_pve_reward_gain": 25000,
        "boss": ['fang_ji_chang', 'ping_san_zhi', 'si_tu_yi_yi'],
        "reward": {
            "banggong": 2000
        }
    },
    'kong_wu_feng': {
        "display_name": "空雾峰",
        "max_pve_reward_gain": 40000,
        "boss": ['feng_du', 'wang_yan_zhi', 'gui_ying_xiao_ci_lang'],
        "reward": {
            "banggong": 3000
        }
    }
}

STAT_DISPLAY_NAME = {
    "weiwang": "威望",
    "banggong": "帮贡",
    "money": "金钱",
    "energy": "体力"
}

CLASS_LIST = [
    '无门派',
    '天策',
    '纯阳',
    '少林',
    '七秀',
    '万花',
    '藏剑',
    '五毒',
    '唐门',
    '明教',
    '丐帮',
    '苍云',
    '长歌',
    '霸刀',
    '蓬莱'
]

QIYU_CHANCE = 0.1

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
                'jjc': {'score': 0, 'last_time': None, 'win': 0, 'lose': 0},
                'dungeon': {},
                'item_usage': {}
            }

def get_dungeon_id_by_display_name(display_name):
    for k, v in DUNGEON_LIST.items():
        if v['display_name'] == display_name:
            return k
    return ""

def calculateRemainingTime(duration, last_time):
    remain_secs = int(math.floor(duration - (time.time() - last_time)))
    hours = remain_secs // 3600
    mins = (remain_secs - hours * 3600) // 60
    secs = remain_secs - hours * 3600 - mins * 60
    return {'hours': hours, 'mins': mins, 'secs': secs}

def calculateGearPoint(equipment):
    weapon = equipment['weapon']
    armor = equipment['armor']
    return {'pve': weapon['pve'] * 50 + armor['pve'] * 10, 'pvp': weapon['pvp'] * 50 + armor['pvp'] * 10}

def get_wa_bao_reward():
    max_index = 0
    wa_bao_items = {}
    for item in random.sample(ITEM_LIST, len(ITEM_LIST)):
        if item['rank'] != 0 and get_key_or_return_default(item, 'wa_bao', True):
            new_max_index = max_index + pow(item['rank'], WA_BAO_RARE_FACTOR)
            wa_bao_items[item['name']] = {'min': max_index, 'max': new_max_index}
            max_index = new_max_index

    rand_index = random.uniform(0, max_index)
    logging.info("wa_bao items: {1} rand index: {0}".format(rand_index, wa_bao_items))
    for item_name, min_max in wa_bao_items.items():
        if rand_index >= min_max['min'] and rand_index < min_max['max']:
            return item_name

    return ""

def isItemExists(item_name):
    return len([v for v in ITEM_LIST if v['name'] == item_name]) > 0

def print_cost(item_cost):
    returnMsg = ""
    for k, v in item_cost.items():
        if k in STAT_DISPLAY_NAME:
            returnMsg += "\n{0}：{1}".format(STAT_DISPLAY_NAME[k], v)
    return returnMsg

def find_item(item_display_name):
    for v in ITEM_LIST:
        if v['display_name'] == item_display_name:
            return v
    return None

def get_item_display_name(item_name):
    for v in ITEM_LIST:
        if v['name'] == item_name:
            return v['display_name']
    return ""

def isItemBuyable(item):
    return 'cost' in item

def isItemUsable(item):
    return 'effect' in item

def getGroupNickName(fromGroup, fromQQ):
    import CQSDK
    from CQGroupMemberInfo import CQGroupMemberInfo
    info = CQGroupMemberInfo(CQSDK.GetGroupMemberInfoV2(int(fromGroup), int(fromQQ)))
    return info.Card if info.Card != None and info.Card != "" else info.Nickname if info.Nickname != None else str(fromQQ)

def use_zhen_cheng_zhi_xin(fromGroup, fromQQ, toQQ):
    import CQSDK
    try:
        CQSDK.SendGroupMsg(fromGroup, "    [CQ:face,id=145][CQ:face,id=145]    [CQ:face,id=145][CQ:face,id=145]    \n[CQ:face,id=145]         [CQ:face,id=145]         [CQ:face,id=145]\n    [CQ:face,id=145]                [CQ:face,id=145]\n          [CQ:face,id=145]    [CQ:face,id=145]\n               [CQ:face,id=145]")
        CQSDK.SendGroupMsg(fromGroup, "“江湖飞马来报！[CQ:at,qq={0}] 侠士对 [CQ:at,qq={1}] 侠士使用了传说中的【真橙之心】！以此向天下宣告其爱慕之心，奉日月以为盟，昭天地以为鉴，啸山河以为证，敬鬼神以为凭。从此山高不阻其志，涧深不断其行，流年不毁其意，风霜不掩其情。纵然前路荆棘遍野，亦将坦然无惧仗剑随行。今生今世，不离不弃，永生永世，相许相从！”".format(fromQQ, toQQ))
    except Exception as e:
            logging.exception(e)

def isTimeSame(time_struct_1, time_struct_2):
    return time_struct_1.tm_year == time_struct_2.tm_year and time_struct_1.tm_yday == time_struct_2.tm_yday

def get_key_or_return_default(dictionary, key, default_value):
    if key in dictionary:
        return dictionary[key]
    else:
        return default_value

def get_faction_display_name(faction_id):
    return FACTION_DISPLAY_NAME[faction_id] if faction_id >= 0 and faction_id < len(FACTION_DISPLAY_NAME) else ""

class Jx3Handler(object):

    commandList = [
        "查看", "查看装备", "背包",
        "签到",
        "押镖",
        "绑定情缘",
        "加入阵营",
        "退出阵营",
        "转换阵营",
        "打劫",
        "购买",
        "使用",
        "商店",
        "挖宝",
        "查看阵营",
        "查看悬赏",
        "悬赏", "抓捕",
        "pve装分排行", "pvp装分排行", "聊天排行", "奇遇排行", "土豪排行", "威望排行", "武器更名", "防具更名",
        "茶馆",
        "交任务", "抓捕混混"]

    jx3_users = {}
    lover_pending = {}
    daliy_action_count = {}
    rob_protect = {}
    equipment = {}
    wanted_list = {}
    jail_list = {}
    qiyu_status = {}
    group_info = {}
    dungeon_status = {}
    jjc_status = {}
    jjc_season_status = {}

    is_locked = False

    def __init__(self, qq_group):
        logging.info('Jx3Handler __init__')
        self.qq_group = qq_group # int

        if os.path.exists(OLD_DATABASE_PATH) and not os.path.exists(DATABASE_PATH):
            logging.info("found old database path! moving to new path...")
            os.rename(OLD_DATABASE_PATH, DATABASE_PATH)

        self.json_file_folder = os.path.join(DATABASE_PATH, str(qq_group))
        self.json_file_path = os.path.join(self.json_file_folder, 'data.json')
        self.json_file_path_old = os.path.join(self.json_file_folder, 'data.json.old')
        self.json_file_path_old_2 = os.path.join(self.json_file_folder, 'data.json.old2')

        if not os.path.exists(self.json_file_folder):
            logging.info("path not exist. create a new one: {0}", self.json_file_folder)
            os.makedirs(self.json_file_folder)

        self.load_data()

        self.mutex = Lock()

    def __del__(self):
        logging.info('Jx3Handler __del__')

    def load_data(self):
        if os.path.exists(self.json_file_path):
            load_old_file = False
            try:
                with open(self.json_file_path, 'r') as f:
                    data = json.loads(f.readline(), encoding='gbk')
                    self.read_file(data)
                    logging.info("loading complete")
            except Exception as e:
                load_old_file = True
                logging.exception(e)

            if load_old_file and os.path.exists(self.json_file_path_old):
                try:
                    with open(self.json_file_path_old, 'r') as f:
                        data = json.loads(f.readline(), encoding='gbk')
                        self.read_file(data)
                        logging.info("loading old file complete")
                except Exception as e:
                    logging.exception(e)

    def read_file(self, data):
        self.jx3_users = copy.deepcopy(get_key_or_return_default(data, "jx3_users", {}))
        self.lover_pending = copy.deepcopy(get_key_or_return_default(data, "lover_pending", {}))
        self.daliy_action_count = copy.deepcopy(get_key_or_return_default(data, "daliy_action_count", {}))
        self.rob_protect = copy.deepcopy(get_key_or_return_default(data, "rob_protect", {}))
        self.equipment = copy.deepcopy(get_key_or_return_default(data, "equipment", {}))
        self.wanted_list = copy.deepcopy(get_key_or_return_default(data, "wanted_list", {}))
        self.jail_list = copy.deepcopy(get_key_or_return_default(data, "jail_list", {}))
        self.qiyu_status = copy.deepcopy(get_key_or_return_default(data, "qiyu_status", {}))
        self.group_info = copy.deepcopy(get_key_or_return_default(data, "group_info", {}))
        self.dungeon_status = copy.deepcopy(get_key_or_return_default(data, "dungeon_status", {}))
        self.jjc_status = copy.deepcopy(get_key_or_return_default(data, "jjc_status", {'season': 1, "day": 0, "last_season_jjc_status": {}}))
        self.jjc_season_status = copy.deepcopy(get_key_or_return_default(data, "jjc_season_status", {}))

    def writeToJsonFile(self):
        returnMsg = ""
        try:
            if os.path.exists(self.json_file_path_old):
                if os.path.exists(self.json_file_path_old_2):
                    os.remove(self.json_file_path_old_2)
                os.rename(self.json_file_path_old, self.json_file_path_old_2)

            if os.path.exists(self.json_file_path):
                if os.path.exists(self.json_file_path_old):
                    os.remove(self.json_file_path_old)
                os.rename(self.json_file_path, self.json_file_path_old)

            with open(self.json_file_path, 'w', ) as f:
                data = {
                    "jx3_users": self.jx3_users,
                    "lover_pending": self.lover_pending,
                    "daliy_action_count": self.daliy_action_count,
                    "rob_protect": self.rob_protect,
                    "equipment": self.equipment,
                    "wanted_list": self.wanted_list,
                    "jail_list": self.jail_list,
                    "qiyu_status": self.qiyu_status,
                    "group_info": self.group_info,
                    "dungeon_status": self.dungeon_status,
                    "jjc_status": self.jjc_status,
                    "jjc_season_status":self.jjc_season_status
                }
                f.write(json.dumps(data, ensure_ascii=False, encoding='gbk'))
        except Exception as e:
            logging.exception(e)

    def _reset_daliy_count(self, qq_account_str=""):
        yday = time.localtime(time.time() - DALIY_REFRESH_OFFSET).tm_yday
        yday_str = str(yday)
        if yday_str not in self.daliy_action_count:
            self.daliy_action_count[yday_str] = {"faction": {"haoqi": {"point": 0, "reward": 0}, "eren": {"point":0, "reward": 0}}}
            self.rob_protect = {}
            self.dungeon_status = {}
            self.group_info = {}

            if self.jjc_status == {}:
                self.jjc_status = {'season': 1, "day": 0, "last_season_jjc_status": {}}

            self.jjc_status['day'] += 1
            if self.jjc_status['day'] > JJC_DAYS_PER_SEASON:
                self.jjc_status['last_season_jjc_status'][str(self.jjc_status['season'])] = copy.deepcopy(self.jjc_season_status)
                self.jjc_status['season'] += 1
                self.jjc_status['day'] = 1
                self.jjc_season_status = {}

            for k in list(self.daliy_action_count.keys()):
                if int(k) < yday - DALIY_COUNT_SAVE_DAY:
                    self.daliy_action_count.pop(k)

        if 'faction' not in self.daliy_action_count[yday_str]:
            self.daliy_action_count[yday_str]['faction'] = {"haoqi": {"point": 0, "reward": 0}, "eren": {"point":0, "reward": 0}}

        self._add_new_daliy_record(yday_str, qq_account_str)

        return yday

    def _add_new_daliy_record(self, yday_str, qq_account_str):
        if qq_account_str != "" and qq_account_str not in self.daliy_action_count[yday_str]:
            self.daliy_action_count[yday_str][qq_account_str] = copy.deepcopy(daliy_dict)

    def getCommandList(self):
        return self.commandList

    def register(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()
        try:
            qq_account_str = str(qq_account)
            if qq_account_str in self.jx3_users.keys():
                returnMsg = "[CQ:at,qq={0}] 注册失败！你已经注册过了。".format(qq_account)
            else:
                self.equipment[qq_account_str] = {
                    'weapon': {"display_name": "大侠剑", 'pvp': 10, 'pve': 10},
                    'armor': {"display_name": "大侠衣", 'pvp': 100, 'pve': 100}
                }

                gear_point = calculateGearPoint(self.equipment[qq_account_str])

                self.jx3_users[qq_account_str] = {
                    "class_id": 0,
                    "faction_id": 0,
                    "faction_join_time": None,
                    "weiwang": 0,
                    "banggong": 0,
                    "money": 0,
                    "pvp_gear_point": gear_point['pvp'],
                    "pve_gear_point": gear_point['pve'],
                    "achievement": 0,
                    "lover": 0,
                    "lover_time": None,
                    "qiyu": 0,
                    "energy": 0,
                    "register_time": time.time(),
                    "qiandao_count": 0,
                    "bag": {}
                }
                returnMsg = "注册成功！\n[CQ:at,qq={0}]\n注册时间：{1}".format(qq_account, time.strftime('%Y-%m-%d', time.localtime(self.jx3_users[qq_account_str]["register_time"])))

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def isUserRegister(self, qq_account):
        try:
            return str(qq_account) in self.jx3_users.keys()
        except Exception as e:
            logging.exception(e)

    # TODO: not thread safe
    def _update_gear_point(self, qq_account_str):
        gear_point = calculateGearPoint(self.equipment[qq_account_str])
        self.jx3_users[qq_account_str]['pve_gear_point'] = gear_point['pve']
        self.jx3_users[qq_account_str]['pvp_gear_point'] = gear_point['pvp']

    def getInfo(self, qq_group, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)
            self._update_gear_point(qq_account_str)

            val = self.jx3_users[qq_account_str]

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if self.daliy_action_count[yday_str][qq_account_str]['qiandao']:
                qiandao_status = "已签到"
            else:
                qiandao_status = "未签到"

            returnMsg = "[CQ:at,qq={0}]\n情缘:\t\t{1}\n门派:\t\t{2}\n阵营:\t\t{3}\n威望:\t\t{4}\n帮贡:\t\t{5}\n金钱:\t\t{6}G\nPVP装分:\t{7}\nPVE装分:\t{8}\n资历:\t\t{9}\n签到状态:\t{10}\n签到次数:\t{11}\n奇遇:\t\t{12}\n注册时间:\t{13}\n今日发言:\t{14}\n体力:\t\t{15}".format(
                    qq_account,
                    "" if val['lover'] == 0 else getGroupNickName(qq_group, val['lover']),
                    CLASS_LIST[val['class_id']],
                    get_faction_display_name(val['faction_id']),
                    val['weiwang'],
                    val['banggong'],
                    int(val['money']),
                    val['pvp_gear_point'],
                    val['pve_gear_point'],
                    val['achievement'],
                    qiandao_status,
                    val['qiandao_count'],
                    val['qiyu'],
                    time.strftime('%Y-%m-%d', time.localtime(val['register_time'])),
                    self.daliy_action_count[yday_str][qq_account_str]['speech_count'],
                    val['energy'])

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def qianDao(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            val = self.jx3_users[qq_account_str]

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if self.daliy_action_count[yday_str][qq_account_str]['qiandao']:
                returnMsg = "[CQ:at,qq={0}]今天已经签到过了!".format(qq_account)
            else:
                banggong_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)
                weiwang_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)
                self.jx3_users[qq_account_str]['weiwang'] += weiwang_reward
                self.jx3_users[qq_account_str]['banggong'] += banggong_reward
                self.jx3_users[qq_account_str]['qiandao_count'] += 1
                self.jx3_users[qq_account_str]['energy'] += DALIY_ENERGY_REWARD
                self.jx3_users[qq_account_str]['money'] += DALIY_MONEY_REWARD

                self.daliy_action_count[yday_str][qq_account_str]['qiandao'] = True
                returnMsg = "[CQ:at,qq={0}] 签到成功！签到奖励: 威望+{1} 帮贡+{2} 金钱+{3} 体力+{4}".format(
                                qq_account,
                                weiwang_reward,
                                banggong_reward,
                                DALIY_MONEY_REWARD,
                                DALIY_ENERGY_REWARD)

                faction_id = val['faction_id']
                if faction_id != 0 and 'faction' in self.daliy_action_count and self.daliy_action_count['faction'][FACTION_NAME_ID[faction_id]]['reward'] != 0:
                    reward = self.daliy_action_count['faction'][FACTION_NAME_ID[faction_id]]['reward']
                    self.jx3_users[qq_account_str]['weiwang'] += reward
                    returnMsg += "\n获得昨日阵营奖励：威望+{0}".format(reward)
                
                if qq_account_str not in self.jjc_season_status and qq_account_str in get_key_or_return_default(self.jjc_status['last_season_jjc_status'], str(self.jjc_status['season'] - 1), {}):
                    jjc_status = self.jjc_status['last_season_jjc_status'][str(self.jjc_status['season'] - 1)][qq_account_str]
                    if 'reward_gain' not in jjc_status:
                        rank = jjc_status['score'] // 100 
                        jjc_weiwang_reward = rank * JJC_SEASON_PER_RANK_WEIWANG_REWARD
                        jjc_money_reward = rank * JJC_SEASON_PER_RANK_MONEY_REWARD

                        rank_list = sorted(self.jjc_status['last_season_jjc_status'][str(self.jjc_status['season'] - 1)].items(), lambda x, y: cmp(x[1]['score'], y[1]['score']), reverse=True)
                        
                        rank_msg = ""
                        i = 0
                        modifier = 1
                        for k, v in rank_list:
                            i += 1
                            if qq_account_str == k:
                                rank_msg = "\n上赛季名剑大会成绩： 分数：{0}，段位：{1}，排名：{2}。".format(v['score'], rank, i)
                                if i == 1:
                                    modifier = 2
                                    rank_msg += "由于上赛季排名为第1，获得2倍奖励。"
                                elif i >= 2 and i <= 3:
                                    modifier = 1.5
                                    rank_msg += "由于上赛季排名为第{0}，获得{1}倍奖励。".format(i, modifier)
                        

                        self.jx3_users[qq_account_str]['weiwang'] += int(jjc_weiwang_reward * modifier)
                        self.jx3_users[qq_account_str]['money'] += int(jjc_money_reward * modifier)
                        self.jjc_status['last_season_jjc_status'][str(self.jjc_status['season'] - 1)][qq_account_str]['reward_gain'] = True
                        returnMsg += "\n获得上赛季名剑大会排行奖励：威望+{0} 金钱+{1}".format(jjc_weiwang_reward, jjc_money_reward)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def addSpeechCount(self, qq_account):
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            self.daliy_action_count[yday_str][qq_account_str]['speech_count'] += 1

            if 'speech_energy_gain' not in self.daliy_action_count[yday_str][qq_account_str]:
                self.daliy_action_count[yday_str][qq_account_str]['speech_energy_gain'] = 0

            if self.daliy_action_count[yday_str][qq_account_str]['speech_energy_gain'] < DALIY_MAX_SPEECH_ENERGY_GAIN:
                self.daliy_action_count[yday_str][qq_account_str]['speech_energy_gain'] += SPEECH_ENERGY_GAIN
                self.jx3_users[qq_account_str]['energy'] += SPEECH_ENERGY_GAIN

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()

    def addLover(self, fromQQ, toQQ):
        returnMsg = ""
        self.mutex.acquire()

        try:
            if str(toQQ) not in self.jx3_users.keys():
                returnMsg = "[CQ:at,qq={0}] 还没有注册哦，请先注册再绑定情缘！".format(toQQ)
            else:
                fromQQ_stat = self.jx3_users[str(fromQQ)]
                toQQ_stat = self.jx3_users[str(toQQ)]

                if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in fromQQ_stat['bag'].keys():
                    returnMsg = "[CQ:at,qq={0}] 绑定情缘需要消耗1个{1}。\n你并没有此物品，请先购买。".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
                else:
                    if str(fromQQ_stat['lover']) == str(toQQ):
                        returnMsg = "[CQ:at,qq={0}] 你们已经绑定过啦！还想乱撒狗粮？".format(fromQQ)
                    elif fromQQ_stat['lover'] != 0:
                        returnMsg = "[CQ:at,qq={0}]  想什么呢？你就不怕[CQ:at,qq={1}]打你吗？".format(fromQQ, fromQQ_stat['lover'])
                    elif toQQ_stat['lover'] != 0:
                        returnMsg = "[CQ:at,qq={0}] 人家已经有情缘啦，你是想上818吗？".format(fromQQ)
                    elif toQQ in self.lover_pending and self.lover_pending[str(toQQ)] != fromQQ:
                        returnMsg = "[CQ:at,qq={0}] 已经有人向[CQ:at,qq={1}]求情缘啦，你是不是再考虑一下？".format(fromQQ, toQQ)
                    else:
                        pendingList = [k for k, v in self.lover_pending.items() if v == fromQQ]
                        for p in pendingList:
                            self.lover_pending.pop(p)
                        self.lover_pending[str(toQQ)] = fromQQ
                        returnMsg = "[CQ:at,qq={1}]\n[CQ:at,qq={0}] 希望与你绑定情缘，请输入 同意 或者 拒绝。".format(fromQQ, toQQ)

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def acceptLover(self, fromGroup, toQQ):
        returnMsg = ""
        self.mutex.acquire()

        try:
            toQQ_str = str(toQQ)
            if toQQ_str in self.lover_pending.keys():
                fromQQ = self.lover_pending.pop(toQQ_str)
                fromQQ_str = str(fromQQ)

                if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in self.jx3_users[fromQQ_str]['bag'].keys():
                    returnMsg = "[CQ:at,qq={1}] 虽然人家同意了但是你并没有1个{1}。".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
                else:
                    self.jx3_users[fromQQ_str]['lover'] = toQQ
                    self.jx3_users[fromQQ_str]['lover_time'] = time.time()
                    self.jx3_users[toQQ_str]['lover'] = fromQQ
                    self.jx3_users[toQQ_str]['lover_time'] = time.time()
                    if LOVE_ITEM_REQUIRED != "":
                        self.jx3_users[fromQQ_str]['bag'][LOVE_ITEM_REQUIRED] -= 1
                        if self.jx3_users[fromQQ_str]['bag'][LOVE_ITEM_REQUIRED] == 0:
                            self.jx3_users[fromQQ_str]['bag'].pop(LOVE_ITEM_REQUIRED)
                        use_zhen_cheng_zhi_xin(fromGroup, fromQQ, toQQ)

                    returnMsg = "[CQ:at,qq={0}] 与 [CQ:at,qq={1}]，喜今日嘉礼初成，良缘遂缔。诗咏关雎，雅歌麟趾。瑞叶五世其昌，祥开二南之化。同心同德，宜室宜家。相敬如宾，永谐鱼水之欢。互助精诚，共盟鸳鸯之誓".format(fromQQ, toQQ)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def rejectLover(self, toQQ):
        returnMsg = ""
        self.mutex.acquire()

        try:
            if str(toQQ) in self.lover_pending.keys():
                fromQQ = self.lover_pending.pop(str(toQQ))
                returnMsg = "落花有意，流水无情，[CQ:at,qq={1}] 婉拒了 [CQ:at,qq={0}]。".format(fromQQ, toQQ)

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def yaBiao(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)
            val = self.jx3_users[qq_account_str]
            if val['faction_id'] == 0 and not NO_FACTION_ALLOW_YA_BIAO:
                returnMsg = "[CQ:at,qq={0}] 中立阵营无法押镖。".format(qq_account)
            elif val['energy'] < YA_BIAO_ENERGY_REQUIRED:
                returnMsg = "[CQ:at,qq={0}] 体力不足！无法押镖。".format(qq_account)
            elif qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] 老实点，你还要在监狱里蹲{1}小时{2}分{3}秒。".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            else:
                if qq_account in self.jail_list:
                    self.jail_list.pop(qq_account)

                yday = self._reset_daliy_count(qq_account_str)
                yday_str = str(yday)

                if self.daliy_action_count[yday_str][qq_account_str]['ya_biao'] < MAX_DALIY_YA_BIAO_COUNT:
                    reward = random.randint(DALIY_YA_BIAO_REWARD_MIN, DALIY_YA_BIAO_REWARD_MAX)
                    self.jx3_users[qq_account_str]['weiwang'] += reward
                    self.jx3_users[qq_account_str]['energy'] -= YA_BIAO_ENERGY_REQUIRED
                    self.jx3_users[qq_account_str]['money'] += DALIY_YA_BIAO_MONEY_REWARD
                    self.daliy_action_count[yday_str][qq_account_str]["ya_biao"] += 1

                    if not NO_FACTION_ALLOW_YA_BIAO:
                        self.daliy_action_count[yday_str]['faction'][FACTION_NAME_ID[val['faction_id']]]['point'] += YA_BIAO_FACTION_POINT_GAIN

                    returnMsg = "[CQ:at,qq={0}] 押镖成功！体力-{1} 威望+{2} 金钱+{3}".format(qq_account, YA_BIAO_ENERGY_REQUIRED, reward, DALIY_YA_BIAO_MONEY_REWARD)
                else:
                    returnMsg = "[CQ:at,qq={0}] 一天最多押镖{1}次。你已经押了{1}趟啦，明天再来吧。".format(qq_account, MAX_DALIY_YA_BIAO_COUNT)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def checkBag(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            bag = get_key_or_return_default(self.jx3_users[str(qq_account)], 'bag', {})
            if bag == {}:
                itemMsg = "\n空空如也"
            else:
                itemMsg = ""
                for k, v in bag.items():
                    itemMsg += "\n{0} x {1}".format(get_item_display_name(k), v)
            returnMsg = "[CQ:at,qq={0}] 的背包：".format(qq_account) + itemMsg

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def joinFaction(self, qq_account, faction_str):
        returnMsg = ""
        self.mutex.acquire()

        try:
            if faction_str in FACTION_DISPLAY_NAME:
                qq_account_str = str(qq_account)
                qq_stat = self.jx3_users[qq_account_str]
                qq_faction_str = get_faction_display_name(qq_stat['faction_id'])
                if faction_str == qq_faction_str:
                    returnMsg = "[CQ:at,qq={0}] 你已经加入了 {1}。".format(qq_account, faction_str)
                elif qq_stat['faction_id'] != 0:
                    returnMsg = "[CQ:at,qq={0}] 你已经加入了 {1}，{2} 并不想接受你的申请。".format(qq_account, qq_faction_str, faction_str)
                elif qq_stat['faction_join_time'] != None and time.time() - qq_stat['faction_join_time'] < FACTION_REJOIN_CD_SECS:
                    time_val = calculateRemainingTime(FACTION_REJOIN_CD_SECS, qq_stat['faction_join_time'])
                    returnMsg = "[CQ:at,qq={0}] 由于不久前才退出阵营，你需要等待{1}小时{2}分{3}秒之后才能重新加入。".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                else:
                    self.jx3_users[qq_account_str]['faction_id'] = FACTION_DISPLAY_NAME.index(faction_str)
                    self.jx3_users[qq_account_str]['faction_join_time'] = time.time()
                    returnMsg = "[CQ:at,qq={0}] 成功加入 {1}。".format(qq_account, faction_str)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def quitFaction(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)
            qq_stat = self.jx3_users[qq_account_str]
            if qq_stat['faction_id'] == 0:
                returnMsg = "[CQ:at,qq={0}] 你并没有加入任何阵营。".format(qq_account)
            else:
                pre_faction_id = qq_stat['faction_id']
                self.jx3_users[qq_account_str]['faction_id'] = 0
                self.jx3_users[qq_account_str]['faction_join_time'] = time.time()
                if FACTION_QUIT_EMPTY_WEIWANG:
                    self.jx3_users[qq_account_str]['weiwang'] = 0
                returnMsg = "[CQ:at,qq={0}] 退出了江湖纷争，脱离了 {1}".format(qq_account, get_faction_display_name(pre_faction_id))

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def transferFaction(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)
            qq_stat = self.jx3_users[qq_account_str]
            if qq_stat['faction_id'] == 0:
                returnMsg = "[CQ:at,qq={0}] 你并没有加入任何阵营。".format(qq_account)
            elif qq_stat['weiwang'] < FACTION_TRANSFER_WEIWANG_COST:
                returnMsg = "[CQ:at,qq={0}] 转换阵营需要消耗{1}威望，当前威望不足。".format(qq_account, FACTION_TRANSFER_WEIWANG_COST)
            elif qq_stat['faction_join_time'] != None and time.time() - qq_stat['faction_join_time'] < FACTION_REJOIN_CD_SECS:
                remain_secs = int(math.floor(FACTION_REJOIN_CD_SECS - (time.time() - qq_stat['faction_join_time'])))
                hours = remain_secs // 3600
                mins = (remain_secs - hours * 3600) // 60
                secs = remain_secs - hours * 3600 - mins * 60
                returnMsg = "[CQ:at,qq={0}] 由于不久前才更改阵营，你需要等待{1}小时{2}分{3}秒之后才能更改。".format(qq_account, hours, mins, secs)
            else:
                pre_faction_id = qq_stat['faction_id']
                new_faction_id = 1 if pre_faction_id == 2 else 2
                self.jx3_users[qq_account_str]['faction_id'] = new_faction_id
                self.jx3_users[qq_account_str]['faction_join_time'] = time.time()
                returnMsg = "[CQ:at,qq={0}] 通过地下交易，花费了{1}威望，成功地脱离了 {2}，加入了 {3}。".format(qq_account, FACTION_TRANSFER_WEIWANG_COST, get_faction_display_name(pre_faction_id), get_faction_display_name(new_faction_id))

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def _calculate_battle(self, fromQQ_str, toQQ_str, gear_mode, fromQQ_modifier=1, toQQ_modifier=1, custom_from_qq_equipment={}, custom_to_qq_equipment={}):

        if custom_to_qq_equipment != {}:
            toQQ_equipment = custom_to_qq_equipment
        elif toQQ_str in NPC_LIST:
            toQQ_equipment = NPC_LIST[toQQ_str]['equipment']
        else:
            toQQ_equipment = self.equipment[toQQ_str]

        toQQ_gear_point = calculateGearPoint(toQQ_equipment)[gear_mode] * toQQ_modifier

        if custom_from_qq_equipment != {}:
            fromQQ_equipment = custom_from_qq_equipment
        else:
            fromQQ_equipment = self.equipment[fromQQ_str]
        fromQQ_gear_point = calculateGearPoint(fromQQ_equipment)[gear_mode] * fromQQ_modifier

        random_base = random.uniform(0.4, 0.5)
        success_chance = random_base + 0.2 * ((fromQQ_gear_point - toQQ_gear_point) / float(toQQ_gear_point)) + 0.3 * float(fromQQ_equipment['weapon'][gear_mode]) / float(toQQ_equipment['armor'][gear_mode])

        logging.info("success_chance: {0} + 0.3 * {1} + 0.2 * {2}".format(
                        random_base,
                        (fromQQ_gear_point - toQQ_gear_point) / float(toQQ_gear_point),
                        float(fromQQ_equipment['weapon'][gear_mode] * fromQQ_modifier)  / float(toQQ_equipment['armor'][gear_mode] * toQQ_modifier)))

        chance = random.uniform(0, 1)
        logging.info("chance: {0}, success_chance: {1}".format(chance, success_chance))
        if chance <= success_chance:
            winner = fromQQ_str
            loser = toQQ_str
        else:
            winner = toQQ_str
            loser = fromQQ_str

        return {'winner': winner, 'loser': loser, 'success_chance': success_chance}

    def rob(self, fromGroup, fromQQ, toQQ):
        returnMsg = ""
        self.mutex.acquire()

        try:
            if not self.isUserRegister(toQQ):
                returnMsg = "[CQ:at,qq={0}] 对方尚未注册，无法打劫。".format(fromQQ)
            else:
                fromQQ_str = str(fromQQ)
                fromQQ_stat = self.jx3_users[fromQQ_str]
                toQQ_str = str(toQQ)
                toQQ_stat = self.jx3_users[toQQ_str]

                yday = self._reset_daliy_count(fromQQ_str)
                yday_str = str(yday)
                self._add_new_daliy_record(yday_str, toQQ_str)

                if 'rob' not in self.daliy_action_count[yday_str][fromQQ_str]:
                    self.daliy_action_count[yday_str][fromQQ_str]['rob'] = {'weiwang': 0, 'money': 0, 'last_rob_time': None}

                if fromQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] 中立阵营无法打劫，请先加入阵营。".format(fromQQ)
                elif toQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] 对方是中立阵营，无法打劫。".format(fromQQ)
                elif fromQQ_stat['faction_id'] == toQQ_stat['faction_id'] and ROB_SAME_FACTION_PROTECTION:
                    returnMsg = "[CQ:at,qq={0}] 同阵营无法打劫！".format(fromQQ)
                elif toQQ_str in self.rob_protect and ROB_PROTECT_COUNT != 0 and self.rob_protect[toQQ_str]['count'] >= ROB_PROTECT_COUNT and (time.time() - self.rob_protect[toQQ_str]['rob_time']) <= ROB_PROTECT_DURATION:
                    time_val = calculateRemainingTime(ROB_PROTECT_DURATION, self.rob_protect[toQQ_str]['rob_time'])
                    returnMsg = "[CQ:at,qq={0}] 对方最近被打劫太多次啦，已经受到了神之护佑。\n剩余时间：{1}小时{2}分{3}秒".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                elif fromQQ_str in self.jail_list and time.time() - self.jail_list[fromQQ_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[fromQQ_str])
                    returnMsg = "[CQ:at,qq={0}] 老实点，你还要在监狱里蹲{1}小时{2}分{3}秒。".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                elif toQQ_str in self.jail_list and time.time() - self.jail_list[toQQ_str] < JAIL_DURATION:
                    returnMsg = "[CQ:at,qq={0}] 对方在监狱里蹲着呢，你这是要劫狱吗？".format(fromQQ)
                elif fromQQ_stat['energy'] < ROB_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] 体力不足！无法打劫。".format(fromQQ)
                elif self.daliy_action_count[yday_str][fromQQ_str]['rob']['last_rob_time'] != None and time.time() - self.daliy_action_count[yday_str][fromQQ_str]['rob']['last_rob_time'] < ROB_LOSE_COOLDOWN:
                    time_val = calculateRemainingTime(ROB_LOSE_COOLDOWN, self.daliy_action_count[yday_str][fromQQ_str]['rob']['last_rob_time'])
                    returnMsg = "[CQ:at,qq={0}] 你还需要恢复{1}小时{2}分{3}秒，无法打劫。".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                else:
                    if fromQQ_str in self.jail_list:
                        self.jail_list.pop(fromQQ_str)

                    battle_result = self._calculate_battle(fromQQ_str, toQQ_str, 'pvp')

                    winner = battle_result['winner']
                    loser = battle_result['loser']
                    success_chance = battle_result['success_chance']

                    weiwang_amount = int(self.jx3_users[loser]['weiwang'] * random.uniform(ROB_GAIN_FACTOR_MIN, ROB_GAIN_FACTOR_MAX))
                    money_amount = int(self.jx3_users[loser]['money'] * random.uniform(ROB_GAIN_FACTOR_MIN, ROB_GAIN_FACTOR_MAX))

                    if toQQ_str == loser:

                        if self.daliy_action_count[yday_str][fromQQ_str]['rob']['weiwang'] < ROB_DALIY_MAX_WEIWANG_GAIN:
                            weiwang_gain = min(weiwang_amount, ROB_DALIY_MAX_WEIWANG_GAIN - self.daliy_action_count[yday_str][fromQQ_str]['rob']['weiwang'])
                        else:
                            weiwang_gain = 0

                        if loser not in self.rob_protect:
                            self.rob_protect[loser] = {"count": 0, "rob_time": None}

                        if self.daliy_action_count[yday_str][fromQQ_str]['rob']['money'] < ROB_DALIY_MAX_MONEY_GAIN and self.rob_protect[loser]['count'] <= ROB_PROTECT_NO_LOST_COUNT:
                            money_gain = min(money_amount, ROB_DALIY_MAX_MONEY_GAIN - self.daliy_action_count[yday_str][fromQQ_str]['rob']['money'])
                        else:
                            money_gain = 0

                        if weiwang_gain != 0 or money_gain != 0:
                            self.jx3_users[fromQQ_str]['energy'] -= ROB_ENERGY_COST
                            energy_cost = ROB_ENERGY_COST
                        else:
                            energy_cost = 0

                        self.jx3_users[winner]['weiwang'] += weiwang_gain
                        self.daliy_action_count[yday_str][fromQQ_str]['rob']['weiwang'] += weiwang_gain

                        self.jx3_users[winner]['money'] += money_gain
                        self.daliy_action_count[yday_str][fromQQ_str]['rob']['money'] += money_gain

                        if loser not in self.rob_protect:
                            self.rob_protect[loser] = {'count': 0, 'rob_time': None}

                        if money_gain != 0:
                            self.rob_protect[loser]['count'] += 1
                            self.rob_protect[loser]['rob_time'] = time.time()

                        if ROB_LOST_WEIWANG and self.rob_protect[loser]['count'] <= ROB_PROTECT_NO_LOST_COUNT:
                            weiwang_lost = weiwang_gain
                        else:
                            weiwang_lost = 0

                        if ROB_LOST_MONEY and self.rob_protect[loser]['count'] <= ROB_PROTECT_NO_LOST_COUNT:
                            money_lost = money_gain
                        else:
                            money_lost = 0

                        self.jx3_users[loser]['weiwang'] -= weiwang_lost
                        self.jx3_users[loser]['money'] -= money_lost

                        returnMsg = "打劫成功！成功率：{0}%\n[CQ:at,qq={1}] 在野外打劫了 [CQ:at,qq={2}]\n{3} 威望+{4} 金钱+{5} 体力-{6}\n{7} 威望-{8} 金钱-{9}".format(
                                        int(math.floor(success_chance * 100)),
                                        fromQQ,
                                        toQQ,
                                        getGroupNickName(fromGroup, int(winner)),
                                        weiwang_gain,
                                        money_gain,
                                        energy_cost,
                                        getGroupNickName(fromGroup, int(loser)),
                                        weiwang_lost,
                                        money_lost)
                        wanted_chance = ROB_WIN_WANTED_CHANCE if energy_cost != 0 else 0

                        if energy_cost != 0:
                            self.daliy_action_count[yday_str]['faction'][FACTION_NAME_ID[fromQQ_stat['faction_id']]]['point'] += ROB_FACTION_POINT_GAIN

                    else:
                        self.daliy_action_count[yday_str][fromQQ_str]['rob']['last_rob_time'] = time.time()
                        time_val = calculateRemainingTime(ROB_LOSE_COOLDOWN, time.time())

                        if self.daliy_action_count[yday_str][fromQQ_str]['rob']['weiwang'] < ROB_DALIY_MAX_WEIWANG_GAIN or self.daliy_action_count[yday_str][fromQQ_str]['rob']['money'] < ROB_DALIY_MAX_MONEY_GAIN:
                            self.jx3_users[fromQQ_str]['energy'] -= ROB_ENERGY_COST
                            energy_cost = ROB_ENERGY_COST
                        else:
                            energy_cost = 0

                        returnMsg = "打劫失败！成功率：{0}%\n[CQ:at,qq={1}] 在野外打劫 [CQ:at,qq={2}] 时被反杀，需要休息{3}小时{4}分{5}秒。体力-{6}".format(
                                        int(math.floor(success_chance * 100)),
                                        fromQQ,
                                        toQQ,
                                        time_val['hours'],
                                        time_val['mins'],
                                        time_val['secs'],
                                        energy_cost)
                        wanted_chance = ROB_LOSE_WANTED_CHANCE if energy_cost != 0 else 0

                    rand = random.uniform(0, 1)
                    logging.info("wanted chance: {0} rand: {1}".format(wanted_chance, rand))
                    if rand <= wanted_chance:
                        import CQSDK
                        CQSDK.SendGroupMsg(self.qq_group, returnMsg)

                        returnMsg = self._put_wanted_internal(fromQQ_str, ROB_WANTED_REWARD)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg



    def buyItem(self, qq_account, item_display_name, item_amount):
        returnMsg = ""
        self.mutex.acquire()
        try:
            item = find_item(item_display_name)
            if item != None:
                if not isItemBuyable(item):
                    returnMsg = "[CQ:at,qq={0}] {1} 不可购买。".format(qq_account, item_display_name)
                else:

                    qq_account_str = str(qq_account)
                    qq_stat = self.jx3_users[qq_account_str]

                    cost_list = item['cost']
                    can_afford = True
                    for k, v in cost_list.items():
                        can_afford = can_afford and (k in qq_stat and qq_stat[k] >= v * item_amount)

                    if can_afford:
                        if item['name'] not in self.jx3_users[qq_account_str]['bag']:
                            self.jx3_users[qq_account_str]['bag'][item['name']] = 0
                        self.jx3_users[qq_account_str]['bag'][item['name']] += item_amount
                        returnMsg = "[CQ:at,qq={0}] 购买成功！\n{1}+{2}".format(qq_account, item_display_name, item_amount)
                        for k, v in cost_list.items():
                            if k in qq_stat:
                                self.jx3_users[qq_account_str][k] -= v * item_amount
                                returnMsg += "\n{0}-{1}".format(STAT_DISPLAY_NAME[k], v * item_amount)
                    else:
                        returnMsg = "[CQ:at,qq={0}] 购买失败！\n购买1个 {1} 需要:{2}".format(qq_account, item_display_name, print_cost(cost_list))

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def useItem(self, qq_account, item_display_name, item_amount):
        returnMsg = ""
        self.mutex.acquire()

        try:
            item = find_item(item_display_name)
            if item != None:
                if not isItemUsable(item):
                    returnMsg = "[CQ:at,qq={0}] {1} 不可使用。".format(qq_account, item_display_name)
                else:

                    qq_account_str = str(qq_account)
                    qq_stat = self.jx3_users[qq_account_str]

                    effect_list = item['effect']

                    if item['name'] not in self.jx3_users[qq_account_str]['bag']:
                        returnMsg = "[CQ:at,qq={0}] 你并没有 {1}，无法使用。".format(qq_account, item_display_name)
                    elif self.jx3_users[qq_account_str]['bag'][item['name']] < item_amount:
                        returnMsg = "[CQ:at,qq={0}] 你并没有那么多 {1}。".format(qq_account, item_display_name)
                    else:
                        item_used = True
                        returnMsg = "[CQ:at,qq={0}] 使用 {1} x {2}".format(qq_account, item_display_name, item_amount)
                        for k, v in effect_list.items():
                            if k in qq_stat:
                                self.jx3_users[qq_account_str][k] += v * item_amount
                                returnMsg += "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v * item_amount)
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
                            elif k == 'attack_count':
                                if qq_account_str in self.group_info:
                                    leader = qq_account_str
                                else:
                                    leader = self._get_leader_by_member(qq_account_str)
                                
                                if leader != "" and leader in self.dungeon_status:
                                    self.dungeon_status[leader]['attack_count'][qq_account_str]['available_attack'] += v * item_amount
                                    returnMsg += "\n攻击次数+{0}".format(v * item_amount)
                                else:
                                    returnMsg = "[CQ:at,qq={0}] 你不在副本里，无法使用。".format(qq_account)
                                    item_used = False

                        if item_used:
                            self.jx3_users[qq_account_str]['bag'][item['name']] -= item_amount
                            if self.jx3_users[qq_account_str]['bag'][item['name']] == 0:
                                self.jx3_users[qq_account_str]['bag'].pop(item['name'])


            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def shopList(self, qq_account):
        try:
            returnMsg = "[CQ:at,qq={0}]\n---------杂货商---------\n--货真价实，童叟无欺--".format(qq_account)
            for item in ITEM_LIST:
                if 'cost' in item:
                    returnMsg += "\n*【{0}】".format(item['display_name'])
                    for k, v in item['cost'].items():
                        returnMsg += "----{0}：{1}".format(STAT_DISPLAY_NAME[k], v)
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def waBao(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)
            val = self.jx3_users[qq_account_str]
            if val['energy'] < WA_BAO_ENERGY_REQUIRED:
                returnMsg = "[CQ:at,qq={0}] 体力不足！无法挖宝。".format(qq_account)
            elif qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] 老实点，你还要在监狱里蹲{1}小时{2}分{3}秒。".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            else:
                if qq_account in self.jail_list:
                    self.jail_list.pop(qq_account)

                yday = self._reset_daliy_count(qq_account_str)
                yday_str = str(yday)

                if self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['count'] < MAX_DALIY_WA_BAO_COUNT:
                    last_time = self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['last_time']
                    if last_time != None and time.time() - last_time <= WA_BAO_COOLDOWN:
                        time_val = calculateRemainingTime(WA_BAO_COOLDOWN, last_time)
                        returnMsg = "[CQ:at,qq={0}] 大侠你刚刚挖完宝藏，身体有些疲惫，请过{1}分{2}秒之后再挖。".format(
                                        qq_account,
                                        time_val['mins'],
                                        time_val['secs'])
                    else:
                        reward_item_name = get_wa_bao_reward()
                        self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['count'] += 1
                        self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['last_time'] = time.time()

                        self.jx3_users[qq_account_str]['energy'] -= WA_BAO_ENERGY_REQUIRED

                        returnMsg = '[CQ:at,qq={0}]\n今日挖宝次数：{1}/{2}'.format(
                                            qq_account,
                                            self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['count'],
                                            MAX_DALIY_WA_BAO_COUNT)

                        if reward_item_name == "":
                            returnMsg += "\n你一铲子下去，什么也没挖到。"
                        else:
                            if reward_item_name not in self.jx3_users[qq_account_str]['bag']:
                                    self.jx3_users[qq_account_str]['bag'][reward_item_name] = 0
                            self.jx3_users[qq_account_str]['bag'][reward_item_name] += 1
                            returnMsg += "\n你一铲子下去，挖到了一个神秘的东西: {0}+1 体力-{1}".format(
                                            get_item_display_name(reward_item_name),
                                            WA_BAO_ENERGY_REQUIRED)
                else:
                    returnMsg = "[CQ:at,qq={0}] 一天最多挖宝{1}次。你已经挖了{1}次啦，今天休息休息吧。".format(qq_account, MAX_DALIY_WA_BAO_COUNT)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def use_firework(self, item_display_name, fromQQ, toQQ):
        returnMsg = ""
        self.mutex.acquire()

        try:
            item = find_item(item_display_name)
            if item != None:

                fromQQ_str = str(fromQQ)
                qq_stat = self.jx3_users[fromQQ_str]

                if item['name'] not in self.jx3_users[fromQQ_str]['bag']:
                    returnMsg = "[CQ:at,qq={0}] 你并没有 {1}，无法使用。".format(fromQQ, item_display_name)
                else:
                    self.jx3_users[fromQQ_str]['bag'][item['name']] -= 1
                    if self.jx3_users[fromQQ_str]['bag'][item['name']] == 0:
                        self.jx3_users[fromQQ_str]['bag'].pop(item['name'])

                    use_zhen_cheng_zhi_xin(self.qq_group, fromQQ, toQQ)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def get_equipment_info(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            val = self.equipment[str(qq_account)]

            returnMsg = "[CQ:at,qq={0}] 装备信息：\n武器：{1}\n----pve攻击：{2}----pvp攻击：{3}\n防具：{4}\n----pve血量：{5}----pvp血量：{6}".format(
                qq_account,
                val['weapon']['display_name'],
                val['weapon']['pve'],
                val['weapon']['pvp'],
                val['armor']['display_name'],
                val['armor']['pve'],
                val['armor']['pvp'])

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def change_weapon_name(self, qq_account, name):
        returnMsg = ""
        self.mutex.acquire()

        try:
            self.equipment[str(qq_account)]['weapon']['display_name'] = name
            returnMsg = "[CQ:at,qq={0}] 的武器已更名为 {1}".format(qq_account, name)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def change_armor_name(self, qq_account, name):
        returnMsg = ""
        self.mutex.acquire()

        try:
            self.equipment[str(qq_account)]['armor']['display_name'] = name
            returnMsg = "[CQ:at,qq={0}] 的防具已更名为 {1}".format(qq_account, name)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def get_faction_info(self):
        returnMsg = "本群阵营信息\n"
        self.mutex.acquire()

        try:
            yday = self._reset_daliy_count()
            yday_str = str(yday)
            retval = self._get_faction_count()
            returnMsg += "本群为{0}群\n恶人谷人数:\t{1} 今日阵营点数：{4}\n浩气盟人数:\t{2} 今日阵营点数：{5}\n中立人数:\t{3}".format(
                        "浩气强势" if retval[2] > retval[1] else "恶人强势" if retval[1] > retval[2] else "势均力敌",
                        retval[1],
                        retval[2],
                        retval[0],
                        self.daliy_action_count[yday_str]['faction']['eren']['point'],
                        self.daliy_action_count[yday_str]['faction']['haoqi']['point'])

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def _get_faction_count(self):
        retval = [0, 0, 0]
        for key, value in self.jx3_users.items():
            retval[value['faction_id']] += 1
        return retval


    def get_pve_gear_point_rank(self):
        returnMsg = "本群pve装备排行榜"
        self.mutex.acquire()

        try:
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['pve_gear_point'], y[1]['pve_gear_point']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['pve_gear_point'])
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def get_pvp_gear_point_rank(self):
        returnMsg = "本群pvp装备排行榜"
        self.mutex.acquire()

        try:
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['pvp_gear_point'], y[1]['pvp_gear_point']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['pvp_gear_point'])
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def get_money_rank(self):
        returnMsg = "本群土豪排行榜"
        self.mutex.acquire()

        try:
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['money'], y[1]['money']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['money'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), int(rank_list[i][1]['money']))
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def get_speech_rank(self, qq_account):
        returnMsg = "本群今日聊天排行榜"
        self.mutex.acquire()

        try:
            yday = self._reset_daliy_count(str(qq_account))
            yday_str = str(yday)

            rank_list = sorted(self._get_daliy_list(yday_str), lambda x, y: cmp(x[1]['speech_count'], y[1]['speech_count']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['speech_count'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(
                        i + 1,
                        getGroupNickName(self.qq_group, int(rank_list[i][0])),
                        rank_list[i][1]['speech_count'])
                else:
                    break

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def get_qiyu_rank(self):
        returnMsg = "本群奇遇排行榜"
        self.mutex.acquire()

        try:
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['qiyu'], y[1]['qiyu']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['qiyu'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['qiyu'])
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def get_weiwang_rank(self):
        returnMsg = "本群威望排行榜"
        self.mutex.acquire()

        try:

            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['weiwang'], y[1]['weiwang']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['weiwang'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['weiwang'])
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def put_wanted(self, fromQQ, toQQ):
        returnMsg = ""
        self.mutex.acquire()

        try:
            if not self.isUserRegister(toQQ):
                returnMsg = "[CQ:at,qq={0}] 对方尚未注册，无法悬赏。".format(fromQQ)
            else:
                fromQQ_str = str(fromQQ)
                toQQ_str = str(toQQ)

                yday = self._reset_daliy_count(toQQ_str)
                yday_str = str(yday)

                if self.jx3_users[fromQQ_str]['money'] < WANTED_MONEY_REWARD:
                    returnMsg = "[CQ:at,qq={0}] 金钱不足，无法悬赏。".format(fromQQ)
                elif self.daliy_action_count[yday_str][toQQ_str]['jailed'] >= JAIL_TIMES_PROTECTION:
                    returnMsg = "[CQ:at,qq={0}] 对方今天已经被抓进去{1}次了，无法悬赏。".format(fromQQ, JAIL_TIMES_PROTECTION)
                else:
                    self.jx3_users[fromQQ_str]['money'] -= WANTED_MONEY_REWARD

                    import CQSDK
                    CQSDK.SendGroupMsg(self.qq_group, "[CQ:at,qq={0}] 悬赏成功！\n金钱-{1}".format(fromQQ, WANTED_MONEY_REWARD))

                    returnMsg = self._put_wanted_internal(toQQ_str, WANTED_MONEY_REWARD)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def _put_wanted_internal(self, toQQ_str, money_amount):
        if toQQ_str in self.wanted_list:
            if time.time() - self.wanted_list[toQQ_str]['wanted_time'] > WANTED_DURATION:
                self.wanted_list[toQQ_str]['reward'] = money_amount
            else:
                self.wanted_list[toQQ_str]['reward'] += money_amount

            self.wanted_list[toQQ_str]['wanted_time'] = time.time()
        else:
            self.wanted_list[toQQ_str] = {'reward': money_amount, 'wanted_time': time.time(), 'failed_try': {}}

        return "江湖恩怨一朝清，惟望群侠多援手。现有人愿付{0}金对 {1} 进行悬赏，总赏金已达{2}金，众侠士切勿错过。".format(
                                money_amount,
                                getGroupNickName(self.qq_group, int(toQQ_str)),
                                self.wanted_list[toQQ_str]['reward'])

    def get_wanted_list(self):
        returnMsg = "本群悬赏榜"
        msg_list = ""
        self.mutex.acquire()

        try:
            rank_list = sorted(self.wanted_list.items(), lambda x, y: cmp(x[1]['reward'], y[1]['reward']), reverse=True)
            list_len = len(rank_list)
            index = 1
            for k, v in rank_list:
                if time.time() - self.wanted_list[k]['wanted_time'] < WANTED_DURATION:
                    time_val = calculateRemainingTime(WANTED_DURATION, self.wanted_list[k]['wanted_time'])
                    msg_list += '\n{0}. {1} {2}金 {3}小时{4}分{5}秒'.format(
                                    index,
                                    getGroupNickName(self.qq_group, int(k)),
                                    v['reward'],
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                    index += 1

            if msg_list == "":
                msg_list = "\n暂无悬赏"

            returnMsg += msg_list

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def catch_wanted(self, fromQQ, toQQ):
        returnMsg = ""
        self.mutex.acquire()

        try:
            fromQQ_str = str(fromQQ)
            toQQ_str = str(toQQ)

            yday = self._reset_daliy_count(toQQ_str)
            yday_str = str(yday)

            if fromQQ_str in self.jail_list and time.time() - self.jail_list[fromQQ_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[fromQQ_str])
                    returnMsg = "[CQ:at,qq={0}] 老实点，你还要在监狱里蹲{1}小时{2}分{3}秒。".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif toQQ_str in self.jail_list and time.time() - self.jail_list[toQQ_str] < JAIL_DURATION:
                    returnMsg = "[CQ:at,qq={0}] 对方在监狱里蹲着呢，你这是要劫狱吗？".format(fromQQ)
            elif toQQ_str in self.wanted_list and time.time() - self.wanted_list[toQQ_str]['wanted_time'] < WANTED_DURATION:
                if 'failed_try' in self.wanted_list[toQQ_str] and fromQQ_str in self.wanted_list[toQQ_str]['failed_try'] and time.time() - self.wanted_list[toQQ_str]['failed_try'][fromQQ_str] < WANTED_COOLDOWN:
                    time_val = calculateRemainingTime(WANTED_COOLDOWN, self.wanted_list[toQQ_str]['failed_try'][fromQQ_str])
                    returnMsg = "[CQ:at,qq={0}] 你已经尝试过抓捕了，奈何技艺不佳。请锻炼{1}小时{2}分{3}秒后再来挑战！".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                elif self.jx3_users[fromQQ_str]['energy'] < WANTED_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] 体力不足！需要消耗{1}体力。".format(fromQQ, WANTED_ENERGY_COST)
                else:
                    battle_result = self._calculate_battle(fromQQ_str, toQQ_str, 'pvp')
                    winner = battle_result['winner']
                    loser = battle_result['loser']
                    success_chance = battle_result['success_chance']

                    self.jx3_users[fromQQ_str]['energy'] -= WANTED_ENERGY_COST

                    if winner == fromQQ_str:
                        reward = int(0.9 * self.wanted_list[toQQ_str]['reward'])
                        self.jx3_users[fromQQ_str]['money'] += reward
                        self.wanted_list.pop(toQQ_str)
                        self.jail_list[toQQ_str] = time.time()

                        self.daliy_action_count[yday_str][toQQ_str]['jailed'] += 1

                        returnMsg = "{0}在时限内被{1}成功抓捕，悬赏解除。成功率：{2}%\n[CQ:at,qq={3}] 获得：\n金钱+{4}金\n体力-{5}".format(
                                        getGroupNickName(self.qq_group, int(toQQ)),
                                        getGroupNickName(self.qq_group, int(fromQQ)),
                                        int(math.floor(success_chance * 100)),
                                        fromQQ,
                                        reward,
                                        WANTED_ENERGY_COST)
                    else:
                        if 'failed_try' not in self.wanted_list[toQQ_str]:
                            self.wanted_list[toQQ_str]['failed_try'] = {}
                        self.wanted_list[toQQ_str]['failed_try'][fromQQ_str] = time.time()
                        returnMsg = "[CQ:at,qq={0}] 抓捕失败，成功率：{1}%\n体力-{2}".format(
                                        fromQQ,
                                        int(math.floor(success_chance * 100)),
                                        WANTED_ENERGY_COST)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def get_cha_guan_quest(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            daliy_stat = self.daliy_action_count[yday_str][qq_account_str]['cha_guan']

            if qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] 老实点，你还要在监狱里蹲{1}小时{2}分{3}秒。".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif len(daliy_stat['complete_quest']) >= len(CHA_GUAN_QUEST_INFO):
                returnMsg = "[CQ:at,qq={0}] 你已经完成了{1}个茶馆任务啦，明天再来吧。".format(qq_account, len(CHA_GUAN_QUEST_INFO))
            elif self.jx3_users[qq_account_str]['energy'] < CHA_GUAN_ENERGY_COST:
                returnMsg = "[CQ:at,qq={0}] 体力不足！需要消耗{1}体力。".format(qq_account, CHA_GUAN_ENERGY_COST)
            elif daliy_stat['current_quest'] != "":
                returnMsg = "[CQ:at,qq={0}] 你已经接了一个任务啦。\n当前任务：{1}".format(qq_account, CHA_GUAN_QUEST_INFO[daliy_stat['current_quest']]['display_name'])
            else:
                remain_quest = list(set(CHA_GUAN_QUEST_INFO.keys()) - set(daliy_stat['complete_quest']))

                quest_name = remain_quest[random.randint(0, len(remain_quest) - 1)]

                self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['current_quest'] = quest_name
                quest = CHA_GUAN_QUEST_INFO[quest_name]

                rewardMsg = ""
                for k, v in quest['reward'].items():
                    rewardMsg += "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v)

                requireMsg = ""
                for k, v in quest['require'].items():
                    requireMsg += "\n{0} x {1}".format(get_item_display_name(k), v)
                requireMsg += "\n体力：{0}".format(CHA_GUAN_ENERGY_COST)

                returnMsg = "[CQ:at,qq={0}] 茶馆任务({1}/{2})\n{3}\n{4}\n需求:{5}\n奖励：{6}".format(
                                qq_account,
                                len(daliy_stat['complete_quest']) + 1,
                                len(CHA_GUAN_QUEST_INFO.keys()),
                                quest['display_name'],
                                quest['description'],
                                requireMsg,
                                rewardMsg)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def complete_cha_guan_quest(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] 老实点，你还要在监狱里蹲{1}小时{2}分{3}秒。".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['current_quest'] != "":

                daliy_stat = self.daliy_action_count[yday_str][qq_account_str]['cha_guan']
                quest = CHA_GUAN_QUEST_INFO[daliy_stat['current_quest']]

                if self.jx3_users[qq_account_str]['energy'] < CHA_GUAN_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] 体力不足！需要消耗{1}体力。".format(qq_account, CHA_GUAN_ENERGY_COST)
                else:

                    has_require = True
                    for k, v in quest['require'].items():
                        has_require = has_require and k in self.jx3_users[qq_account_str]['bag'] and self.jx3_users[qq_account_str]['bag'][k] >= v

                    if has_require:
                        itemMsg = ""

                        for k, v in quest['require'].items():
                            self.jx3_users[qq_account_str]['bag'][k] -= v
                            if self.jx3_users[qq_account_str]['bag'][k] == 0:
                                self.jx3_users[qq_account_str]['bag'].pop(k)
                            itemMsg += "\n{0}-{1}".format(get_item_display_name(k), v)

                        self.jx3_users[qq_account_str]['energy'] -= CHA_GUAN_ENERGY_COST
                        self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['complete_quest'].append(daliy_stat['current_quest'])
                        self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['current_quest'] = ""

                        rewardMsg = ""
                        for k, v in quest['reward'].items():
                            if k in self.jx3_users[qq_account_str]:
                                self.jx3_users[qq_account_str][k] += v
                                rewardMsg += "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v)

                        returnMsg = "[CQ:at,qq={0}] 茶馆任务完成！{1}/{2}\n消耗任务物品：{3}\n体力-{4}\n获得奖励：{5}".format(
                                        qq_account,
                                        len(self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['complete_quest']),
                                        len(CHA_GUAN_QUEST_INFO),
                                        itemMsg,
                                        CHA_GUAN_ENERGY_COST,
                                        rewardMsg)
                    else:
                        returnMsg = "[CQ:at,qq={0}] 任务物品不足！".format(qq_account)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def catch_hun_hun(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] 老实点，你还要在监狱里蹲{1}小时{2}分{3}秒。".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['current_quest'] == "cha_guan_hun_hun":
                if 'hun_hun_zheng_ming' in self.jx3_users[qq_account_str]['bag'] and self.jx3_users[qq_account_str]['bag']['hun_hun_zheng_ming'] >= 3:
                    returnMsg = "[CQ:at,qq={0}] 你已经抓了太多混混啦，休息一下吧。".format(qq_account_str)
                else:
                    battle_result = self._calculate_battle(qq_account_str, "hun_hun", 'pve')
                    winner = battle_result['winner']
                    loser = battle_result['loser']
                    success_chance = battle_result['success_chance']

                    if winner == qq_account_str:

                        npc = NPC_LIST["hun_hun"]

                        reward_list = npc['reward']

                        rewardMsg = ""
                        for k, v in reward_list.items():
                            if k in self.jx3_users[qq_account_str]:
                                rand = random.uniform(0, 1)
                                if rand <= npc['reward_chance']:
                                    self.jx3_users[qq_account_str][k] += v
                                    rewardMsg = "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v)

                        if 'hun_hun_zheng_ming' not in self.jx3_users[qq_account_str]['bag']:
                            self.jx3_users[qq_account_str]['bag']['hun_hun_zheng_ming'] = 0
                        self.jx3_users[qq_account_str]['bag']['hun_hun_zheng_ming'] += 1
                        rewardMsg += '\n{0}+1'.format(get_item_display_name('hun_hun_zheng_ming'))

                        returnMsg = "[CQ:at,qq={0}] 抓捕混混成功！成功率：{1}%\n获得奖励：{2}".format(
                                        qq_account,
                                        int(math.floor(success_chance * 100)),
                                        rewardMsg)
                    else:
                        returnMsg = "[CQ:at,qq={0}] 抓捕失败，成功率：{1}%".format(
                                        qq_account,
                                        int(math.floor(success_chance * 100)))

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def do_qiyu(self, qiyu_type):
        returnMsg = ""
        self.mutex.acquire()

        try:
            logging.info(qiyu_type)

            for qq_account_str, qiyu_name in qiyu_type.items():
                qiyu = QIYU_LIST[qiyu_name]

                if qiyu_name in self.qiyu_status and self.qiyu_status[qiyu_name]['qq'] == qq_account_str and time.time() - self.qiyu_status[qiyu_name]['last_time'] < qiyu['cooldown']:
                    time_val = calculateRemainingTime(qiyu['cooldown'], self.qiyu_status[qiyu_name]['last_time'])
                    logging.info("qiyu in cd! qq: {0} remain_time: {1}hour {2}min {3}sec".format(
                                    qq_account_str,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs']))
                else:
                    requireMsg = ""
                    require_meet = True
                    if 'require' in qiyu:
                        for k, v in qiyu['require'].items():
                            if k in self.jx3_users[qq_account_str]:
                                require_meet = require_meet and (self.jx3_users[qq_account_str][k] >= v)
                                requireMsg += "{0}:{1} > {2}; ".format(k, self.jx3_users[qq_account_str][k], v)

                    if not require_meet:
                        logging.info("qiyu require not met! qq: {0} require: {1}".format(
                                        qq_account_str,
                                        requireMsg))
                    else:
                        rand = random.uniform(0, 1)

                        if rand > qiyu['chance']:
                            logging.info("No qiyu qq: {0} chance: {1} > {2}".format(
                                            qq_account_str,
                                            rand,
                                            qiyu['chance']))
                        else:
                            rewardMsg = ""
                            for k, v in qiyu['reward'].items():
                                if k in self.jx3_users[qq_account_str]:
                                    self.jx3_users[qq_account_str][k] += v
                                    rewardMsg += "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v)

                            self.jx3_users[qq_account_str]['qiyu'] += 1

                            if qiyu_name not in self.qiyu_status:
                                self.qiyu_status[qiyu_name] = {'qq': "", "last_time": None}
                            self.qiyu_status[qiyu_name]['qq'] = qq_account_str
                            self.qiyu_status[qiyu_name]['last_time'] = time.time()

                            returnMsg = "{0}\n获得奖励：{1}".format(qiyu['description'].format(qq_account_str), rewardMsg)

                            logging.info("qiyu! qq: {0} qiyu_name: {1} success_chance: {2} < {3}".format(
                                            qq_account_str,
                                            qiyu_name,
                                            rand,
                                            qiyu['chance']))

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def practise(self, fromQQ, toQQ):
        returnMsg = ""
        self.mutex.acquire()

        try:
            fromQQ_str = str(fromQQ)
            toQQ_str = str(toQQ)

            if not self.isUserRegister(toQQ_str):
                returnMsg = "[CQ:at,qq={0}] 对方尚未注册。".format(toQQ)
            else:
                yday = self._reset_daliy_count(toQQ_str)
                yday_str = str(yday)
                self._add_new_daliy_record(yday_str, fromQQ_str)

                fromQQ_stat = self.jx3_users[fromQQ_str]
                toQQ_stat = self.jx3_users[toQQ_str]

                if fromQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] 中立阵营无法切磋，请先加入阵营。".format(fromQQ)
                elif toQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] 对方是中立阵营，无法切磋。".format(fromQQ)
                elif fromQQ_stat['faction_id'] != toQQ_stat['faction_id'] and ROB_SAME_FACTION_PROTECTION:
                    returnMsg = "[CQ:at,qq={0}] 不同阵营无法切磋！".format(fromQQ)
                elif fromQQ_str in self.jail_list and time.time() - self.jail_list[fromQQ_str] < JAIL_DURATION:
                        time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[fromQQ_str])
                        returnMsg = "[CQ:at,qq={0}] 老实点，你还要在监狱里蹲{1}小时{2}分{3}秒。".format(
                                        fromQQ,
                                        time_val['hours'],
                                        time_val['mins'],
                                        time_val['secs'])
                elif toQQ_str in self.jail_list and time.time() - self.jail_list[toQQ_str] < JAIL_DURATION:
                        returnMsg = "[CQ:at,qq={0}] 对方在监狱里蹲着呢，没法跟你切磋。".format(fromQQ)
                elif self.jx3_users[fromQQ_str]['energy'] < PRACTISE_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] 体力不足！需要消耗{1}体力。".format(fromQQ, PRACTISE_ENERGY_COST)
                else:
                    battle_result = self._calculate_battle(fromQQ_str, toQQ_str, 'pvp')
                    winner = battle_result['winner']
                    loser = battle_result['loser']
                    success_chance = battle_result['success_chance']

                    if 'practise' not in self.daliy_action_count[yday_str][toQQ_str]:
                        self.daliy_action_count[yday_str][fromQQ_str]['practise'] = {'weiwang': 0}
                    if 'practise' not in self.daliy_action_count[yday_str][toQQ_str]:
                        self.daliy_action_count[yday_str][toQQ_str]['practise'] = {'weiwang': 0}

                    weiwang_amount = random.randint(PRACTISE_WEIWANG_GAIN_MIN, PRACTISE_WEIWANG_GAIN_MAX)

                    if self.daliy_action_count[yday_str][winner]['practise']['weiwang'] < DALIY_PRACITSE_WEIWANG_GAIN:
                        winner_weiwang_gain = min(weiwang_amount, DALIY_PRACITSE_WEIWANG_GAIN - self.daliy_action_count[yday_str][winner]['practise']['weiwang'])
                    else:
                        winner_weiwang_gain = 0

                    if winner_weiwang_gain != 0 and self.daliy_action_count[yday_str][loser]['practise']['weiwang'] < DALIY_PRACITSE_WEIWANG_GAIN:
                        loser_weiwang_gain = min(int(weiwang_amount * PRACTISE_LOSER_GAIN_PERCENTAGE), DALIY_PRACITSE_WEIWANG_GAIN - self.daliy_action_count[yday_str][loser]['practise']['weiwang'])
                    else:
                        loser_weiwang_gain = 0

                    if (winner_weiwang_gain != 0 and winner == fromQQ_str) or (loser_weiwang_gain != 0 and loser == fromQQ_str):
                        energy_cost = PRACTISE_ENERGY_COST
                    else:
                        energy_cost = 0

                    self.jx3_users[fromQQ_str]['energy'] -= energy_cost

                    self.jx3_users[winner]['weiwang'] += winner_weiwang_gain
                    self.daliy_action_count[yday_str][winner]['practise']['weiwang'] += winner_weiwang_gain
                    self.jx3_users[loser]['weiwang'] += loser_weiwang_gain
                    self.daliy_action_count[yday_str][loser]['practise']['weiwang'] += loser_weiwang_gain

                    if energy_cost != 0:
                        self.daliy_action_count[yday_str]['faction'][FACTION_NAME_ID[fromQQ_stat['faction_id']]]['point'] += PRACTISE_FACTION_POINT_GAIN

                    returnMsg = "[CQ:at,qq={0}]与[CQ:at,qq={1}]进行了切磋。{2} 战胜了 {3}，成功率{4}%。\n{5} 威望+{6} {7}\n{8} 威望+{9} {10}".format(
                                    fromQQ,
                                    toQQ,
                                    getGroupNickName(self.qq_group, int(winner)),
                                    getGroupNickName(self.qq_group, int(loser)),
                                    int(math.floor(success_chance * 100)),
                                    getGroupNickName(self.qq_group, int(winner)),
                                    winner_weiwang_gain,
                                    "体力-{0}".format(energy_cost) if winner == fromQQ_str else "",
                                    getGroupNickName(self.qq_group, int(loser)),
                                    loser_weiwang_gain,
                                    "体力-{0}".format(energy_cost) if loser == fromQQ_str else "")

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def jjc(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)
            qq_account_stat = self.jx3_users[qq_account_str]

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if qq_account_str not in self.jjc_season_status:
                self.jjc_season_status[qq_account_str] = {'score': 0, 'last_time': None, 'win': 0, 'lose': 0}

            if qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] 老实点，你还要在监狱里蹲{1}小时{2}分{3}秒。".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif self.jx3_users[qq_account_str]['energy'] < JJC_ENERGY_COST:
                returnMsg = "[CQ:at,qq={0}] 体力不足！需要消耗{1}体力。".format(qq_account, JJC_ENERGY_COST)
            elif self.jjc_season_status[qq_account_str]['last_time'] != None and time.time() - self.jjc_season_status[qq_account_str]['last_time'] < JJC_COOLDOWN:
                    time_val = calculateRemainingTime(JJC_COOLDOWN, self.jjc_season_status[qq_account_str]['last_time'])
                    returnMsg = "[CQ:at,qq={0}] 你刚排过名剑大会了，请过{1}小时{2}分钟{3}秒后再来吧。".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            else:
                jjc_stat = self.jjc_season_status[qq_account_str]

                rank = min(MAX_JJC_RANK, jjc_stat['score'] // 100)

                available_list = list(set(self.jx3_users.keys()) - set([qq_account_str]))
                random_person = available_list[random.randint(0, len(available_list) - 1)]

                self._add_new_daliy_record(yday_str, random_person)

                if random_person not in self.jjc_season_status:
                    self.jjc_season_status[random_person] = {'score': 0, 'last_time': None, 'win': 0, 'lose': 0}
                random_person_jjc_stat = self.jjc_season_status[random_person]

                random_person_rank = random_person_jjc_stat['score'] // 100

                fromQQ_modifier = 1
                toQQ_modifier = 1
                if rank >= 0 and random_person_rank >= 0:
                    if rank > random_person_rank:
                        toQQ_modifier = 1 + JJC_GEAR_MODIFIER * int(rank - random_person_rank)
                    elif rank < random_person_rank:
                        fromQQ_modifier = 1 + JJC_GEAR_MODIFIER * int(random_person_rank - rank)

                logging.info("fromqq: {0} score: {1} rank: {2} modifier: {3}; toqq: {4} score: {5} rank: {6} modifier: {7}".format(
                                qq_account_str,
                                jjc_stat['score'],
                                rank,
                                fromQQ_modifier,
                                random_person,
                                random_person_jjc_stat['score'],
                                random_person_rank,
                                toQQ_modifier))

                returnMsg = "[CQ:at,qq={0}] 加入名剑大会排位。\n你的名剑大会分数：{1} 段位：{2}段。匹配到的对手是 {3}，名剑大会分数：{4} 段位：{5}段".format(
                                qq_account,
                                jjc_stat['score'],
                                rank,
                                getGroupNickName(self.qq_group, int(random_person)),
                                random_person_jjc_stat['score'],
                                random_person_rank)
                import CQSDK
                CQSDK.SendGroupMsg(self.qq_group, returnMsg)

                battle_result = self._calculate_battle(qq_account_str, random_person, 'pvp', fromQQ_modifier, toQQ_modifier)
                winner = battle_result['winner']
                loser = battle_result['loser']
                success_chance = battle_result['success_chance']

                self.jx3_users[qq_account_str]['energy'] -= JJC_ENERGY_COST

                if winner == qq_account_str:

                    if 'jjc' in self.daliy_action_count[yday_str][qq_account_str] and self.daliy_action_count[yday_str][qq_account_str]['jjc']['win'] < DALIY_JJC_DOUBLE_REWARD_COUNT:
                        reward_modifier = 2
                    else:
                        reward_modifier = 1

                    weiwang_reward = int(random.randint(JJC_REWARD_WEIWANG_MIN, JJC_REWARD_WEIWANG_MAX) * (1 + JJC_REWARD_RANK_MODIFIER * rank)  * reward_modifier)

                    self.jx3_users[qq_account_str]['weiwang'] += weiwang_reward

                    if rank < random_person_rank:
                        score_reward = int(JJC_REWARD_RANK * (random_person_rank - rank) * reward_modifier)
                        score_lost = JJC_REWARD_RANK
                    else:
                        score_reward = JJC_REWARD_RANK * reward_modifier
                        score_lost = 0

                    double_msg = " (每日{1}场双倍奖励加成中：{0}/{1})".format(self.daliy_action_count[yday_str][qq_account_str]['jjc']['win'] + 1, DALIY_JJC_DOUBLE_REWARD_COUNT) if reward_modifier == 2 else ""

                    self.jjc_season_status[qq_account_str]['score'] += score_reward
                    self.jjc_season_status[qq_account_str]['last_time'] = time.time()

                    if self.jjc_season_status[random_person]['score'] < JJC_REWARD_RANK:
                        score_lost = 0

                    self.jjc_season_status[random_person]['score'] -= score_lost
                    self.jjc_season_status[qq_account_str]['win'] += 1
                    self.daliy_action_count[yday_str][qq_account_str]['jjc']['win'] += 1
                    self.jjc_season_status[random_person]['lose'] += 1

                    returnMsg = "[CQ:at,qq={0}] 战斗结果：胜利！成功率：{1}%\n {2} 威望+{3} 分数+{4} 体力-{5}{6}\n{7} 分数-{8}".format(
                                    qq_account_str,
                                    int(math.floor(success_chance * 100)),
                                    getGroupNickName(self.qq_group, int(qq_account)),
                                    weiwang_reward,
                                    score_reward,
                                    JJC_ENERGY_COST,
                                    double_msg,
                                    getGroupNickName(self.qq_group, int(random_person)),
                                    score_lost)

                    new_rank = self.jjc_season_status[qq_account_str]['score'] // 100
                    if  new_rank != rank:
                        returnMsg += "\n段位变更为：{0}".format(new_rank)
                else:
                    if rank < random_person_rank:
                        score_reward = JJC_REWARD_RANK
                        score_lost = 0
                    elif rank > random_person_rank:
                        score_reward = int(JJC_REWARD_RANK * (rank - random_person_rank))
                        score_lost = JJC_REWARD_RANK
                    else:
                        score_reward = JJC_REWARD_RANK
                        score_lost = 0

                    if self.jjc_season_status[qq_account_str]['score'] < JJC_REWARD_RANK:
                        score_lost = 0
                    self.jjc_season_status[qq_account_str]['score'] -= score_lost

                    self.jjc_season_status[qq_account_str]['last_time'] = time.time()
                    self.jjc_season_status[random_person]['score'] += score_reward

                    self.jjc_season_status[random_person]['win'] += 1
                    self.jjc_season_status[qq_account_str]['lose'] += 1

                    returnMsg = "[CQ:at,qq={0}] 战斗结果：失败！成功率：{1}%\n {2} 分数-{3} 体力-{4}；{5} 分数+{6}".format(
                                    qq_account_str,
                                    int(math.floor(success_chance * 100)),
                                    getGroupNickName(self.qq_group, int(qq_account)),
                                    score_lost,
                                    JJC_ENERGY_COST,
                                    getGroupNickName(self.qq_group, int(random_person)),
                                    score_reward)

                    new_rank = self.jjc_season_status[qq_account_str]['score'] // 100
                    if  new_rank != rank:
                        returnMsg += "\n段位变更为：{0}".format(new_rank)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def get_jjc_rank(self):
        returnMsg = ""
        self.mutex.acquire()

        try:
            returnMsg = "名剑大会排名榜 赛季：{0} 天数：{1}".format(self.jjc_status['season'], self.jjc_status['day'])

            yday = self._reset_daliy_count()
            yday_str = str(yday)

            rank_list = sorted(self.jjc_season_status.items(), lambda x, y: cmp(x[1]['score'], y[1]['score']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['score'] != 0:
                    returnMsg += '\n{0}. {1} 分数：{2} 段位：{3}'.format(
                        i + 1,
                        getGroupNickName(self.qq_group, int(rank_list[i][0])),
                        rank_list[i][1]['score'],
                        min(rank_list[i][1]['score'] // 100, MAX_JJC_RANK))
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def get_jjc_info(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)
            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if qq_account_str not in self.jjc_season_status:
                self.jjc_season_status[qq_account_str] = {'score': 0, 'last_time': None, 'win': 0, 'lose': 0}

            jjc_status = self.jjc_season_status[qq_account_str]

            returnMsg = "[CQ:at,qq={0}] 第{1}赛季名剑大会分数：{2} 段位：{3} 胜负：{4}/{5} 胜率：{6}%".format(
                    qq_account,
                    self.jjc_status['season'],
                    jjc_status['score'],
                    jjc_status['score'] // 100,
                    jjc_status['win'],
                    jjc_status['lose'],
                    int(math.floor(jjc_status['win'] * 100 / (jjc_status['win'] + jjc_status['lose']))) if (jjc_status['win'] + jjc_status['lose']) > 0 else 100)

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def _get_daliy_list(self, yday_str):
        logging.info([(k, v) for k, v in self.daliy_action_count[yday_str].items() if k not in ['jjc', 'faction']])
        return_list = []
        for k, v in self.daliy_action_count[yday_str].items():
            if k not in ['jjc', 'faction']:
                for d_k, d_v in daliy_dict.items():
                    if d_k not in v:
                        v[d_k] = d_v
                return_list.append((k, v))
        return return_list

    def join_class(self, qq_account, class_display_name):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            if self.jx3_users[qq_account_str]['class_id'] != 0:
                returnMsg = "[CQ:at,qq={0}] 你已经加入了门派了！".format(qq_account)
            elif class_display_name in CLASS_LIST:
                self.jx3_users[qq_account_str]['class_id'] = CLASS_LIST.index(class_display_name)
                returnMsg = "[CQ:at,qq={0}] 加入门派{1}！".format(qq_account, class_display_name)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def remove_lover(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            if self.jx3_users[qq_account_str]['lover'] == 0:
                returnMsg = "[CQ:at,qq={0}] 你没有情缘，别乱用。".format(qq_account)
            else:
                lover = self.jx3_users[qq_account_str]['lover']
                love_time = time.time() - self.jx3_users[qq_account_str]['lover_time']
                self.jx3_users[qq_account_str]['lover_time'] = None
                self.jx3_users[qq_account_str]['lover'] = 0
                self.jx3_users[str(lover)]['lover_time'] = None
                self.jx3_user[str(lover)]['lover'] = 0
                returnMsg = "[CQ:at,qq={0}] 决定去寻找新的旅程。".format(qq_account)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def create_group(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()
        try:
            qq_account_str = str(qq_account)

            if qq_account_str in self.group_info:
                returnMsg = "[CQ:at,qq={0}] 你已经创建了一个队伍了！".format(qq_account)
            else:
                find_leader = self._get_leader_by_member(qq_account_str)
                if find_leader != "":
                    returnMsg = "[CQ:at,qq={0}] 你已经加入了 {1} 的队伍！".format(qq_account, getGroupNickName(self.qq_group, int(find_leader)))
                else:
                    self.group_info[qq_account_str] = {
                        'member_list': [],
                        'create_time': time.time()
                    }
                    returnMsg = "[CQ:at,qq={0}] 创建队伍成功！请让队友输入【加入队伍[CQ:at,qq={0}]】加入队伍。\n进入副本后此队伍无法被加入，请确认人数正确后再进入副本。".format(qq_account)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def join_group(self, qq_account, leader):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)
            leader_str = str(leader)

            if qq_account_str in self.group_info:
                returnMsg = "[CQ:at,qq={0}] 你已经创建了一个队伍，不能加入其他人的队伍，输入【退出队伍】退出当前队伍。".format(qq_account)
            elif leader_str not in self.group_info:
                returnMsg = "[CQ:at,qq={0}] 队伍不存在。".format(qq_account)
            elif leader_str in self.dungeon_status:
                returnMsg = "[CQ:at,qq={0}] {1} 的队伍正在副本里，无法加入。".format(qq_account, getGroupNickName(self.qq_group, int(leader)))
            elif len(self.group_info[leader_str]['member_list']) >= MAX_GROUP_MEMBER:
                returnMsg = "[CQ:at,qq={0}] 队伍已满，无法加入。".format(qq_account)
            else:
                find_leader = self._get_leader_by_member(qq_account_str)
                if find_leader != "":
                    returnMsg = "[CQ:at,qq={0}] 你已经加入了 {1} 的队伍，输入【退出队伍】退出当前队伍".format(qq_account, getGroupNickName(self.qq_group, int(find_leader)))
                else:
                    self.group_info[leader_str]['member_list'].append(qq_account_str)
                    returnMsg = "[CQ:at,qq={0}] 成功加入 {1} 的队伍。".format(qq_account, getGroupNickName(self.qq_group, int(leader)))

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def get_group_info(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            if qq_account_str in self.group_info:
                leader = qq_account_str
            else:
                leader = self._get_leader_by_member(qq_account_str)
            
            if leader == "":
                returnMsg = "[CQ:at,qq={0}] 你没有加入任何队伍。".format(qq_account)
            else:
                returnMsg = "[CQ:at,qq={0}] 当前队伍信息：\n队长：{1} pve装分：{2}".format(
                    qq_account_str,
                    getGroupNickName(self.qq_group, int(leader)),
                    self.jx3_users[leader]['pve_gear_point'])
                if self.group_info[leader]['member_list'] != []:
                    for member in self.group_info[leader]['member_list']:
                        returnMsg += "\n{0} pve装分：{1}".format(
                            getGroupNickName(self.qq_group, int(member)),
                            self.jx3_users[member]['pve_gear_point'])

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def quit_group(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()
        self.is_locked = True

        try:
            qq_account_str = str(qq_account)

            if qq_account_str not in self.group_info:
                leader = self._get_leader_by_member(qq_account_str)
                if leader == "":
                    returnMsg = "[CQ:at,qq={0}] 你不在任何队伍里。".format(qq_account)
                else:
                    self.group_info[leader]['member_list'].remove(qq_account_str)
                    returnMsg = "[CQ:at,qq={0}] 你离开了 {1} 的队伍。".format(qq_account, getGroupNickName(self.qq_group, int(leader)))
            else:
                self.group_info.pop(qq_account_str)
                if qq_account_str in self.dungeon_status:
                    self.dungeon_status.pop(qq_account_str)
                returnMsg = "[CQ:at,qq={0}] 你的队伍解散了。".format(qq_account)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def _get_leader_by_member(self, qq_account_str):
        for k, v in self.group_info.items():
            if qq_account_str in v['member_list']:
                return k
        return ""

    def list_dungeon(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            returnMsg = "[CQ:at,qq={0}] 副本列表：".format(qq_account)
            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if 'dungeon' not in self.daliy_action_count[yday_str][qq_account_str]:
                self.daliy_action_count[yday_str][qq_account_str]['dungeon'] = {}
            
            self._update_gear_point(qq_account_str)

            for k, v in DUNGEON_LIST.items():
                has_cd = k in self.daliy_action_count[yday_str][qq_account_str]['dungeon'] and self.daliy_action_count[yday_str][qq_account_str]['dungeon'][k] == True
                has_reward = self.jx3_users[qq_account_str]['pve_gear_point'] < v['max_pve_reward_gain']
                returnMsg += "\n{0} {1} {2}".format(v['display_name'], "已攻略" if has_cd else "可攻略", "有boss奖励" if has_reward else "无boss奖励")

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def start_dungeon(self, qq_account, dungeon_name):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            dungeon_id = get_dungeon_id_by_display_name(dungeon_name)
            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if 'dungeon' not in self.daliy_action_count[yday_str][qq_account_str]:
                self.daliy_action_count[yday_str][qq_account_str]['dungeon'] = {}

            if dungeon_id != "":
                if qq_account_str not in self.group_info:
                    leader = self._get_leader_by_member(qq_account_str)
                    if leader == "":
                        returnMsg = "[CQ:at,qq={0}] 必须创建队伍才能进入副本。".format(qq_account)
                    else:
                        returnMsg = "[CQ:at,qq={0}] 你不是队长！无法使用此命令。".format(qq_account)
                elif qq_account_str in self.dungeon_status:
                    returnMsg = "[CQ:at,qq={0}] 你已经在副本里了。".format(qq_account)
                elif dungeon_id in self.daliy_action_count[yday_str][qq_account_str]['dungeon'] and self.daliy_action_count[yday_str][qq_account_str]['dungeon'][dungeon_id] == True:
                    returnMsg = "[CQ:at,qq={0}] 你有此副本cd，无法进入。".format(qq_account)
                else:
                    leader = qq_account_str
                    self._update_gear_point(qq_account_str)

                    has_cd = False
                    cd_msg = ""
                    has_energy = True
                    energy_msg = ""
                    pve_gear_point_too_high = [leader] if self.jx3_users[qq_account_str]['pve_gear_point'] >= DUNGEON_LIST[dungeon_id]['max_pve_reward_gain'] else []
                    for m in self.group_info[leader]['member_list']:
                        if dungeon_id in self.daliy_action_count[yday_str][str(m)]['dungeon'] and self.daliy_action_count[yday_str][str(m)]['dungeon'][dungeon_id] == True:
                            cd_msg += "[CQ:at,qq={0}] ".format(m)
                            has_cd = True
                        self._update_gear_point(str(m))
                        if self.jx3_users[str(m)]['pve_gear_point'] >= DUNGEON_LIST[dungeon_id]['max_pve_reward_gain']:
                            pve_gear_point_too_high.append(m)
                        elif self.jx3_users[str(m)]['energy'] < DUNGEON_ENERGY_REQUIRED:
                            energy_msg += "[CQ:at,qq={0}] ".format(m)
                            has_energy = False

                    if has_cd:
                        returnMsg = "[CQ:at,qq={0}] 你的队友有此副本cd，无法进入。".format(qq_account)
                    elif self.jx3_users[qq_account_str]['energy'] < DUNGEON_ENERGY_REQUIRED and qq_account_str not in pve_gear_point_too_high:
                        returnMsg = "[CQ:at,qq={0}] 你的体力不足，进入副本需要耗费体力：{1}".format(qq_account, DUNGEON_ENERGY_REQUIRED)
                    elif has_energy and energy_msg != "":
                        returnMsg = "{0} 体力不足，进入副本需要耗费体力：{1}".format(energy_msg, DUNGEON_ENERGY_REQUIRED)
                    else:
                        force_enter = True
                        if pve_gear_point_too_high != []:
                            pve_msg = ""

                            for m in pve_gear_point_too_high:
                                force_enter = force_enter and dungeon_id in self.daliy_action_count[yday_str][str(m)]['dungeon']
                                if dungeon_id not in self.daliy_action_count[yday_str][str(m)]['dungeon']:
                                    pve_msg += "[CQ:at,qq={0}] ".format(m)
                                    self.daliy_action_count[yday_str][str(m)]['dungeon'][dungeon_id] = False

                        if not force_enter:
                            returnMsg += "队伍中{0}pve装备太厉害啦，已经不能获得boss奖励了，仅可获得通关奖励且不消耗体力。如果确定还要进本的话，请再次输入 进入副本{1}".format(pve_msg, DUNGEON_LIST[dungeon_id]['display_name'])
                        else:
                            self.dungeon_status[leader] = copy.deepcopy(DUNGEON_LIST[dungeon_id])
                            self.dungeon_status[leader]['boss_detail'] = []
                            self.dungeon_status[leader]['attack_count'] = {}
                            self.dungeon_status[leader]['no_reward'] = copy.deepcopy(pve_gear_point_too_high)
                            for boss_id in self.dungeon_status[leader]['boss']:
                                boss = copy.deepcopy(NPC_LIST[boss_id])
                                boss['remain_hp'] = boss['equipment']['armor']['pve']
                                self.dungeon_status[leader]['boss_detail'].append(boss)

                            self.daliy_action_count[yday_str][leader]['dungeon'][dungeon_id] = True

                            energy_msg = ""
                            if leader not in pve_gear_point_too_high:
                                self.jx3_users[leader]['energy'] -= DUNGEON_ENERGY_REQUIRED
                                energy_msg = "[CQ:at,qq={0}] ".format(leader)
                                
                            for m in self.group_info[leader]['member_list']:
                                self.daliy_action_count[yday_str][str(m)]['dungeon'][dungeon_id] = True
                                if m not in pve_gear_point_too_high:
                                    self.jx3_users[str(m)]['energy'] -= DUNGEON_ENERGY_REQUIRED
                                    energy_msg += "[CQ:at,qq={0}] ".format(m)
                            returnMsg = "[CQ:at,qq={0}] 进入副本 {1} 成功！{2}体力-{3}".format(qq_account, dungeon_name, energy_msg, DUNGEON_ENERGY_REQUIRED)

                            import CQSDK
                            CQSDK.SendGroupMsg(self.qq_group, returnMsg)

                            boss = self.dungeon_status[leader]['boss_detail'][0]
                            returnMsg = "boss战：{0} (1/{1})\n请输入每位队员输入【攻击boss】开始战斗。".format(boss['display_name'], len(self.dungeon_status[qq_account_str]['boss_detail']))

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def attack_boss(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            if qq_account_str in self.group_info:
                leader = qq_account_str
            else:
                leader = self._get_leader_by_member(qq_account_str)

            dungeon = get_key_or_return_default(self.dungeon_status, leader, {})

            if dungeon != {} and leader != "":
                current_boss = dungeon['boss_detail'][0]

                if qq_account_str not in dungeon['attack_count']:
                    dungeon['attack_count'][qq_account_str] = {'damage': 0, 'available_attack': DUNGEON_MAX_ATTACK_COUNT, 'last_attack_time': None, 'total_attack_count': 0, 'success_attack_count': 0}

                if dungeon['attack_count'][qq_account_str]['last_attack_time'] == None:
                    dungeon['attack_count'][qq_account_str]['last_attack_time'] = time.time()

                if dungeon['attack_count'][qq_account_str]['available_attack'] < DUNGEON_MAX_ATTACK_COUNT:
                    count = int(math.floor((time.time() - dungeon['attack_count'][qq_account_str]['last_attack_time']) / float(DUNGEON_ATTACK_COOLDOWN)))
                    min_count = min(count, DUNGEON_MAX_ATTACK_COUNT - dungeon['attack_count'][qq_account_str]['available_attack'])
                    dungeon['attack_count'][qq_account_str]['available_attack'] += min_count
                    if min_count > 0:
                        dungeon['attack_count'][qq_account_str]['last_attack_time'] += min_count * DUNGEON_ATTACK_COOLDOWN
                
                if dungeon['attack_count'][qq_account_str]['available_attack'] >= DUNGEON_MAX_ATTACK_COUNT:
                    dungeon['attack_count'][qq_account_str]['last_attack_time'] = time.time()

                if dungeon['attack_count'][qq_account_str]['available_attack'] < 1:
                    time_val = calculateRemainingTime(DUNGEON_ATTACK_COOLDOWN * (1 - dungeon['attack_count'][qq_account_str]['available_attack']), dungeon['attack_count'][qq_account_str]['last_attack_time'])
                    returnMsg = "[CQ:at,qq={0}] 你没有攻击次数啦，还需要等{1}小时{2}分{3}秒。".format(
                                    qq_account_str,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                else:
                    boss_equipment = copy.deepcopy(current_boss['equipment'])
                    qq_equipment = copy.deepcopy(self.equipment[qq_account_str])
                    buff_msg = ""
                    if 'buff' in current_boss:
                        modifier = {}
                        for buff in current_boss['buff']:
                            fix_chance = 'hp' in buff and current_boss['remain_hp'] <= buff['hp'] * boss_equipment['armor']['pve']
                            rand = random.uniform(0, 1)
                            if rand <= buff['chance'] and fix_chance:
                                modifier = copy.deepcopy(buff)
                            logging.info(buff)
                            logging.info(rand)

                        if modifier != {}:
                            if 'count' in modifier and 'max_count' in modifier and modifier['count'] != 0:
                                boss_equipment['weapon']['pve'] = int(boss_equipment['weapon']['pve'] * (1 + modifier['weapon'] * modifier['count']))
                                description = modifier['description'].format(modifier['count'], modifier['max_count'])
                            elif 'money' in modifier:
                                current_boss['reward']['money'] += modifier['money']
                                current_boss['remain_hp'] += modifier['hp_recover']
                                description = modifier['description']
                            else:
                                boss_equipment['weapon']['pve'] = int(boss_equipment['weapon']['pve'] * modifier['weapon'])
                                description = modifier['description']
                            buff_msg = "\n{0}使出了招数：{1}。{2}".format(current_boss['display_name'], modifier['display_name'], description)
                    logging.info(buff_msg)
                    debuff_msg = ""
                    if 'debuff' in current_boss:
                        modifier = {}
                        for buff in current_boss['debuff']:
                            fix_chance = 'hp' in buff and current_boss['remain_hp'] <= buff['hp'] * boss_equipment['armor']['pve']

                            rand = random.uniform(0, 1)
                            if rand <= buff['chance'] and fix_chance:
                                modifier = copy.deepcopy(buff)

                        if modifier != {}:

                            if "attack_count" in modifier:
                                dungeon['attack_count'][qq_account_str]['available_attack'] -= modifier['attack_count']
                            else:
                                qq_equipment['weapon']['pve'] = int(qq_equipment['weapon']['pve'] * modifier['weapon'])
                            debuff_msg = "\n{0}使出了招数：{1}。{2}".format(current_boss['display_name'], modifier['display_name'], modifier['description'])

                    battle_result = self._calculate_battle(qq_account_str, '', 'pve', custom_from_qq_equipment=qq_equipment, custom_to_qq_equipment=boss_equipment)

                    winner = battle_result['winner']
                    loser = battle_result['loser']
                    success_chance = battle_result['success_chance']

                    dungeon['attack_count'][qq_account_str]['total_attack_count'] += 1
                    

                    returnMsg = "[CQ:at,qq={0}] 你对{1}发起了攻击。剩余攻击次数：{2}/{3}".format(qq_account, current_boss['display_name'], dungeon['attack_count'][qq_account_str]['available_attack'] - 1, DUNGEON_MAX_ATTACK_COUNT) + buff_msg + debuff_msg

                    if winner == qq_account_str:
                        damage = int(min(qq_equipment['weapon']['pve'], current_boss['remain_hp']))
                        dungeon['attack_count'][qq_account_str]['damage'] += damage
                        dungeon['attack_count'][qq_account_str]['available_attack'] -= 1
                        current_boss['remain_hp'] -= damage
                        dungeon['attack_count'][qq_account_str]['success_attack_count'] += 1

                        if 'buff' in current_boss:
                            for buff in current_boss['buff']:
                                if 'increase_type' in buff and buff['increase_type'] == 'win' and 'count' in buff and 'max_count' in buff:
                                    buff['count'] += 1 if buff['count'] < buff['max_count'] else 0

                        returnMsg += "\n攻击成功！成功率：{0}%，造成伤害：{1}。{2}血量：{3}/{4}".format(
                            int(math.floor(success_chance * 100)),
                            qq_equipment['weapon']['pve'],
                            current_boss['display_name'],
                            current_boss['remain_hp'],
                            boss_equipment['armor']['pve'])

                        if current_boss['remain_hp'] == 0:
                            import CQSDK
                            CQSDK.SendGroupMsg(self.qq_group, returnMsg)

                            reward_msg = ""
                            reward_member = ""
                            
                            for k, v in current_boss['reward'].items():
                                if k in self.jx3_users[leader] and leader not in dungeon['no_reward']:
                                    self.jx3_users[leader][k] += v

                                for m in self.group_info[leader]['member_list']:
                                    if k in self.jx3_users[m] and m not in dungeon['no_reward']:
                                        self.jx3_users[m][k] += v
                                reward_msg += "{0}+{1} ".format(STAT_DISPLAY_NAME[k], v)

                            item_reward_msg = ""
                            for k, v in current_boss['reward_item'].items():
                                if leader not in dungeon['no_reward']:
                                    rand = random.uniform(0, 1)
                                    if rand <= v:
                                        if k not in self.jx3_users[leader]['bag']:
                                            self.jx3_users[leader]['bag'][k] = 0
                                        self.jx3_users[leader]['bag'][k] += 1
                                        item_reward_msg += "\n{0}获得额外奖励：{1} x 1 概率：{2}%".format(getGroupNickName(self.qq_group, int(leader)), get_item_display_name(k), int(v * 100))

                                for m in self.group_info[leader]['member_list']:
                                    if m not in dungeon['no_reward']:
                                        rand = random.uniform(0, 1)
                                        if rand <= v:
                                            if k not in self.jx3_users[m]['bag']:
                                                self.jx3_users[m]['bag'][k] = 0
                                            self.jx3_users[m]['bag'][k] += 1
                                            item_reward_msg += "\n{0}获得额外奖励：{1} x 1 概率：{2}%".format(getGroupNickName(self.qq_group, int(m)), get_item_display_name(k), int(v * 100))

                            member_list = copy.deepcopy(self.group_info[leader]['member_list'])
                            member_list.append(leader)
                            for m in list(set(member_list) - set(dungeon['no_reward'])):
                                reward_member += "[CQ:at,qq={0}]".format(m)

                            if reward_member != "":
                                reward_msg = "{0}获得奖励{1}".format(reward_member, reward_msg)
                            else:
                                reward_msg = ""

                            mvp = sorted(dungeon['attack_count'].items(), lambda x, y: cmp(x[1]['damage'], y[1]['damage']), reverse=True)[0]
                            returnMsg = "{0}成功被击倒！{1}{2}\nmvp：{3} 伤害：{4} 攻击次数：{5}/{6}".format(
                                current_boss['display_name'],
                                reward_msg,
                                item_reward_msg,
                                getGroupNickName(self.qq_group, int(mvp[0])), mvp[1]['damage'],
                                dungeon['attack_count'][mvp[0]]['success_attack_count'],
                                dungeon['attack_count'][mvp[0]]['total_attack_count'])

                            for k, v in dungeon['attack_count'].items():
                                dungeon['attack_count'][k] = {'damage': 0, 'available_attack': max(DUNGEON_MAX_ATTACK_COUNT, v['available_attack']), 'last_attack_time': None, 'total_attack_count': 0, 'success_attack_count': 0}

                            dungeon['boss_detail'].pop(0)

                            CQSDK.SendGroupMsg(self.qq_group, returnMsg)
                            if len(dungeon['boss_detail']) > 0:
                                next_boss =  dungeon['boss_detail'][0]
                                returnMsg = "boss战：{0} ({1}/{2})\n请输入每位队员输入【攻击boss】开始战斗。".format(
                                    next_boss['display_name'],
                                    len(dungeon['boss']) - len(dungeon['boss_detail']) + 1,
                                    len(dungeon['boss']))
                            else:
                                returnMsg = "副本已结束！恭喜通关{0}！全员获得通关奖励：".format(dungeon['display_name'])
                                reward_msg = ""
                                for k, v in dungeon['reward'].items():
                                    if k in self.jx3_users[leader]:
                                        self.jx3_users[leader][k] += v

                                    for m in self.group_info[leader]['member_list']:
                                        if k in self.jx3_users[m]:
                                            self.jx3_users[m][k] += v
                                    reward_msg += "{0} + {1} ".format(STAT_DISPLAY_NAME[k], v)
                                returnMsg += reward_msg
                                CQSDK.SendGroupMsg(self.qq_group, returnMsg)
                                returnMsg = "队伍已解散。"
                                self.group_info.pop(leader)
                                self.dungeon_status.pop(leader)
                    else:
                        dungeon['attack_count'][qq_account_str]['available_attack'] -= 1
                        returnMsg += "\n攻击失败！成功率：{0}%。{1}血量：{2}/{3}".format(
                            int(math.floor(success_chance * 100)),
                            current_boss['display_name'],
                            current_boss['remain_hp'],
                            boss_equipment['armor']['pve'])

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg


    def get_current_boss_info(self, qq_account):
        returnMsg = ""
        self.mutex.acquire()

        try:
            qq_account_str = str(qq_account)

            if qq_account_str in self.group_info:
                leader = qq_account_str
            else:
                leader = self._get_leader_by_member(qq_account_str)

            dungeon = get_key_or_return_default(self.dungeon_status, leader, {})

            if dungeon != {} and leader != "":
                current_boss = dungeon['boss_detail'][0]
                rank_list = sorted(dungeon['attack_count'].items(), lambda x, y: cmp(x[1]['damage'], y[1]['damage']), reverse=True)
                list_len = len(rank_list)
                damage_msg = ""
                for i in range(5):
                    if i < list_len:
                        damage_msg += '\n{0}. {1} 伤害：{2} 次数：{3}/{4}'.format(
                            i + 1,
                            getGroupNickName(self.qq_group, int(rank_list[i][0])),
                            rank_list[i][1]['damage'],
                            dungeon['attack_count'][rank_list[i][0]]['success_attack_count'],
                            dungeon['attack_count'][rank_list[i][0]]['total_attack_count'])
                    else:
                        break
                returnMsg = "[CQ:at,qq={0}] 当前副本：{1} 当前boss：{2} {3}/{4}\n血量：{5}/{6} pve装分：{7}\n伤害排行榜：{8}".format(
                    qq_account,
                    dungeon['display_name'],
                    current_boss['display_name'],
                    len(dungeon['boss']) - len(dungeon['boss_detail']) + 1,
                    len(dungeon['boss']),
                    current_boss['remain_hp'],
                    current_boss['equipment']['armor']['pve'],
                    calculateGearPoint(current_boss['equipment'])['pve'],
                    damage_msg)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg
