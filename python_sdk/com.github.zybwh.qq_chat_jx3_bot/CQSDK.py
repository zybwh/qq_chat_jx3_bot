# -*- coding:gbk -*-
# -*- coding: utf-8 -*-
import _CQSDK

EVENT_IGNORE        = 0     # �¼�_����
EVENT_BLOCK         = 1     # �¼�_����

REQUEST_ALLOW       = 1     # ����_ͨ��
REQUEST_DENY        = 2     # ����_�ܾ�

REQUEST_GROUPADD    = 1     # ����_Ⱥ���
REQUEST_GROUPINVITE = 2     # ����_Ⱥ����

CQLOG_DEBUG         = 0     # ���� ��ɫ
CQLOG_INFO          = 10    # ��Ϣ ��ɫ
CQLOG_INFOSUCCESS   = 11    # ��Ϣ(�ɹ�) ��ɫ
CQLOG_INFORECV      = 12    # ��Ϣ(����) ��ɫ
CQLOG_INFOSEND      = 13    # ��Ϣ(����) ��ɫ
CQLOG_WARNING       = 20    # ���� ��ɫ
CQLOG_ERROR         = 30    # ���� ��ɫ
CQLOG_FATAL         = 40    # �������� ���


def MessageBox(msg, title):
    return _CQSDK.MessageBox(msg, title)

def GetAppID():
    return _CQSDK.GetAppID()

def SendPrivateMsg(QQID, msg):
    return _CQSDK.SendPrivateMsg(QQID, msg)
def SendGroupMsg(groupid, msg):
    return _CQSDK.SendGroupMsg(groupid, msg)

def SendDiscussMsg(discussid, msg):
    return _CQSDK.SendDiscussMsg(discussid, msg)

def SendLike(QQID):
    return _CQSDK.SendLike(QQID)

def SetGroupKick(groupid, QQID, rejectaddrequest):
    return _CQSDK.SetGroupKick(groupid, QQID, rejectaddrequest)

def SetGroupBan(groupid, QQID, duration):
    return _CQSDK.SetGroupBan(groupid, QQID, duration)

def SetGroupAdmin(groupid, QQID, setadmin):
    return _CQSDK.SetGroupAdmin(groupid, QQID, setadmin)

def SetGroupWholeBan(groupid, enableban):
    return _CQSDK.SetGroupWholeBan(groupid, enableban)

def SetGroupAnonymousBan(groupid, anomymous, duration):
    return _CQSDK.SetGroupAnonymousBan(groupid, anomymous, duration)

def SetGroupAnonymous(groupid, enableanomymous):
    return _CQSDK.SetGroupAnonymous(groupid, enableanomymous)

def SetGroupCard(groupid, QQID, newcard):
    return _CQSDK.SetGroupCard(groupid, QQID, newcard)

def SetGroupLeave(groupid, isdismiss):
    return _CQSDK.SetGroupLeave(groupid, isdismiss)

def SetGroupSpecialTitle(groupid, QQID, newspecialtitle, duration):
    return _CQSDK.SetGroupSpecialTitle(groupid, QQID, newspecialtitle, duration)

def SetDiscussLeave(discussid):
    return _CQSDK.SetDiscussLeave(discussid)

def SetFriendAddRequest(responseflag, responseoperation, remark):
    return _CQSDK.SetFriendAddRequest(responseflag, responseoperation, remark)

def SetGroupAddRequestV2(responseflag, requesttype, responseoperation, reason):
    return _CQSDK.SetGroupAddRequestV2(responseflag, requesttype, responseoperation, reason)

def GetGroupMemberInfoV2(groupid, QQID, nocache = False):
    return _CQSDK.GetGroupMemberInfoV2(groupid, QQID, nocache)

def GetGroupMemberList(groupid):
    return _CQSDK.GetGroupMemberList(groupid)
    
def GetStrangerInfo(QQID, nocache = False):
    return _CQSDK.GetStrangerInfo(QQID, nocache)

def AddLog(priority, category, content):
    return _CQSDK.AddLog(priority, category, content)

def GetCookies():
    return _CQSDK.GetCookies()

def GetCsrfToken():
    return _CQSDK.GetCsrfToken()

def GetLoginQQ():
    return _CQSDK.GetLoginQQ()

def GetLoginNick():
    return _CQSDK.GetLoginNick()

def GetAppDirectory():
    return _CQSDK.GetAppDirectory()

def SetFatal(errorinfo):
    return _CQSDK.SetFatal(errorinfo)

def GetGroupList():
    return _CQSDK.GetGroupList()
