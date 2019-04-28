DUNGEON_LIST = {
    'san_cai_zhen': {
        "display_name": "三才阵",
        'min_pve_reward_enter': 0,
        "max_pve_reward_gain": 12000,
        "boss": ['xiong_chi', 'deng_wen_feng', 'shang_zhong_yong'],
        "reward": {
            "banggong": 1000
        },
        "mvp_reward": {
            "bamggong": 500
        }
    },
    'tian_gong_fang': {
        "display_name": "天工坊",
        'min_pve_reward_enter': 10000,
        "max_pve_reward_gain": 25000,
        "boss": ['fang_ji_chang', 'ping_san_zhi', 'si_tu_yi_yi'],
        "reward": {
            "banggong": 2000
        },
        "mvp_reward": {
            "bamggong": 1000
        }
    },
    'kong_wu_feng': {
        "display_name": "空雾峰",
        'min_pve_reward_enter': 20000,
        "max_pve_reward_gain": 40000,
        "boss": ['feng_du', 'wang_yan_zhi', 'gui_ying_xiao_ci_lang'],
        "reward": {
            "banggong": 2000
        },
        "mvp_reward": {
            "bamggong": 1000
        }
    }
}

NPC_LIST = {
    "hun_hun": {
        "display_name": "熊痴",
        "equipment": {'weapon': {"display_name": "混混棍", 'pvp': 0, 'pve': 10},
                        'armor': {"display_name": "混混衣", 'pvp': 0, 'pve': 50}},
        "reward": {"money": 50},
        "reward_chance": 0.5
    },
    'xiong_chi': {
        "display_name": "熊痴",
        "equipment": {'weapon': {"display_name": "熊痴拳套", 'pvp': 0, 'pve': 100},
                        'armor': {"display_name": "熊痴衣", 'pvp': 0, 'pve': 500}},
        "reward": {
            "money": 50,
            "banggong": 2000,
        },
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.2,
            "ran": 0.2
        }
    },
    'deng_wen_feng': {
        "display_name": "邓文峰",
        "equipment": {'weapon': {"display_name": "“邓文峰枪", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "邓文峰衣", 'pvp': 0, 'pve': 1500}},
        "reward": {
            "money": 100,
            "banggong": 5000,
        },
        "buff": [
            {
                "display_name": "邓家阵法",
                "description": "自身武器攻击+50%",
                "weapon": 1.5,
                "chance": 0.1,
            },
            {
                "display_name": "邓家将",
                "description": "自身武器攻击+20%",
                "weapon": 1.2,
                "chance": 0.3
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.6,
            "ran": 1
        }
    },
    'shang_zhong_yong': {
        "display_name": "商仲永",
        "equipment": {'weapon': {"display_name": "“商仲永扇", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "商仲永衣", 'pvp': 0, 'pve': 3000}},
        "reward": {
            "money": 200,
            "banggong": 10000,
        },
        "buff": [
            {
                "display_name": "木人阵攻击",
                "description": "自身武器攻击+50%",
                "weapon": 1.5,
                "chance": 0.1,
            }
        ],
        "debuff": [
            {
                "display_name": "八卦阵防御",
                "description": "敌方武器攻击-50%",
                "weapon": 0.5,
                "chance": 0.2,
            },
            {
                "display_name": "天雷阵防御",
                "description": "敌方武器攻击-20%",
                "weapon": 0.8,
                "chance": 0.4
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 1,
            "ran": 1,
            "jia_zhuan_shen_can": 1,
            "zhen_cheng_zhi_xin": 0.1
        }
    },
    'fang_ji_chang': {
        "display_name": "方季常",
        "equipment": {'weapon': {"display_name": "方季常剑", 'pvp': 0, 'pve': 100},
                        'armor': {"display_name": "方季常衣", 'pvp': 0, 'pve': 1000}},
        "reward": {
            "money": 50,
            "banggong": 2000,
        },
        "buff": [
            {
                "display_name": "毒气蔓延",
                "description": "每次受到攻击时自身武器攻击+10%，现在已叠{0}层，最高{1}层",
                "weapon": 0.1,
                "chance": 1,
                'increase_type': 'lose',
                'count': 0,
                'max_count':10
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.2,
            "ran": 0.2
        }
    },
    'ping_san_zhi': {
        "display_name": "平三指",
        "equipment": {'weapon': {"display_name": "平三指剑", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "平三指衣", 'pvp': 0, 'pve': 3000}},
        "reward": {
            "money": 100,
            "banggong": 5000,
        },
        "debuff": [
            {
                "display_name": "毒液喷射",
                "description": "对方攻击-100%",
                "weapon": 0,
                "chance": 0.25,
            },
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.6,
            "ran": 1
        }
    },
    'si_tu_yi_yi': {
        "display_name": "司徒一一",
        "equipment": {'weapon': {"display_name": "司徒一一剑", 'pvp': 0, 'pve': 300},
                        'armor': {"display_name": "司徒一一衣", 'pvp': 0, 'pve': 5000}},
        "reward": {
            "money": 200,
            "banggong": 10000,
        },
        "buff": [
            {
                "display_name": "巨龙横扫",
                "description": "自身武器攻击+50%",
                "weapon": 1.5,
                "chance": 0.2,
            }
        ],
        "debuff": [
            {
                "display_name": "巨龙吐息",
                "description": "敌方需要消耗额外1次攻击次数",
                "weapon": 1,
                "chance": 1,
                'attack_count': 1,
                'max_hp': 0.3
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 1,
            "ran": 2,
            "jia_zhuan_shen_can": 1,
            "zhen_cheng_zhi_xin": 0.2
        }
    },
    'feng_du': {
        "display_name": "冯度",
        "equipment": {'weapon': {"display_name": "冯度剑", 'pvp': 0, 'pve': 200},
                        'armor': {"display_name": "冯度衣", 'pvp': 0, 'pve': 2000}},
        "reward": {
            "money": 50,
            "banggong": 2000,
        },
        "buff": [
            {
                "display_name": "跪地求饶",
                "description": "自身回血50，奖励金钱+10",
                "hp_recover": 50,
                "money": 10,
                "chance": 0.2,
                "max_hp": 0.25
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.2,
            "ran": 0.2
        }
    },
    'wang_yan_zhi': {
        "display_name": "王彦直",
        "equipment": {'weapon': {"display_name": "王彦直剑", 'pvp': 0, 'pve': 300},
                        'armor': {"display_name": "王彦直衣", 'pvp': 0, 'pve': 5000}},
        "reward": {
            "money": 100,
            "banggong": 5000,
        },
        "buff": [
            {
                "display_name": "碎星辰",
                "description": "每次受到攻击时自身武器攻击+20%，现在已叠{0}层，最高{1}层",
                "weapon": 0.2,
                "chance": 1,
                'increase_type': 'lose',
                'count': 0,
                'max_count':10
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 0.6,
            "ran": 1,
            "tuan_yuan_yan": 0.4
        }
    },
    'gui_ying_xiao_ci_lang': {
        "display_name": "鬼影小次郎",
        "equipment": {'weapon': {"display_name": "鬼影小次郎剑", 'pvp': 0, 'pve': 400},
                        'armor': {"display_name": "鬼影小次郎衣", 'pvp': 0, 'pve': 8000}},
        "reward": {
            "money": 200,
            "banggong": 10000,
        },
        "buff": [
            {
                "display_name": "一闪",
                "description": "自身武器攻击+20%",
                "weapon": 1.2,
                "chance": 0.4,
            }
        ],
        "debuff": [
            {
                "display_name": "真·天珠·一闪",
                "description": "敌方需要消耗额外1次攻击次数",
                "chance": 0.5,
                'attack_count': 1,
                'max_hp': 0.5
            }
        ],
        "reward_chance": 1,
        "reward_item": {
            "rong_ding": 1,
            "ran": 2,
            "jia_zhuan_shen_can": 1,
            "zhen_cheng_zhi_xin": 0.2
        }
    }
}

def get_dungeon_id_by_display_name(display_name):
    for k, v in DUNGEON_LIST.items():
        if v['display_name'] == display_name:
            return k
    return ""