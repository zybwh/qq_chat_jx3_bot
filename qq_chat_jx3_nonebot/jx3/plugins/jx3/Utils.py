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
    
def get_remaining_time_string(duration, last_time):
    remain_secs = int(math.floor(duration - (time.time() - last_time)))
    hours = remain_secs // 3600
    mins = (remain_secs - hours * 3600) // 60
    secs = remain_secs - hours * 3600 - mins * 60
    return '{0}小时{1}分{2}秒'.format(hours, mins, secs)