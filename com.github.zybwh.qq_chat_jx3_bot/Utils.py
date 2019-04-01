
def get_key_or_return_default(dictionary, key, default_value):
    return dictionary[key] if key in dictionary else default_value

def get_group_nick_name(fromGroup, fromQQ):
    from CQGroupMemberInfo import CQGroupMemberInfo
    info = CQGroupMemberInfo(CQSDK.GetGroupMemberInfoV2(fromGroup, fromQQ))
    return info.Card if info.Card != None and info.Card != "" else info.Nickname if info.Nickname != None else str(fromQQ)
