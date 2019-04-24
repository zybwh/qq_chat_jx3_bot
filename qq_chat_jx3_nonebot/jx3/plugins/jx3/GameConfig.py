HELP_URL = 'https://www.jianshu.com/p/94b3cf27dcd7'

LOVE_ITEM_REQUIRED = 'zhen_cheng_zhi_xin'

DALIY_REFRESH_OFFSET = 7 * 60 * 60
DALIY_COUNT_SAVE_DAY = 3
DALIY_REWARD_MIN = 1000
DALIY_REWARD_MAX = 3000
DALIY_ENERGY_REWARD = 500
DALIY_MONEY_REWARD = 100

DALIY_MAX_SPEECH_ENERGY_GAIN = 500
SPEECH_ENERGY_GAIN = 5

YA_BIAO_ENERGY_REQUIRED = 50
MAX_DALIY_YA_BIAO_COUNT = 3
DALIY_YA_BIAO_REWARD_MIN = 1000
DALIY_YA_BIAO_REWARD_MAX = 3000
DALIY_YA_BIAO_MONEY_REWARD = 50
YA_BIAO_FACTION_POINT_GAIN = 1000

WA_BAO_ENERGY_REQUIRED = 50
MAX_DALIY_WA_BAO_COUNT = 10
WA_BAO_COOLDOWN = 10 * 60
WA_BAO_RARE_FACTOR = 2

MAX_DALIY_CHA_GUAN_COUNT = 5
CHA_GUAN_ENERGY_COST = 30
CHA_GUAN_FINAL_REWARD_MONEY = 100
CHA_GUAN_FINAL_REWARD_BANGGONG_MIN = 1000
CHA_GUAN_FINAL_REWARD_BANGGONG_MAX = 3000

FACTION_REJOIN_CD_SECS = 24 * 60 * 60
FACTION_TRANSFER_WEIWANG_COST = 5000
FACTION_QUIT_EMPTY_WEIWANG = True
NO_FACTION_ALLOW_YA_BIAO = False

ROB_ENERGY_COST = 30
ROB_PROTECT_COUNT = 2
ROB_PROTECT_DURATION = 30 * 60
ROB_LOSE_COOLDOWN = 10 * 60
ROB_SAME_FACTION_PROTECTION = True
ROB_GAIN_FACTOR_MIN = 0.05
ROB_GAIN_FACTOR_MAX = 0.1
ROB_LOST_MONEY = True
ROB_LOST_WEIWANG = True
ROB_PROTECT_NO_LOST_COUNT = 3
ROB_DALIY_MAX_WEIWANG_GAIN = 5000
ROB_DALIY_MAX_MONEY_GAIN = 300
ROB_WIN_WANTED_CHANCE = 0.1
ROB_LOSE_WANTED_CHANCE = 0.05
ROB_WANTED_REWARD = 200
ROB_FACTION_POINT_GAIN = 100

PRACTISE_ENERGY_COST = 50
DALIY_PRACITSE_WEIWANG_GAIN = 5000
PRACTISE_LOSER_GAIN_PERCENTAGE = 0.5
PRACTISE_WEIWANG_GAIN_MIN = 800
PRACTISE_WEIWANG_GAIN_MAX = 1200
PRACTISE_FACTION_POINT_GAIN = 50

WANTED_MONEY_REWARD = 1000
WANTED_DURATION = 24 * 60 * 60
WANTED_COOLDOWN = 10 * 60
WANTED_ENERGY_COST = 50

JAIL_DURATION = 1 * 60 * 60
JAIL_TIMES_PROTECTION = 2

JJC_ENERGY_COST = 20
JJC_REWARD_WEIWANG_MIN = 100
JJC_REWARD_WEIWANG_MAX = 150
JJC_REWARD_RANK = 10
JJC_COOLDOWN = 10 * 60
JJC_GEAR_MODIFIER = 0.5
JJC_RANK_DIFF_PROTECTION = 2
JJC_REWARD_RANK_MODIFIER = 0.1
DALIY_JJC_DOUBLE_REWARD_COUNT = 5
JJC_DAYS_PER_SEASON = 7
MAX_JJC_RANK = 14

MAX_GROUP_MEMBER = 5

DUNGEON_MAX_ATTACK_COUNT = 5
DUNGEON_ATTACK_COOLDOWN = 10 * 60
DUNGEON_ENERGY_REQUIRED = 100

CHA_GUAN_QUEST_INFO = {
    "cha_guan_sui_rou": {
        "display_name": "茶馆：碎肉",
        "description": "需要提交一份碎肉，可在商店购买。",
        "require": {"sui_rou": 1},
        "reward": {"money": 50, "banggong": 500}
    },
    "cha_guan_cu_bu": {
        "display_name": "茶馆：粗布",
        "description": "需要提交一份粗布，可在商店购买。",
        "require": {"cu_bu": 1},
        "reward": {"money": 50, "banggong": 500}
    },
    "cha_guan_gan_cao": {
        "display_name": "茶馆：甘草",
        "description": "需要提交一份甘草，可在商店购买。",
        "require": {"gan_cao": 1},
        "reward": {"money": 50, "banggong": 500}
    },
    "cha_guan_hong_tong": {
        "display_name": "茶馆：红铜",
        "description": "需要提交一份红铜，可在商店购买。",
        "require": {"hong_tong": 1},
        "reward": {"money": 50, "banggong": 500}
    },
    "cha_guan_hun_hun": {
        "display_name": "茶馆：抓捕混混",
        "description": "抓捕混混三个。使用指令 抓捕混混",
        "require": {"hun_hun_zheng_ming": 3},
        "reward": {"money": 50, "banggong": 500}
    }
}