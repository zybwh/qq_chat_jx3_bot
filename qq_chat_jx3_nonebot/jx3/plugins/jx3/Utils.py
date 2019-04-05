import logging

from nonebot import get_bot

async def get_group_nickname(qq_group, qq_account):
    bot = get_bot()
    try:
        info = await bot.get_group_member_info(group_id=int(qq_group), user_id=int(qq_account))
        print(info)
        return info['card'] if info.get('card' '') != '' else info['nickname']
    except Exception as e:
        logging.exception(e)