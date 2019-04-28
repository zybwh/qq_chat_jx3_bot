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

import sqlite3
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


FACTION_DISPLAY_NAME = ['����', '���˹�', '������']
FACTION_NAME_ID = ['zhongli', 'eren', 'haoqi']

ITEM_LIST = [
    {"name": "zhen_cheng_zhi_xin", "display_name": "���֮��", "rank": 2, "cost": {"money": 999}},
    {"name": "hai_shi_shan_meng", "display_name": "����ɽ��", "rank": 1, "cost": {"money": 9999}},
    {"name": "jin_zhuan", "display_name": "��ש", "rank": 5, "effect": {"money": 50}},
    {"name": "jin_ye_zi", "display_name": "��Ҷ��", "rank": 6, "effect": {"money": 10}},
    {"name": "zhuan_shen_can", "display_name": "ת���", "rank": 5, "effect": {"energy": 5}, "cost": {"money": 100}},
    {"name": "jia_zhuan_shen_can", "display_name": "�ѡ�ת���", "rank": 3, "effect": {"energy": 30}, "cost": {"money": 500}},
    {"name": "rong_ding", "display_name": "�۶�", "rank": 3, "effect": {'pve_weapon': 5}, "cost": {"banggong": 5000}},
    {"name": "mo_shi", "display_name": "ĥʯ", "rank": 3, "effect": {'pvp_weapon': 5}, "cost": {"weiwang": 5000}},
    {"name": "ran", "display_name": "��", "rank": 4, "effect": {'pve_armor': 10}, "cost": {"banggong": 2000}},
    {"name": "yin", "display_name": "ӡ", "rank": 4, "effect": {'pvp_armor': 10}, "cost": {"weiwang": 2000}},
    {"name": "sui_rou", "display_name": "����", "rank": 4, "cost": {"money": 10}},
    {"name": "cu_bu", "display_name": "�ֲ�", "rank": 4, "cost": {"money": 10}},
    {"name": "gan_cao", "display_name": "�ʲ�", "rank": 4, "cost": {"money": 10}},
    {"name": "hong_tong", "display_name": "��ͭ", "rank": 4, "cost": {"money": 10}},
    {"name": "hun_hun_zheng_ming", "display_name": "���ץ��֤��", "rank": 0},
    {"name": "tuan_yuan_yan", "display_name": "��Բ��", "rank": 2, "effect": {'attack_count': 5}, "cost": {"money": 500}}
]

CHA_GUAN_QUEST_INFO = {
    "cha_guan_sui_rou": {"display_name": "��ݣ�����",
                            "description": "��Ҫ�ύһ�����⣬�����̵깺��",
                            "require": {"sui_rou": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_cu_bu": {"display_name": "��ݣ��ֲ�",
                            "description": "��Ҫ�ύһ�ݴֲ��������̵깺��",
                            "require": {"cu_bu": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_gan_cao": {"display_name": "��ݣ��ʲ�",
                            "description": "��Ҫ�ύһ�ݸʲݣ������̵깺��",
                            "require": {"gan_cao": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_hong_tong": {"display_name": "��ݣ���ͭ",
                            "description": "��Ҫ�ύһ�ݺ�ͭ�������̵깺��",
                            "require": {"hong_tong": 1},
                            "reward": {"money": 50, "banggong": 500}},
    "cha_guan_hun_hun": {"display_name": "��ݣ�ץ�����",
                            "description": "ץ�����������ʹ��ָ�� ץ�����",
                            "require": {"hun_hun_zheng_ming": 3},
                            "reward": {"money": 50, "banggong": 500}}
}

NPC_LIST = {
    "hun_hun": {
        "display_name": "�ܳ�",
        "equipment": {'weapon': {"display_name": "����", 'pvp': 0, 'pve': 10},
                        'armor': {"display_name": "�����", 'pvp': 0, 'pve': 50}},
        "reward": {"money": 50},
        "reward_chance": 0.5
    },
    'xiong_chi': {
        "display_name": "�ܳ�",
        "equipment": {'weapon': {"display_name": "�ܳ�ȭ��", 'pvp': 0, 'pve': 100},
                        'armor': {"display_name": "�ܳ���", 'pvp': 0, 'pve': 500}},
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
        "display_name": "���ķ�",
        "equipment": {'weapon': {"display_name": "�����ķ�ǹ", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "���ķ���", 'pvp': 0, 'pve': 1500}},
        "reward": {
            "money": 100,
            "banggong": 5000,
        },
        "buff": [
            {
                "display_name": "�˼���",
                "description": "������������+50%",
                "weapon": 1.5,
                "chance": 0.1,
            },
            {
                "display_name": "�˼ҽ�",
                "description": "������������+20%",
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
        "display_name": "������",
        "equipment": {'weapon': {"display_name": "����������", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "��������", 'pvp': 0, 'pve': 3000}},
        "reward": {
            "money": 200,
            "banggong": 10000,
        },
        "buff": [
            {
                "display_name": "ľ���󹥻�",
                "description": "������������+50%",
                "weapon": 1.5,
                "chance": 0.1,
            }
        ],
        "debuff": [
            {
                "display_name": "���������",
                "description": "�з���������-50%",
                "weapon": 0.5,
                "chance": 0.2,
            },
            {
                "display_name": "���������",
                "description": "�з���������-20%",
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
        "display_name": "������",
        "equipment": {'weapon': {"display_name": "��������", 'pvp': 0, 'pve': 100},
                        'armor': {"display_name": "��������", 'pvp': 0, 'pve': 1000}},
        "reward": {
            "money": 50,
            "banggong": 2000,
        },
        "buff": [
            {
                "display_name": "��������",
                "description": "ÿ���ܵ�����ʱ������������+10%�������ѵ�{0}�㣬���{1}��",
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
        "display_name": "ƽ��ָ",
        "equipment": {'weapon': {"display_name": "ƽ��ָ��", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "ƽ��ָ��", 'pvp': 0, 'pve': 3000}},
        "reward": {
            "money": 100,
            "banggong": 5000,
        },
        "debuff": [
            {
                "display_name": "��Һ����",
                "description": "�Է�����-100%",
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
        "display_name": "˾ͽһһ",
        "equipment": {'weapon': {"display_name": "˾ͽһһ��", 'pvp': 0, 'pve': 300},
                        'armor': {"display_name": "˾ͽһһ��", 'pvp': 0, 'pve': 5000}},
        "reward": {
            "money": 200,
            "banggong": 10000,
        },
        "buff": [
            {
                "display_name": "������ɨ",
                "description": "������������+50%",
                "weapon": 1.5,
                "chance": 0.2,
            }
        ],
        "debuff": [
            {
                "display_name": "������Ϣ",
                "description": "�з���Ҫ���Ķ���1�ι�������",
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
        "display_name": "���",
        "equipment": {'weapon': {"display_name": "��Ƚ�", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "�����", 'pvp': 0, 'pve': 2000}},
        "reward": {
            "money": 50,
            "banggong": 2000,
        },
        "buff": [
            {
                "display_name": "�������",
                "description": "�����Ѫ50��������Ǯ+10",
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
        "display_name": "����ֱ",
        "equipment": {'weapon': {"display_name": "����ֱ��", 'pvp': 0, 'pve': 300},
                        'armor': {"display_name": "����ֱ��", 'pvp': 0, 'pve': 5000}},
        "reward": {
            "money": 100,
            "banggong": 5000,
        },
        "buff": [
            {
                "display_name": "���ǳ�",
                "description": "ÿ���ܵ�����ʱ������������+20%�������ѵ�{0}�㣬���{1}��",
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
        "display_name": "��ӰС����",
        "equipment": {'weapon': {"display_name": "��ӰС���ɽ�", 'pvp': 0, 'pve': 400},
                        'armor': {"display_name": "��ӰС������", 'pvp': 0, 'pve': 8000}},
        "reward": {
            "money": 200,
            "banggong": 10000,
        },
        "buff": [
            {
                "display_name": "һ��",
                "description": "������������+20%",
                "weapon": 1.2,
                "chance": 0.4,
            }
        ],
        "debuff": [
            {
                "display_name": "�桤���顤һ��",
                "description": "�з���Ҫ���Ķ���1�ι�������",
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
    'hong_fu_qi_tian': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ���˵�ͷ��ǩ��ʱ��ö��⽱����",
                        "chance": 0.1,
                        "cooldown": 0,
                        "reward": {"money": DALIY_MONEY_REWARD, "weiwang": DALIY_REWARD_MIN, "banggong": DALIY_REWARD_MIN}},
    'luan_shi_wu_ji': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ���ݾ��޾��ף�������䴥�������������輧������Ƕ�������ϡ����������Ӱ���ң�",
                        "chance": 0.01,
                        "cooldown": 1 * 60 * 60,
                        "reward": {"money": 200, "energy": 100}},
    'hu_xiao_shan_lin': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ����ԡѪ��ս��������䴥����������Хɽ�֡�������νʮ��ĥһ������©���â��ֻ�����ʳ���ն������­��",
                        "chance": 0.05,
                        "cooldown": 2 * 60 * 60,
                        "reward": {"weiwang": 5000}},
    'hu_you_cang_sheng': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ���ı������ˣ�������䴥�����������Ӳ���������������ϵ��һ�ģ��˷��ص��ܷ�һ�絣�����乲�㣡",
                        "chance": 0.05,
                        "cooldown": 2 * 60 * 60,
                        "reward": {"weiwang": 5000}},
    'fu_yao_jiu_tian': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ�Ṧ������������������ҡ���졿������������ǧ���ҡ�쳾��",
                        "chance": 0.01,
                        "cooldown": 1 * 60 * 60,
                        "reward": {"money": 200, "energy": 100}},
    'cha_guan_qi_yuan': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ���ڲ��������������䴥�������������Ե�������ǣ�߳�彭�����������˹˻������������ȴ�������Ƿǣ�",
                        "chance": 0.05,
                        "cooldown": 2 * 60 * 60,
                        "require": {'money': 10000},
                        "reward": {"money": 1000, "banggong": 5000}},
    'qing_feng_bu_wang': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ��������������������䴥����������粶������",
                        "chance": 0.05,
                        "cooldown": 0,
                        "reward": {"money": 500, "weiwang": 5000}},
    'san_shan_si_hai': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ�������飬������䴥����������ɽ�ĺ��������ǣ�������ɽ���ĺ����о����������",
                        "chance": 0.01,
                        "cooldown": 2 * 60 * 60,
                        "reward": {"money": 1000}},
    'yin_yang_liang_jie': {"description": "��������ɱ���[CQ:at,qq={0}]��ʿ��Ե��ǳ�������������������硿����ǧ����Ե�������������������������������",
                        "chance": 0.05,
                        "cooldown": 24 * 60 * 60,
                        "require": {"pvp_gear_point": 3000, "pve_gear_point": 3000},
                        "reward": {"money": 500, "weiwang": 5000}},
}

DUNGEON_LIST = {
    'san_cai_zhen': {
        "display_name": "������",
        "max_pve_reward_gain": 12000,
        "boss": ['xiong_chi', 'deng_wen_feng', 'shang_zhong_yong'],
        "reward": {
            "banggong": 1000
        }
    },
    'tian_gong_fang': {
        "display_name": "�칤��",
        "max_pve_reward_gain": 25000,
        "boss": ['fang_ji_chang', 'ping_san_zhi', 'si_tu_yi_yi'],
        "reward": {
            "banggong": 2000
        }
    },
    'kong_wu_feng': {
        "display_name": "�����",
        "max_pve_reward_gain": 40000,
        "boss": ['feng_du', 'wang_yan_zhi', 'gui_ying_xiao_ci_lang'],
        "reward": {
            "banggong": 3000
        }
    }
}

STAT_DISPLAY_NAME = {
    "weiwang": "����",
    "banggong": "�ﹱ",
    "money": "��Ǯ",
    "energy": "����"
}

CLASS_LIST = [
    '������',
    '���',
    '����',
    '����',
    '����',
    '��',
    '�ؽ�',
    '�嶾',
    '����',
    '����',
    'ؤ��',
    '����',
    '����',
    '�Ե�',
    '����'
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
            returnMsg += "\n{0}��{1}".format(STAT_DISPLAY_NAME[k], v)
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
        CQSDK.SendGroupMsg(fromGroup, "����������������[CQ:at,qq={0}] ��ʿ�� [CQ:at,qq={1}] ��ʿʹ���˴�˵�еġ����֮�ġ����Դ������������䰮Ľ֮�ģ���������Ϊ�ˣ��������Ϊ����Хɽ����Ϊ֤����������Ϊƾ���Ӵ�ɽ�߲�����־����������У����겻�����⣬��˪�������顣��Ȼǰ·������Ұ���ཫ̹Ȼ�޾��̽����С��������������벻��������������������ӣ���".format(fromQQ, toQQ))
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
        "�鿴", "�鿴װ��", "����",
        "ǩ��",
        "Ѻ��",
        "����Ե",
        "������Ӫ",
        "�˳���Ӫ",
        "ת����Ӫ",
        "���",
        "����",
        "ʹ��",
        "�̵�",
        "�ڱ�",
        "�鿴��Ӫ",
        "�鿴����",
        "����", "ץ��",
        "pveװ������", "pvpװ������", "��������", "��������", "��������", "��������", "��������", "���߸���",
        "���",
        "������", "ץ�����"]

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
                returnMsg = "[CQ:at,qq={0}] ע��ʧ�ܣ����Ѿ�ע����ˡ�".format(qq_account)
            else:
                self.equipment[qq_account_str] = {
                    'weapon': {"display_name": "������", 'pvp': 10, 'pve': 10},
                    'armor': {"display_name": "������", 'pvp': 100, 'pve': 100}
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
                returnMsg = "ע��ɹ���\n[CQ:at,qq={0}]\nע��ʱ�䣺{1}".format(qq_account, time.strftime('%Y-%m-%d', time.localtime(self.jx3_users[qq_account_str]["register_time"])))

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
                qiandao_status = "��ǩ��"
            else:
                qiandao_status = "δǩ��"

            returnMsg = "[CQ:at,qq={0}]\n��Ե:\t\t{1}\n����:\t\t{2}\n��Ӫ:\t\t{3}\n����:\t\t{4}\n�ﹱ:\t\t{5}\n��Ǯ:\t\t{6}G\nPVPװ��:\t{7}\nPVEװ��:\t{8}\n����:\t\t{9}\nǩ��״̬:\t{10}\nǩ������:\t{11}\n����:\t\t{12}\nע��ʱ��:\t{13}\n���շ���:\t{14}\n����:\t\t{15}".format(
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
                returnMsg = "[CQ:at,qq={0}]�����Ѿ�ǩ������!".format(qq_account)
            else:
                banggong_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)
                weiwang_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)
                self.jx3_users[qq_account_str]['weiwang'] += weiwang_reward
                self.jx3_users[qq_account_str]['banggong'] += banggong_reward
                self.jx3_users[qq_account_str]['qiandao_count'] += 1
                self.jx3_users[qq_account_str]['energy'] += DALIY_ENERGY_REWARD
                self.jx3_users[qq_account_str]['money'] += DALIY_MONEY_REWARD

                self.daliy_action_count[yday_str][qq_account_str]['qiandao'] = True
                returnMsg = "[CQ:at,qq={0}] ǩ���ɹ���ǩ������: ����+{1} �ﹱ+{2} ��Ǯ+{3} ����+{4}".format(
                                qq_account,
                                weiwang_reward,
                                banggong_reward,
                                DALIY_MONEY_REWARD,
                                DALIY_ENERGY_REWARD)

                faction_id = val['faction_id']
                if faction_id != 0 and 'faction' in self.daliy_action_count and self.daliy_action_count['faction'][FACTION_NAME_ID[faction_id]]['reward'] != 0:
                    reward = self.daliy_action_count['faction'][FACTION_NAME_ID[faction_id]]['reward']
                    self.jx3_users[qq_account_str]['weiwang'] += reward
                    returnMsg += "\n���������Ӫ����������+{0}".format(reward)
                
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
                                rank_msg = "\n�������������ɼ��� ������{0}����λ��{1}��������{2}��".format(v['score'], rank, i)
                                if i == 1:
                                    modifier = 2
                                    rank_msg += "��������������Ϊ��1�����2��������"
                                elif i >= 2 and i <= 3:
                                    modifier = 1.5
                                    rank_msg += "��������������Ϊ��{0}�����{1}��������".format(i, modifier)
                        

                        self.jx3_users[qq_account_str]['weiwang'] += int(jjc_weiwang_reward * modifier)
                        self.jx3_users[qq_account_str]['money'] += int(jjc_money_reward * modifier)
                        self.jjc_status['last_season_jjc_status'][str(self.jjc_status['season'] - 1)][qq_account_str]['reward_gain'] = True
                        returnMsg += "\n�������������������н���������+{0} ��Ǯ+{1}".format(jjc_weiwang_reward, jjc_money_reward)

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
                returnMsg = "[CQ:at,qq={0}] ��û��ע��Ŷ������ע���ٰ���Ե��".format(toQQ)
            else:
                fromQQ_stat = self.jx3_users[str(fromQQ)]
                toQQ_stat = self.jx3_users[str(toQQ)]

                if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in fromQQ_stat['bag'].keys():
                    returnMsg = "[CQ:at,qq={0}] ����Ե��Ҫ����1��{1}��\n�㲢û�д���Ʒ�����ȹ���".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
                else:
                    if str(fromQQ_stat['lover']) == str(toQQ):
                        returnMsg = "[CQ:at,qq={0}] �����Ѿ��󶨹�������������������".format(fromQQ)
                    elif fromQQ_stat['lover'] != 0:
                        returnMsg = "[CQ:at,qq={0}]  ��ʲô�أ���Ͳ���[CQ:at,qq={1}]������".format(fromQQ, fromQQ_stat['lover'])
                    elif toQQ_stat['lover'] != 0:
                        returnMsg = "[CQ:at,qq={0}] �˼��Ѿ�����Ե������������818��".format(fromQQ)
                    elif toQQ in self.lover_pending and self.lover_pending[str(toQQ)] != fromQQ:
                        returnMsg = "[CQ:at,qq={0}] �Ѿ�������[CQ:at,qq={1}]����Ե�������ǲ����ٿ���һ�£�".format(fromQQ, toQQ)
                    else:
                        pendingList = [k for k, v in self.lover_pending.items() if v == fromQQ]
                        for p in pendingList:
                            self.lover_pending.pop(p)
                        self.lover_pending[str(toQQ)] = fromQQ
                        returnMsg = "[CQ:at,qq={1}]\n[CQ:at,qq={0}] ϣ���������Ե�������� ͬ�� ���� �ܾ���".format(fromQQ, toQQ)

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
                    returnMsg = "[CQ:at,qq={1}] ��Ȼ�˼�ͬ���˵����㲢û��1��{1}��".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
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

                    returnMsg = "[CQ:at,qq={0}] �� [CQ:at,qq={1}]��ϲ���ռ�����ɣ���Ե��ޡ�ʫӽ���£��Ÿ���ֺ����Ҷ����������鿪����֮����ͬ��ͬ�£������˼ҡ��ྴ�������г��ˮ֮�����������ϣ�����ԧ��֮��".format(fromQQ, toQQ)

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
                returnMsg = "�仨���⣬��ˮ���飬[CQ:at,qq={1}] ����� [CQ:at,qq={0}]��".format(fromQQ, toQQ)

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
                returnMsg = "[CQ:at,qq={0}] ������Ӫ�޷�Ѻ�ڡ�".format(qq_account)
            elif val['energy'] < YA_BIAO_ENERGY_REQUIRED:
                returnMsg = "[CQ:at,qq={0}] �������㣡�޷�Ѻ�ڡ�".format(qq_account)
            elif qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
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

                    returnMsg = "[CQ:at,qq={0}] Ѻ�ڳɹ�������-{1} ����+{2} ��Ǯ+{3}".format(qq_account, YA_BIAO_ENERGY_REQUIRED, reward, DALIY_YA_BIAO_MONEY_REWARD)
                else:
                    returnMsg = "[CQ:at,qq={0}] һ�����Ѻ��{1}�Ρ����Ѿ�Ѻ��{1}���������������ɡ�".format(qq_account, MAX_DALIY_YA_BIAO_COUNT)

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
                itemMsg = "\n�տ���Ҳ"
            else:
                itemMsg = ""
                for k, v in bag.items():
                    itemMsg += "\n{0} x {1}".format(get_item_display_name(k), v)
            returnMsg = "[CQ:at,qq={0}] �ı�����".format(qq_account) + itemMsg

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
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ������� {1}��".format(qq_account, faction_str)
                elif qq_stat['faction_id'] != 0:
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ������� {1}��{2} ���������������롣".format(qq_account, qq_faction_str, faction_str)
                elif qq_stat['faction_join_time'] != None and time.time() - qq_stat['faction_join_time'] < FACTION_REJOIN_CD_SECS:
                    time_val = calculateRemainingTime(FACTION_REJOIN_CD_SECS, qq_stat['faction_join_time'])
                    returnMsg = "[CQ:at,qq={0}] ���ڲ���ǰ���˳���Ӫ������Ҫ�ȴ�{1}Сʱ{2}��{3}��֮��������¼��롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                else:
                    self.jx3_users[qq_account_str]['faction_id'] = FACTION_DISPLAY_NAME.index(faction_str)
                    self.jx3_users[qq_account_str]['faction_join_time'] = time.time()
                    returnMsg = "[CQ:at,qq={0}] �ɹ����� {1}��".format(qq_account, faction_str)

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
                returnMsg = "[CQ:at,qq={0}] �㲢û�м����κ���Ӫ��".format(qq_account)
            else:
                pre_faction_id = qq_stat['faction_id']
                self.jx3_users[qq_account_str]['faction_id'] = 0
                self.jx3_users[qq_account_str]['faction_join_time'] = time.time()
                if FACTION_QUIT_EMPTY_WEIWANG:
                    self.jx3_users[qq_account_str]['weiwang'] = 0
                returnMsg = "[CQ:at,qq={0}] �˳��˽��������������� {1}".format(qq_account, get_faction_display_name(pre_faction_id))

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
                returnMsg = "[CQ:at,qq={0}] �㲢û�м����κ���Ӫ��".format(qq_account)
            elif qq_stat['weiwang'] < FACTION_TRANSFER_WEIWANG_COST:
                returnMsg = "[CQ:at,qq={0}] ת����Ӫ��Ҫ����{1}��������ǰ�������㡣".format(qq_account, FACTION_TRANSFER_WEIWANG_COST)
            elif qq_stat['faction_join_time'] != None and time.time() - qq_stat['faction_join_time'] < FACTION_REJOIN_CD_SECS:
                remain_secs = int(math.floor(FACTION_REJOIN_CD_SECS - (time.time() - qq_stat['faction_join_time'])))
                hours = remain_secs // 3600
                mins = (remain_secs - hours * 3600) // 60
                secs = remain_secs - hours * 3600 - mins * 60
                returnMsg = "[CQ:at,qq={0}] ���ڲ���ǰ�Ÿ�����Ӫ������Ҫ�ȴ�{1}Сʱ{2}��{3}��֮����ܸ��ġ�".format(qq_account, hours, mins, secs)
            else:
                pre_faction_id = qq_stat['faction_id']
                new_faction_id = 1 if pre_faction_id == 2 else 2
                self.jx3_users[qq_account_str]['faction_id'] = new_faction_id
                self.jx3_users[qq_account_str]['faction_join_time'] = time.time()
                returnMsg = "[CQ:at,qq={0}] ͨ�����½��ף�������{1}�������ɹ��������� {2}�������� {3}��".format(qq_account, FACTION_TRANSFER_WEIWANG_COST, get_faction_display_name(pre_faction_id), get_faction_display_name(new_faction_id))

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
                returnMsg = "[CQ:at,qq={0}] �Է���δע�ᣬ�޷���١�".format(fromQQ)
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
                    returnMsg = "[CQ:at,qq={0}] ������Ӫ�޷���٣����ȼ�����Ӫ��".format(fromQQ)
                elif toQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] �Է���������Ӫ���޷���١�".format(fromQQ)
                elif fromQQ_stat['faction_id'] == toQQ_stat['faction_id'] and ROB_SAME_FACTION_PROTECTION:
                    returnMsg = "[CQ:at,qq={0}] ͬ��Ӫ�޷���٣�".format(fromQQ)
                elif toQQ_str in self.rob_protect and ROB_PROTECT_COUNT != 0 and self.rob_protect[toQQ_str]['count'] >= ROB_PROTECT_COUNT and (time.time() - self.rob_protect[toQQ_str]['rob_time']) <= ROB_PROTECT_DURATION:
                    time_val = calculateRemainingTime(ROB_PROTECT_DURATION, self.rob_protect[toQQ_str]['rob_time'])
                    returnMsg = "[CQ:at,qq={0}] �Է���������̫��������Ѿ��ܵ�����֮���ӡ�\nʣ��ʱ�䣺{1}Сʱ{2}��{3}��".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                elif fromQQ_str in self.jail_list and time.time() - self.jail_list[fromQQ_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[fromQQ_str])
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                elif toQQ_str in self.jail_list and time.time() - self.jail_list[toQQ_str] < JAIL_DURATION:
                    returnMsg = "[CQ:at,qq={0}] �Է��ڼ���������أ�������Ҫ������".format(fromQQ)
                elif fromQQ_stat['energy'] < ROB_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] �������㣡�޷���١�".format(fromQQ)
                elif self.daliy_action_count[yday_str][fromQQ_str]['rob']['last_rob_time'] != None and time.time() - self.daliy_action_count[yday_str][fromQQ_str]['rob']['last_rob_time'] < ROB_LOSE_COOLDOWN:
                    time_val = calculateRemainingTime(ROB_LOSE_COOLDOWN, self.daliy_action_count[yday_str][fromQQ_str]['rob']['last_rob_time'])
                    returnMsg = "[CQ:at,qq={0}] �㻹��Ҫ�ָ�{1}Сʱ{2}��{3}�룬�޷���١�".format(
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

                        returnMsg = "��ٳɹ����ɹ��ʣ�{0}%\n[CQ:at,qq={1}] ��Ұ������ [CQ:at,qq={2}]\n{3} ����+{4} ��Ǯ+{5} ����-{6}\n{7} ����-{8} ��Ǯ-{9}".format(
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

                        returnMsg = "���ʧ�ܣ��ɹ��ʣ�{0}%\n[CQ:at,qq={1}] ��Ұ���� [CQ:at,qq={2}] ʱ����ɱ����Ҫ��Ϣ{3}Сʱ{4}��{5}�롣����-{6}".format(
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
                    returnMsg = "[CQ:at,qq={0}] {1} ���ɹ���".format(qq_account, item_display_name)
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
                        returnMsg = "[CQ:at,qq={0}] ����ɹ���\n{1}+{2}".format(qq_account, item_display_name, item_amount)
                        for k, v in cost_list.items():
                            if k in qq_stat:
                                self.jx3_users[qq_account_str][k] -= v * item_amount
                                returnMsg += "\n{0}-{1}".format(STAT_DISPLAY_NAME[k], v * item_amount)
                    else:
                        returnMsg = "[CQ:at,qq={0}] ����ʧ�ܣ�\n����1�� {1} ��Ҫ:{2}".format(qq_account, item_display_name, print_cost(cost_list))

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
                    returnMsg = "[CQ:at,qq={0}] {1} ����ʹ�á�".format(qq_account, item_display_name)
                else:

                    qq_account_str = str(qq_account)
                    qq_stat = self.jx3_users[qq_account_str]

                    effect_list = item['effect']

                    if item['name'] not in self.jx3_users[qq_account_str]['bag']:
                        returnMsg = "[CQ:at,qq={0}] �㲢û�� {1}���޷�ʹ�á�".format(qq_account, item_display_name)
                    elif self.jx3_users[qq_account_str]['bag'][item['name']] < item_amount:
                        returnMsg = "[CQ:at,qq={0}] �㲢û����ô�� {1}��".format(qq_account, item_display_name)
                    else:
                        item_used = True
                        returnMsg = "[CQ:at,qq={0}] ʹ�� {1} x {2}".format(qq_account, item_display_name, item_amount)
                        for k, v in effect_list.items():
                            if k in qq_stat:
                                self.jx3_users[qq_account_str][k] += v * item_amount
                                returnMsg += "\n{0}+{1}".format(STAT_DISPLAY_NAME[k], v * item_amount)
                            elif k == 'pve_weapon':
                                self.equipment[qq_account_str]['weapon']['pve'] += v * item_amount
                                returnMsg += "\n����pve�˺�+{0}".format(v * item_amount)
                                self._update_gear_point(qq_account_str)
                            elif k == 'pvp_weapon':
                                self.equipment[qq_account_str]['weapon']['pvp'] += v * item_amount
                                returnMsg += "\n����pvp�˺�+{0}".format(v * item_amount)
                                self._update_gear_point(qq_account_str)
                            elif k == 'pve_armor':
                                self.equipment[qq_account_str]['armor']['pve'] += v * item_amount
                                returnMsg += "\n����pveѪ��+{0}".format(v * item_amount)
                                self._update_gear_point(qq_account_str)
                            elif k == 'pvp_armor':
                                self.equipment[qq_account_str]['armor']['pvp'] += v * item_amount
                                returnMsg += "\n����pvpѪ��+{0}".format(v * item_amount)
                                self._update_gear_point(qq_account_str)
                            elif k == 'attack_count':
                                if qq_account_str in self.group_info:
                                    leader = qq_account_str
                                else:
                                    leader = self._get_leader_by_member(qq_account_str)
                                
                                if leader != "" and leader in self.dungeon_status:
                                    self.dungeon_status[leader]['attack_count'][qq_account_str]['available_attack'] += v * item_amount
                                    returnMsg += "\n��������+{0}".format(v * item_amount)
                                else:
                                    returnMsg = "[CQ:at,qq={0}] �㲻�ڸ�����޷�ʹ�á�".format(qq_account)
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
            returnMsg = "[CQ:at,qq={0}]\n---------�ӻ���---------\n--�����ʵ��ͯ������--".format(qq_account)
            for item in ITEM_LIST:
                if 'cost' in item:
                    returnMsg += "\n*��{0}��".format(item['display_name'])
                    for k, v in item['cost'].items():
                        returnMsg += "----{0}��{1}".format(STAT_DISPLAY_NAME[k], v)
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
                returnMsg = "[CQ:at,qq={0}] �������㣡�޷��ڱ���".format(qq_account)
            elif qq_account_str in self.jail_list and time.time() - self.jail_list[qq_account_str] < JAIL_DURATION:
                    time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[qq_account_str])
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
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
                        returnMsg = "[CQ:at,qq={0}] ������ո����걦�أ�������Щƣ�������{1}��{2}��֮�����ڡ�".format(
                                        qq_account,
                                        time_val['mins'],
                                        time_val['secs'])
                    else:
                        reward_item_name = get_wa_bao_reward()
                        self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['count'] += 1
                        self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['last_time'] = time.time()

                        self.jx3_users[qq_account_str]['energy'] -= WA_BAO_ENERGY_REQUIRED

                        returnMsg = '[CQ:at,qq={0}]\n�����ڱ�������{1}/{2}'.format(
                                            qq_account,
                                            self.daliy_action_count[yday_str][qq_account_str]["wa_bao"]['count'],
                                            MAX_DALIY_WA_BAO_COUNT)

                        if reward_item_name == "":
                            returnMsg += "\n��һ������ȥ��ʲôҲû�ڵ���"
                        else:
                            if reward_item_name not in self.jx3_users[qq_account_str]['bag']:
                                    self.jx3_users[qq_account_str]['bag'][reward_item_name] = 0
                            self.jx3_users[qq_account_str]['bag'][reward_item_name] += 1
                            returnMsg += "\n��һ������ȥ���ڵ���һ�����صĶ���: {0}+1 ����-{1}".format(
                                            get_item_display_name(reward_item_name),
                                            WA_BAO_ENERGY_REQUIRED)
                else:
                    returnMsg = "[CQ:at,qq={0}] һ������ڱ�{1}�Ρ����Ѿ�����{1}������������Ϣ��Ϣ�ɡ�".format(qq_account, MAX_DALIY_WA_BAO_COUNT)

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
                    returnMsg = "[CQ:at,qq={0}] �㲢û�� {1}���޷�ʹ�á�".format(fromQQ, item_display_name)
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

            returnMsg = "[CQ:at,qq={0}] װ����Ϣ��\n������{1}\n----pve������{2}----pvp������{3}\n���ߣ�{4}\n----pveѪ����{5}----pvpѪ����{6}".format(
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
            returnMsg = "[CQ:at,qq={0}] �������Ѹ���Ϊ {1}".format(qq_account, name)

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
            returnMsg = "[CQ:at,qq={0}] �ķ����Ѹ���Ϊ {1}".format(qq_account, name)

            self.writeToJsonFile()
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.load_data()

        self.mutex.release()
        return returnMsg

    def get_faction_info(self):
        returnMsg = "��Ⱥ��Ӫ��Ϣ\n"
        self.mutex.acquire()

        try:
            yday = self._reset_daliy_count()
            yday_str = str(yday)
            retval = self._get_faction_count()
            returnMsg += "��ȺΪ{0}Ⱥ\n���˹�����:\t{1} ������Ӫ������{4}\n����������:\t{2} ������Ӫ������{5}\n��������:\t{3}".format(
                        "����ǿ��" if retval[2] > retval[1] else "����ǿ��" if retval[1] > retval[2] else "�ƾ�����",
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
        returnMsg = "��Ⱥpveװ�����а�"
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
        returnMsg = "��Ⱥpvpװ�����а�"
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
        returnMsg = "��Ⱥ�������а�"
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
        returnMsg = "��Ⱥ�����������а�"
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
        returnMsg = "��Ⱥ�������а�"
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
        returnMsg = "��Ⱥ�������а�"
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
                returnMsg = "[CQ:at,qq={0}] �Է���δע�ᣬ�޷����͡�".format(fromQQ)
            else:
                fromQQ_str = str(fromQQ)
                toQQ_str = str(toQQ)

                yday = self._reset_daliy_count(toQQ_str)
                yday_str = str(yday)

                if self.jx3_users[fromQQ_str]['money'] < WANTED_MONEY_REWARD:
                    returnMsg = "[CQ:at,qq={0}] ��Ǯ���㣬�޷����͡�".format(fromQQ)
                elif self.daliy_action_count[yday_str][toQQ_str]['jailed'] >= JAIL_TIMES_PROTECTION:
                    returnMsg = "[CQ:at,qq={0}] �Է������Ѿ���ץ��ȥ{1}���ˣ��޷����͡�".format(fromQQ, JAIL_TIMES_PROTECTION)
                else:
                    self.jx3_users[fromQQ_str]['money'] -= WANTED_MONEY_REWARD

                    import CQSDK
                    CQSDK.SendGroupMsg(self.qq_group, "[CQ:at,qq={0}] ���ͳɹ���\n��Ǯ-{1}".format(fromQQ, WANTED_MONEY_REWARD))

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

        return "������Թһ���壬Ω��Ⱥ����Ԯ�֡�������Ը��{0}��� {1} �������ͣ����ͽ��Ѵ�{2}������ʿ��������".format(
                                money_amount,
                                getGroupNickName(self.qq_group, int(toQQ_str)),
                                self.wanted_list[toQQ_str]['reward'])

    def get_wanted_list(self):
        returnMsg = "��Ⱥ���Ͱ�"
        msg_list = ""
        self.mutex.acquire()

        try:
            rank_list = sorted(self.wanted_list.items(), lambda x, y: cmp(x[1]['reward'], y[1]['reward']), reverse=True)
            list_len = len(rank_list)
            index = 1
            for k, v in rank_list:
                if time.time() - self.wanted_list[k]['wanted_time'] < WANTED_DURATION:
                    time_val = calculateRemainingTime(WANTED_DURATION, self.wanted_list[k]['wanted_time'])
                    msg_list += '\n{0}. {1} {2}�� {3}Сʱ{4}��{5}��'.format(
                                    index,
                                    getGroupNickName(self.qq_group, int(k)),
                                    v['reward'],
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                    index += 1

            if msg_list == "":
                msg_list = "\n��������"

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
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif toQQ_str in self.jail_list and time.time() - self.jail_list[toQQ_str] < JAIL_DURATION:
                    returnMsg = "[CQ:at,qq={0}] �Է��ڼ���������أ�������Ҫ������".format(fromQQ)
            elif toQQ_str in self.wanted_list and time.time() - self.wanted_list[toQQ_str]['wanted_time'] < WANTED_DURATION:
                if 'failed_try' in self.wanted_list[toQQ_str] and fromQQ_str in self.wanted_list[toQQ_str]['failed_try'] and time.time() - self.wanted_list[toQQ_str]['failed_try'][fromQQ_str] < WANTED_COOLDOWN:
                    time_val = calculateRemainingTime(WANTED_COOLDOWN, self.wanted_list[toQQ_str]['failed_try'][fromQQ_str])
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ����Թ�ץ���ˣ��κμ��ղ��ѡ������{1}Сʱ{2}��{3}���������ս��".format(
                                    fromQQ,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
                elif self.jx3_users[fromQQ_str]['energy'] < WANTED_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] �������㣡��Ҫ����{1}������".format(fromQQ, WANTED_ENERGY_COST)
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

                        returnMsg = "{0}��ʱ���ڱ�{1}�ɹ�ץ�������ͽ�����ɹ��ʣ�{2}%\n[CQ:at,qq={3}] ��ã�\n��Ǯ+{4}��\n����-{5}".format(
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
                        returnMsg = "[CQ:at,qq={0}] ץ��ʧ�ܣ��ɹ��ʣ�{1}%\n����-{2}".format(
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
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif len(daliy_stat['complete_quest']) >= len(CHA_GUAN_QUEST_INFO):
                returnMsg = "[CQ:at,qq={0}] ���Ѿ������{1}����������������������ɡ�".format(qq_account, len(CHA_GUAN_QUEST_INFO))
            elif self.jx3_users[qq_account_str]['energy'] < CHA_GUAN_ENERGY_COST:
                returnMsg = "[CQ:at,qq={0}] �������㣡��Ҫ����{1}������".format(qq_account, CHA_GUAN_ENERGY_COST)
            elif daliy_stat['current_quest'] != "":
                returnMsg = "[CQ:at,qq={0}] ���Ѿ�����һ����������\n��ǰ����{1}".format(qq_account, CHA_GUAN_QUEST_INFO[daliy_stat['current_quest']]['display_name'])
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
                requireMsg += "\n������{0}".format(CHA_GUAN_ENERGY_COST)

                returnMsg = "[CQ:at,qq={0}] �������({1}/{2})\n{3}\n{4}\n����:{5}\n������{6}".format(
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
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['current_quest'] != "":

                daliy_stat = self.daliy_action_count[yday_str][qq_account_str]['cha_guan']
                quest = CHA_GUAN_QUEST_INFO[daliy_stat['current_quest']]

                if self.jx3_users[qq_account_str]['energy'] < CHA_GUAN_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] �������㣡��Ҫ����{1}������".format(qq_account, CHA_GUAN_ENERGY_COST)
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

                        returnMsg = "[CQ:at,qq={0}] ���������ɣ�{1}/{2}\n����������Ʒ��{3}\n����-{4}\n��ý�����{5}".format(
                                        qq_account,
                                        len(self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['complete_quest']),
                                        len(CHA_GUAN_QUEST_INFO),
                                        itemMsg,
                                        CHA_GUAN_ENERGY_COST,
                                        rewardMsg)
                    else:
                        returnMsg = "[CQ:at,qq={0}] ������Ʒ���㣡".format(qq_account)

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
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif self.daliy_action_count[yday_str][qq_account_str]['cha_guan']['current_quest'] == "cha_guan_hun_hun":
                if 'hun_hun_zheng_ming' in self.jx3_users[qq_account_str]['bag'] and self.jx3_users[qq_account_str]['bag']['hun_hun_zheng_ming'] >= 3:
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ�ץ��̫����������Ϣһ�°ɡ�".format(qq_account_str)
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

                        returnMsg = "[CQ:at,qq={0}] ץ�����ɹ����ɹ��ʣ�{1}%\n��ý�����{2}".format(
                                        qq_account,
                                        int(math.floor(success_chance * 100)),
                                        rewardMsg)
                    else:
                        returnMsg = "[CQ:at,qq={0}] ץ��ʧ�ܣ��ɹ��ʣ�{1}%".format(
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

                            returnMsg = "{0}\n��ý�����{1}".format(qiyu['description'].format(qq_account_str), rewardMsg)

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
                returnMsg = "[CQ:at,qq={0}] �Է���δע�ᡣ".format(toQQ)
            else:
                yday = self._reset_daliy_count(toQQ_str)
                yday_str = str(yday)
                self._add_new_daliy_record(yday_str, fromQQ_str)

                fromQQ_stat = self.jx3_users[fromQQ_str]
                toQQ_stat = self.jx3_users[toQQ_str]

                if fromQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] ������Ӫ�޷��д裬���ȼ�����Ӫ��".format(fromQQ)
                elif toQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] �Է���������Ӫ���޷��д衣".format(fromQQ)
                elif fromQQ_stat['faction_id'] != toQQ_stat['faction_id'] and ROB_SAME_FACTION_PROTECTION:
                    returnMsg = "[CQ:at,qq={0}] ��ͬ��Ӫ�޷��д裡".format(fromQQ)
                elif fromQQ_str in self.jail_list and time.time() - self.jail_list[fromQQ_str] < JAIL_DURATION:
                        time_val = calculateRemainingTime(JAIL_DURATION, self.jail_list[fromQQ_str])
                        returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                        fromQQ,
                                        time_val['hours'],
                                        time_val['mins'],
                                        time_val['secs'])
                elif toQQ_str in self.jail_list and time.time() - self.jail_list[toQQ_str] < JAIL_DURATION:
                        returnMsg = "[CQ:at,qq={0}] �Է��ڼ���������أ�û�������д衣".format(fromQQ)
                elif self.jx3_users[fromQQ_str]['energy'] < PRACTISE_ENERGY_COST:
                    returnMsg = "[CQ:at,qq={0}] �������㣡��Ҫ����{1}������".format(fromQQ, PRACTISE_ENERGY_COST)
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

                    returnMsg = "[CQ:at,qq={0}]��[CQ:at,qq={1}]�������д衣{2} սʤ�� {3}���ɹ���{4}%��\n{5} ����+{6} {7}\n{8} ����+{9} {10}".format(
                                    fromQQ,
                                    toQQ,
                                    getGroupNickName(self.qq_group, int(winner)),
                                    getGroupNickName(self.qq_group, int(loser)),
                                    int(math.floor(success_chance * 100)),
                                    getGroupNickName(self.qq_group, int(winner)),
                                    winner_weiwang_gain,
                                    "����-{0}".format(energy_cost) if winner == fromQQ_str else "",
                                    getGroupNickName(self.qq_group, int(loser)),
                                    loser_weiwang_gain,
                                    "����-{0}".format(energy_cost) if loser == fromQQ_str else "")

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
                    returnMsg = "[CQ:at,qq={0}] ��ʵ�㣬�㻹Ҫ�ڼ������{1}Сʱ{2}��{3}�롣".format(
                                    qq_account,
                                    time_val['hours'],
                                    time_val['mins'],
                                    time_val['secs'])
            elif self.jx3_users[qq_account_str]['energy'] < JJC_ENERGY_COST:
                returnMsg = "[CQ:at,qq={0}] �������㣡��Ҫ����{1}������".format(qq_account, JJC_ENERGY_COST)
            elif self.jjc_season_status[qq_account_str]['last_time'] != None and time.time() - self.jjc_season_status[qq_account_str]['last_time'] < JJC_COOLDOWN:
                    time_val = calculateRemainingTime(JJC_COOLDOWN, self.jjc_season_status[qq_account_str]['last_time'])
                    returnMsg = "[CQ:at,qq={0}] ����Ź���������ˣ����{1}Сʱ{2}����{3}��������ɡ�".format(
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

                returnMsg = "[CQ:at,qq={0}] �������������λ��\n���������������{1} ��λ��{2}�Ρ�ƥ�䵽�Ķ����� {3}��������������{4} ��λ��{5}��".format(
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

                    double_msg = " (ÿ��{1}��˫�������ӳ��У�{0}/{1})".format(self.daliy_action_count[yday_str][qq_account_str]['jjc']['win'] + 1, DALIY_JJC_DOUBLE_REWARD_COUNT) if reward_modifier == 2 else ""

                    self.jjc_season_status[qq_account_str]['score'] += score_reward
                    self.jjc_season_status[qq_account_str]['last_time'] = time.time()

                    if self.jjc_season_status[random_person]['score'] < JJC_REWARD_RANK:
                        score_lost = 0

                    self.jjc_season_status[random_person]['score'] -= score_lost
                    self.jjc_season_status[qq_account_str]['win'] += 1
                    self.daliy_action_count[yday_str][qq_account_str]['jjc']['win'] += 1
                    self.jjc_season_status[random_person]['lose'] += 1

                    returnMsg = "[CQ:at,qq={0}] ս�������ʤ�����ɹ��ʣ�{1}%\n {2} ����+{3} ����+{4} ����-{5}{6}\n{7} ����-{8}".format(
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
                        returnMsg += "\n��λ���Ϊ��{0}".format(new_rank)
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

                    returnMsg = "[CQ:at,qq={0}] ս�������ʧ�ܣ��ɹ��ʣ�{1}%\n {2} ����-{3} ����-{4}��{5} ����+{6}".format(
                                    qq_account_str,
                                    int(math.floor(success_chance * 100)),
                                    getGroupNickName(self.qq_group, int(qq_account)),
                                    score_lost,
                                    JJC_ENERGY_COST,
                                    getGroupNickName(self.qq_group, int(random_person)),
                                    score_reward)

                    new_rank = self.jjc_season_status[qq_account_str]['score'] // 100
                    if  new_rank != rank:
                        returnMsg += "\n��λ���Ϊ��{0}".format(new_rank)

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
            returnMsg = "������������� ������{0} ������{1}".format(self.jjc_status['season'], self.jjc_status['day'])

            yday = self._reset_daliy_count()
            yday_str = str(yday)

            rank_list = sorted(self.jjc_season_status.items(), lambda x, y: cmp(x[1]['score'], y[1]['score']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['score'] != 0:
                    returnMsg += '\n{0}. {1} ������{2} ��λ��{3}'.format(
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

            returnMsg = "[CQ:at,qq={0}] ��{1}����������������{2} ��λ��{3} ʤ����{4}/{5} ʤ�ʣ�{6}%".format(
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
                returnMsg = "[CQ:at,qq={0}] ���Ѿ������������ˣ�".format(qq_account)
            elif class_display_name in CLASS_LIST:
                self.jx3_users[qq_account_str]['class_id'] = CLASS_LIST.index(class_display_name)
                returnMsg = "[CQ:at,qq={0}] ��������{1}��".format(qq_account, class_display_name)

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
                returnMsg = "[CQ:at,qq={0}] ��û����Ե�������á�".format(qq_account)
            else:
                lover = self.jx3_users[qq_account_str]['lover']
                love_time = time.time() - self.jx3_users[qq_account_str]['lover_time']
                self.jx3_users[qq_account_str]['lover_time'] = None
                self.jx3_users[qq_account_str]['lover'] = 0
                self.jx3_users[str(lover)]['lover_time'] = None
                self.jx3_user[str(lover)]['lover'] = 0
                returnMsg = "[CQ:at,qq={0}] ����ȥѰ���µ��ó̡�".format(qq_account)

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
                returnMsg = "[CQ:at,qq={0}] ���Ѿ�������һ�������ˣ�".format(qq_account)
            else:
                find_leader = self._get_leader_by_member(qq_account_str)
                if find_leader != "":
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ������� {1} �Ķ��飡".format(qq_account, getGroupNickName(self.qq_group, int(find_leader)))
                else:
                    self.group_info[qq_account_str] = {
                        'member_list': [],
                        'create_time': time.time()
                    }
                    returnMsg = "[CQ:at,qq={0}] ��������ɹ������ö������롾�������[CQ:at,qq={0}]��������顣\n���븱����˶����޷������룬��ȷ��������ȷ���ٽ��븱����".format(qq_account)

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
                returnMsg = "[CQ:at,qq={0}] ���Ѿ�������һ�����飬���ܼ��������˵Ķ��飬���롾�˳����顿�˳���ǰ���顣".format(qq_account)
            elif leader_str not in self.group_info:
                returnMsg = "[CQ:at,qq={0}] ���鲻���ڡ�".format(qq_account)
            elif leader_str in self.dungeon_status:
                returnMsg = "[CQ:at,qq={0}] {1} �Ķ������ڸ�����޷����롣".format(qq_account, getGroupNickName(self.qq_group, int(leader)))
            elif len(self.group_info[leader_str]['member_list']) >= MAX_GROUP_MEMBER:
                returnMsg = "[CQ:at,qq={0}] �����������޷����롣".format(qq_account)
            else:
                find_leader = self._get_leader_by_member(qq_account_str)
                if find_leader != "":
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ������� {1} �Ķ��飬���롾�˳����顿�˳���ǰ����".format(qq_account, getGroupNickName(self.qq_group, int(find_leader)))
                else:
                    self.group_info[leader_str]['member_list'].append(qq_account_str)
                    returnMsg = "[CQ:at,qq={0}] �ɹ����� {1} �Ķ��顣".format(qq_account, getGroupNickName(self.qq_group, int(leader)))

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
                returnMsg = "[CQ:at,qq={0}] ��û�м����κζ��顣".format(qq_account)
            else:
                returnMsg = "[CQ:at,qq={0}] ��ǰ������Ϣ��\n�ӳ���{1} pveװ�֣�{2}".format(
                    qq_account_str,
                    getGroupNickName(self.qq_group, int(leader)),
                    self.jx3_users[leader]['pve_gear_point'])
                if self.group_info[leader]['member_list'] != []:
                    for member in self.group_info[leader]['member_list']:
                        returnMsg += "\n{0} pveװ�֣�{1}".format(
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
                    returnMsg = "[CQ:at,qq={0}] �㲻���κζ����".format(qq_account)
                else:
                    self.group_info[leader]['member_list'].remove(qq_account_str)
                    returnMsg = "[CQ:at,qq={0}] ���뿪�� {1} �Ķ��顣".format(qq_account, getGroupNickName(self.qq_group, int(leader)))
            else:
                self.group_info.pop(qq_account_str)
                if qq_account_str in self.dungeon_status:
                    self.dungeon_status.pop(qq_account_str)
                returnMsg = "[CQ:at,qq={0}] ��Ķ����ɢ�ˡ�".format(qq_account)

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

            returnMsg = "[CQ:at,qq={0}] �����б�".format(qq_account)
            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if 'dungeon' not in self.daliy_action_count[yday_str][qq_account_str]:
                self.daliy_action_count[yday_str][qq_account_str]['dungeon'] = {}
            
            self._update_gear_point(qq_account_str)

            for k, v in DUNGEON_LIST.items():
                has_cd = k in self.daliy_action_count[yday_str][qq_account_str]['dungeon'] and self.daliy_action_count[yday_str][qq_account_str]['dungeon'][k] == True
                has_reward = self.jx3_users[qq_account_str]['pve_gear_point'] < v['max_pve_reward_gain']
                returnMsg += "\n{0} {1} {2}".format(v['display_name'], "�ѹ���" if has_cd else "�ɹ���", "��boss����" if has_reward else "��boss����")

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
                        returnMsg = "[CQ:at,qq={0}] ���봴��������ܽ��븱����".format(qq_account)
                    else:
                        returnMsg = "[CQ:at,qq={0}] �㲻�Ƕӳ����޷�ʹ�ô����".format(qq_account)
                elif qq_account_str in self.dungeon_status:
                    returnMsg = "[CQ:at,qq={0}] ���Ѿ��ڸ������ˡ�".format(qq_account)
                elif dungeon_id in self.daliy_action_count[yday_str][qq_account_str]['dungeon'] and self.daliy_action_count[yday_str][qq_account_str]['dungeon'][dungeon_id] == True:
                    returnMsg = "[CQ:at,qq={0}] ���д˸���cd���޷����롣".format(qq_account)
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
                        returnMsg = "[CQ:at,qq={0}] ��Ķ����д˸���cd���޷����롣".format(qq_account)
                    elif self.jx3_users[qq_account_str]['energy'] < DUNGEON_ENERGY_REQUIRED and qq_account_str not in pve_gear_point_too_high:
                        returnMsg = "[CQ:at,qq={0}] ����������㣬���븱����Ҫ�ķ�������{1}".format(qq_account, DUNGEON_ENERGY_REQUIRED)
                    elif has_energy and energy_msg != "":
                        returnMsg = "{0} �������㣬���븱����Ҫ�ķ�������{1}".format(energy_msg, DUNGEON_ENERGY_REQUIRED)
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
                            returnMsg += "������{0}pveװ��̫���������Ѿ����ܻ��boss�����ˣ����ɻ��ͨ�ؽ����Ҳ��������������ȷ����Ҫ�����Ļ������ٴ����� ���븱��{1}".format(pve_msg, DUNGEON_LIST[dungeon_id]['display_name'])
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
                            returnMsg = "[CQ:at,qq={0}] ���븱�� {1} �ɹ���{2}����-{3}".format(qq_account, dungeon_name, energy_msg, DUNGEON_ENERGY_REQUIRED)

                            import CQSDK
                            CQSDK.SendGroupMsg(self.qq_group, returnMsg)

                            boss = self.dungeon_status[leader]['boss_detail'][0]
                            returnMsg = "bossս��{0} (1/{1})\n������ÿλ��Ա���롾����boss����ʼս����".format(boss['display_name'], len(self.dungeon_status[qq_account_str]['boss_detail']))

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
                    returnMsg = "[CQ:at,qq={0}] ��û�й���������������Ҫ��{1}Сʱ{2}��{3}�롣".format(
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
                            buff_msg = "\n{0}ʹ����������{1}��{2}".format(current_boss['display_name'], modifier['display_name'], description)
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
                            debuff_msg = "\n{0}ʹ����������{1}��{2}".format(current_boss['display_name'], modifier['display_name'], modifier['description'])

                    battle_result = self._calculate_battle(qq_account_str, '', 'pve', custom_from_qq_equipment=qq_equipment, custom_to_qq_equipment=boss_equipment)

                    winner = battle_result['winner']
                    loser = battle_result['loser']
                    success_chance = battle_result['success_chance']

                    dungeon['attack_count'][qq_account_str]['total_attack_count'] += 1
                    

                    returnMsg = "[CQ:at,qq={0}] ���{1}�����˹�����ʣ�๥��������{2}/{3}".format(qq_account, current_boss['display_name'], dungeon['attack_count'][qq_account_str]['available_attack'] - 1, DUNGEON_MAX_ATTACK_COUNT) + buff_msg + debuff_msg

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

                        returnMsg += "\n�����ɹ����ɹ��ʣ�{0}%������˺���{1}��{2}Ѫ����{3}/{4}".format(
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
                                        item_reward_msg += "\n{0}��ö��⽱����{1} x 1 ���ʣ�{2}%".format(getGroupNickName(self.qq_group, int(leader)), get_item_display_name(k), int(v * 100))

                                for m in self.group_info[leader]['member_list']:
                                    if m not in dungeon['no_reward']:
                                        rand = random.uniform(0, 1)
                                        if rand <= v:
                                            if k not in self.jx3_users[m]['bag']:
                                                self.jx3_users[m]['bag'][k] = 0
                                            self.jx3_users[m]['bag'][k] += 1
                                            item_reward_msg += "\n{0}��ö��⽱����{1} x 1 ���ʣ�{2}%".format(getGroupNickName(self.qq_group, int(m)), get_item_display_name(k), int(v * 100))

                            member_list = copy.deepcopy(self.group_info[leader]['member_list'])
                            member_list.append(leader)
                            for m in list(set(member_list) - set(dungeon['no_reward'])):
                                reward_member += "[CQ:at,qq={0}]".format(m)

                            if reward_member != "":
                                reward_msg = "{0}��ý���{1}".format(reward_member, reward_msg)
                            else:
                                reward_msg = ""

                            mvp = sorted(dungeon['attack_count'].items(), lambda x, y: cmp(x[1]['damage'], y[1]['damage']), reverse=True)[0]
                            returnMsg = "{0}�ɹ���������{1}{2}\nmvp��{3} �˺���{4} ����������{5}/{6}".format(
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
                                returnMsg = "bossս��{0} ({1}/{2})\n������ÿλ��Ա���롾����boss����ʼս����".format(
                                    next_boss['display_name'],
                                    len(dungeon['boss']) - len(dungeon['boss_detail']) + 1,
                                    len(dungeon['boss']))
                            else:
                                returnMsg = "�����ѽ�������ϲͨ��{0}��ȫԱ���ͨ�ؽ�����".format(dungeon['display_name'])
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
                                returnMsg = "�����ѽ�ɢ��"
                                self.group_info.pop(leader)
                                self.dungeon_status.pop(leader)
                    else:
                        dungeon['attack_count'][qq_account_str]['available_attack'] -= 1
                        returnMsg += "\n����ʧ�ܣ��ɹ��ʣ�{0}%��{1}Ѫ����{2}/{3}".format(
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
                        damage_msg += '\n{0}. {1} �˺���{2} ������{3}/{4}'.format(
                            i + 1,
                            getGroupNickName(self.qq_group, int(rank_list[i][0])),
                            rank_list[i][1]['damage'],
                            dungeon['attack_count'][rank_list[i][0]]['success_attack_count'],
                            dungeon['attack_count'][rank_list[i][0]]['total_attack_count'])
                    else:
                        break
                returnMsg = "[CQ:at,qq={0}] ��ǰ������{1} ��ǰboss��{2} {3}/{4}\nѪ����{5}/{6} pveװ�֣�{7}\n�˺����а�{8}".format(
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
