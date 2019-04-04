import logging

from nonebot import get_bot

def get_group_nick_name(qq_group, qq_account):
    bot = get_bot()
    try:
        info = bot.get_group_member_info(group_id=int(qq_group), user_id=int(qq_account))
        print(info)
        return info['card'] if info.get('card' '') != '' else info['nickname']
    except Exception as e:
        logging.exception(e)