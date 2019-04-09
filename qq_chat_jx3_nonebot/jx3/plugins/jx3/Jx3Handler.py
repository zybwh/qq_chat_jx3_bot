import random
import logging
import os

from .Jx3Class import *
from .Jx3User import *
from .Jx3Faction import *
from .Jx3Qiyu import *
from .Jx3Item import *
from .GameConfig import *
from .Utils import *

class Jx3Handler(object):

    self.json_file_path = ""

    _jx3_users = {}
    _today = 0
    _jx3_faction = {}
    _lover_pending = {}
    _jail_list = {}
    _jjc_data = {
        'season': 1,
        'day': 1
    }
    _jjc_history = {}
    
    def __init__(self, qq_group, DATABASE_PATH):
        self._qq_group = qq_group

        self.json_file_path = os.path.join(DATABASE_PATH, str(qq_group), 'data.json')

        self.read_data(self.json_file_path)

    def read_data(self, json_file_path):
        try:
            game_data = {}
            if os.path.exists(json_file_path):
                with open(json_file_path, 'r') as f:
                    game_data = json.loads(f.readline())

            self._load_user_data(game_data.get('jx3_users', {}))
            self._load_equipment(game_data.get('equipment', {}))
            self._load_daily_count(game_data.get('daily_action_count', {}))

            self._jx3_faction = game_data.get('jx3_faction', copy.deepcopy(faction_daily_dict))
            self._lover_pending = game_data.get('lover_pending', {})
            self._jail_list = game_data.get('jail_list', {})
        except Exception as e:
            logging.exception(e)

    def _load_user_data(self, user_data):
        try:
            for k, v in user_data.items():
                val = copy.deepcopy(v)
                if isinstance(val['class_id'], int):
                    val['class_id'] = OLD_CLASS_LIST_TO_NEW_LIST[val['class_id']]
                if isinstance(val['faction_id'], int):
                    val['faction_id'] = OLD_FACTION_LIST[val['faction_id']]
                if isinstance(val['qiyu'], int):
                    val['qiyu'] = {'unknown': val['qiyu']}

                self._jx3_users[str(k)] = val
        except Exception as e:
            logging.exception(e)
    
    def _load_equipment(self, equipment_data):
        if equipment_data != {}:
            for k, v in equipment_data['equipment'].items():
                if k in self['jx3_users']:
                    self['jx3_users'][k]['equipment'] = copy.deepcopy(v)
    
    def _load_daily_count(self, daily_count_data):
        sorted_list = sorted(daily_count_data['daily_action_count'].items, key=lambda x: int(x[0]), reverse=True)
        day, count_list = sorted_list.items()[0]
        for k, v in count_list.items():
            if k in self._jx3_users['jx3_users']:
                self._jx3_users['jx3_users'][k]['day'] = day
                self._jx3_users['jx3_users'][k]['daily_count'] = copy.deepcopy(v)
    
    def dump_data(self):
        try:
            data = {
                "jx3_users": self._jx3_users,
                "jx3_faction": self._jx3_faction,
                "lover_pending": self._lover_pending,
                "jail_list": self._jail_list
            }
            return data
        except Exception as e:
            logging.exception(e)
    
    def add_speech_count(self, qq_account: str):
        try:
            self._jx3_users[qq_account]['daily_count']['speech_count'] += 1

            if self._jx3_users[qq_account]['daily_count']['speech_energy_gain'] < DALIY_MAX_SPEECH_ENERGY_GAIN:
                self._jx3_users[qq_account]['daily_count']['speech_energy_gain'] += SPEECH_ENERGY_GAIN
                self._jx3_users[qq_account]['energy'] += SPEECH_ENERGY_GAIN
        except Exception as e:
            logging.exception(e)
            self.read_data(self.json_file_path)

    def register(self, qq_account: str):
        returnMsg = ""

        try:
            if qq_account in self._jx3_users:
                returnMsg = "[CQ:at,qq={0}] 注册失败！你已经注册过了。".format(qq_account)
            else:
                self._jx3_users[qq_account] = {
                    'class_id': 'da_xia',
                    'faction_id': 'zhong_li',
                    'faction_join_time': None,
                    'weiwang': 0,
                    'banggong': 0,
                    'money': 0,
                    'energy': 0,
                    'achievement': {},
                    'lover': '',
                    'lover_time': None,
                    'qiyu': {},
                    'register_time': time.time(),
                    'bag': {},
                    'equipment': copy.deepcopy(default_equipment),
                    'today': self._today,
                    'daily_count': copy.deepcopy(daily_dict)
                }
                returnMsg = "注册成功！\n[CQ:at,qq={0}]\n注册时间：{1}".format(
                    qq_account,
                    time.strftime('%Y-%m-%d', time.localtime(self._jx3_users[qq_account].register_time))
                )
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)
        
        return returnMsg

    def is_user_register(self, qq_account: str):
        return qq_account in self._jx3_users

    async def get_info(self, qq_account: str):
        returnMsg = ""
        try:
            returnMsg = "[CQ:at,qq={0}]\n情缘:\t\t{1}\n门派:\t\t{2}\n阵营:\t\t{3}\n威望:\t\t{4}\n帮贡:\t\t{5}\n金钱:\t\t{6}G\n体力:\t\t{7}\n签到状态:\t{8}\n奇遇:\t\t{9}\n今日发言:\t{10}".format(
                qq_account,
                await get_group_nickname(self._qq_group, self._jx3_users[qq_account]['lover']) if self._jx3_users[qq_account]['lover'] != "" else "",
                CLASS_LIST[self._jx3_users[qq_account]],
                FACTION_LIST[self._jx3_users[qq_account]],
                self._jx3_users[qq_account]['weiwang'],
                self._jx3_users[qq_account]['banggong'],
                self._jx3_users[qq_account]['money'],
                self._jx3_users[qq_account]['energy'],
                '已签到' if self._jx3_users[qq_account]['daily_count']['qiandao'] else '未签到',
                get_qiyu_count(self._jx3_users[qq_account]),
                self._jx3_users[qq_account]['daily_count']['speech_count'])

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
        
        return returnMsg
    
    def qiandao(self, qq_account: str):
        returnMsg = ""
        try:
            qq_account_str = str(qq_account)
            val = self._jx3_users[qq_account_str]

            if self._jx3_users[qq_account]['daily_count']['qiandao']:
                returnMsg = "[CQ:at,qq={0}]今天已经签到过了!".format(qq_account)
            else:
                banggong_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)
                weiwang_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)

                self._jx3_users[qq_account]['weiwang'] += weiwang_reward
                self._jx3_users[qq_account]['weiwang'] += banggong_reward
                self._jx3_users[qq_account]['weiwang'] += DALIY_MONEY_REWARD
                self._jx3_users[qq_account]['weiwang'] += DALIY_ENERGY_REWARD
                
                self._jx3_users[qq_account]['qiandao_count'] += 1

                self._jx3_users[qq_account]['daily_count']['qiandao'] = True

                returnMsg = "[CQ:at,qq={0}] 签到成功！签到奖励: 威望+{1} 帮贡+{2} 金钱+{3} 体力+{4}".format(
                    self._qq_account_str,
                    weiwang_reward,
                    banggong_reward,
                    DALIY_MONEY_REWARD,
                    DALIY_ENERGY_REWARD)
                
                faction_reward =  self._jx3_faction[self._jx3_users[qq_account]['faction_id']]['yesterday_reward']

                if faction_reward != 0:
                    self._weiwang += faction_reward
                    returnMsg += "\n获得昨日阵营奖励：威望+{0}".format(faction_reward)
    
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)
        
        return returnMsg
    
    def add_lover(self, fromQQ: str, toQQ: str):
        returnMsg = []

        try:
            fromQQ_stat = self._jx3_users[fromQQ]
            toQQ_stat = self._jx3_users[toQQ]

            if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in fromQQ_stat['bag']:
                returnMsg = "[CQ:at,qq={0}] 绑定情缘需要消耗1个{1}。\n你并没有此物品，请先购买。".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
            else:
                if fromQQ_stat['lover'] == toQQ:
                    returnMsg = "[CQ:at,qq={0}] 你们已经绑定过啦！还想乱撒狗粮？".format(fromQQ)
                elif fromQQ_stat['lover'] != 0:
                    returnMsg = "[CQ:at,qq={0}]  想什么呢？你就不怕[CQ:at,qq={1}]打你吗？".format(fromQQ, fromQQ_stat['lover'])
                elif toQQ_stat['lover'] != 0:
                    returnMsg = "[CQ:at,qq={0}] 人家已经有情缘啦，你是想上818吗？".format(fromQQ)
                elif toQQ in self._lover_pending and self._lover_pending[toQQ] != fromQQ:
                    returnMsg = "[CQ:at,qq={0}] 已经有人向[CQ:at,qq={1}]求情缘啦，你是不是再考虑一下？".format(fromQQ, toQQ)
                else:
                    pendingList = [k for k, v in self._lover_pending.items() if v == fromQQ]
                    for p in pendingList:
                        self._lover_pending.pop(p)
                    self._lover_pending[toQQ] = fromQQ
                    returnMsg = "[CQ:at,qq={1}]\n[CQ:at,qq={0}] 希望与你绑定情缘，请输入 同意 或者 拒绝。".format(fromQQ, toQQ)
        except Exception as e:
            logging.exception(e)
            returnMsg = []
            self.read_data(self.json_file_path)
        
        return returnMsg
    
    async def accept_lover(self, toQQ: str):
        returnMsg = []

        try:
            if toQQ in self.lover_pending.keys():
                fromQQ = self.lover_pending.pop(toQQ)

                if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in self._jx3_users[fromQQ]['bag'].keys():
                    returnMsg = "[CQ:at,qq={1}] 虽然人家同意了但是你并没有1个{1}。".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
                else:
                    self._jx3_users[fromQQ]['lover'] = toQQ
                    self._jx3_users[fromQQ]['lover_time'] = time.time()
                    self._jx3_users[toQQ]['lover'] = fromQQ
                    self._jx3_users[toQQ_str]['lover_time'] = time.time()
                    if LOVE_ITEM_REQUIRED != "":
                        self._jx3_users[fromQQ]['bag'][LOVE_ITEM_REQUIRED] -= 1
                        if self._jx3_users[fromQQ]['bag'][LOVE_ITEM_REQUIRED] == 0:
                            self._jx3_users[fromQQ]['bag'].pop(LOVE_ITEM_REQUIRED)

                        fromQQ_nickname = await get_group_nickname(self._qq_group, fromQQ)
                        toQQ_nickname = await get_group_nickname(self._qq_group, toQQ)
                        
                        for m in ITEM_LIST[LOVE_ITEM_REQUIRED].get('firework', []):
                            returnMsg += m.format(fromQQ_nickname, toQQ_nickname)

                    returnMsg += "[CQ:at,qq={0}] 与 [CQ:at,qq={1}]，喜今日嘉礼初成，良缘遂缔。诗咏关雎，雅歌麟趾。瑞叶五世其昌，祥开二南之化。同心同德，宜室宜家。相敬如宾，永谐鱼水之欢。互助精诚，共盟鸳鸯之誓".format(fromQQ, toQQ)

        except Exception as e:
            logging.exception(e)
            returnMsg = []
            self.read_data(self.json_file_path)

        return returnMsg
    
    def reject_lover(self, toQQ: str):
        returnMsg = ""

        try:
            if toQQ in self.lover_pending:
                fromQQ = self.lover_pending.pop(toQQ)
                returnMsg = "落花有意，流水无情，[CQ:at,qq={1}] 婉拒了 [CQ:at,qq={0}]。".format(fromQQ, toQQ)

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def _is_in_jailed(self, qq_account: str):
        if qq_account in self._jail_list:
            if time.time() - self._jail_list[qq_account] < JAIL_DURATION:
                return get_remaining_time_string(JAIL_DURATION, self._jail_list[qq_account])
            else:
                self._jail_list.pop(qq_account)
        return ""
    
    def ya_biao(self, qq_account: str):
        returnMsg = ""

        try:
            val = self._jx3_users[qq_account]
            if val['faction_id'] == 0 and not NO_FACTION_ALLOW_YA_BIAO:
                returnMsg = "[CQ:at,qq={0}] 中立阵营无法押镖。".format(qq_account)
            elif val['energy'] < YA_BIAO_ENERGY_REQUIRED:
                returnMsg = "[CQ:at,qq={0}] 体力不足！无法押镖。".format(qq_account)
            else:
                jail_remaining_time = self._is_in_jailed(qq_account)
                if jail_remaining_time != "":
                    returnMsg = "[CQ:at,qq={0}] 老实点，你还要在监狱里蹲{1}。".format(
                        qq_account,
                        jail_remaining_time)
                else:
                    if self._jx3_users[qq_account]['daily_count']['ya_biao'] < MAX_DALIY_YA_BIAO_COUNT:
                        reward = random.randint(DALIY_YA_BIAO_REWARD_MIN, DALIY_YA_BIAO_REWARD_MAX)
                        self._jx3_users[qq_account]['weiwang'] += reward
                        self._jx3_users[qq_account]['energy'] -= YA_BIAO_ENERGY_REQUIRED
                        self._jx3_users[qq_account]['money'] += DALIY_YA_BIAO_MONEY_REWARD
                        self._jx3_users[qq_account]['daily_count']["ya_biao"] += 1

                        self._jx3_faction[self._jx3_users[qq_account]['faction_id']]['faction_point'] += YA_BIAO_FACTION_POINT_GAIN

                        returnMsg = "[CQ:at,qq={0}] 押镖成功！体力-{1} 威望+{2} 金钱+{3}".format(qq_account, YA_BIAO_ENERGY_REQUIRED, reward, DALIY_YA_BIAO_MONEY_REWARD)
                    else:
                        returnMsg = "[CQ:at,qq={0}] 一天最多押镖{1}次。你已经押了{1}趟啦，明天再来吧。".format(qq_account, MAX_DALIY_YA_BIAO_COUNT)
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg
    
    def check_bag(self, qq_account):
        returnMsg = ""

        try:
            if self._jx3_users[qq_account]['bag'] == {}:
                itemMsg = "\n空空如也"
            else:
                itemMsg = ""
                for k, v in self._jx3_users[qq_account]['bag'].items():
                    itemMsg += "\n{0} x {1}".format(get_item_display_name(k), v)
            returnMsg = "[CQ:at,qq={0}] 的背包：{1}".format(qq_account, itemMsg)

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg
    

    def join_faction(self, qq_account: str, faction: str):
        returnMsg = ""

        try:
            if faction in FACTION_LIST.values():
                qq_stat = self._jx3_users[qq_account]
                qq_faction_str = FACTION_LIST[qq_stat['faction_id']]
                if faction == qq_faction_str:
                    returnMsg = "[CQ:at,qq={0}] 你已经加入了 {1}。".format(qq_account, faction)
                elif qq_stat['faction_id'] != 0:
                    returnMsg = "[CQ:at,qq={0}] 你已经加入了 {1}，{2} 并不想接受你的申请。".format(qq_account, qq_faction_str, faction)
                else:
                    remain_time = get_remaining_time_string(FACTION_REJOIN_CD_SECS, qq_stat['faction_join_time'])
                    if remain_time != "":
                        returnMsg = "[CQ:at,qq={0}] 由于不久前才退出阵营，你需要等待{1}之后才能重新加入。".format(
                            qq_account,
                            remain_time)
                    else:
                        self._jx3_users[qq_account]['faction_id'] = convert_display_name_to_faction_id(faction)
                        self._jx3_users[qq_account]['faction_join_time'] = time.time()
                        returnMsg = "[CQ:at,qq={0}] 成功加入 {1}。".format(qq_account, faction)

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg
    
    def quit_faction(self, qq_account: str):
        returnMsg = ""

        try:
            qq_stat = self._jx3_users[qq_account]
            if qq_stat['faction_id'] == 0:
                returnMsg = "[CQ:at,qq={0}] 你并没有加入任何阵营。".format(qq_account)
            else:
                pre_faction_id = qq_stat['faction_id']
                self._jx3_users[qq_account]['faction_id'] = "zhong_li"
                self._jx3_users[qq_account]['faction_join_time'] = time.time()
                if FACTION_QUIT_EMPTY_WEIWANG:
                    self._jx3_users[qq_account]['weiwang'] = 0
                returnMsg = "[CQ:at,qq={0}] 退出了江湖纷争，脱离了 {1}。".format(qq_account, FACTION_LIST(pre_faction_id))

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg
    
    def transfer_faction(self, qq_account: str):
        returnMsg = ""

        try:
            qq_stat = self._jx3_users[qq_account]
            if qq_stat['faction_id'] == 0:
                returnMsg = "[CQ:at,qq={0}] 你并没有加入任何阵营。".format(qq_account)
            elif qq_stat['weiwang'] < FACTION_TRANSFER_WEIWANG_COST:
                returnMsg = "[CQ:at,qq={0}] 转换阵营需要消耗{1}威望，当前威望不足。".format(qq_account, FACTION_TRANSFER_WEIWANG_COST)
            else:
                remain_time = get_remaining_time_string(FACTION_REJOIN_CD_SECS, qq_stat['faction_join_time'])
                if remain_time != "":
                    returnMsg = "[CQ:at,qq={0}] 由于不久前才更改阵营，你需要等待{1}之后才能更改。".format(
                        qq_account,
                        remain_time)
                else:
                    pre_faction_id = qq_stat['faction_id']
                    new_faction_id = 'e_ren' if pre_faction_id == 'hao_qi' else 'hao_qi'
                    self._jx3_users[qq_account]['faction_id'] = new_faction_id
                    self._jx3_users[qq_account]['faction_join_time'] = time.time()
                    returnMsg = "[CQ:at,qq={0}] 通过地下交易，花费了{1}威望，成功地脱离了 {2}，加入了 {3}。".format(
                        qq_account, 
                        FACTION_TRANSFER_WEIWANG_COST, 
                        FACTION_LIST[pre_faction_id],
                        FACTION_LIST[new_faction_id])

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg
    
    def buy_item(self, qq_account, item_display_name, item_amount):
        returnMsg = ""

        try:
            item = get_item_id_by_display_name(item_display_name)
            if item != "":
                if 'cost' not in ITEM_LIST[item]:
                    returnMsg = "[CQ:at,qq={0}] {1} 不可购买。".format(qq_account, item_display_name)
                else:
                    qq_stat = self._jx3_users[qq_account]

                    cost_list = ITEM_LIST[item]['cost']
                    can_afford = True
                    for k, v in cost_list.items():
                        can_afford = can_afford and (k in qq_stat and qq_stat[k] >= v * item_amount)

                    if can_afford:
                        if item not in self._jx3_users[qq_account]['bag']:
                            self._jx3_users[qq_account]['bag'][item] = 0

                        self._jx3_users[qq_account]['bag'][item] += item_amount
                        returnMsg = "[CQ:at,qq={0}] 购买成功！\n{1}+{2} ".format(
                            qq_account,
                            item_display_name,
                            item_amount)

                        for k, v in cost_list.items():
                            if k in qq_stat:
                                self._jx3_users[qq_account][k] -= v * item_amount
                                returnMsg += "{0}-{1} ".format(USER_STAT_DISPLAY[k], v * item_amount)
                    else:
                        returnMsg = "[CQ:at,qq={0}] 购买失败！\n购买1个 {1} 需要:{2}".format(
                            qq_account,
                            item_display_name, 
                            print_item_cost(item))

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

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
                    qq_stat = self._jx3_users[qq_account_str]

                    effect_list = item['effect']

                    if item['name'] not in self._jx3_users[qq_account_str]['bag']:
                        returnMsg = "[CQ:at,qq={0}] 你并没有 {1}，无法使用。".format(qq_account, item_display_name)
                    elif self._jx3_users[qq_account_str]['bag'][item['name']] < item_amount:
                        returnMsg = "[CQ:at,qq={0}] 你并没有那么多 {1}。".format(qq_account, item_display_name)
                    else:
                        item_used = True
                        returnMsg = "[CQ:at,qq={0}] 使用 {1} x {2}".format(qq_account, item_display_name, item_amount)
                        for k, v in effect_list.items():
                            if k in qq_stat:
                                self._jx3_users[qq_account_str][k] += v * item_amount
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
                            self._jx3_users[qq_account_str]['bag'][item['name']] -= item_amount
                            if self._jx3_users[qq_account_str]['bag'][item['name']] == 0:
                                self._jx3_users[qq_account_str]['bag'].pop(item['name'])


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
