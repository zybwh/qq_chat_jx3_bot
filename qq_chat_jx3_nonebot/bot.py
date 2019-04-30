import os

import nonebot
import config
import logging

DATABASE_PATH = os.path.join(os.getcwd(), 'data')
LOG_FILE_NAME = os.path.join(DATABASE_PATH, 'bot.log')

if not os.path.exists(DATABASE_PATH):
    os.makedirs(DATABASE_PATH)

logging.basicConfig(
    level       = logging.INFO,
    format      = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt     = '%Y-%m-%d %H:%M:%S',
    handlers    = [logging.FileHandler(LOG_FILE_NAME, 'w+', 'utf-8')]
)

if __name__ == '__main__':
    nonebot.init(config)
    nonebot.load_plugins(
        os.path.join(os.path.dirname(__file__), 'jx3', 'plugins'),
        'jx3.plugins',
    )
    nonebot.run(host='0.0.0.0', port=8080)