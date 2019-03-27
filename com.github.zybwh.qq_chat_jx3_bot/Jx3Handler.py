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
    filename    = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'CQHanlder.log'),
    filemode    = 'w+'
)

import sqlite3
import json
import copy
import random

from threading import Lock

DATABASE_PATH = os.path.join('data', 'app', 'com.github.qq_jx3_chat_bot')

DATA_JSON_FILE = os.path.join(DATABASE_PATH, 'jx3.json')
DATA_JSON_FILE_OLD = os.path.join(DATABASE_PATH, 'jx3.json.old')
DATA_JSON_FILE_OLD_2 = os.path.join(DATABASE_PATH, 'jx3.json.old2')

LOVE_ITEM_REQUIRED = "zhen_cheng_zhi_xin"

DALIY_REFRESH_OFFSET = 7 * 60 * 60
DALIY_COUNT_SAVE_DAY = 3
DALIY_REWARD_MIN = 1000
DALIY_REWARD_MAX = 3000
DALIY_ENERGY_REWARD = 500
DALIY_MONEY_REWARD = 100

DALIY_MAX_SPEECH_ENERGY_GAIN = 500
SPEECH_ENERGY_GAIN = 5

YA_BIAO_ENERGY_REQUIRED = 100
MAX_DALIY_YA_BIAO_COUNT = 3
DALIY_YA_BIAO_REWARD_MIN = 4000
DALIY_YA_BIAO_REWARD_MAX = 6000
DALIY_YA_BIAO_MONEY_REWARD = 50

WA_BAO_ENERGY_REQUIRED = 50
MAX_DALIY_WA_BAO_COUNT = 10
WA_BAO_COOLDOWN = 10 * 60
WA_BAO_RARE_FACTOR = 2

MAX_DALIY_CHA_GUAN_COUNT = 5
CHA_GUAN_ENERGY_COST = 30

FACTION_REJOIN_CD_SECS = 24 * 60 * 60
FACTION_TRANSFER_WEIWANG_COST = 20000
NO_FACTION_ALLOW_YA_BIAO = False

ROB_ENERGY_COST = 50
ROB_PROTECT_COUNT = 2
ROB_PROTECT_DURATION = 60 * 60

WANTED_MONEY_REWARD = 1000
WANTED_DURATION = 24 * 60 * 60
WANTED_COOLDOWN = 10 * 60
WANTED_ENERGY_COST = 50

JAIL_DURATION = 1 * 60 * 60
JAIL_TIMES_PROTECTION = 2

FACTION_DISPLAY_NAME = ['中立', '恶人谷', '浩气盟']

ITEM_LIST = [
    {"name": "zhen_cheng_zhi_xin", "display_name": "真橙之心", "rank": 2, "cost": {"money": 999}},
    {"name": "hai_shi_shan_meng", "display_name": "海誓山盟", "rank": 1, "cost": {"money": 9999}},
    {"name": "jin_zhuan", "display_name": "金砖", "rank": 5, "effect": {"money": 50}},
    {"name": "jin_ye_zi", "display_name": "金叶子", "rank": 6, "effect": {"money": 10}},
    {"name": "zhuan_shen_can", "display_name": "转神餐", "rank": 4, "effect": {"energy": 50}, "cost": {"money": 100}},
    {"name": "jia_zhuan_shen_can", "display_name": "佳·转神餐", "rank": 3, "effect": {"energy": 300}, "cost": {"money": 500}},
    {"name": "rong_ding", "display_name": "熔锭", "rank": 4, "effect": {'pve_weapon': 5}, "cost": {"banggong": 5000}},
    {"name": "mo_shi", "display_name": "磨石", "rank": 4, "effect": {'pvp_weapon': 5}, "cost": {"weiwang": 5000}},
    {"name": "ran", "display_name": "绣", "rank": 4, "effect": {'pve_armor': 10}, "cost": {"banggong": 2000}},
    {"name": "yin", "display_name": "印", "rank": 4, "effect": {'pvp_armor': 10}, "cost": {"weiwang": 2000}},
    {"name": "sui_rou", "display_name": "碎肉", "rank": 6, "cost": {"money": 10}},
    {"name": "cu_bu", "display_name": "粗布", "rank": 6, "cost": {"money": 10}},
    {"name": "gan_cao", "display_name": "甘草", "rank": 6, "cost": {"money": 10}},
    {"name": "hong_tong", "display_name": "红铜", "rank": 6, "cost": {"money": 10}},
    {"name": "hun_hun_zheng_ming", "display_name": "混混抓捕证明", "rank": 0}
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
        "equipment": {'weapon': {"display_name": "混混棍", 'pvp': 0, 'pve': 10}, 
                        'armor': {"display_name": "混混衣", 'pvp': 0, 'pve': 50}},
        "reward": {"money": 50},
        "reward_chance": 0.5
    }
}

QIYU_LIST = {
    'hong_fu_qi_tian': {"description": "江湖快马飞报！[CQ:at,qq={0}]侠士鸿运当头！签到时获得额外奖励。",
                        "chance": 0.1,
                        "cooldown": 0,
                        "reward": {"money": DALIY_MONEY_REWARD, "weiwang": DALIY_REWARD_MAX, "banggong": DALIY_REWARD_MAX}},
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
                        "cooldown": 0,
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

STAT_DISPLAY_NAME = {
    "weiwang": "威望",
    "banggong": "帮贡",
    "money": "金钱",
    "energy": "体力"
}

QIYU_CHANCE = 0.1

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
    info = CQGroupMemberInfo(CQSDK.GetGroupMemberInfoV2(fromGroup, fromQQ))
    return info.Card if info.Card != None and info.Card != "" else info.Nickname

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

    def __init__(self, qq_group):
        logging.info('Jx3Handler __init__')
        self.qq_group = qq_group # int

        self.json_file_folder = os.path.join(DATABASE_PATH, str(qq_group))
        self.json_file_path = os.path.join(self.json_file_folder, 'data.json')
        self.json_file_path_old = os.path.join(self.json_file_folder, 'data.json.old')
        self.json_file_path_old_2 = os.path.join(self.json_file_folder, 'data.json.old2')

        if not os.path.exists(self.json_file_folder):
            logging.info("path not exist. create a new one: {0}", self.json_file_folder)
            os.makedirs(self.json_file_folder)

        if os.path.exists(self.json_file_path):
            load_old_file = False
            try:
                with open(self.json_file_path, 'r') as f:
                    data = json.loads(f.readline(), encoding='gbk')
                    self.jx3_users = copy.deepcopy(get_key_or_return_default(data, "jx3_users", {}))
                    self.lover_pending = copy.deepcopy(get_key_or_return_default(data, "lover_pending", {}))
                    self.daliy_action_count = copy.deepcopy(get_key_or_return_default(data, "daliy_action_count", {}))
                    self.rob_protect = copy.deepcopy(get_key_or_return_default(data, "rob_protect", {}))
                    self.equipment = copy.deepcopy(get_key_or_return_default(data, "equipment", {}))
                    self.wanted_list = copy.deepcopy(get_key_or_return_default(data, "wanted_list", {}))
                    self.jail_list = copy.deepcopy(get_key_or_return_default(data, "jail_list", {}))
                    self.qiyu_status = copy.deepcopy(get_key_or_return_default(data, "qiyu_status", {}))
                    logging.info("loading complete")
            except Exception as e:
                load_old_file = True
                logging.exception(e)
            
            if load_old_file and os.path.exists(self.json_file_path_old):
                try:
                    with open(self.json_file_path_old, 'r') as f:
                        data = json.loads(f.readline(), encoding='gbk')
                        self.jx3_users = copy.deepcopy(get_key_or_return_default(data, "jx3_users", {}))
                        self.lover_pending = copy.deepcopy(get_key_or_return_default(data, "lover_pending", {}))
                        self.daliy_action_count = copy.deepcopy(get_key_or_return_default(data, "daliy_action_count", {}))
                        self.rob_protect = copy.deepcopy(get_key_or_return_default(data, "rob_protect", {}))
                        self.equipment = copy.deepcopy(get_key_or_return_default(data, "equipment", {}))
                        self.wanted_list = copy.deepcopy(get_key_or_return_default(data, "wanted_list", {}))
                        self.jail_list = copy.deepcopy(get_key_or_return_default(data, "jail_list", {}))
                        self.qiyu_status = copy.deepcopy(get_key_or_return_default(data, "qiyu_status", {}))
                        logging.info("loading old file complete")
                except Exception as e:
                    logging.exception(e)

        self.mutex = Lock()
        
    def __del__(self):
        logging.info('Jx3Handler __del__')

    def writeToJsonFile(self):
        returnMsg = ""
        self.mutex.acquire()
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
                    "qiyu_status": self.qiyu_status
                }
                f.write(json.dumps(data, ensure_ascii=False, encoding='gbk'))
        except Exception as e:
            logging.exception(e)
        self.mutex.release()

    
    def _reset_daliy_count(self, qq_account_str):
        yday = time.localtime(time.time() - DALIY_REFRESH_OFFSET).tm_yday
        yday_str = str(yday)
        if yday_str not in self.daliy_action_count:
            self.daliy_action_count[yday_str] = {}
            for k in self.daliy_action_count:
                if int(k) < yday - DALIY_COUNT_SAVE_DAY:
                    self.daliy_action_count.pop(k)

        if qq_account_str not in self.daliy_action_count[yday_str]:
            self.daliy_action_count[yday_str][qq_account_str] = {
                'qiandao': False,
                'speech_count': 0,
                'ya_biao': 0,
                'wa_bao': {'count': 0, 'last_time': None},
                'jailed': 0,
                'cha_guan': {'complete_quest': [], 'current_quest': ""},
                "speech_energy_gain": 0
            }

        return yday
    
    def getCommandList(self):
        return self.commandList

    def register(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()

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
        
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
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
        try:
            self.mutex.acquire()
            qq_account_str = str(qq_account)
            self._update_gear_point(qq_account_str)

            val = self.jx3_users[qq_account_str]
            self.mutex.release()

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            if self.daliy_action_count[yday_str][qq_account_str]['qiandao']:
                qiandao_status = "已签到"
            else:
                qiandao_status = "未签到"

            return "[CQ:at,qq={0}]\n情缘:\t\t{1}\n门派:\t\t{2}\n阵营:\t\t{3}\n威望:\t\t{4}\n帮贡:\t\t{5}\n金钱:\t\t{6}G\nPVP装分:\t{7}\nPVE装分:\t{8}\n资历:\t\t{9}\n签到状态:\t{10}\n签到次数:\t{11}\n奇遇:\t\t{12}\n注册时间:\t{13}\n今日发言:\t{14}\n体力:\t\t{15}".format(
                    qq_account,
                    "" if val['lover'] == 0 else getGroupNickName(qq_group, val['lover']),
                    "无门派" if val['class_id'] == 0 else val['class_id'],
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

    def qianDao(self, qq_account):
        returnMsg = ""
        try:
            qq_account_str = str(qq_account)
            self.mutex.acquire()
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

                returnMsg = "[CQ:at,qq={0}] 签到成功!\n今日签到奖励:\n威望+{1}\n帮贡+{2}\n金钱+{3}\n体力+{4}".format(
                                qq_account,
                                weiwang_reward,
                                banggong_reward,
                                DALIY_MONEY_REWARD,
                                DALIY_ENERGY_REWARD)
            
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def addSpeechCount(self, qq_account):
        try:
            qq_account_str = str(qq_account)
            self.mutex.acquire()

            yday = self._reset_daliy_count(qq_account_str)
            yday_str = str(yday)

            self.daliy_action_count[yday_str][qq_account_str]['speech_count'] += 1

            if 'speech_energy_gain' not in self.daliy_action_count[yday_str][qq_account_str]:
                self.daliy_action_count[yday_str][qq_account_str]['speech_energy_gain'] = 0
            
            if self.daliy_action_count[yday_str][qq_account_str]['speech_energy_gain'] < DALIY_MAX_SPEECH_ENERGY_GAIN:
                self.daliy_action_count[yday_str][qq_account_str]['speech_energy_gain'] += SPEECH_ENERGY_GAIN
                self.jx3_users[qq_account_str]['energy'] += SPEECH_ENERGY_GAIN
            
            self.mutex.release()

        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def addLover(self, fromQQ, toQQ):
        returnMsg = ""
        try:
            self.mutex.acquire()

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

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def acceptLover(self, fromGroup, toQQ):
        returnMsg = ""
        try:
            self.mutex.acquire()
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
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()

    def rejectLover(self, toQQ):
        returnMsg = ""
        try:
            self.mutex.acquire()
            if str(toQQ) in self.lover_pending.keys():
                fromQQ = self.lover_pending.pop(str(toQQ))
                returnMsg = "落花有意，流水无情，[CQ:at,qq={1}] 婉拒了 [CQ:at,qq={0}]。".format(fromQQ, toQQ)
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
    
    def yaBiao(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
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
                    returnMsg = "[CQ:at,qq={0}] 押镖成功！\n体力-{1}\n威望+{2}\n金钱+{3}".format(qq_account, YA_BIAO_ENERGY_REQUIRED, reward, DALIY_YA_BIAO_MONEY_REWARD)
                else:
                    returnMsg = "[CQ:at,qq={0}] 一天最多押镖{1}次。你已经押了{1}趟啦，明天再来吧。".format(qq_account, MAX_DALIY_YA_BIAO_COUNT)

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()

    def checkBag(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            bag = get_key_or_return_default(self.jx3_users[str(qq_account)], 'bag', {})
            if bag == {}:
                itemMsg = "\n空空如也"
            else:
                itemMsg = ""
                for k, v in bag.items():
                    itemMsg += "\n{0} x {1}".format(get_item_display_name(k), v)
            returnMsg = "[CQ:at,qq={0}] 的背包：".format(qq_account) + itemMsg
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
    
    def joinFaction(self, qq_account, faction_str):
        returnMsg = ""
        try:
            self.mutex.acquire()
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
            
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def quitFaction(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            qq_account_str = str(qq_account)
            qq_stat = self.jx3_users[qq_account_str]
            if qq_stat['faction_id'] == 0:
                returnMsg = "[CQ:at,qq={0}] 你并没有加入任何阵营。".format(qq_account)
            else:
                pre_faction_id = qq_stat['faction_id']
                self.jx3_users[qq_account_str]['faction_id'] = 0
                self.jx3_users[qq_account_str]['faction_join_time'] = time.time()
                returnMsg = "[CQ:at,qq={0}] 退出了江湖纷争，脱离了 {1}".format(qq_account, get_faction_display_name(pre_faction_id))
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def transferFaction(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
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
                returnMsg = "[CQ:at,qq={0}] 通过地下交易，成功地脱离了 {1}，加入了 {2}。".format(qq_account, get_faction_display_name(pre_faction_id), get_faction_display_name(new_faction_id))
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def _calculate_battle(self, fromQQ_str, toQQ_str, gear_mode):

        if toQQ_str in NPC_LIST:
            toQQ_equipment = NPC_LIST[toQQ_str]['equipment']
            toQQ_gear_point = calculateGearPoint(toQQ_equipment)[gear_mode]
        else:
            toQQ_equipment = self.equipment[toQQ_str]
            toQQ_gear_point = calculateGearPoint(toQQ_equipment)[gear_mode]

        fromQQ_equipment = self.equipment[fromQQ_str]
        fromQQ_gear_point = calculateGearPoint(fromQQ_equipment)[gear_mode]

        random_base = random.uniform(0.4, 0.5)
        success_chance = random_base + 0.2 * ((fromQQ_gear_point - toQQ_gear_point) / float(toQQ_gear_point)) + 0.3 * float(fromQQ_equipment['weapon'][gear_mode]) / float(toQQ_equipment['armor'][gear_mode])
        
        logging.info("success_chance: {0} + 0.3 * {1} + 0.2 * {2}".format(
                        random_base,
                        (fromQQ_gear_point - toQQ_gear_point) / float(toQQ_gear_point), 
                        float(fromQQ_equipment['weapon'][gear_mode]) / float(toQQ_equipment['armor'][gear_mode])))
        
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
        try:
            if not self.isUserRegister(toQQ):
                returnMsg = "[CQ:at,qq={0}] 对方尚未注册，无法打劫。".format(fromQQ)
            else:
                self.mutex.acquire()
                fromQQ_str = str(fromQQ)
                fromQQ_stat = self.jx3_users[fromQQ_str]
                toQQ_str = str(toQQ)
                toQQ_stat = self.jx3_users[toQQ_str]

                if fromQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] 中立阵营无法打劫，请先加入阵营。".format(fromQQ)
                elif toQQ_stat['faction_id'] == 0:
                    returnMsg = "[CQ:at,qq={0}] 对方是中立阵营，无法打劫。".format(fromQQ)
                elif fromQQ_stat['faction_id'] == toQQ_stat['faction_id']:
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
                else:
                    if fromQQ_str in self.jail_list:
                        self.jail_list.pop(fromQQ_str)

                    battle_result = self._calculate_battle(fromQQ_str, toQQ_str, 'pvp')

                    winner = battle_result['winner']
                    loser = battle_result['loser']
                    success_chance = battle_result['success_chance']

                    weiwang_amount = int(self.jx3_users[loser]['weiwang'] * random.uniform(0.1, 0.2))
                    money_amount = int(self.jx3_users[loser]['money'] * random.uniform(0.1, 0.2))
                    self.jx3_users[winner]['weiwang'] += weiwang_amount
                    self.jx3_users[loser]['weiwang'] -= weiwang_amount

                    self.jx3_users[winner]['money'] += money_amount
                    self.jx3_users[loser]['money'] -= money_amount

                    self.jx3_users[fromQQ_str]['energy'] -= ROB_ENERGY_COST

                    if toQQ_str == loser:
                        if loser not in self.rob_protect or self.rob_protect[loser]['count'] >= ROB_PROTECT_COUNT:
                            self.rob_protect[loser] = {'count': 0, 'rob_time': None}
                        self.rob_protect[loser]['count'] += 1
                        self.rob_protect[loser]['rob_time'] = time.time()

                    logging.info("{0} rob {1} weiwang: {2} money: {3}".format(fromQQ, toQQ, weiwang_amount, money_amount))

                    returnMsg = "打劫{0}！成功率：{1}%".format("成功" if winner == fromQQ_str else "失败", int(math.floor(success_chance * 100)))
                    returnMsg += "\n[CQ:at,qq={0}] 在野外打劫了 [CQ:at,qq={1}]\n{2} 威望+{4} 金钱+{5} 体力-{6}\n{3} 威望-{4} 金钱-{5}".format(
                                    fromQQ,
                                    toQQ,
                                    getGroupNickName(fromGroup, int(winner)),
                                    getGroupNickName(fromGroup, int(loser)),
                                    weiwang_amount,
                                    money_amount,
                                    ROB_ENERGY_COST)
                self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def buyItem(self, qq_account, item_display_name, item_amount):
        returnMsg = ""
        try:
            item = find_item(item_display_name)
            if item != None:
                if not isItemBuyable(item):
                    returnMsg = "[CQ:at,qq={0}] {1} 不可购买。".format(qq_account, item_display_name)
                else:
                    self.mutex.acquire()
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
                    self.mutex.release()
                return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def useItem(self, qq_account, item_display_name, item_amount):
        returnMsg = ""
        try:
            item = find_item(item_display_name)
            if item != None:
                if not isItemUsable(item):
                    returnMsg = "[CQ:at,qq={0}] {1} 不可使用。".format(qq_account, item_display_name)
                else:
                    self.mutex.acquire()
                    qq_account_str = str(qq_account)
                    qq_stat = self.jx3_users[qq_account_str]

                    effect_list = item['effect']

                    if item['name'] not in self.jx3_users[qq_account_str]['bag']:
                        returnMsg = "[CQ:at,qq={0}] 你并没有 {1}，无法使用。".format(qq_account, item_display_name)
                    elif self.jx3_users[qq_account_str]['bag'][item['name']] < item_amount:
                        returnMsg = "[CQ:at,qq={0}] 你并没有那么多 {1}。".format(qq_account, item_display_name)
                    else:
                        self.jx3_users[qq_account_str]['bag'][item['name']] -= item_amount
                        if self.jx3_users[qq_account_str]['bag'][item['name']] == 0:
                            self.jx3_users[qq_account_str]['bag'].pop(item['name'])

                        returnMsg = "[CQ:at,qq={0}]\n使用 {1} x {2}".format(qq_account, item_display_name, item_amount)
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

                    self.mutex.release()

                return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
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
        try:
            self.mutex.acquire()
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
                            returnMsg += "\n你一铲子下去，挖到了一个神秘的东西\n{0}+1\n体力-{1}".format(
                                            get_item_display_name(reward_item_name),
                                            WA_BAO_ENERGY_REQUIRED)
                else:
                    returnMsg = "[CQ:at,qq={0}] 一天最多挖宝{1}次。你已经挖了{1}次啦，今天休息休息吧。".format(qq_account, MAX_DALIY_WA_BAO_COUNT)

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()


    def use_firework(self, item_display_name, fromQQ, toQQ):
        returnMsg = ""
        try:
            item = find_item(item_display_name)
            if item != None:
                self.mutex.acquire()
                fromQQ_str = str(fromQQ)
                qq_stat = self.jx3_users[fromQQ_str]

                if item['name'] not in self.jx3_users[fromQQ_str]['bag']:
                    returnMsg = "[CQ:at,qq={0}] 你并没有 {1}，无法使用。".format(fromQQ, item_display_name)
                else:
                    self.jx3_users[fromQQ_str]['bag'][item['name']] -= 1
                    if self.jx3_users[fromQQ_str]['bag'][item['name']] == 0:
                        self.jx3_users[fromQQ_str]['bag'].pop(item['name'])

                    use_zhen_cheng_zhi_xin(self.qq_group, fromQQ, toQQ)

                self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def get_equipment_info(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
            val = self.equipment[str(qq_account)]

            returnMsg = "[CQ:at,qq={0}]\n装备信息：\n武器：{1}\n----pve攻击：{2}----pvp攻击：{3}\n防具：{4}\n----pve血量：{5}----pvp血量：{6}".format(
                qq_account,
                val['weapon']['display_name'],
                val['weapon']['pve'],
                val['weapon']['pvp'],
                val['armor']['display_name'],
                val['armor']['pve'],
                val['armor']['pvp'])

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
    
    def change_weapon_name(self, qq_account, name):
        returnMsg = ""
        try:
            self.mutex.acquire()
            self.equipment[str(qq_account)]['weapon']['display_name'] = name
            returnMsg = "[CQ:at,qq={0}] 的武器已更名为 {1}".format(qq_account, name)
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()

    def change_armor_name(self, qq_account, name):
        returnMsg = ""
        try:
            self.mutex.acquire()
            self.equipment[str(qq_account)]['armor']['display_name'] = name
            returnMsg = "[CQ:at,qq={0}] 的防具已更名为 {1}".format(qq_account, name)
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def get_faction_info(self):
        returnMsg = "本群阵营信息\n"
        try:
            self.mutex.acquire()
            no_faction = 0
            hao_qi = 0
            e_ren = 0
            for key, value in self.jx3_users.items():
                if value['faction_id'] == 0:
                    no_faction += 1
                elif value['faction_id'] == 1:
                    e_ren += 1
                elif value['faction_id'] == 2:
                    hao_qi += 1
            returnMsg += "本群为{0}群\n恶人谷人数:\t{1}\n浩气盟人数:\t{2}\n中立人数:\t{3}".format(
                        "浩气强势" if hao_qi > e_ren else "恶人强势" if e_ren > hao_qi else "势均力敌",
                        e_ren,
                        hao_qi,
                        no_faction)

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
    
    def get_pve_gear_point_rank(self):
        returnMsg = "本群pve装备排行榜"
        try:
            self.mutex.acquire()
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['pve_gear_point'], y[1]['pve_gear_point']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['pve_gear_point'])
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def get_pvp_gear_point_rank(self):
        returnMsg = "本群pvp装备排行榜"
        try:
            self.mutex.acquire()
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['pvp_gear_point'], y[1]['pvp_gear_point']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['pvp_gear_point'])
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def get_money_rank(self):
        returnMsg = "本群土豪排行榜"
        try:
            self.mutex.acquire()
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['money'], y[1]['money']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['money'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), int(rank_list[i][1]['money']))
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def get_speech_rank(self, qq_account):
        returnMsg = "本群今日聊天排行榜"
        try:
            self.mutex.acquire()

            yday = self._reset_daliy_count(str(qq_account))
            yday_str = str(yday)

            rank_list = sorted(self.daliy_action_count[yday_str].items(), lambda x, y: cmp(x[1]['speech_count'], y[1]['speech_count']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['speech_count'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(
                        i + 1,
                        getGroupNickName(self.qq_group, int(rank_list[i][0])), 
                        rank_list[i][1]['speech_count'])
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def get_qiyu_rank(self):
        returnMsg = "本群奇遇排行榜"
        try:
            self.mutex.acquire()
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['qiyu'], y[1]['qiyu']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['qiyu'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['qiyu'])
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)

    def get_weiwang_rank(self):
        returnMsg = "本群威望排行榜"
        try:
            self.mutex.acquire()
            rank_list = sorted(self.jx3_users.items(), lambda x, y: cmp(x[1]['weiwang'], y[1]['weiwang']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['weiwang'] != 0:
                    returnMsg += '\n{0}. {1} {2}'.format(i + 1, getGroupNickName(self.qq_group, int(rank_list[i][0])), rank_list[i][1]['weiwang'])
                else:
                    break
            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
    
    def put_wanted(self, fromQQ, toQQ):
        returnMsg = ""
        try:
            if not self.isUserRegister(toQQ):
                returnMsg = "[CQ:at,qq={0}] 对方尚未注册，无法悬赏。".format(fromQQ)
            else:
                self.mutex.acquire()
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
                    if toQQ_str in self.wanted_list:
                        if time.time() - self.wanted_list[toQQ_str]['wanted_time'] > WANTED_DURATION:
                            self.wanted_list[toQQ_str]['reward'] = WANTED_MONEY_REWARD
                        else:
                            self.wanted_list[toQQ_str]['reward'] += WANTED_MONEY_REWARD
    
                        self.wanted_list[toQQ_str]['wanted_time'] = time.time()
                    else:
                        self.wanted_list[toQQ_str] = {'reward': WANTED_MONEY_REWARD, 'wanted_time': time.time(), 'failed_try': {}}
                    
                    import CQSDK
                    CQSDK.SendGroupMsg(self.qq_group, "[CQ:at,qq={0}] 悬赏成功！\n金钱-{1}".format(fromQQ, WANTED_MONEY_REWARD))

                    returnMsg = "江湖恩怨一朝清，惟望群侠多援手。现有人愿付{0}金对 {1} 进行悬赏，总赏金已达{2}金，众侠士切勿错过。".format(
                                    WANTED_MONEY_REWARD,
                                    getGroupNickName(self.qq_group, int(toQQ)),
                                    self.wanted_list[toQQ_str]['reward'])

                self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()

    def get_wanted_list(self):
        returnMsg = "本群悬赏榜"
        msg_list = ""
        try:
            self.mutex.acquire()
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

            self.mutex.release()

            if msg_list == "":
                msg_list = "\n暂无悬赏"
            return returnMsg + msg_list
        except Exception as e:
            logging.exception(e)

    def catch_wanted(self, fromQQ, toQQ):
        returnMsg = ""
        try:
            self.mutex.acquire()
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

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def get_cha_guan_quest(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
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

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def complete_cha_guan_quest(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
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

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def catch_hun_hun(self, qq_account):
        returnMsg = ""
        try:
            self.mutex.acquire()
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

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
    
    def do_qiyu(self, qiyu_type):
        returnMsg = ""
        try:
            self.mutex.acquire()
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

            self.mutex.release()
            return returnMsg
        except Exception as e:
            logging.exception(e)
        finally:
            self.writeToJsonFile()
