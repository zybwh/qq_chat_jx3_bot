import random
import logging
import os

from .Jx3Class import *
from .Jx3User import *
from .Jx3Faction import *
from .Jx3Qiyu import *
from .Jx3Item import *
from .Jx3Dungeon import *
from .GameConfig import *
from .Utils import *

class Jx3Handler(object):

    self.json_file_path = ""

    _jx3_users = {}
    _today = 0
    _jx3_faction = {}
    _lover_pending = {}
    _jail_list = {}
    _group_info = {}
    _jjc_data = {
        'season': 1,
        'day': 1,
        'last_season_data': {},
        'current_season_data': {}
    }

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
                returnMsg = f"[CQ:at,qq={qq_account}] 注册失败！你已经注册过了。"
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
                returnMsg = (
                    f"注册成功！\n"
                    f"[CQ:at,qq={qq_account}]\n"
                    f"注册时间：{time.strftime('%Y-%m-%d', time.localtime(self._jx3_users[qq_account].register_time))}"
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
            lover_name = await get_group_nickname(self._qq_group, self._jx3_users[qq_account]['lover']) if self._jx3_users[qq_account]['lover'] != "" else ""
            returnMsg = (
                f"[CQ:at,qq={qq_account}]\n"
                f"情缘:\t\t{lover_name}\n"
                f"门派:\t\t{CLASS_LIST[self._jx3_users[qq_account]]}\n"
                f"阵营:\t\t{FACTION_LIST[self._jx3_users[qq_account]]}\n"
                f"威望:\t\t{self._jx3_users[qq_account]['weiwang']}\n"
                f"帮贡:\t\t{self._jx3_users[qq_account]['banggong']}\n"
                f"金钱:\t\t{self._jx3_users[qq_account]['money']}G\n"
                f"体力:\t\t{self._jx3_users[qq_account]['energy']}\n"
                f"签到状态:\t{'已签到' if self._jx3_users[qq_account]['daily_count']['qiandao'] else '未签到',}\n"
                f"奇遇:\t\t{get_qiyu_count(self._jx3_users[qq_account])}\n"
                f"今日发言:\t{self._jx3_users[qq_account]['daily_count']['speech_count']}"
            )

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
                returnMsg = f"[CQ:at,qq={qq_account}]今天已经签到过了!"
            else:
                banggong_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)
                weiwang_reward = random.randint(DALIY_REWARD_MIN, DALIY_REWARD_MAX)

                self._jx3_users[qq_account]['weiwang'] += weiwang_reward
                self._jx3_users[qq_account]['weiwang'] += banggong_reward
                self._jx3_users[qq_account]['weiwang'] += DALIY_MONEY_REWARD
                self._jx3_users[qq_account]['weiwang'] += DALIY_ENERGY_REWARD

                self._jx3_users[qq_account]['qiandao_count'] += 1

                self._jx3_users[qq_account]['daily_count']['qiandao'] = True

                returnMsg = (
                    f"[CQ:at,qq={qq_account}] 签到成功！"
                    f"签到奖励: 威望+{weiwang_reward} 帮贡+{banggong_reward} 金钱+{DALIY_MONEY_REWARD} 体力+{DALIY_ENERGY_REWARD}"
                )

                faction_reward =  self._jx3_faction[self._jx3_users[qq_account]['faction_id']]['yesterday_reward']

                if faction_reward != 0:
                    self._weiwang += faction_reward
                    returnMsg += f"\n获得昨日阵营奖励：威望+{faction_reward}"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def add_lover(self, fromQQ: str, toQQ: str):
        returnMsg = ""

        try:
            fromQQ_stat = self._jx3_users[fromQQ]
            toQQ_stat = self._jx3_users[toQQ]

            if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in fromQQ_stat['bag']:
                returnMsg = "[CQ:at,qq={0}] 绑定情缘需要消耗1个{1}。\n你并没有此物品，请先购买。".format(fromQQ, get_item_display_name(LOVE_ITEM_REQUIRED))
            else:
                if fromQQ_stat['lover'] == toQQ:
                    returnMsg = f"[CQ:at,qq={fromQQ}] 你们已经绑定过啦！还想乱撒狗粮？".format()
                elif fromQQ_stat['lover'] != 0:
                    returnMsg = f"[CQ:at,qq={fromQQ}]  想什么呢？你就不怕[CQ:at,qq={fromQQ_stat['lover']}]打你吗？"
                elif toQQ_stat['lover'] != 0:
                    returnMsg = f"[CQ:at,qq={fromQQ}] 人家已经有情缘啦，你是想上818吗？"
                elif toQQ in self._lover_pending and self._lover_pending[toQQ] != fromQQ:
                    returnMsg = f"[CQ:at,qq={fromQQ}] 已经有人向[CQ:at,qq={toQQ}]求情缘啦，你是不是再考虑一下？"
                else:
                    pendingList = [k for k, v in self._lover_pending.items() if v == fromQQ]
                    for p in pendingList:
                        self._lover_pending.pop(p)
                    self._lover_pending[toQQ] = fromQQ
                    returnMsg = f"[CQ:at,qq={fromQQ}]\n[CQ:at,qq={toQQ}] 希望与你绑定情缘，请输入 同意 或者 拒绝。"
        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    async def accept_lover(self, toQQ: str):
        returnMsg = []

        try:
            if toQQ in self.lover_pending.keys():
                fromQQ = self.lover_pending.pop(toQQ)

                if LOVE_ITEM_REQUIRED != "" and LOVE_ITEM_REQUIRED not in self._jx3_users[fromQQ]['bag'].keys():
                    returnMsg.append(f"[CQ:at,qq={fromQQ}] 虽然人家同意了但是你并没有1个{get_item_display_name(LOVE_ITEM_REQUIRED)}。")
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
                            returnMsg.append(m.format(fromQQ_nickname, toQQ_nickname))

                    returnMsg.append((
                        f"[CQ:at,qq={fromQQ}] 与 [CQ:at,qq={toQQ}]，喜今日嘉礼初成，良缘遂缔。诗咏关雎，雅歌麟趾。瑞叶五世其昌，祥开二南之化。"
                        "同心同德，宜室宜家。相敬如宾，永谐鱼水之欢。互助精诚，共盟鸳鸯之誓"
                    ))

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
                returnMsg = f"落花有意，流水无情，[CQ:at,qq={fromQQ}] 婉拒了 [CQ:at,qq={toQQ}]。"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def _is_in_jailed(self, qq_account: str):
        if qq_account in self._jail_list:
            if time.time() - self._jail_list[qq_account] < JAIL_DURATION:
                return f"[CQ:at,qq={qq_account}] 老实点，你还要在监狱里蹲{get_remaining_time_string(JAIL_DURATION, self._jail_list[qq_account])}。"
            else:
                self._jail_list.pop(qq_account)
        return ""

    def ya_biao(self, qq_account: str):
        returnMsg = ""

        try:
            val = self._jx3_users[qq_account]
            if val['faction_id'] == 0 and not NO_FACTION_ALLOW_YA_BIAO:
                returnMsg = f"[CQ:at,qq={qq_account}] 中立阵营无法押镖。"
            elif val['energy'] < YA_BIAO_ENERGY_REQUIRED:
                returnMsg = f"[CQ:at,qq={qq_account}] 体力不足！无法押镖。"
            else:
                jail_status = self._is_in_jailed(qq_account)
                if jail_status != "":
                    returnMsg = jail_status
                else:
                    if self._jx3_users[qq_account]['daily_count']['ya_biao'] < MAX_DALIY_YA_BIAO_COUNT:
                        reward = random.randint(DALIY_YA_BIAO_REWARD_MIN, DALIY_YA_BIAO_REWARD_MAX)
                        self._jx3_users[qq_account]['weiwang'] += reward
                        self._jx3_users[qq_account]['energy'] -= YA_BIAO_ENERGY_REQUIRED
                        self._jx3_users[qq_account]['money'] += DALIY_YA_BIAO_MONEY_REWARD
                        self._jx3_users[qq_account]['daily_count']["ya_biao"] += 1

                        self._jx3_faction[self._jx3_users[qq_account]['faction_id']]['faction_point'] += YA_BIAO_FACTION_POINT_GAIN

                        returnMsg = (
                            f"[CQ:at,qq={qq_account}] 押镖成功！"
                            f"体力-{YA_BIAO_ENERGY_REQUIRED} 威望+{reward} 金钱+{DALIY_YA_BIAO_MONEY_REWARD}"
                        )
                    else:
                        returnMsg = f"[CQ:at,qq={0}] 一天最多押镖{1}次。你已经押了{1}趟啦，明天再来吧。".format(qq_account, MAX_DALIY_YA_BIAO_COUNT)
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
                    itemMsg += f"\n{get_item_display_name(k)} x {v}"
            returnMsg = f"[CQ:at,qq={qq_account}] 的背包：{itemMsg}"

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
                    returnMsg = f"[CQ:at,qq={qq_account}] 你已经加入了 {faction}。"
                elif qq_stat['faction_id'] != 0:
                    returnMsg = f"[CQ:at,qq={qq_account}] 你已经加入了 {qq_faction_str}，{faction} 并不想接受你的申请。"
                else:
                    remain_time = get_remaining_time_string(FACTION_REJOIN_CD_SECS, qq_stat['faction_join_time'])
                    if remain_time != "":
                        returnMsg = f"[CQ:at,qq={qq_account}] 由于不久前才退出阵营，你需要等待{remain_time}之后才能重新加入。"
                    else:
                        self._jx3_users[qq_account]['faction_id'] = convert_display_name_to_faction_id(faction)
                        self._jx3_users[qq_account]['faction_join_time'] = time.time()
                        returnMsg = f"[CQ:at,qq={qq_account}] 成功加入 {faction}。"

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
                returnMsg = f"[CQ:at,qq={qq_account}] 你并没有加入任何阵营。"
            else:
                pre_faction_id = qq_stat['faction_id']
                self._jx3_users[qq_account]['faction_id'] = "zhong_li"
                self._jx3_users[qq_account]['faction_join_time'] = time.time()
                if FACTION_QUIT_EMPTY_WEIWANG:
                    self._jx3_users[qq_account]['weiwang'] = 0
                returnMsg = f"[CQ:at,qq={qq_account}] 退出了江湖纷争，脱离了 {FACTION_LIST[pre_faction_id]}。"

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
                returnMsg = f"[CQ:at,qq={qq_account}] 你并没有加入任何阵营。"
            elif qq_stat['weiwang'] < FACTION_TRANSFER_WEIWANG_COST:
                returnMsg = f"[CQ:at,qq={qq_account}] 转换阵营需要消耗{FACTION_TRANSFER_WEIWANG_COST}威望，当前威望不足。"
            else:
                remain_time = get_remaining_time_string(FACTION_REJOIN_CD_SECS, qq_stat['faction_join_time'])
                if remain_time != "":
                    returnMsg = f"[CQ:at,qq={qq_account}] 由于不久前才更改阵营，你需要等待{remain_time}之后才能更改。"
                else:
                    pre_faction_id = qq_stat['faction_id']
                    new_faction_id = 'e_ren' if pre_faction_id == 'hao_qi' else 'hao_qi'
                    self._jx3_users[qq_account]['faction_id'] = new_faction_id
                    self._jx3_users[qq_account]['faction_join_time'] = time.time()
                    returnMsg = (
                        f"[CQ:at,qq={qq_account}] 通过地下交易，"
                        f"花费了{FACTION_TRANSFER_WEIWANG_COST}威望，成功地脱离了 {FACTION_LIST[pre_faction_id]}，"
                        f"加入了 {FACTION_LIST[new_faction_id]}。"
                    )

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def _modify_item_in_bag(self, qq_account, item_name, amount):
        if item_name not in self._jx3_users[qq_account]['bag']:
            self._jx3_users[qq_account]['bag'][item_name] = 0
        self._jx3_users[qq_account]['bag'][item_name] += amount

        if self._jx3_users[qq_account]['bag'][item_name] == 0:
            self._jx3_users[qq_account]['bag'].pop(item_name)

    def buy_item(self, qq_account, item_display_name, item_amount):
        returnMsg = ""

        try:
            item = get_item_id_by_display_name(item_display_name)
            if item != "":
                if 'cost' not in ITEM_LIST[item]:
                    returnMsg = f"[CQ:at,qq={qq_account}] {item_display_name} 不可购买。"
                else:
                    qq_stat = self._jx3_users[qq_account]

                    cost_list = ITEM_LIST[item]['cost']
                    can_afford = True
                    for k, v in cost_list.items():
                        can_afford = can_afford and (k in qq_stat and qq_stat[k] >= v * item_amount)

                    if can_afford:
                        self._modify_item_in_bag(qq_account, item, item_amount)

                        returnMsg = (
                            f"[CQ:at,qq={qq_account}] 购买成功！\n"
                            f"{item_display_name}+{item_amount} "
                        )

                        for k, v in cost_list.items():
                            if k in qq_stat:
                                self._jx3_users[qq_account][k] -= v * item_amount
                                returnMsg += "{0}-{1} ".format(USER_STAT_DISPLAY[k], v * item_amount)
                    else:
                        returnMsg = (
                            f"[CQ:at,qq={qq_account}] 购买失败！\n"
                            f"购买1个 {item_display_name} 需要:{print_item_cost(item)}"
                        )

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    async def use_item(self, qq_account, item_display_name, item_amount=1, toQQ=""):
        returnMsg = []

        try:
            item = get_item_id_by_display_name(item_display_name)
            if item != None:
                if 'firework' in ITEM_LIST[item] and toQQ == "":
                    returnMsg.append(f"[CQ:at,qq={qq_account}] {item_display_name} 需要使用对象。")
                elif 'effect' not in ITEM_LIST[item] and 'firework' not in ITEM_LIST[item]:
                    returnMsg.append(f"[CQ:at,qq={qq_account}] {item_display_name} 不可使用。")
                else:
                    qq_stat = self._jx3_users[qq_account]

                    if item not in self._jx3_users[qq_account]['bag']:
                        returnMsg = f"[CQ:at,qq={qq_account}] 你并没有 {item_display_name}，无法使用。"
                    elif self._jx3_users[qq_account]['bag'][item] < item_amount:
                        returnMsg = f"[CQ:at,qq={qq_account}] 你并没有那么多 {item_display_name}。"
                    else:
                        item_used = True

                        if 'firework' in ITEM_LIST[item]:
                            fromQQ_nickname = await get_group_nickname(self._qq_group, qq_account)
                            toQQ_nickname = await get_group_nickname(self._qq_group, toQQ)

                            for m in ITEM_LIST[LOVE_ITEM_REQUIRED].get('firework', []):
                                returnMsg.append(m.format(fromQQ_nickname, toQQ_nickname))
                        else:
                            effect_list = item['effect']

                            msg = f"[CQ:at,qq={qq_account}] 使用 {item_display_name} x {item_amount}"
                            for k, v in effect_list.items():
                                if k in qq_stat:
                                    self._jx3_users[qq_account][k] += v * item_amount
                                    msg += f"\n{USER_STAT_DISPLAY[k]}+{v * item_amount}"
                                elif k == 'attack_count':
                                    if qq_account in self._group_info:
                                        leader = qq_account
                                    else:
                                        leader = self._get_leader_by_member(qq_account)

                                    if leader != "" and leader in self.dungeon_status:
                                        self.dungeon_status[leader]['attack_count'][qq_account]['available_attack'] += v * item_amount
                                        msg += f"\n攻击次数+{v * item_amount}"
                                    else:
                                        msg = f"[CQ:at,qq={qq_account}] 你不在副本里，无法使用。"
                                        item_used = False
                                else:
                                    if k == 'pve_weapon':
                                        self.equipment[qq_account_str]['weapon']['pve'] += v * item_amount
                                        msg += f"\n武器pve伤害+{v * item_amount}"
                                    elif k == 'pvp_weapon':
                                        self.equipment[qq_account_str]['weapon']['pvp'] += v * item_amount
                                        msg += f"\n武器pvp伤害+{v * item_amount}"
                                    elif k == 'pve_armor':
                                        self.equipment[qq_account_str]['armor']['pve'] += v * item_amount
                                        msg += f"\n防具pve血量+{v * item_amount}"
                                    elif k == 'pvp_armor':
                                        self.equipment[qq_account_str]['armor']['pvp'] += v * item_amount
                                        msg += f"\n防具pvp血量+{v * item_amount}"

                            returnMsg.append(msg)

                        if item_used:
                            self._modify_item_in_bag(qq_account, item, 0 - item_amount)

        except Exception as e:
            logging.exception(e)
            returnMsg = []
            self.read_data(self.json_file_path)

        return returnMsg


    def shop_list(self, qq_account):
        returnMsg = ""

        try:
            returnMsg = (
                f"[CQ:at,qq={qq_account}]\n"
                f"---------杂货商---------\n"
                f"----货真价实，童叟无欺----"
            )
            for item in ITEM_LIST.values():
                if 'cost' in item:
                    returnMsg += f"\n*【{item['display_name']}】"
                    for k, v in item['cost'].items():
                        returnMsg += f"----{USER_STAT_DISPLAY[k]}：{v}"

        except Exception as e:
            logging.exception(e)

        return returnMsg

    def _get_wa_bao_reward(self):
        max_index = 0
        wa_bao_items = {}
        for item in random.sample(ITEM_LIST, len(ITEM_LIST)):
            if item['rank'] != 0:
                new_max_index = max_index + pow(item['rank'], WA_BAO_RARE_FACTOR)
                wa_bao_items[item['name']] = {'min': max_index, 'max': new_max_index}
                max_index = new_max_index

        rand_index = random.uniform(0, max_index)
        logging.info("wa_bao items: {1} rand index: {0}".format(rand_index, wa_bao_items))
        for item_name, min_max in wa_bao_items.items():
            if rand_index >= min_max['min'] and rand_index < min_max['max']:
                return item_name
        return ""

    def wa_bao(self, qq_account):
        returnMsg = ""

        try:
            val = self._jx3_users[qq_account]
            if val['energy'] < WA_BAO_ENERGY_REQUIRED:
                returnMsg = f"[CQ:at,qq={qq_account}] 体力不足！无法挖宝。"
            else:
                jail_status = self._is_in_jailed(qq_account)
                if jail_status != "":
                    returnMsg = jail_status
                else:
                    if qq_account in self.jail_list:
                        self.jail_list.pop(qq_account)

                    if val['daily_count']["wa_bao"]['count'] < MAX_DALIY_WA_BAO_COUNT:
                        remain_time = get_remaining_time_string(WA_BAO_COOLDOWN, val['daily_count']["wa_bao"]['last_time'])
                        if remain_time != "":
                            returnMsg = f"[CQ:at,qq={qq_account}] 大侠你刚刚挖完宝藏，身体有些疲惫，请过{remain_time}之后再挖。"
                        else:
                            reward_item_name = self._get_wa_bao_reward()
                            self._jx3_users[qq_account]['daily_count']["wa_bao"]['count'] += 1
                            self._jx3_users[qq_account]['daily_count']["wa_bao"]['last_time'] = time.time()

                            self._jx3_users[qq_account]['energy'] -= WA_BAO_ENERGY_REQUIRED

                            returnMsg = (
                                f"[CQ:at,qq={qq_account}]\n"
                                f"今日挖宝次数：{self._jx3_users[qq_account]['daily_count']['wa_bao']['count']}/{MAX_DALIY_WA_BAO_COUNT}"
                            )

                            if reward_item_name == "":
                                returnMsg += "\n你一铲子下去，什么也没挖到。"
                            else:
                                self._modify_item_in_bag(qq_account, reward_item_name, 1)
                                returnMsg += f"\n你一铲子下去，挖到了一个神秘的东西: {get_item_display_name(reward_item_name)}+1 体力-{WA_BAO_ENERGY_REQUIRED}"
                    else:
                        returnMsg = f"[CQ:at,qq={0}] 一天最多挖宝{MAX_DALIY_WA_BAO_COUNT}次。你已经挖了{MAX_DALIY_WA_BAO_COUNT}次啦，今天休息休息吧。"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def _calculate_gear_point(self, equipment):
        weapon = equipment['weapon']
        armor = equipment['armor']
        return {'pve': weapon['pve'] * 30 + armor['pve'] * 10, 'pvp': weapon['pvp'] * 30 + armor['pvp'] * 10}

    def get_equipment_info(self, qq_account):
        returnMsg = ""

        try:
            val = self._jx3_users[qq_account]['equipment']
            gear_point = self._calculate_gear_point(val)
            returnMsg = (
                f"[CQ:at,qq={qq_account}] 装备信息：\n"
                f"pve评分：{gear_point['pve']} pvp评分：{gear_point['pvp']}\n"
                f"武器：{val['weapon']['display_name']}\n"
                f"pve攻击：{val['weapon']['pve']}\tpvp攻击：{val['weapon']['pvp']}\n"
                f"防具：{val['armor']['display_name']}\n"
                f"pve血量：{val['armor']['pve']}\tpvp血量：{val['armor']['pvp']}"
            )

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg

    def change_weapon_name(self, qq_account: str, name: str):
            returnMsg = ""

            try:
                self.equipment[qq_account]['weapon']['display_name'] = name
                returnMsg = f"[CQ:at,qq={qq_account}] 的武器已更名为 {name}"

            except Exception as e:
                logging.exception(e)
                returnMsg = ""
                self.read_data(self.json_file_path)

            return returnMsg

    def change_armor_name(self, qq_account: str, name: str):
        returnMsg = ""

        try:
            self.equipment[str(qq_account)]['armor']['display_name'] = name
            returnMsg = f"[CQ:at,qq={qq_account}] 的防具已更名为 {name}"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def _get_faction_count(self):
        retval = {
            'zhong_li': 0,
            'e_ren': 0,
            'hao_qi': 0
        }
        for key, value in self._jx3_users.items():
            retval[value['faction_id']] += 1
        return retval

    def get_faction_info(self):
        returnMsg = ""

        try:
            yday = self._reset_daliy_count()
            yday_str = str(yday)
            retval = self._get_faction_count()
            strong_faction = "浩气强势" if retval['hao_qi'] > retval['e_ren'] else "恶人强势" if retval['e_ren'] > retval['hao_qi'] else "势均力敌"
            returnMsg = (
                f"本群阵营信息\n"
                f"本群为{strong_faction}群\n"
                f"恶人谷人数:\t{retval['e_ren']} 今日阵营点数：{self._jx3_faction['e_ren']['faction_point']}\n"
                f"浩气盟人数:\t{retval['hao_qi']} 今日阵营点数：{self._jx3_faction['hao_qi']['faction_point']}\n"
                f"中立人数:\t{retval['zhong_li']}"
            )

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg

    async def get_pve_gear_point_rank(self):
        returnMsg = "本群pve装备排行榜"

        try:
            pve_gear_point_list = {k: self._calculate_gear_point(v['equipment'])['pve'] for k, v in self._jx3_users.items()}
            rank_list = sorted(pve_gear_point_list.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len:
                    qq_nickname = await get_group_nickname(self._qq_group, rank_list[i][0])
                    returnMsg += f"\n{i + 1}. {qq_nickname} {rank_list[i][1]}"
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg


    async def get_pvp_gear_point_rank(self):
        returnMsg = "本群pvp装备排行榜"

        try:
            pvp_gear_point_list = {k: self._calculate_gear_point(v['equipment'])['pvp'] for k, v in self._jx3_users.items()}
            rank_list = sorted(pvp_gear_point_list.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len:
                    qq_nickname = await get_group_nickname(self._qq_group, rank_list[i][0])
                    returnMsg += f"\n{i + 1}. {qq_nickname} {rank_list[i][1]}"
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg

    async def get_money_rank(self):
        returnMsg = "本群土豪排行榜"

        try:
            rank_list = sorted(self._jx3_users.items(), lambda x, y: cmp(x[1]['money'], y[1]['money']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['money'] != 0:
                    qq_nickname = await get_group_nickname(self._qq_group, rank_list[i][0])
                    returnMsg += f"\n{i + 1}. {qq_nickname} {rank_list[i][1]['money']}"
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg


    async def get_speech_rank(self, qq_account):
        returnMsg = "本群今日聊天排行榜"

        try:
            rank_list = sorted(self._jx3_users.items(), lambda x, y: cmp(x[1]['daily_count']['speech_count'], y[1]['daily_count']['speech_count']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['speech_count'] != 0:
                    qq_nickname = await get_group_nickname(self._qq_group, rank_list[i][0])
                    returnMsg += f"\n{i + 1}. {qq_nickname} {rank_list[i][1]['daily_count']['speech_count']}"
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg

    async def get_qiyu_rank(self):
        returnMsg = "本群奇遇排行榜"

        try:
            rank_list = sorted(self._jx3_users.items(), lambda x, y: cmp(get_qiyu_count(x[1]), get_qiyu_count(y[1])), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and get_qiyu_count(rank_list[i][1]) != 0:
                    qq_nickname = await get_group_nickname(self._qq_group, rank_list[i][0])
                    returnMsg += f"\n{i + 1}. {qq_nickname} {get_qiyu_count(rank_list[i][1])}"
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg

    async def get_weiwang_rank(self):
        returnMsg = "本群威望排行榜"

        try:
            rank_list = sorted(self._jx3_users.items(), lambda x, y: cmp(x[1]['weiwang'], y[1]['weiwang']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['weiwang'] != 0:
                    qq_nickname = await get_group_nickname(self._qq_group, rank_list[i][0])
                    returnMsg += f"\n{i + 1}. {qq_nickname} {rank_list[i][1]['weiwang']}"
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg

    async def get_jjc_rank(self):
        returnMsg = ""

        try:
            returnMsg = f"名剑大会排名榜 赛季：{self._jjc_data['season']} 天数：{self._jjc_data['day']}"

            rank_list = sorted(self._jjc_data['current_season_data'].items(), lambda x, y: cmp(x[1]['score'], y[1]['score']), reverse=True)
            list_len = len(rank_list)
            for i in range(10):
                if i < list_len and rank_list[i][1]['score'] != 0:
                    qq_nickname = await get_group_nickname(self._qq_group, rank_list[i][0])
                    returnMsg += (
                        f"\n{i + 1}. {qq_nickname} "
                        f"分数：{rank_list[i][1]['score']} 段位：{min(rank_list[i][1]['score'] // 100, MAX_JJC_RANK)}"
                    )
                else:
                    break

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg

    async def get_wanted_list(self):
        returnMsg = ""

        try:
            msg_list = ""
            rank_list = sorted(self.wanted_list.items(), lambda x, y: cmp(x[1]['reward'], y[1]['reward']), reverse=True)
            index = 1
            for k, v in rank_list:
                if time.time() - self.wanted_list[k]['wanted_time'] < WANTED_DURATION:
                    remain_time_msg = get_remaining_time_string(WANTED_DURATION, self.wanted_list[k]['wanted_time'])
                    qq_nickname = await get_group_nickname(self._qq_group, k)
                    msg_list += f"\n{index}. {qq_nickname} {v['reward']}金 {remain_time_msg}"
                    index += 1

            if msg_list == "":
                msg_list = "\n暂无悬赏"

            returnMsg = "本群悬赏榜" + msg_list

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

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

        return (
            f"江湖恩怨一朝清，惟望群侠多援手。现有人愿付{money_amount}金对[CQ:at,qq={toQQ_str}]进行悬赏，"
            f"总赏金已达{self.wanted_list[toQQ_str]['reward']}金，众侠士切勿错过。"
        )

    def put_wanted(self, fromQQ: str, toQQ: str):
        returnMsg = []

        try:
            if self._jx3_users[fromQQ]['money'] < WANTED_MONEY_REWARD:
                returnMsg = f"[CQ:at,qq={fromQQ}] 金钱不足，无法悬赏。".format()
            elif self._jx3_users[toQQ]['daily_count']['jailed'] >= JAIL_TIMES_PROTECTION:
                returnMsg = f"[CQ:at,qq={fromQQ}] 对方今天已经被抓进去{JAIL_TIMES_PROTECTION}次了，无法悬赏。"
            else:
                self._jx3_users[fromQQ]['money'] -= WANTED_MONEY_REWARD

                returnMsg += f"[CQ:at,qq={fromQQ}] 悬赏成功！\n金钱-{WANTED_MONEY_REWARD}"
                returnMsg += self._put_wanted_internal(toQQ, WANTED_MONEY_REWARD)

        except Exception as e:
            logging.exception(e)
            returnMsg = []
            self.read_data(self.json_file_path)

        return returnMsg

    def get_cha_guan_quest(self, qq_account: str):
        returnMsg = ""

        try:
            daliy_stat = self._jx3_users[qq_account]['daily_count']['cha_guan']

            jail_status = self._is_in_jailed(qq_account)

            if jail_status != "":
                returnMsg = jail_status
            else:
                if len(daliy_stat['complete_quest']) >= len(CHA_GUAN_QUEST_INFO):
                    returnMsg = f"[CQ:at,qq={qq_account}] 你已经完成了{len(CHA_GUAN_QUEST_INFO)}个茶馆任务啦，明天再来吧。"
                elif self._jx3_users[qq_account]['energy'] < CHA_GUAN_ENERGY_COST:
                    returnMsg = f"[CQ:at,qq={qq_account}] 体力不足！需要消耗{CHA_GUAN_ENERGY_COST}体力。"
                elif daliy_stat['current_quest'] != "":
                    returnMsg = f"[CQ:at,qq={qq_account}] 你已经接了一个任务啦。\n当前任务：{CHA_GUAN_QUEST_INFO[daliy_stat['current_quest']]['display_name']}"
                else:
                    remain_quest = list(set(CHA_GUAN_QUEST_INFO.keys()) - set(daliy_stat['complete_quest']))

                    quest_name = remain_quest[random.randint(0, len(remain_quest) - 1)]

                    self._jx3_users[qq_account]['daily_count']['cha_guan']['current_quest'] = quest_name
                    quest = CHA_GUAN_QUEST_INFO[quest_name]

                    rewardMsg = ""
                    for k, v in quest['reward'].items():
                        rewardMsg += f"{USER_STAT_DISPLAY[k]}+{v} "

                    requireMsg = ""
                    for k, v in quest['require'].items():
                        requireMsg += f"{get_item_display_name(k)}x{v} "
                    requireMsg += f"体力：{CHA_GUAN_ENERGY_COST}"

                    returnMsg = (
                        f"[CQ:at,qq={qq_account}] 茶馆任务({len(daliy_stat['complete_quest']) + 1}/{len(CHA_GUAN_QUEST_INFO.keys())})\n"
                        f"{quest['display_name']}\n"
                        f"{quest['description']}\n"
                        f"需求：{requireMsg}\n"
                        f"奖励：{rewardMsg}"
                    )

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg


    def complete_cha_guan_quest(self, qq_account):
        returnMsg = ""

        try:
            jail_status = self._is_in_jailed(qq_account)
            if jail_status != "":
                returnMsg = jail_status
            else:
                if self._jx3_users[qq_account]['daily_count']['cha_guan']['current_quest'] != "":

                    daliy_stat = self._jx3_users[qq_account]['daily_count']['cha_guan']
                    quest = CHA_GUAN_QUEST_INFO[daliy_stat['current_quest']]

                    if self._jx3_users[qq_account]['energy'] < CHA_GUAN_ENERGY_COST:
                        returnMsg = f"[CQ:at,qq={qq_account}] 体力不足！需要消耗{CHA_GUAN_ENERGY_COST}体力。"
                    else:
                        has_require = True
                        for k, v in quest['require'].items():
                            has_require = has_require and k in self._jx3_users[qq_account]['bag'] and self._jx3_users[qq_account]['bag'][k] >= v

                        if has_require:
                            itemMsg = ""

                            for k, v in quest['require'].items():
                                self._jx3_users[qq_account]['bag'][k] -= v
                                if self._jx3_users[qq_account]['bag'][k] == 0:
                                    self._jx3_users[qq_account]['bag'].pop(k)
                                itemMsg += f"{get_item_display_name(k)}-{v} "

                            self._jx3_users[qq_account]['energy'] -= CHA_GUAN_ENERGY_COST
                            self._jx3_users[qq_account]['daily_count']['cha_guan']['complete_quest'].append(daliy_stat['current_quest'])
                            self._jx3_users[qq_account]['daily_count']['cha_guan']['current_quest'] = ""

                            rewardMsg = ""
                            for k, v in quest['reward'].items():
                                if k in self._jx3_users[qq_account]:
                                    self._jx3_users[qq_account][k] += v
                                    rewardMsg += f"{USER_STAT_DISPLAY[k]}+{v} "

                            returnMsg = (
                                f"[CQ:at,qq={qq_account}] 茶馆任务完成！"
                                f"{len(self._jx3_users[qq_account]['daily_count']['cha_guan']['complete_quest'])}/{len(CHA_GUAN_QUEST_INFO)}\n"
                                f"消耗任务物品：{itemMsg}\n"
                                f"体力-{CHA_GUAN_ENERGY_COST}\n"
                                f"获得奖励：{rewardMsg}"
                            )
                        else:
                            returnMsg = f"[CQ:at,qq={qq_account}] 任务物品不足！"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def do_qiyu(self, qiyu_type):
        returnMsg = ""

        try:
            logging.info(qiyu_type)

            for qq_account_str, qiyu_name in qiyu_type.items():
                qiyu = QIYU_LIST[qiyu_name]

                if qiyu_name in self.qiyu_status and self.qiyu_status[qiyu_name]['qq'] == qq_account_str and time.time() - self.qiyu_status[qiyu_name]['last_time'] < qiyu['cooldown']:
                    remaining_time_msg = get_remaining_time_string(qiyu['cooldown'], self.qiyu_status[qiyu_name]['last_time'])
                    logging.info(f"qiyu in cd! qq: {qq_account_str} remain_time: {remaining_time_msg}")
                else:
                    requireMsg = ""
                    require_meet = True
                    if 'require' in qiyu:
                        for k, v in qiyu['require'].items():
                            if k in self._jx3_users[qq_account_str]:
                                require_meet = require_meet and (self._jx3_users[qq_account_str][k] >= v)
                                requireMsg += f"{k}:{self._jx3_users[qq_account_str][k]} > {v}; "

                    if not require_meet:
                        logging.info(f"qiyu require not met! qq: {qq_account_str} require: {requireMsg}")
                    else:
                        rand = random.uniform(0, 1)

                        if rand > qiyu['chance']:
                            logging.info(f"No qiyu qq: {qq_account_str} chance: {rand} > {qiyu['chance']}")
                        else:
                            rewardMsg = ""
                            for k, v in qiyu['reward'].items():
                                if k in self._jx3_users[qq_account_str]:
                                    self._jx3_users[qq_account_str][k] += v
                                    rewardMsg += f"\n{USER_STAT_DISPLAY[k]}+{v}"

                            self._jx3_users[qq_account_str]['qiyu'][qiyu_name] += 1

                            if qiyu_name not in self.qiyu_status:
                                self.qiyu_status[qiyu_name] = {'qq': "", 'last_time': None}
                            self.qiyu_status[qiyu_name]['qq'] = qq_account_str
                            self.qiyu_status[qiyu_name]['last_time'] = time.time()

                            returnMsg = (
                                f"{qiyu['description'].format(qq_account_str)}\n"
                                f"获得奖励：{rewardMsg}"
                            )

                            logging.info(f"qiyu! qq: {qq_account_str} qiyu_name: {qiyu_name} success_chance: {rand} < {qiyu['chance']}")

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def get_jjc_info(self, qq_account: str):
        returnMsg = ""

        try:
            if qq_account not in self._jjc_data['current_season_data']:
                self._jjc_data['current_season_data'][qq_account] = {'score': 0, 'last_time': None, 'win': 0, 'lose': 0}

            jjc_status = self._jjc_data['current_season_data'][qq_account]

            total_match = jjc_status['win'] + jjc_status['lose']
            win_chance = int(jjc_status['win'] * 100 / total_match) if total_match > 0 else 100

            returnMsg = (
                f"[CQ:at,qq={qq_account}] 第{self._jjc_data['season']}赛季名剑大会分数："
                f"{jjc_status['score']} 段位：{jjc_status['score'] // 100} "
                f"胜负：{jjc_status['win']}/{total_match} 胜率：{win_chance}%"
            )

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg

    def join_class(self, qq_account: str, class_display_name):
        returnMsg = ""

        try:
            if self._jx3_users[qq_account]['class_id'] != 0:
                returnMsg = f"[CQ:at,qq={qq_account}] 你已经加入了门派{CLASS_LIST[self._jx3_users[qq_account]['class_id']]}！"
            elif class_display_name in CLASS_LIST.values():
                self._jx3_users[qq_account]['class_id'] = get_class_id_by_display_name(class_display_name)
                returnMsg = f"[CQ:at,qq={qq_account}] 加入门派{class_display_name}！"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def remove_lover(self, qq_account):
        returnMsg = ""

        try:
            if self._jx3_users[qq_account]['lover'] == 0:
                returnMsg = f"[CQ:at,qq={qq_account}] 你没有情缘，别乱用。"
            else:
                lover = self._jx3_users[qq_account]['lover']
                love_time = time.time() - self._jx3_users[qq_account]['lover_time']
                self._jx3_users[qq_account]['lover_time'] = None
                self._jx3_users[qq_account]['lover'] = ""
                self._jx3_users[lover]['lover_time'] = None
                self.jx3_user[lover]['lover'] = ""
                returnMsg = f"[CQ:at,qq={qq_account}] 决定去寻找新的旅程。"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def _get_leader_by_member(self, qq_account_str):
        for k, v in self._group_info.items():
            if qq_account_str in v['member_list']:
                return k
        return ""

    async def create_group(self, qq_account: str):
        returnMsg = ""

        try:
            if qq_account in self._group_info:
                returnMsg = f"[CQ:at,qq={qq_account}] 你已经创建了一个队伍了！"
            else:
                find_leader = self._get_leader_by_member(qq_account)
                if find_leader != "":
                    leader_nickname = await get_group_nickname(self._qq_group, find_leader)
                    returnMsg = "[CQ:at,qq={qq_account}] 你已经加入了 {leader_nickname} 的队伍！"
                else:
                    self._group_info[qq_account] = {
                        'member_list': [qq_account],
                        'create_time': time.time()
                    }
                    returnMsg = (
                        f"[CQ:at,qq={qq_account}] 创建队伍成功！请让队友输入【加入队伍[CQ:at,qq={qq_account}]】加入队伍。\n"
                        f"进入副本后此队伍无法被加入，请确认人数正确后再进入副本。"
                    )

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg


    async def join_group(self, qq_account: str, leader: str):
        returnMsg = ""

        try:

            if qq_account in self._group_info:
                returnMsg = f"[CQ:at,qq={qq_account}] 你已经创建了一个队伍，不能加入其他人的队伍，输入【退出队伍】退出当前队伍。"
            elif leader not in self._group_info:
                returnMsg = f"[CQ:at,qq={qq_account}] 队伍不存在。"
            elif leader in self.dungeon_status:
                leader_nickname = await get_group_nickname(self._qq_group, leader)
                returnMsg = f"[CQ:at,qq={qq_account}] {leader_nickname} 的队伍正在副本里，无法加入。"
            elif len(self._group_info[leader]['member_list']) >= MAX_GROUP_MEMBER:
                returnMsg = f"[CQ:at,qq={qq_account}] 队伍已满，无法加入。"
            else:
                find_leader = self._get_leader_by_member(qq_account)
                if find_leader != "":
                    leader_nickname = await get_group_nickname(self._qq_group, find_leader)
                    returnMsg = f"[CQ:at,qq={qq_account}] 你已经加入了 {1} 的队伍，输入【退出队伍】退出当前队伍"
                else:
                    self._group_info[leader]['member_list'].append(qq_account)
                    leader_nickname = await get_group_nickname(self._qq_group, leader)
                    returnMsg = f"[CQ:at,qq={qq_account}] 成功加入 {leader_nickname} 的队伍。"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg


    async def get_group_info(self, qq_account: str):
        returnMsg = ""

        try:
            if qq_account in self._group_info:
                leader = qq_account
            else:
                leader = self._get_leader_by_member(qq_account)

            if leader == "":
                returnMsg = f"[CQ:at,qq={qq_account}] 你没有加入任何队伍。"
            else:

                returnMsg = f"[CQ:at,qq={qq_account}] 当前队伍信息：\n"
                if self._group_info[leader]['member_list'] != []:
                    for member in self._group_info[leader]['member_list']:
                        member_nickname = await get_group_nickname(self._qq_group, leader)
                        returnMsg += (
                            f"\n{'(队长) ' if member == leader else ''}{member_nickname} "
                            f"pve装分：{self._jx3_users[member]['pve_gear_point']}"
                        )

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    async def quit_group(self, qq_account: str) -> str:
        returnMsg = ""

        try:
            if qq_account not in self._group_info:
                leader = self._get_leader_by_member(qq_account)
                if leader == "":
                    returnMsg = f"[CQ:at,qq={qq_account}] 你不在任何队伍里。"
                else:
                    self._group_info[leader]['member_list'].remove(qq_account)
                    leader_nickname = await get_group_nickname(self._qq_group, leader)
                    returnMsg = f"[CQ:at,qq={qq_account}] 你离开了 {leader_nickname} 的队伍。"
            else:
                self._group_info.pop(qq_account)
                if qq_account in self.dungeon_status:
                    self.dungeon_status.pop(qq_account)
                returnMsg = f"[CQ:at,qq={qq_account}] 你的队伍解散了。"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def kick_group(self, fromQQ: str, toQQ: str) -> str:
        returnMsg = ""

        try:
            if fromQQ not in self._group_info:
                returnMsg = f"[CQ:at,qq={fromQQ}] 你不是队长，无法使用此命令。"
            else:
                if toQQ not in self._group_info[fromQQ]:
                    returnMsg = f"[CQ:at,qq={fromQQ}] 对方不在你的队里。"
                else:
                    self._group_info[fromQQ]['member_list'].remove(toQQ)
                    returnMsg = f"[CQ:at,qq={toQQ}] 被[CQ:at,qq={fromQQ}] 踢出了队伍。"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""
            self.read_data(self.json_file_path)

        return returnMsg

    def list_dungeon(self, qq_account: str) -> str:
        returnMsg = ""

        try:
            returnMsg = f"[CQ:at,qq={qq_account}] 副本列表："
            val = self._jx3_users[qq_account]

            if 'dungeon' not in val['daily_count']:
                self._jx3_users[qq_account]['daily_count']['dungeon'] = {}

            gear_point = self._calculate_gear_point(val['equipment'])
            dungeon_list = sorted(DUNGEON_LIST.items(), lambda x, y: cmp(x[1]['max_pve_reward_gain'], y[1]['max_pve_reward_gain']))
            for k, v in dungeon_list:
                has_cd = k in val['daily_count']['dungeon'] and val['daily_count']['dungeon'][k] == True
                has_reward = gear_point['pve'] <= v['max_pve_reward_gain']
                can_enter = gear_point['pve'] >= v.get('min_pve_reward_enter', 0)
                can_enter_msg = "有cd" if has_cd else "可进入" if can_enter else "不可进入"
                has_reward_msg = "无boss奖励" if not has_reward else "有boss奖励" if can_enter else "装分不足"
                returnMsg += f"\n{v['display_name']} {can_enter_msg} {has_reward_msg}"

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg

    def start_dungeon(self, qq_account, dungeon_name) -> list:
        returnMsg = []

        try:
            dungeon_id = get_dungeon_id_by_display_name(dungeon_name)

            if 'dungeon' not in self._jx3_users[qq_account]['daily_count']:
                self._jx3_users[qq_account]['daily_count']['dungeon'] = {}
            
            val = self._jx3_users[qq_account]

            if dungeon_id != "":
                if qq_account not in self._group_info:
                    leader = self._get_leader_by_member(qq_account)
                    if leader == "":
                        returnMsg.append(f"[CQ:at,qq={qq_account}] 必须创建队伍才能进入副本。")
                    else:
                        returnMsg.append(f"[CQ:at,qq={qq_account}] 你不是队长！无法使用此命令。")
                elif qq_account in self.dungeon_status:
                    returnMsg.append(f"[CQ:at,qq={qq_account}] 你已经在副本里了。")
                else:
                    leader = qq_account
                    group = self._group_info[leader]

                    has_cd = False
                    cd_msg = ""
                    has_energy = True
                    energy_msg = ""

                    has_cd = []
                    no_energy = []
                    pve_gear_point_too_high = []
                    pve_gear_point_too_low = []

                    for m in group['member_list']:
                        val = self._jx3_users[m]
                        if val['daily_count']['dungeon'].get(dungeon_id, False) == True:
                            has_cd.append(m)
                        else:
                            pve_gear_point = self._calculate_gear_point(val['equipment'])['pve']

                            if pve_gear_point >= DUNGEON_LIST[dungeon_id]['max_pve_reward_gain'] and val['daily_count']['dungeon'].get(dungeon_id, True):
                                    pve_gear_point_too_high.append(m)
                                    self._jx3_users[m]['daily_count']['dungeon'][dungeon_id] = False
                            elif pve_gear_point < DUNGEON_LIST[dungeon_id].get('min_pve_reward_enter', 0):
                                pve_gear_point_too_low.append(m)
                            elif val['energy'] < DUNGEON_ENERGY_REQUIRED:
                                no_energy.append(m)

                    if len(has_cd) > 0:
                        returnMsg.append(f"队伍中{' '.join(['[CQ:at,qq={}}]'.format(m) for m in has_cd])}有此副本cd，无法进入。")
                    elif len(pve_gear_point_too_high) > 0:
                        returnMsg.append(
                            (
                                f"队伍中{' '.join(['[CQ:at,qq={}}]'.format(m) for m in pve_gear_point_too_high])}pve装备太厉害啦，"
                                f"已经不能获得boss奖励了，仅可获得通关奖励且不消耗体力。如果确定还要进本的话，请再次输入 进入副本{DUNGEON_LIST[dungeon_id]['display_name']}"
                            )
                        )
                    elif len(pve_gear_point_too_low) > 0:
                        returnMsg.append(
                            (
                                f"队伍中{' '.join(['[CQ:at,qq={}}]'.format(m) for m in pve_gear_point_too_low])}"
                                f"装分未满副本要求({DUNGEON_LIST[dungeon_id].getget('min_pve_reward_enter', 0)})，无法进入。"
                            )
                        )
                    elif len(no_energy) > 0:
                        returnMsg.append(f"队伍中{' '.join(['[CQ:at,qq={}}]'.format(m) for m in no_energy])}体力不足({DUNGEON_ENERGY_REQUIRED})，无法进入。")
                    else:
                        self.dungeon_status[leader] = copy.deepcopy(DUNGEON_LIST[dungeon_id])
                        self.dungeon_status[leader]['boss_detail'] = []
                        self.dungeon_status[leader]['attack_count'] = {}
                        self.dungeon_status[leader]['no_reward'] = copy.deepcopy(pve_gear_point_too_high)
                        
                        for boss_id in self.dungeon_status[leader]['boss']:
                            boss = copy.deepcopy(NPC_LIST[boss_id])
                            boss['remain_hp'] = boss['equipment']['armor']['pve']
                            self.dungeon_status[leader]['boss_detail'].append(boss)

                        energy_msg = ""

                        for m in group['member_list']:
                            self._jx3_users[m]['daily_count']['dungeon'][dungeon_id] = True
                            if m not in pve_gear_point_too_high:
                                self._jx3_users[m]['energy'] -= DUNGEON_ENERGY_REQUIRED
                                energy_msg += "[CQ:at,qq={0}] ".format(m)
                        returnMsg.append(f"[CQ:at,qq={qq_account}] 进入副本 {dungeon_name} 成功！{energy_msg}体力-{DUNGEON_ENERGY_REQUIRED}")

                        boss = self.dungeon_status[leader]['boss_detail'][0]
                        returnMsg.append(
                            (
                                f"boss战：{boss['display_name']} (1/{len(self.dungeon_status[leader]['boss_detail'])}\n"
                                f"请输入每位队员输入【攻击boss】开始战斗。"
                            )
                        )

        except Exception as e:
            logging.exception(e)
            returnMsg = []
            self.read_data(self.json_file_path)

        return returnMsg

    async def get_current_boss_info(self, qq_account: str) -> str:
        returnMsg = ""

        try:
            if qq_account in self.group_info:
                leader = qq_account
            else:
                leader = self._get_leader_by_member(qq_account)

            dungeon = self.dungeon_status.get(leader, {})

            if dungeon != {} and leader != "":
                current_boss = dungeon['boss_detail'][0]
                rank_list = sorted(dungeon['attack_count'].items(), lambda x, y: cmp(x[1]['damage'], y[1]['damage']), reverse=True)
                list_len = len(rank_list)
                damage_msg = ""
                for i in range(MAX_GROUP_MEMBER):
                    if i < list_len:
                        nickname = await get_group_nickname(self.qq_group, int(rank_list[i][0]))
                        damage_msg += (
                            f"\n{i + 1}. {nickname} 伤害：{rank_list[i][1]['damage']}"
                            f" 次数：{dungeon['attack_count'][rank_list[i][0]]['success_attack_count']}/{dungeon['attack_count'][rank_list[i][0]]['total_attack_count']}"
                        )
                    else:
                        break

                current_boss_index = len(dungeon['boss']) - len(dungeon['boss_detail']) + 1
                boss_gear_point = self._calculate_gear_point(current_boss['equipment'])['pve']
                returnMsg = (
                    f"[CQ:at,qq={qq_account}] 当前副本：{dungeon['display_name']} "
                    f"当前boss：{current_boss['display_name']} {current_boss_index}/{len(dungeon['boss'])}\n"
                    f"血量：{current_boss['remain_hp']}/{current_boss['equipment']['armor']['pve']} pve装分：{boss_gear_point}\n"
                    f"伤害排行榜：{damage_msg}"
                )

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg

    def get_dungeon_info(self, qq_account: str, dungeon_name: str) -> str:
        returnMsg = ""

        try:
            dungeon_id = get_dungeon_id_by_display_name(dungeon_name)
            
            if dungeon_id != "":
                dungeon = DUNGEON_LIST[dungeon_id]
                boss_msg = ""
                for boss_id in dungeon['boss']:
                    boss = NPC_LIST[boss_id]
                    boss_gear_point = self._calculate_gear_point(boss['equipment'])['pve']
                    boss_msg += f"\nboss: {boss['display_name']} 装分：{boss_gear_point}"
                
                reward_msg = " ".join([f"{USER_STAT_DISPLAY[k]}+{v}" for k, v in dungeon['reward'].items()])
                returnMsg = (
                    f"[CQ:at,qq={qq_account}] 【{dungeon['display_name']}】副本信息："
                    f"{boss_msg}\n"
                    f"副本装分区间：{dungeon['min_pve_reward_enter']} ~ {dungeon['max_pve_reward_gain']}\n"
                    f"体力要求：{DUNGEON_ENERGY_REQUIRED} 通关奖励：{reward_msg}"
                )

        except Exception as e:
            logging.exception(e)
            returnMsg = ""

        return returnMsg