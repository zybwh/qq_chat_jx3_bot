#-*- coding: utf-8 -*-
import base64
from CQPack import CQUnpack
class CQGroupListInfo(object):
	GroupID                 = None
	GroupName               = None
	def __init__(self, data, is_base64 = True):
		data = base64.decodestring(data) if is_base64 else data
		info = CQUnpack(data)
		self.GroupID                        = info.GetLong()
		self.GroupName                      = info.GetLenStr()
	def __GroupInfoStr__(self):
		t = {
			'qq群号' : self.GroupID,
			'群名称' : self.GroupName,
		}
		lines = []
		for (k, v) in t.items():
			lines.append('{0}:{1}'.format(k, v))
		return '\n'.join(lines)

	def _groupID_(self):
		return self.GroupID

def GetGrouplistInfo(data):
	memList =[]
	data = base64.decodestring(data)
	info = CQUnpack(data)
	count = info.GetInt()
	while count:
		if info.Len() <= 0:
			break
		retData = info.GetLenStr()
		memInfo = CQGroupListInfo(retData,False).__GroupInfoStr__()
		memList.append(memInfo)
	return memList

def GetGroupIDlist(data):
	memList =[]
	data = base64.decodestring(data)
	info = CQUnpack(data)
	count = info.GetInt()
	while count:
		if info.Len() <= 0:
			break
		retData = info.GetLenStr()
		memInfo = CQGroupListInfo(retData,False)._groupID_()
		memList.append(memInfo)
	return memList

