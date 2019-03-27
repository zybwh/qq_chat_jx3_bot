# -*- coding:gbk -*-

import sys
reload(sys)
sys.setdefaultencoding('gbk')

import os
import logging
import json

from threading import Lock

logging.basicConfig(
    level       = logging.INFO,
    format      = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt     = '%Y-%m-%d %H:%M:%S',
    filename    = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'CQHanlder.log'),
    filemode    = 'w+'
)

import CQSDK

try:
    import Jx3Handler
except Exception as e:
    logging.exception(e)

DATABASE_PATH = os.path.join('data', 'app', 'com.github.qq_jx3_chat_bot')
GROUP_DATA_JSON_FILE = os.path.join(DATABASE_PATH, 'jx3_group.json')
HELP_URL = 'https://www.jianshu.com/p/94b3cf27dcd7'

class CQHandler(object):

    group_data = {}
    active_group = []

    def __init__(self):
        logging.info('__init__')
        try:
            if not os.path.exists(DATABASE_PATH):
                os.makedirs(DATABASE_PATH)
            
            if os.path.exists(GROUP_DATA_JSON_FILE):
                with open(GROUP_DATA_JSON_FILE, 'r') as f:
                    data =  json.loads(f.readline())
                    for group in data:
                        self.active_group.append(group)
                        self.group_data[str(group)] = Jx3Handler.Jx3Handler(int(group))
            
            logging.info(self.active_group)
        except Exception as e:
            logging.exception(e)

        self.mutex = Lock()
        
    def __del__(self):
        logging.info('__del__')
        
    def _register_group(self, fromGroup):
        logging.info('_register_group: {0}'.format(fromGroup))

        try:
            self.mutex.acquire()
            self.active_group.append(fromGroup)
            self.group_data[str(fromGroup)] = Jx3Handler.Jx3Handler(int(fromGroup))
            with open(GROUP_DATA_JSON_FILE, 'w') as f:
                f.write(json.dumps(self.active_group))
            self.mutex.release()        
        except Exception as e:
            logging.exception(e)

    def OnEvent_Enable(self):
        logging.info('OnEvent_Enable')

    def OnEvent_Disable(self):
        logging.info('OnEvent_Disable')

    def OnEvent_PrivateMsg(self, subType, sendTime, fromQQ, msg, font):
        logging.info('OnEvent_PrivateMsg: subType={0}, sendTime={1}, fromQQ={2}, msg={3}, font={4}'.format(subType, sendTime, fromQQ, msg, font))

        try:
            CQSDK.SendPrivateMsg(fromQQ, msg)
        except Exception as e:
            logging.exception(e)

    def OnEvent_GroupMsg(self, subType, sendTime, fromGroup, fromQQ, fromAnonymous, msg, font):
        logging.info('OnEvent_GroupMsg: subType={0}, sendTime={1}, fromGroup={2}, fromQQ={3}, fromAnonymous={4}, msg={5}, font={6}'.format(subType, sendTime, fromGroup, fromQQ, fromAnonymous, msg, font))

        # TODO: move to on add group request
        if fromGroup not in self.active_group:
            self._register_group(fromGroup)

        jx3Handler = self.group_data[str(fromGroup)]

        returnMsg = ""
        qiyu_type = {}
        try:
            if msg == "注册":
                returnMsg = jx3Handler.register(fromQQ)
            elif msg == "指令":
                    returnMsg = "指令说明：{0}".format(HELP_URL)
            elif jx3Handler.isUserRegister(fromQQ):
                jx3Handler.addSpeechCount(fromQQ)
                qiyu_type = {str(fromQQ): 'fu_yao_jiu_tian'}

                if '[CQ:image,file=' in msg:
                    qiyu_type = {str(fromQQ): 'luan_shi_wu_ji'}

                if msg == "查看":
                    returnMsg = jx3Handler.getInfo(fromGroup, fromQQ)
                elif msg == "查看装备":
                    returnMsg = jx3Handler.get_equipment_info(fromQQ)
                elif msg == "查看阵营":
                    returnMsg = jx3Handler.get_faction_info()
                elif msg == "查看悬赏":
                    returnMsg = jx3Handler.get_wanted_list()
                elif msg == "pve装分排行":
                    returnMsg = jx3Handler.get_pve_gear_point_rank()
                elif msg == "pvp装分排行":
                    returnMsg = jx3Handler.get_pvp_gear_point_rank()
                elif msg == "土豪排行":
                    returnMsg = jx3Handler.get_money_rank()
                elif msg == "聊天排行":
                    returnMsg = jx3Handler.get_speech_rank(fromQQ)
                elif msg == "奇遇排行":
                    returnMsg = jx3Handler.get_qiyu_rank()
                elif msg == "威望排行":
                    returnMsg = jx3Handler.get_weiwang_rank()
                elif msg == "签到":
                    returnMsg = jx3Handler.qianDao(fromQQ)
                    if '签到成功' in returnMsg:
                        qiyu_type = {str(fromQQ): 'hong_fu_qi_tian'}
                elif "绑定情缘[CQ:at,qq=" in msg:
                    msg_list = msg.split("绑定情缘[CQ:at,qq=")
                    if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "":
                        toQQ = msg_list[1].strip('] ')
                        if int(toQQ) == fromQQ:
                            returnMsg = "[CQ:at,qq={0}]为什么要和自己绑定情缘？你也太惨了吧".format(fromQQ)
                        else:
                            returnMsg = jx3Handler.addLover(fromQQ, toQQ)
                elif msg == "同意":
                    returnMsg = jx3Handler.acceptLover(fromGroup, fromQQ)
                elif msg == "拒绝":
                    returnMsg = jx3Handler.rejectLover(fromQQ)
                elif msg == "押镖":
                    returnMsg = jx3Handler.yaBiao(fromQQ)
                    if "押镖成功" in returnMsg:
                        qiyu_type = {str(fromQQ): 'hu_you_cang_sheng'}
                elif msg == "背包":
                    returnMsg = jx3Handler.checkBag(fromQQ)
                elif "加入阵营" in msg:
                    msg_list = msg.split("加入阵营")
                    if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "":
                        faction_str = msg_list[1].rstrip()
                        returnMsg = jx3Handler.joinFaction(fromQQ, faction_str)
                elif msg == "退出阵营":
                    returnMsg = jx3Handler.quitFaction(fromQQ)
                elif msg == "转换阵营":
                    returnMsg = jx3Handler.transferFaction(fromQQ)
                elif "打劫[CQ:at,qq=" in msg:
                    msg_list = msg.split("打劫[CQ:at,qq=")
                    if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "":
                        toQQ = msg_list[1].strip('] ')
                        if int(toQQ) == fromQQ:
                            returnMsg = "[CQ:at,qq={0}] 为什么要打劫自己？".format(fromQQ)
                        else:
                            returnMsg = jx3Handler.rob(fromGroup, fromQQ, toQQ)
                        if '打劫成功' in returnMsg:
                            qiyu_type = {str(fromQQ): 'hu_xiao_shan_lin', str(toQQ): 'yin_yang_liang_jie'}
                elif "购买" in msg:
                    msg_list = msg.split("购买")
                    if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "":
                        msg_list_2 = msg_list[1].split("*")
                        item_amount = 1
                        if len(msg_list_2) == 2 and msg_list_2[1] != "":
                            item_amount = int(msg_list_2[1])
                        returnMsg = jx3Handler.buyItem(fromQQ, msg_list_2[0], item_amount)
                elif "使用" in msg:
                    if "使用真橙之心[CQ:at,qq=" in msg:
                        msg_list = msg.split("使用真橙之心[CQ:at,qq=")
                        if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "":
                            toQQ = msg_list[1].strip('] ')
                            if int(toQQ) == fromQQ:
                                returnMsg = "[CQ:at,qq={0}] 不能对自己使用真橙之心".format(fromQQ)
                            else:
                                returnMsg = jx3Handler.use_firework("真橙之心", fromQQ, toQQ)
                    else:
                        msg_list = msg.split("使用")
                        if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "":
                            msg_list_2 = msg_list[1].split("*")
                            item_amount = 1
                            if len(msg_list_2) == 2 and msg_list_2[1] != "":
                                item_amount = int(msg_list_2[1])
                            returnMsg = jx3Handler.useItem(fromQQ, msg_list_2[0], item_amount)
                elif msg == "商店":
                    returnMsg = jx3Handler.shopList(fromQQ)
                elif msg == "挖宝":
                    returnMsg = jx3Handler.waBao(fromQQ)
                    if "挖到了" in returnMsg:
                        qiyu_type = {str(fromQQ): 'san_shan_si_hai'}
                elif "武器更名" in msg:
                    msg_list = msg.split("武器更名")
                    if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "" and len(msg_list) <= 50:
                        returnMsg = jx3Handler.change_weapon_name(fromQQ, msg_list[1])
                elif "防具更名" in msg:
                    msg_list = msg.split("防具更名")
                    if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "" and len(msg_list) <= 50:
                        returnMsg = jx3Handler.change_armor_name(fromQQ, msg_list[1])
                elif "悬赏[CQ:at,qq=" in msg:
                    msg_list = msg.split("悬赏[CQ:at,qq=")
                    if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "":
                            toQQ = msg_list[1].strip('] ')
                            if int(toQQ) == fromQQ:
                                returnMsg = "[CQ:at,qq={0}] 为什么要悬赏自己？".format(fromQQ)
                            else:
                                returnMsg = jx3Handler.put_wanted(fromQQ, toQQ)
                elif "抓捕[CQ:at,qq=" in msg:
                    msg_list = msg.split("抓捕[CQ:at,qq=")
                    if len(msg_list) == 2 and msg_list[0] == "" and msg_list[1] != "":
                            toQQ = msg_list[1].strip('] ')
                            if int(toQQ) == fromQQ:
                                returnMsg = "[CQ:at,qq={0}] 就算你有悬赏，也不能抓捕自己啊。".format(fromQQ)
                            else:
                                returnMsg = jx3Handler.catch_wanted(fromQQ, toQQ)
                            if '成功抓捕' in returnMsg:
                                qiyu_type = {str(fromQQ): 'qing_feng_bu_wang', str(toQQ): 'yin_yang_liang_jie'}
                elif msg == "茶馆":
                    returnMsg = jx3Handler.get_cha_guan_quest(fromQQ)
                elif msg == "交任务":
                    returnMsg = jx3Handler.complete_cha_guan_quest(fromQQ)
                    if '任务完成' in returnMsg:
                        qiyu_type = {str(fromQQ): 'cha_guan_qi_yuan'}
                elif msg == "抓捕混混":
                    returnMsg = jx3Handler.catch_hun_hun(fromQQ)
            elif msg in jx3Handler.getCommandList():
                returnMsg = "大侠还未注册！无法使用指令"

            if returnMsg != "":
                CQSDK.SendGroupMsg(fromGroup, returnMsg)

            if qiyu_type != {}:
                returnMsg = jx3Handler.do_qiyu(qiyu_type)
                if returnMsg != "":
                    CQSDK.SendGroupMsg(fromGroup, returnMsg)
        except Exception as e:
            logging.exception(e)

    def OnEvent_DiscussMsg(self, subType, sendTime, fromDiscuss, fromQQ, msg, font):
        logging.info('OnEvent_DiscussMsg: subType={0}, sendTime={1}, fromDiscuss={2}, fromQQ={3}, msg={4}, font={5}'.format(subType, sendTime, fromDiscuss, fromQQ, msg, font))

    def OnEvent_System_GroupAdmin(self, subType, sendTime, fromGroup, beingOperateQQ):
        logging.info('OnEvent_System_GroupAdmin: subType={0}, sendTime={1}, fromGroup={2}, beingOperateQQ={3}'.format(subType, sendTime, fromGroup, beingOperateQQ))

    def OnEvent_System_GroupMemberDecrease(self, subType, sendTime, fromGroup, fromQQ, beingOperateQQ):
        logging.info('OnEvent_System_GroupMemberDecrease: subType={0}, sendTime={1}, fromGroup={2}, fromQQ={3}, beingOperateQQ={4}'.format(subType, sendTime, fromGroup, fromQQ, beingOperateQQ))

    def OnEvent_System_GroupMemberIncrease(self, subType, sendTime, fromGroup, fromQQ, beingOperateQQ):
        logging.info('OnEvent_System_GroupMemberIncrease: subType={0}, sendTime={1}, fromGroup={2}, fromQQ={3}, beingOperateQQ={4}'.format(subType, sendTime, fromGroup, fromQQ, beingOperateQQ))

    def OnEvent_Friend_Add(self, subType, sendTime, fromQQ):
        logging.info('OnEvent_Friend_Add: subType={0}, sendTime={1}, fromQQ={2}'.format(subType, sendTime, fromQQ))

    def OnEvent_Request_AddFriend(self, subType, sendTime, fromQQ, msg, responseFlag):
        logging.info('OnEvent_Request_AddFriend: subType={0}, sendTime={1}, fromQQ={2}, msg={3}, responseFlag={4}'.format(subType, sendTime, fromQQ, msg, responseFlag))

    def OnEvent_Request_AddGroup(self, subType, sendTime, fromGroup, fromQQ, msg, responseFlag):
        logging.info('OnEvent_Request_AddGroup: subType={0}, sendTime={1}, fromGroup={2}, fromQQ={3}, msg={4}, responseFlag={5}'.format(subType, sendTime, fromGroup, fromQQ, msg, responseFlag))

    def OnEvent_Menu01(self):
        logging.info('OnEvent_Menu01')

    def OnEvent_Menu02(self):
        logging.info('OnEvent_Menu02')

    def OnEvent_Menu03(self):
        logging.info('OnEvent_Menu03')

    def OnEvent_Menu04(self):
        logging.info('OnEvent_Menu04')

    def OnEvent_Menu05(self):
        logging.info('OnEvent_Menu05')

    def OnEvent_Menu06(self):
        logging.info('OnEvent_Menu06')

    def OnEvent_Menu07(self):
        logging.info('OnEvent_Menu07')

    def OnEvent_Menu08(self):
        logging.info('OnEvent_Menu08')

    def OnEvent_Menu09(self):
        logging.info('OnEvent_Menu09')
