#!/usr/bin/env python3
"""
龙胤立志传 - Web 存档修改器
Flask 后端 API 服务器
"""

import json
import shutil
import os
from datetime import datetime
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='web', static_url_path='')

# ========== 全局状态 ==========
hero_data = None
hero_filepath = 'Hero'
save_data = None
save_filepath = 'Save'
DEFAULT_SAVE_FOLDER = r'C:\Program Files (x86)\Steam\steamapps\common\LongYinLiZhiZhuan\LongYinLiZhiZhuan_Data\Save'
save_folder = DEFAULT_SAVE_FOLDER if os.path.exists(DEFAULT_SAVE_FOLDER) else None

# ========== 数据加载 ==========

SKILL_NAMES = {}
if os.path.exists('skill_names.json'):
    with open('skill_names.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for k, v in data.items():
            SKILL_NAMES[int(k)] = v

SPE_ATTR_MAP = {}
if os.path.exists('spe_attr_map.json'):
    with open('spe_attr_map.json', 'r', encoding='utf-8') as f:
        SPE_ATTR_MAP = json.load(f)

TALENT_NAMES = {}
if os.path.exists('talent_names.json'):
    with open('talent_names.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for k, v in data.items():
            TALENT_NAMES[int(k)] = v

# 天赋标签(tagID)名称映射
TAG_NAMES = {}
if os.path.exists('tag_names.json'):
    with open('tag_names.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for k, v in data.items():
            TAG_NAMES[int(k)] = v

# 天赋标签(tagID)名称映射
TAG_NAMES = {}
if os.path.exists('tag_names.json'):
    with open('tag_names.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for k, v in data.items():
            TAG_NAMES[int(k)] = v

# ========== 常量定义 ==========

ATTR_NAMES = ['力道', '灵巧', '智力', '意志', '体质', '经脉']
FIGHT_SKILL_NAMES = ['内功', '轻功', '绝技', '拳掌', '剑法', '刀法', '长兵', '奇门', '射术']
LIVING_SKILL_NAMES = ['医术', '毒术', '学识', '口才', '采伐', '木植', '锻造', '炼丹', '烹饪']

NATURE_MAP = {
    0: '仁善', 1: '正直', 2: '刚正', 3: '忠义', 4: '稳妥', 5: '温和',
    6: '平常', 7: '狡黠', 8: '乖张', 9: '叛逆', 10: '唯我', 11: '冷酷'
}

FORCE_MAP = {
    0: '无', 1: '少林派', 2: '武当派', 3: '峨眉派', 4: '丐帮', 5: '华山派',
    6: '衡山派', 7: '青城派', 8: '点苍派', 9: '昆仑派', 10: '崆峒派',
    11: '天山派', 12: '雪山派', 13: '点星阁', 14: '五毒教', 15: '明教',
    16: '日月神教', 17: '红花会', 18: '天地会', 19: '六扇门', 20: '锦衣卫',
    21: '东厂', 22: '西厂', 23: '大理段氏', 24: '全真教', 25: '仙霞派',
    26: '茅山派', 27: '桃花岛', 28: '逍遥派', 29: '灵鹫宫'
}

EQUIPMENT_SLOTS = {
    'weaponSaveRecord': '武器',
    'armorSaveRecord': '护甲',
    'helmetSaveRecord': '头盔',
    'shoesSaveRecord': '鞋子',
    'decorationSaveRecord': '饰品'
}

ITEM_TYPES = {
    0: '武器', 1: '护甲', 2: '头盔', 3: '鞋子', 4: '饰品', 5: '药品',
    6: '坐骑', 7: '秘籍', 8: '材料', 9: '宝物', 10: '杂项'
}

# ========== 工具函数 ==========

def backup_file(filepath='Hero'):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    return backup_path

def load_data(filepath='Hero'):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data_file(data, filepath='Hero'):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def get_skill_name(skill_id):
    if skill_id in SKILL_NAMES:
        return SKILL_NAMES[skill_id].get('name', f'未知({skill_id})')
    return f'未知({skill_id})'

def get_spe_attr_name(attr_id):
    return SPE_ATTR_MAP.get(str(attr_id), f'属性{attr_id}')

def get_talent_name(talent_id):
    """获取天赋名称"""
    if talent_id in TALENT_NAMES:
        return TALENT_NAMES[talent_id].get('name', f'未知({talent_id})')
    return f'未知({talent_id})'

def get_talent_info(talent_id):
    """获取天赋资质完整信息"""
    if talent_id in TALENT_NAMES:
        return TALENT_NAMES[talent_id]
    return {'name': f'未知({talent_id})', 'description': '', 'color': '#ffffff'}

def get_tag_name(tag_id):
    """获取天赋标签名称"""
    if tag_id in TAG_NAMES:
        return TAG_NAMES[tag_id].get('name', f'未知({tag_id})')
    return f'未知({tag_id})'

def get_tag_info(tag_id):
    """获取天赋标签完整信息"""
    if tag_id in TAG_NAMES:
        return TAG_NAMES[tag_id]
    return {'name': f'未知({tag_id})', 'description': ''}

def find_hero_by_id(hero_id):
    """根据 heroID 查找角色"""
    if hero_data is None:
        return None
    for hero in hero_data:
        if hero.get('heroID') == hero_id:
            return hero
    return None

def find_hero_index(hero_id):
    """根据 heroID 查找角色索引"""
    if hero_data is None:
        return -1
    for i, hero in enumerate(hero_data):
        if hero.get('heroID') == hero_id:
            return i
    return -1

# ========== 修改函数 ==========

def modify_base_attr(hero, idx, value):
    hero['baseAttri'][idx] = float(value)
    hero['totalAttri'][idx] = float(value)
    hero['maxAttri'][idx] = float(value)

def modify_fight_skill(hero, idx, value):
    hero['baseFightSkill'][idx] = float(value)
    hero['totalFightSkill'][idx] = float(value)
    hero['maxFightSkill'][idx] = float(value)

def modify_living_skill(hero, idx, value):
    hero['baseLivingSkill'][idx] = float(value)
    hero['totalLivingSkill'][idx] = float(value)
    hero['maxLivingSkill'][idx] = float(value)

def modify_status(hero, hp=None, power=None, mana=None):
    if hp is not None:
        hero['hp'] = float(hp)
        hero['maxhp'] = float(hp)
        hero['realMaxHp'] = float(hp)
    if power is not None:
        hero['power'] = float(power)
        hero['maxPower'] = float(power)
        hero['realMaxPower'] = float(power)
    if mana is not None:
        hero['mana'] = float(mana)
        hero['maxMana'] = float(mana)
        hero['realMaxMana'] = float(mana)

def modify_fame(hero, fame=None, bad_fame=None):
    if fame is not None:
        hero['fame'] = float(fame)
    if bad_fame is not None:
        hero['badFame'] = float(bad_fame)

def modify_money(hero, money):
    if 'itemListData' not in hero:
        hero['itemListData'] = {'money': 0, 'weight': 0, 'maxWeight': 100, 'allItem': []}
    hero['itemListData']['money'] = int(money)

def modify_skill_lv(skill, lv):
    skill['lv'] = int(lv)

def add_skill(hero, skill_id, lv=1):
    new_skill = {
        'skillID': skill_id, 'lv': lv, 'fightExp': 0.0, 'bookExp': 0.0,
        'equiped': False, 'isNew': True, 'belongHeroID': hero.get('heroID'),
        'speEquipData': {'heroSpeAddData': {}}, 'equipUseSpeAddValue': 0.0,
        'speUseData': {'heroSpeAddData': {}}, 'damageUseSpeAddValue': 0.0,
        'selfUseSpeAddValue': 0.0, 'enemyUseSpeAddValue': 0.0,
        'extraAddData': {'heroSpeAddData': {}}, 'maxManaChanged': False
    }
    hero['kungfuSkills'].append(new_skill)

def all_skills_max(hero, lv=10, damage=999):
    for skill in hero.get('kungfuSkills', []):
        skill['lv'] = lv
        skill['damageUseSpeAddValue'] = float(damage)

def remove_skill(hero, idx):
    skills = hero.get('kungfuSkills', [])
    if not (0 <= idx < len(skills)):
        return None
    removed = skills.pop(idx)
    for field in ['internalSkillSaveRecord', 'dodgeSkillSaveRecord', 'uniqueSkillSaveRecord']:
        if field in hero:
            val = hero[field]
            if isinstance(val, int):
                if val == idx:
                    hero[field] = -1
                elif val > idx:
                    hero[field] = val - 1
    if 'attackSkillSaveRecord' in hero:
        new_records = []
        for val in hero['attackSkillSaveRecord']:
            if val == idx:
                new_records.append(-1)
            elif val > idx:
                new_records.append(val - 1)
            else:
                new_records.append(val)
        hero['attackSkillSaveRecord'] = new_records
    return removed

def heal_hero(hero):
    hero['hp'] = hero.get('maxhp', 999)
    hero['power'] = hero.get('maxPower', 999)
    hero['mana'] = hero.get('maxMana', 999)
    hero['internalInjury'] = 0.0
    hero['externalInjury'] = 0.0
    hero['poisonInjury'] = 0.0

def revive_hero(hero):
    hero['dead'] = False
    heal_hero(hero)

def max_all_attrs(hero, value=999):
    for i in range(6):
        modify_base_attr(hero, i, value)
    for i in range(9):
        modify_fight_skill(hero, i, value)
        modify_living_skill(hero, i, value)
    modify_status(hero, value, value, value)

# ========== 好感度/人际关系函数 ==========

def modify_favor(hero, value):
    """修改角色对玩家的好感度

    Args:
        hero: 角色数据字典
        value: 好感度值 (-999999 表示未知, -100 到 100 为正常范围)
    """
    if value == -999999.0:
        # 允许重置为未知状态
        hero['favor'] = -999999.0
    else:
        # 限制在 -100 到 100 范围内
        hero['favor'] = max(-100.0, min(100.0, float(value)))

def add_friend(hero, friend_id):
    """添加好友

    Args:
        hero: 角色数据字典
        friend_id: 好友的角色ID
    """
    if 'Friends' not in hero:
        hero['Friends'] = []
    if friend_id not in hero['Friends']:
        hero['Friends'].append(friend_id)

def remove_friend(hero, friend_id):
    """移除好友

    Args:
        hero: 角色数据字典
        friend_id: 好友的角色ID
    """
    if 'Friends' in hero and friend_id in hero['Friends']:
        hero['Friends'].remove(friend_id)

def add_hater(hero, hater_id):
    """添加仇人

    Args:
        hero: 角色数据字典
        hater_id: 仇人的角色ID
    """
    if 'Haters' not in hero:
        hero['Haters'] = []
    if hater_id not in hero['Haters']:
        hero['Haters'].append(hater_id)

def remove_hater(hero, hater_id):
    """移除仇人

    Args:
        hero: 角色数据字典
        hater_id: 仇人的角色ID
    """
    if 'Haters' in hero and hater_id in hero['Haters']:
        hero['Haters'].remove(hater_id)

def set_lover(hero, lover_id):
    """设置恋人

    Args:
        hero: 角色数据字典
        lover_id: 恋人的角色ID (-1 表示无恋人)
    """
    hero['Lover'] = lover_id

# ========== 物品管理函数 ==========

def add_item(hero, item):
    """添加物品到角色背包

    Args:
        hero: 角色数据字典
        item: 物品数据字典
    """
    if 'itemListData' not in hero:
        hero['itemListData'] = {'money': 0, 'weight': 0, 'maxWeight': 100, 'allItem': []}
    if 'allItem' not in hero['itemListData']:
        hero['itemListData']['allItem'] = []
    hero['itemListData']['allItem'].append(item)
    # 更新负重
    hero['itemListData']['weight'] = hero['itemListData'].get('weight', 0) + item.get('weight', 0)

def remove_item(hero, idx):
    """从角色背包移除物品

    Args:
        hero: 角色数据字典
        idx: 物品索引

    Returns:
        被移除的物品，如果索引无效则返回 None
    """
    if 'itemListData' not in hero:
        return None
    items = hero['itemListData'].get('allItem', [])
    if not (0 <= idx < len(items)):
        return None
    removed = items.pop(idx)
    # 更新负重
    hero['itemListData']['weight'] = hero['itemListData'].get('weight', 0) - removed.get('weight', 0)
    return removed

def modify_item(hero, idx, field, value):
    """修改物品属性

    Args:
        hero: 角色数据字典
        idx: 物品索引
        field: 字段名
        value: 新值

    Returns:
        True 如果修改成功，False 如果失败
    """
    if 'itemListData' not in hero:
        return False
    items = hero['itemListData'].get('allItem', [])
    if not (0 <= idx < len(items)):
        return False
    items[idx][field] = value
    return True

# ========== API 路由 ==========

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/world')
def world():
    return send_from_directory('web', 'world.html')

@app.route('/api/status')
def api_status():
    return jsonify({
        'loaded': hero_data is not None,
        'hero_count': len(hero_data) if hero_data else 0,
        'filepath': hero_filepath,
        'save_folder': save_folder,
        'save_loaded': save_data is not None
    })

# ========== Save 文件 API ==========

@app.route('/api/save/load', methods=['POST'])
def api_save_load():
    global save_data, save_filepath
    try:
        req = request.get_json(silent=True) or {}
        slot = req.get('slot')
        if slot is not None and save_folder:
            slot_dir = os.path.join(save_folder, f'SaveSlot{slot}')
            save_path = os.path.join(slot_dir, 'Save')
            if not os.path.exists(save_path):
                return jsonify({'success': False, 'error': f'存档槽{slot}的Save文件不存在'}), 400
            save_data = load_data(save_path)
            save_filepath = save_path
        else:
            filepath = req.get('path', 'Save')
            save_data = load_data(filepath)
            save_filepath = filepath
        return jsonify({'success': True, 'filepath': save_filepath})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/save/status')
def api_save_status():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    return jsonify({
        'loaded': True,
        'filepath': save_filepath,
        'chapter': save_data.get('chapter', 1),
        'worldTime': save_data.get('worldTime', {}),
        'hour': save_data.get('hour', 0),
        'gameMode': save_data.get('gameMode', 0),
        'gameDifficulty': save_data.get('gameDifficulty', 1),
        'relaxMode': save_data.get('relaxMode', False),
        'cheating': save_data.get('cheating', False),
        'cheated': save_data.get('cheated', False),
        'totalFightCount': save_data.get('totalFightCount', 0),
        'totalWinFightCount': save_data.get('totalWinFightCount', 0),
        'totalEnemyKilled': save_data.get('totalEnemyKilled', 0),
        'totalHeroMeet': save_data.get('totalHeroMeet', 0),
        'finishForceMissionCount': save_data.get('finishForceMissionCount', 0),
        'areasCount': len(save_data.get('Areas', [])),
        'forcesCount': len(save_data.get('Forces', [])),
        'resourcePointsCount': len(save_data.get('ResourcePoints', [])),
        'innsCount': len(save_data.get('Inns', [])),
    })

@app.route('/api/save/world_time')
def api_save_world_time():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    return jsonify(save_data.get('worldTime', {'year': 1, 'month': 1, 'day': 1}))

@app.route('/api/save/world_time', methods=['PUT'])
def api_save_world_time_update():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        req = request.get_json()
        wt = save_data.get('worldTime', {'year': 1, 'month': 1, 'day': 1})
        if 'year' in req:
            wt['year'] = max(1, int(req['year']))
        if 'month' in req:
            wt['month'] = max(1, min(12, int(req['month'])))
        if 'day' in req:
            wt['day'] = max(1, min(30, int(req['day'])))
        save_data['worldTime'] = wt
        return jsonify({'success': True, 'worldTime': wt})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/game_settings')
def api_save_game_settings():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    return jsonify({
        'chapter': save_data.get('chapter', 1),
        'gameMode': save_data.get('gameMode', 0),
        'gameDifficulty': save_data.get('gameDifficulty', 1),
        'relaxMode': save_data.get('relaxMode', False),
        'cheating': save_data.get('cheating', False),
        'cheated': save_data.get('cheated', False),
        'hour': save_data.get('hour', 0),
        'TimeDifficulty': save_data.get('TimeDifficulty', 10.0),
        'battleTimeScale': save_data.get('battleTimeScale', 10.0),
    })

@app.route('/api/save/game_settings', methods=['PUT'])
def api_save_game_settings_update():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        req = request.get_json()
        if 'chapter' in req:
            save_data['chapter'] = int(req['chapter'])
        if 'gameMode' in req:
            save_data['gameMode'] = int(req['gameMode'])
        if 'gameDifficulty' in req:
            save_data['gameDifficulty'] = int(req['gameDifficulty'])
        if 'relaxMode' in req:
            save_data['relaxMode'] = bool(req['relaxMode'])
        if 'cheating' in req:
            save_data['cheating'] = bool(req['cheating'])
        if 'hour' in req:
            save_data['hour'] = float(req['hour'])
        if 'TimeDifficulty' in req:
            save_data['TimeDifficulty'] = float(req['TimeDifficulty'])
        if 'battleTimeScale' in req:
            save_data['battleTimeScale'] = float(req['battleTimeScale'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/month_limits')
def api_save_month_limits():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    return jsonify({
        'monthCatchBadFamePlayerTime': save_data.get('monthCatchBadFamePlayerTime', 0),
        'monthGambleTime': save_data.get('monthGambleTime', 0),
        'monthPartyTime': save_data.get('monthPartyTime', 0),
        'monthForcePartyTime': save_data.get('monthForcePartyTime', 0),
        'monthDoctorTime': save_data.get('monthDoctorTime', 0),
        'monthPerformForMoneyTime': save_data.get('monthPerformForMoneyTime', 0),
        'monthCoachTime': save_data.get('monthCoachTime', 0),
        'monthAttackMartialClubTime': save_data.get('monthAttackMartialClubTime', 0),
        'monthChallengeTime': save_data.get('monthChallengeTime', 0),
        'monthBuyAreaInfoTime': save_data.get('monthBuyAreaInfoTime', 0),
        'monthGiveMoneyToGovernTime': save_data.get('monthGiveMoneyToGovernTime', 0),
        'monthKillTime': save_data.get('monthKillTime', 0),
        'monthFreshBountyTime': save_data.get('monthFreshBountyTime', 0),
        'monthFreshAuctionTime': save_data.get('monthFreshAuctionTime', 0),
    })

@app.route('/api/save/month_limits', methods=['PUT'])
def api_save_month_limits_update():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        req = request.get_json()
        for field in ['monthCatchBadFamePlayerTime', 'monthGambleTime', 'monthPartyTime',
                      'monthForcePartyTime', 'monthDoctorTime', 'monthPerformForMoneyTime',
                      'monthCoachTime', 'monthAttackMartialClubTime', 'monthChallengeTime',
                      'monthBuyAreaInfoTime', 'monthGiveMoneyToGovernTime', 'monthKillTime',
                      'monthFreshBountyTime', 'monthFreshAuctionTime']:
            if field in req:
                save_data[field] = int(req[field])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/reset_month_limits', methods=['POST'])
def api_save_reset_month_limits():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        for field in ['monthCatchBadFamePlayerTime', 'monthGambleTime', 'monthPartyTime',
                      'monthForcePartyTime', 'monthDoctorTime', 'monthPerformForMoneyTime',
                      'monthCoachTime', 'monthAttackMartialClubTime', 'monthChallengeTime',
                      'monthBuyAreaInfoTime', 'monthGiveMoneyToGovernTime', 'monthKillTime',
                      'monthFreshBountyTime', 'monthFreshAuctionTime',
                      'monthSpeReduceBadFameTime', 'monthSpeAddFameTime',
                      'monthSpeGetTalentPointTime', 'monthBreakEquipTime',
                      'monthLeaderInteractOtherForceTime']:
            if field in save_data:
                save_data[field] = 0
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/statistics')
def api_save_statistics():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    return jsonify({
        'totalFightCount': save_data.get('totalFightCount', 0),
        'totalWinFightCount': save_data.get('totalWinFightCount', 0),
        'totalEnemyKilled': save_data.get('totalEnemyKilled', 0),
        'totalBadFame': save_data.get('totalBadFame', 0),
        'totalHeroMeet': save_data.get('totalHeroMeet', 0),
        'finishForceMissionCount': save_data.get('finishForceMissionCount', 0),
        'studyFightWithGreatHeroSingleWinNum': save_data.get('studyFightWithGreatHeroSingleWinNum', 0),
        'studyFightWithGreatHeroMultiWinNum': save_data.get('studyFightWithGreatHeroMultiWinNum', 0),
        'studyFightWithGreatHeroFinalWinNum': save_data.get('studyFightWithGreatHeroFinalWinNum', 0),
    })

@app.route('/api/save/statistics', methods=['PUT'])
def api_save_statistics_update():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        req = request.get_json()
        for field in ['totalFightCount', 'totalWinFightCount', 'totalEnemyKilled',
                      'totalBadFame', 'totalHeroMeet', 'finishForceMissionCount',
                      'studyFightWithGreatHeroSingleWinNum', 'studyFightWithGreatHeroMultiWinNum',
                      'studyFightWithGreatHeroFinalWinNum']:
            if field in req:
                if field == 'totalBadFame':
                    save_data[field] = float(req[field])
                else:
                    save_data[field] = int(req[field])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/areas')
def api_save_areas():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    areas = save_data.get('Areas', [])
    result = []
    for area in areas:
        result.append({
            'areaID': area.get('areaID'),
            'areaName': area.get('areaName', '未知'),
            'areaType': area.get('areaType', 0),
            'belongForceID': area.get('belongForceID', -1),
            'forceName': FORCE_MAP.get(area.get('belongForceID', -1), '无'),
            'people': area.get('people', 0),
            'maxPeople': area.get('maxPeople', 0),
            'safe': area.get('safe', 0),
            'support': area.get('support', 0),
            'defence': area.get('defence', 0),
            'insideHerosCount': len(area.get('insideHeros', [])),
        })
    return jsonify(result)

@app.route('/api/save/area/<int:area_id>')
def api_save_area_detail(area_id):
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    areas = save_data.get('Areas', [])
    area = None
    for a in areas:
        if a.get('areaID') == area_id:
            area = a
            break
    if area is None:
        return jsonify({'error': '区域未找到'}), 404
    
    buildings = []
    for i, tile in enumerate(area.get('areaTiles', [])):
        if tile.get('building'):
            b = tile['building']
            buildings.append({
                'tileIndex': i,
                'row': tile.get('row'),
                'column': tile.get('column'),
                'buildingID': b.get('buildingID'),
                'lv': b.get('lv', 0),
                'buildTimeLeft': b.get('buildTimeLeft', 0),
                'upgradeTimeLeft': b.get('upgradeTimeLeft', 0),
            })
    
    return jsonify({
        'areaID': area.get('areaID'),
        'areaName': area.get('areaName', '未知'),
        'areaType': area.get('areaType', 0),
        'areaStartLv': area.get('areaStartLv', 1),
        'belongForceID': area.get('belongForceID', -1),
        'forceName': FORCE_MAP.get(area.get('belongForceID', -1), '无'),
        'bigMapPos': area.get('bigMapPos', {}),
        'people': area.get('people', 0),
        'maxPeople': area.get('maxPeople', 0),
        'safe': area.get('safe', 0),
        'support': area.get('support', 0),
        'defence': area.get('defence', 0),
        'changeAreaState': area.get('changeAreaState', []),
        'changeResource': area.get('changeResource', []),
        'resourceValueRateBase': area.get('resourceValueRateBase', []),
        'insideHeros': area.get('insideHeros', []),
        'connectAreaID': area.get('connectAreaID', []),
        'connectResourcePointID': area.get('connectResourcePointID', []),
        'speProduct': area.get('speProduct', []),
        'branchLeaderID': area.get('branchLeaderID', -1),
        'areaBranchDefenceLv': area.get('areaBranchDefenceLv', []),
        'missionNumCount': area.get('missionNumCount', 0),
        'plotNumCount': area.get('plotNumCount', 0),
        'thisMonthManaged': area.get('thisMonthManaged', 0),
        'buildings': buildings,
    })

@app.route('/api/save/area/<int:area_id>', methods=['PUT'])
def api_save_area_update(area_id):
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    areas = save_data.get('Areas', [])
    area = None
    for a in areas:
        if a.get('areaID') == area_id:
            area = a
            break
    if area is None:
        return jsonify({'error': '区域未找到'}), 404
    
    try:
        req = request.get_json()
        if 'belongForceID' in req:
            area['belongForceID'] = int(req['belongForceID'])
        if 'people' in req:
            area['people'] = float(req['people'])
        if 'maxPeople' in req:
            area['maxPeople'] = float(req['maxPeople'])
        if 'safe' in req:
            area['safe'] = float(req['safe'])
        if 'support' in req:
            area['support'] = float(req['support'])
        if 'defence' in req:
            area['defence'] = float(req['defence'])
        if 'changeResource' in req:
            area['changeResource'] = [float(v) for v in req['changeResource']]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/area/<int:area_id>/buildings')
def api_save_area_buildings(area_id):
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    areas = save_data.get('Areas', [])
    area = None
    for a in areas:
        if a.get('areaID') == area_id:
            area = a
            break
    if area is None:
        return jsonify({'error': '区域未找到'}), 404
    
    buildings = []
    for i, tile in enumerate(area.get('areaTiles', [])):
        if tile.get('building'):
            b = tile['building']
            buildings.append({
                'tileIndex': i,
                'row': tile.get('row'),
                'column': tile.get('column'),
                'buildingID': b.get('buildingID'),
                'lv': b.get('lv', 0),
                'buildTimeLeft': b.get('buildTimeLeft', 0),
                'upgradeTimeLeft': b.get('upgradeTimeLeft', 0),
                'produceRate': b.get('produceRate', 0),
                'resourceStoreRate': b.get('resourceStoreRate', 0),
            })
    return jsonify(buildings)

@app.route('/api/save/area/<int:area_id>/building/<int:tile_index>', methods=['PUT'])
def api_save_area_building_update(area_id, tile_index):
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    areas = save_data.get('Areas', [])
    area = None
    for a in areas:
        if a.get('areaID') == area_id:
            area = a
            break
    if area is None:
        return jsonify({'error': '区域未找到'}), 404
    
    tiles = area.get('areaTiles', [])
    if not (0 <= tile_index < len(tiles)):
        return jsonify({'error': '地块索引无效'}), 400
    
    tile = tiles[tile_index]
    if not tile.get('building'):
        return jsonify({'error': '该地块没有建筑'}), 400
    
    try:
        req = request.get_json()
        building = tile['building']
        if 'lv' in req:
            building['lv'] = int(req['lv'])
        if 'buildTimeLeft' in req:
            building['buildTimeLeft'] = int(req['buildTimeLeft'])
        if 'upgradeTimeLeft' in req:
            building['upgradeTimeLeft'] = int(req['upgradeTimeLeft'])
        if 'produceRate' in req:
            building['produceRate'] = float(req['produceRate'])
        if 'resourceStoreRate' in req:
            building['resourceStoreRate'] = float(req['resourceStoreRate'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/area/<int:area_id>/buildings/batch', methods=['POST'])
def api_save_area_buildings_batch(area_id):
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    areas = save_data.get('Areas', [])
    area = None
    for a in areas:
        if a.get('areaID') == area_id:
            area = a
            break
    if area is None:
        return jsonify({'error': '区域未找到'}), 404
    
    try:
        req = request.get_json()
        target_lv = req.get('lv')
        if target_lv is None:
            return jsonify({'error': '缺少等级参数'}), 400
        
        count = 0
        for tile in area.get('areaTiles', []):
            if tile.get('building'):
                building = tile['building']
                building['lv'] = int(target_lv)
                building['buildTimeLeft'] = 0
                building['upgradeTimeLeft'] = 0
                count += 1
        
        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/forces')
def api_save_forces():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    forces = save_data.get('Forces', [])
    result = []
    for force in forces:
        result.append({
            'forceID': force.get('forceID'),
            'forceName': force.get('forceName', '未知'),
            'forceLv': force.get('forceLv', 1),
            'bigForce': force.get('bigForce', False),
            'forceStyle': force.get('forceStyle', '中庸'),
            'leader': force.get('leader', -1),
            'mainAreaID': force.get('mainAreaID', -1),
            'ownAreasCount': len(force.get('ownAreasID', [])),
            'ownHerosCount': len(force.get('ownHeros', [])),
            'totalPopulation': force.get('totalPopulation', 0),
            'totalSalary': force.get('totalSalary', 0),
            'resourceStore': force.get('resourceStore', []),
            'allyForce': force.get('allyForce', []),
        })
    return jsonify(result)

@app.route('/api/save/force/<int:force_id>')
def api_save_force_detail(force_id):
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    forces = save_data.get('Forces', [])
    force = None
    for f in forces:
        if f.get('forceID') == force_id:
            force = f
            break
    if force is None:
        return jsonify({'error': '门派未找到'}), 404
    
    return jsonify({
        'forceID': force.get('forceID'),
        'forceName': force.get('forceName', '未知'),
        'forceLv': force.get('forceLv', 1),
        'bigForce': force.get('bigForce', False),
        'forceStyle': force.get('forceStyle', '中庸'),
        'leader': force.get('leader', -1),
        'mainAreaID': force.get('mainAreaID', -1),
        'masterForce': force.get('masterForce', -1),
        'servantForce': force.get('servantForce', []),
        'ownAreasID': force.get('ownAreasID', []),
        'ownResourcePointsID': force.get('ownResourcePointsID', []),
        'ownHeros': force.get('ownHeros', []),
        'totalPopulation': force.get('totalPopulation', 0),
        'totalSalary': force.get('totalSalary', 0),
        'resourceStore': force.get('resourceStore', []),
        'resourceStoreMax': force.get('resourceStoreMax', []),
        'resourceChange': force.get('resourceChange', []),
        'forceStorage': force.get('forceStorage', {}),
        'allyForce': force.get('allyForce', []),
        'kungfuSkillFocus': force.get('kungfuSkillFocus', []),
        'livingSkillFocus': force.get('livingSkillFocus', []),
        'nowResearchTech': force.get('nowResearchTech', -1),
        'speBuildingID': force.get('speBuildingID', -1),
    })

@app.route('/api/save/force/<int:force_id>', methods=['PUT'])
def api_save_force_update(force_id):
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    forces = save_data.get('Forces', [])
    force = None
    for f in forces:
        if f.get('forceID') == force_id:
            force = f
            break
    if force is None:
        return jsonify({'error': '门派未找到'}), 404
    
    try:
        req = request.get_json()
        if 'forceLv' in req:
            force['forceLv'] = int(req['forceLv'])
        if 'totalPopulation' in req:
            force['totalPopulation'] = int(req['totalPopulation'])
        if 'totalSalary' in req:
            force['totalSalary'] = int(req['totalSalary'])
        if 'resourceStore' in req:
            force['resourceStore'] = [float(v) for v in req['resourceStore']]
        if 'resourceStoreMax' in req:
            force['resourceStoreMax'] = [float(v) for v in req['resourceStoreMax']]
        if 'leader' in req:
            force['leader'] = int(req['leader'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/resource_points')
def api_save_resource_points():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    rps = save_data.get('ResourcePoints', [])
    result = []
    for rp in rps:
        result.append({
            'resourcePointID': rp.get('resourcePointID'),
            'resourcePointName': rp.get('resourcePointName', '未知'),
            'resourcePointTypeID': rp.get('resourcePointTypeID', 0),
            'belongForceID': rp.get('belongForceID', -1),
            'forceName': FORCE_MAP.get(rp.get('belongForceID', -1), '无'),
            'connectAreaID': rp.get('connectAreaID', -1),
            'changeResource': rp.get('changeResource', []),
        })
    return jsonify(result)

@app.route('/api/save/resource_point/<int:rp_id>')
def api_save_resource_point_detail(rp_id):
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    rps = save_data.get('ResourcePoints', [])
    rp = None
    for r in rps:
        if r.get('resourcePointID') == rp_id:
            rp = r
            break
    if rp is None:
        return jsonify({'error': '资源点未找到'}), 404
    
    return jsonify({
        'resourcePointID': rp.get('resourcePointID'),
        'resourcePointName': rp.get('resourcePointName', '未知'),
        'resourcePointFullName': rp.get('resourcePointFullName', ''),
        'resourcePointTypeID': rp.get('resourcePointTypeID', 0),
        'belongForceID': rp.get('belongForceID', -1),
        'forceName': FORCE_MAP.get(rp.get('belongForceID', -1), '无'),
        'connectAreaID': rp.get('connectAreaID', -1),
        'changeResource': rp.get('changeResource', []),
    })

@app.route('/api/save/resource_point/<int:rp_id>', methods=['PUT'])
def api_save_resource_point_update(rp_id):
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    
    rps = save_data.get('ResourcePoints', [])
    rp = None
    for r in rps:
        if r.get('resourcePointID') == rp_id:
            rp = r
            break
    if rp is None:
        return jsonify({'error': '资源点未找到'}), 404
    
    try:
        req = request.get_json()
        if 'belongForceID' in req:
            rp['belongForceID'] = int(req['belongForceID'])
        if 'changeResource' in req:
            rp['changeResource'] = [float(v) for v in req['changeResource']]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/prison')
def api_save_prison():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    return jsonify(save_data.get('prisonData', {}))

@app.route('/api/save/prison', methods=['PUT'])
def api_save_prison_update():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        req = request.get_json()
        prison = save_data.get('prisonData', {})
        if 'guardAlert' in req:
            prison['guardAlert'] = float(req['guardAlert'])
        if 'guardFavor' in req:
            prison['guardFavor'] = float(req['guardFavor'])
        if 'buyGuardCd' in req:
            prison['buyGuardCd'] = float(req['buyGuardCd'])
        save_data['prisonData'] = prison
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/govern_storage')
def api_save_govern_storage():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    gs = save_data.get('governStorage', {})
    return jsonify({
        'heroID': gs.get('heroID', -1),
        'forceID': gs.get('forceID', -1),
        'money': gs.get('money', 0),
        'weight': gs.get('weight', 0),
        'maxWeight': gs.get('maxWeight', -1),
        'itemCount': len(gs.get('allItem', [])),
    })

@app.route('/api/save/govern_storage', methods=['PUT'])
def api_save_govern_storage_update():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        req = request.get_json()
        gs = save_data.get('governStorage', {})
        if 'money' in req:
            gs['money'] = int(req['money'])
        save_data['governStorage'] = gs
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/unlock_flags')
def api_save_unlock_flags():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    return jsonify({
        'openLeaveForce': save_data.get('openLeaveForce', False),
        'openForceBuilding': save_data.get('openForceBuilding', False),
        'openForceAttackResource': save_data.get('openForceAttackResource', False),
        'openForceAttackArea': save_data.get('openForceAttackArea', False),
        'openForceAttackBasement': save_data.get('openForceAttackBasement', False),
    })

@app.route('/api/save/unlock_flags', methods=['PUT'])
def api_save_unlock_flags_update():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        req = request.get_json()
        for field in ['openLeaveForce', 'openForceBuilding', 'openForceAttackResource',
                      'openForceAttackArea', 'openForceAttackBasement']:
            if field in req:
                save_data[field] = bool(req[field])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/unlock_all', methods=['POST'])
def api_save_unlock_all():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        save_data['openLeaveForce'] = True
        save_data['openForceBuilding'] = True
        save_data['openForceAttackResource'] = True
        save_data['openForceAttackArea'] = True
        save_data['openForceAttackBasement'] = True
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/weather')
def api_save_weather():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    return jsonify({
        'nowWeather': save_data.get('nowWeather', 0),
        'weatherLastTime': save_data.get('weatherLastTime', 0),
    })

@app.route('/api/save/weather', methods=['PUT'])
def api_save_weather_update():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        req = request.get_json()
        if 'nowWeather' in req:
            save_data['nowWeather'] = int(req['nowWeather'])
        if 'weatherLastTime' in req:
            save_data['weatherLastTime'] = float(req['weatherLastTime'])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/missions_finished')
def api_save_missions_finished():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    return jsonify(save_data.get('missionFinished', []))

@app.route('/api/save/tutorials_finished')
def api_save_tutorials_finished():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    return jsonify(save_data.get('tutorialFinished', []))

@app.route('/api/save/spe_enhance_stone')
def api_save_spe_enhance_stone():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    return jsonify({'speEnhanceStone': save_data.get('speEnhanceStone', 0)})

@app.route('/api/save/spe_enhance_stone', methods=['PUT'])
def api_save_spe_enhance_stone_update():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        req = request.get_json()
        save_data['speEnhanceStone'] = int(req.get('speEnhanceStone', 0))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save/save', methods=['POST'])
def api_save_save_file():
    if save_data is None:
        return jsonify({'error': 'Save存档未加载'}), 400
    try:
        backup_path = backup_file(save_filepath)
        save_data_file(save_data, save_filepath)
        return jsonify({'success': True, 'backup': backup_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save_folder', methods=['POST'])
def api_set_save_folder():
    global save_folder
    try:
        req = request.get_json(silent=True) or {}
        folder = req.get('folder', '')
        if not folder or not os.path.isdir(folder):
            return jsonify({'success': False, 'error': '无效的存档文件夹'}), 400
        save_folder = folder
        return jsonify({'success': True, 'folder': folder})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/browse_folders', methods=['GET'])
def api_browse_folders():
    path = request.args.get('path', '.')
    try:
        if path == '.':
            path = os.getcwd()
        if not os.path.exists(path):
            return jsonify({'error': '路径不存在'}), 400
        items = []
        for item in sorted(os.listdir(path)):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                items.append({'name': item, 'path': full_path, 'type': 'folder'})
        parent = os.path.dirname(path) if path != '/' else None
        return jsonify({'current': path, 'parent': parent, 'items': items})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/save_slots')
def api_save_slots():
    if not save_folder:
        return jsonify({'error': '请先选择存档文件夹'}), 400
    slots = []
    slot_names = {
        0: '自动存档',
        10: '快速存档'
    }
    for i in range(0, 11):
        if i == 0 or i == 10:
            slot_dir = os.path.join(save_folder, f'SaveSlot{i}')
        else:
            slot_dir = os.path.join(save_folder, f'SaveSlot{i}')
        info_path = os.path.join(slot_dir, 'Info')
        hero_path = os.path.join(slot_dir, 'Hero')
        slot_info = {
            'slot': i,
            'name': slot_names.get(i, f'存档{i}'),
            'exists': os.path.exists(hero_path),
            'info': None
        }
        if os.path.exists(info_path):
            try:
                with open(info_path, 'r', encoding='utf-8') as f:
                    slot_info['info'] = json.load(f)
            except:
                pass
        slots.append(slot_info)
    return jsonify(slots)

@app.route('/api/load', methods=['POST'])
def api_load():
    global hero_data, hero_filepath, save_data, save_filepath
    try:
        req = request.get_json(silent=True) or {}
        slot = req.get('slot')
        if slot is not None and save_folder:
            slot_dir = os.path.join(save_folder, f'SaveSlot{slot}')
            hero_path = os.path.join(slot_dir, 'Hero')
            if not os.path.exists(hero_path):
                return jsonify({'success': False, 'error': f'存档槽{slot}不存在'}), 400
            hero_data = load_data(hero_path)
            hero_filepath = hero_path
            save_path = os.path.join(slot_dir, 'Save')
            if os.path.exists(save_path):
                save_data = load_data(save_path)
                save_filepath = save_path
        elif 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify({'success': False, 'error': '未选择文件'}), 400
            filename = secure_filename(file.filename)
            temp_path = os.path.join('/tmp', filename)
            file.save(temp_path)
            hero_data = load_data(temp_path)
            hero_filepath = temp_path
        else:
            filepath = req.get('path', 'Hero')
            hero_data = load_data(filepath)
            hero_filepath = filepath
        return jsonify({'success': True, 'hero_count': len(hero_data), 'filepath': hero_filepath})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/heroes')
def api_heroes():
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    heroes = []
    for hero in hero_data:
        if hero is None:
            continue
        force_id = hero.get('belongForceID', -1)
        talent_id = hero.get('talent', 2)
        heroes.append({
            'heroID': hero.get('heroID'),
            'heroName': hero.get('heroName', '未知'),
            'age': hero.get('age', 0),
            'forceID': force_id,
            'forceName': FORCE_MAP.get(force_id, f'未知({force_id})'),
            'isLeader': hero.get('isLeader', False),
            'dead': hero.get('dead', False),
            'inTeam': hero.get('inTeam', False),
            'isFemale': hero.get('isFemale', False),
            'nature': hero.get('nature', 6),
            'natureName': NATURE_MAP.get(hero.get('nature', 6), '未知'),
            'talent': talent_id,
            'talentName': get_talent_name(talent_id),
            'hp': hero.get('hp', 0),
            'maxhp': hero.get('maxhp', 0),
            'fame': hero.get('fame', 0),
            'badFame': hero.get('badFame', 0),
        })
    return jsonify(heroes)

@app.route('/api/hero/<int:hero_id>')
def api_hero_detail(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404

    # 构建详细数据
    base_attri = hero.get('baseAttri', [0]*6)
    total_attri = hero.get('totalAttri', [0]*6)
    max_attri = hero.get('maxAttri', [0]*6)

    base_fight = hero.get('baseFightSkill', [0]*9)
    total_fight = hero.get('totalFightSkill', [0]*9)
    max_fight = hero.get('maxFightSkill', [0]*9)

    base_living = hero.get('baseLivingSkill', [0]*9)
    total_living = hero.get('totalLivingSkill', [0]*9)
    max_living = hero.get('maxLivingSkill', [0]*9)

    result = {
        'heroID': hero.get('heroID'),
        'heroName': hero.get('heroName', '未知'),
        'heroFamilyName': hero.get('heroFamilyName', ''),
        'age': hero.get('age', 0),
        'isFemale': hero.get('isFemale', False),
        'forceID': hero.get('belongForceID', -1),
        'forceName': FORCE_MAP.get(hero.get('belongForceID', -1), '未知'),
        'isLeader': hero.get('isLeader', False),
        'forceJobID': hero.get('forceJobID', -1),
        'heroForceLv': hero.get('heroForceLv', 0),
        'forceContribution': hero.get('forceContribution', 0),
        'nature': hero.get('nature', 6),
        'natureName': NATURE_MAP.get(hero.get('nature', 6), '未知'),
        'talent': hero.get('talent', 2),
        'talentName': get_talent_name(hero.get('talent', 2)),
        'hp': hero.get('hp', 0),
        'maxhp': hero.get('maxhp', 0),
        'power': hero.get('power', 0),
        'maxPower': hero.get('maxPower', 0),
        'mana': hero.get('mana', 0),
        'maxMana': hero.get('maxMana', 0),
        'armor': hero.get('armor', 0),
        'internalInjury': hero.get('internalInjury', 0),
        'externalInjury': hero.get('externalInjury', 0),
        'poisonInjury': hero.get('poisonInjury', 0),
        'dead': hero.get('dead', False),
        'inPrison': hero.get('inPrison', False),
        'rest': hero.get('rest', False),
        'inTeam': hero.get('inTeam', False),
        'fame': hero.get('fame', 0),
        'badFame': hero.get('badFame', 0),
        'fightScore': hero.get('fightScore', 0),
        'baseAttri': base_attri,
        'totalAttri': total_attri,
        'maxAttri': max_attri,
        'baseFightSkill': base_fight,
        'totalFightSkill': total_fight,
        'maxFightSkill': max_fight,
        'baseLivingSkill': base_living,
        'totalLivingSkill': total_living,
        'maxLivingSkill': max_living,
    }

    # 物品/金钱
    items_data = hero.get('itemListData', {})
    result['money'] = items_data.get('money', 0)
    result['weight'] = items_data.get('weight', 0)
    result['maxWeight'] = items_data.get('maxWeight', 0)

    return jsonify(result)

@app.route('/api/hero/<int:hero_id>/details')
def api_hero_details(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    
    def parse_spe_data(data):
        result = {}
        for k, v in data.items():
            result[k] = v
        return result
    
    base_add_data = hero.get('baseAddData', {}).get('heroSpeAddData', {})
    total_add_data = hero.get('totalAddData', {}).get('heroSpeAddData', {})
    
    return jsonify({
        'realMaxHp': hero.get('realMaxHp', 0),
        'realMaxPower': hero.get('realMaxPower', 0),
        'realMaxMana': hero.get('realMaxMana', 0),
        'armor': hero.get('armor', 0),
        'fightScore': hero.get('fightScore', 0),
        'baseAddData': parse_spe_data(base_add_data),
        'totalAddData': parse_spe_data(total_add_data),
    })

@app.route('/api/hero/<int:hero_id>/detail_attr', methods=['PUT'])
def api_hero_detail_attr(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        attr_id = str(req.get('attrId', ''))
        value = float(req.get('value', 0))
        
        if 'baseAddData' not in hero:
            hero['baseAddData'] = {'heroSpeAddData': {}}
        if 'heroSpeAddData' not in hero['baseAddData']:
            hero['baseAddData']['heroSpeAddData'] = {}
        
        if value == 0:
            hero['baseAddData']['heroSpeAddData'].pop(attr_id, None)
        else:
            hero['baseAddData']['heroSpeAddData'][attr_id] = value
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/force')
def api_hero_force(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    
    force_id = hero.get('belongForceID', -1)
    return jsonify({
        'forceID': force_id,
        'forceName': FORCE_MAP.get(force_id, f'未知({force_id})'),
        'heroForceLv': hero.get('heroForceLv', 0),
        'forceContribution': hero.get('forceContribution', 0),
        'thisYearContribution': hero.get('thisYearContribution', 0),
        'lastYearContribution': hero.get('lastYearContribution', 0),
        'thisMonthContribution': hero.get('thisMonthContribution', 0),
        'lastMonthContribution': hero.get('lastMonthContribution', 0),
        'lastFightContribution': hero.get('lastFightContribution', 0),
        'governContribution': hero.get('governContribution', 0),
        'forceJobID': hero.get('forceJobID', -1),
        'forceJobType': hero.get('forceJobType', -1),
        'forceJobCD': hero.get('forceJobCD', 0),
    })

@app.route('/api/hero/<int:hero_id>/force', methods=['PUT'])
def api_hero_force_update(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        for field in ['heroForceLv', 'forceContribution', 'thisYearContribution', 
                      'lastYearContribution', 'thisMonthContribution', 'lastMonthContribution',
                      'lastFightContribution', 'governContribution', 'forceJobID', 'forceJobType', 'forceJobCD']:
            if field in req:
                hero[field] = float(req[field]) if 'Contribution' in field or field == 'forceJobCD' else int(req[field])
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/force_contributions')
def api_hero_force_contributions(hero_id):
    if hero_data is None or save_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    
    if hero_id != 0:
        return jsonify({'error': '只有主角有各派功绩数据', 'contributions': []})
    
    forces = save_data.get('Forces', [])
    contributions = []
    for f in forces:
        contributions.append({
            'forceID': f.get('forceID'),
            'forceName': f.get('forceName', '未知'),
            'contribution': f.get('playerOutForceContribution', 0)
        })
    return jsonify({'contributions': contributions})

@app.route('/api/hero/<int:hero_id>/force_contributions', methods=['PUT'])
def api_hero_force_contributions_update(hero_id):
    if hero_data is None or save_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    
    if hero_id != 0:
        return jsonify({'error': '只有主角有各派功绩数据'}), 400
    
    try:
        req = request.get_json()
        force_id = req.get('forceID')
        contribution = float(req.get('contribution', 0))
        
        forces = save_data.get('Forces', [])
        for f in forces:
            if f.get('forceID') == force_id:
                f['playerOutForceContribution'] = contribution
                return jsonify({'success': True})
        return jsonify({'error': '门派未找到'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/talents')
def api_hero_talents(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404

    # 为每个天赋标签添加名称和描述
    tags = hero.get('heroTagData', [])
    tags_with_names = []
    for tag in tags:
        tag_info = {
            'tagID': tag.get('tagID'),
            'leftTime': tag.get('leftTime'),
            'sourceHero': tag.get('sourceHero'),
            'name': get_tag_name(tag.get('tagID')),
            'description': get_tag_info(tag.get('tagID')).get('description', '')
        }
        tags_with_names.append(tag_info)

    return jsonify({
        'heroTagPoint': hero.get('heroTagPoint', 0),
        'heroTagData': tags_with_names
    })

@app.route('/api/hero/<int:hero_id>/talents', methods=['PUT'])
def api_hero_talents_update(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        if 'heroTagPoint' in req:
            hero['heroTagPoint'] = float(req['heroTagPoint'])
        if 'heroTagData' in req:
            hero['heroTagData'] = req['heroTagData']
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/talent', methods=['POST'])
def api_hero_talent_add(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        tag_id = req.get('tagID')
        if tag_id is None:
            return jsonify({'error': '缺少tagID'}), 400
        
        tags = hero.get('heroTagData', [])
        for t in tags:
            if t.get('tagID') == tag_id:
                return jsonify({'error': '该天赋已存在'}), 400
        
        tags.append({
            'tagID': tag_id,
            'leftTime': -1.0,
            'sourceHero': None
        })
        hero['heroTagData'] = tags
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/talent/<int:tag_id>', methods=['DELETE'])
def api_hero_talent_delete(hero_id, tag_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        tags = hero.get('heroTagData', [])
        hero['heroTagData'] = [t for t in tags if t.get('tagID') != tag_id]
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/attr', methods=['PUT'])
def api_hero_attr(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        attr_type = req.get('type')
        idx = req.get('index')
        value = float(req.get('value', 0))
        
        if attr_type == 'base':
            hero['baseAttri'][idx] = value
            hero['totalAttri'][idx] = value
        elif attr_type == 'max':
            hero['maxAttri'][idx] = value
        elif attr_type == 'fight_base':
            hero['baseFightSkill'][idx] = value
            hero['totalFightSkill'][idx] = value
        elif attr_type == 'fight_max':
            hero['maxFightSkill'][idx] = value
        elif attr_type == 'living_base':
            hero['baseLivingSkill'][idx] = value
            hero['totalLivingSkill'][idx] = value
        elif attr_type == 'living_max':
            hero['maxLivingSkill'][idx] = value
        else:
            return jsonify({'error': '无效的属性类型'}), 400
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/basic', methods=['PUT'])
def api_hero_basic(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        attr_type = req.get('type')  # 'base', 'fight', 'living'
        idx = req.get('index')
        value = req.get('value')
        if attr_type == 'base':
            modify_base_attr(hero, idx, value)
        elif attr_type == 'fight':
            modify_fight_skill(hero, idx, value)
        elif attr_type == 'living':
            modify_living_skill(hero, idx, value)
        else:
            return jsonify({'error': '无效的属性类型'}), 400
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/fight-skill', methods=['PUT'])
def api_hero_fight_skill(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        idx = req.get('index')
        value = req.get('value')
        modify_fight_skill(hero, idx, value)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/living-skill', methods=['PUT'])
def api_hero_living_skill(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        idx = req.get('index')
        value = req.get('value')
        modify_living_skill(hero, idx, value)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/status', methods=['PUT'])
def api_hero_status(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        modify_status(hero,
            hp=req.get('hp'),
            power=req.get('power'),
            mana=req.get('mana'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/fame', methods=['PUT'])
def api_hero_fame(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        modify_fame(hero, fame=req.get('fame'), bad_fame=req.get('badFame'))
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/talent', methods=['PUT'])
def api_hero_talent(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        talent = int(req.get('talent', 2))
        if talent < 0 or talent > 4:
            return jsonify({'error': '天赋值必须在0-4之间'}), 400
        hero['talent'] = talent
        return jsonify({'success': True, 'talent': talent, 'name': get_talent_name(talent)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/money', methods=['PUT'])
def api_hero_money(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        money = min(999999, max(0, int(req.get('money', 0))))
        modify_money(hero, money)
        return jsonify({'success': True, 'money': money})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/skills')
def api_hero_skills(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    skills = hero.get('kungfuSkills', [])
    result = []
    for i, skill in enumerate(skills):
        skill_id = skill.get('skillID')
        skill_info = SKILL_NAMES.get(skill_id, {})
        spe_data = skill.get('speUseData', {}).get('heroSpeAddData', {})
        spe_str = ', '.join([f"{get_spe_attr_name(k)}:{v}" for k, v in list(spe_data.items())[:3]])
        extra_data = skill.get('extraAddData', {}).get('heroSpeAddData', {})
        extra_attrs = [{'id': k, 'name': get_spe_attr_name(k), 'value': v} for k, v in extra_data.items()]
        result.append({
            'index': i,
            'skillID': skill_id,
            'name': get_skill_name(skill_id),
            'type': skill_info.get('type', ''),
            'lv': skill.get('lv', 0),
            'equiped': skill.get('equiped', False),
            'isNew': skill.get('isNew', False),
            'fightExp': skill.get('fightExp', 0),
            'bookExp': skill.get('bookExp', 0),
            'damageUseSpeAddValue': skill.get('damageUseSpeAddValue', 0),
            'selfUseSpeAddValue': skill.get('selfUseSpeAddValue', 0),
            'enemyUseSpeAddValue': skill.get('enemyUseSpeAddValue', 0),
            'speAttrs': spe_str,
            'extraAddData': extra_attrs,
        })
    return jsonify(result)

@app.route('/api/hero/<int:hero_id>/skill/<int:idx>')
def api_hero_skill_detail(hero_id, idx):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    skills = hero.get('kungfuSkills', [])
    if not (0 <= idx < len(skills)):
        return jsonify({'error': '武功序号无效'}), 400
    skill = skills[idx]
    skill_id = skill.get('skillID')
    skill_info = SKILL_NAMES.get(skill_id, {})
    
    def parse_spe_data(data):
        result = []
        for k, v in data.items():
            result.append({'id': k, 'name': get_spe_attr_name(k), 'value': v})
        return result
    
    return jsonify({
        'index': idx,
        'skillID': skill_id,
        'name': get_skill_name(skill_id),
        'type': skill_info.get('type', ''),
        'lv': skill.get('lv', 0),
        'equiped': skill.get('equiped', False),
        'isNew': skill.get('isNew', False),
        'fightExp': skill.get('fightExp', 0),
        'bookExp': skill.get('bookExp', 0),
        'damageUseSpeAddValue': skill.get('damageUseSpeAddValue', 0),
        'selfUseSpeAddValue': skill.get('selfUseSpeAddValue', 0),
        'enemyUseSpeAddValue': skill.get('enemyUseSpeAddValue', 0),
        'speEquipData': parse_spe_data(skill.get('speEquipData', {}).get('heroSpeAddData', {})),
        'speUseData': parse_spe_data(skill.get('speUseData', {}).get('heroSpeAddData', {})),
        'extraAddData': parse_spe_data(skill.get('extraAddData', {}).get('heroSpeAddData', {})),
    })

@app.route('/api/hero/<int:hero_id>/skill/<int:idx>', methods=['PUT'])
def api_hero_skill_update(hero_id, idx):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    skills = hero.get('kungfuSkills', [])
    if not (0 <= idx < len(skills)):
        return jsonify({'error': '武功序号无效'}), 400
    try:
        req = request.get_json()
        skill = skills[idx]
        if 'lv' in req:
            skill['lv'] = int(req['lv'])
        if 'damageUseSpeAddValue' in req:
            skill['damageUseSpeAddValue'] = float(req['damageUseSpeAddValue'])
        if 'selfUseSpeAddValue' in req:
            skill['selfUseSpeAddValue'] = float(req['selfUseSpeAddValue'])
        if 'enemyUseSpeAddValue' in req:
            skill['enemyUseSpeAddValue'] = float(req['enemyUseSpeAddValue'])
        if 'equiped' in req:
            skill['equiped'] = bool(req['equiped'])
        if 'speEquipData' in req or 'speUseData' in req or 'extraAddData' in req:
            for field in ['speEquipData', 'speUseData', 'extraAddData']:
                if field in req:
                    if field not in skill:
                        skill[field] = {'heroSpeAddData': {}}
                    if 'heroSpeAddData' not in skill[field]:
                        skill[field]['heroSpeAddData'] = {}
                    skill[field]['heroSpeAddData'] = {}
                    for item in req[field]:
                        attr_id = str(item['id'])
                        value = float(item['value'])
                        if value != 0:
                            skill[field]['heroSpeAddData'][attr_id] = value
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/skill/<int:idx>', methods=['DELETE'])
def api_hero_skill_delete(hero_id, idx):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    removed = remove_skill(hero, idx)
    if removed is None:
        return jsonify({'error': '武功序号无效'}), 400
    return jsonify({'success': True, 'removed': get_skill_name(removed.get('skillID'))})

@app.route('/api/hero/<int:hero_id>/skill', methods=['POST'])
def api_hero_skill_add(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        skill_id = req.get('skillID')
        lv = req.get('lv', 1)
        add_skill(hero, skill_id, lv)
        return jsonify({'success': True, 'name': get_skill_name(skill_id)})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/action', methods=['POST'])
def api_hero_action(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        action = req.get('action')
        if action == 'max_all':
            value = req.get('value', 999)
            max_all_attrs(hero, value)
        elif action == 'heal':
            heal_hero(hero)
        elif action == 'revive':
            revive_hero(hero)
        elif action == 'skills_max':
            lv = req.get('lv', 10)
            damage = req.get('damage', 999)
            all_skills_max(hero, lv, damage)
        elif action == 'money_max':
            modify_money(hero, 999999)
        elif action == 'fame_max':
            modify_fame(hero, fame=99999, bad_fame=0)
        else:
            return jsonify({'error': '未知操作'}), 400
        return jsonify({'success': True, 'action': action})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/batch/action', methods=['POST'])
def api_batch_action():
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    try:
        req = request.get_json()
        action = req.get('action')
        count = 0
        for hero in hero_data:
            if action == 'max_all':
                max_all_attrs(hero, req.get('value', 999))
            elif action == 'heal':
                heal_hero(hero)
            elif action == 'revive':
                if hero.get('dead'):
                    revive_hero(hero)
            elif action == 'skills_max':
                all_skills_max(hero, req.get('lv', 10), req.get('damage', 999))
            count += 1
        return jsonify({'success': True, 'action': action, 'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/skills/search')
def api_skills_search():
    q = request.args.get('q', '').strip()
    if not q:
        return jsonify([])
    matches = []
    for sid, info in SKILL_NAMES.items():
        if q.lower() in info.get('name', '').lower():
            matches.append({'id': sid, 'name': info['name'], 'type': info.get('type', '')})
        if len(matches) >= 50:
            break
    return jsonify(matches)

@app.route('/api/attrs/search')
def api_attrs_search():
    q = request.args.get('q', '').strip()
    matches = []
    for aid, aname in SPE_ATTR_MAP.items():
        if not q or q.lower() in aname.lower():
            matches.append({'id': aid, 'name': aname})
    return jsonify(matches)

@app.route('/api/tags/search')
def api_tags_search():
    """搜索天赋标签"""
    q = request.args.get('q', '').strip()
    matches = []
    for tid, info in TAG_NAMES.items():
        name = info.get('name', '')
        desc = info.get('description', '')
        if not q or q.lower() in name.lower() or q.lower() in desc.lower():
            matches.append({
                'id': tid,
                'name': name,
                'description': desc[:50] + '...' if len(desc) > 50 else desc,
                'category': info.get('category', '')
            })
        if len(matches) >= 100:
            break
    return jsonify(matches)

@app.route('/api/save', methods=['POST'])
def api_save():
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    try:
        backup_path = backup_file(hero_filepath)
        save_data_file(hero_data, hero_filepath)
        if save_data is not None and save_filepath:
            backup_file(save_filepath)
            save_data_file(save_data, save_filepath)
        return jsonify({'success': True, 'backup': backup_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/backup', methods=['POST'])
def api_backup():
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    try:
        backup_path = backup_file(hero_filepath)
        return jsonify({'success': True, 'backup': backup_path})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/items')
def api_hero_items(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    items_data = hero.get('itemListData', {})
    equip = hero.get('nowEquipment', {})
    all_items = items_data.get('allItem', [])
    
    def parse_spe_data(data):
        result = []
        for k, v in data.items():
            result.append({'id': k, 'name': get_spe_attr_name(k), 'value': v})
        return result
    
    def get_item_detail(item, index):
        equip_data = item.get('equipmentData', {})
        return {
            'index': index,
            'name': item.get('name', '未知'),
            'itemID': item.get('itemID', 0),
            'type': item.get('type', 0),
            'typeName': ITEM_TYPES.get(item.get('type', 0), '未知'),
            'itemLv': item.get('itemLv', 0),
            'rareLv': item.get('rareLv', 0),
            'weight': item.get('weight', 0),
            'value': item.get('value', 0),
            'equipped': equip_data.get('equiped', False) if equip_data else False,
            'baseAddData': parse_spe_data(equip_data.get('baseAddData', {}).get('heroSpeAddData', {})) if equip_data else [],
            'extraAddData': parse_spe_data(equip_data.get('extraAddData', {}).get('heroSpeAddData', {})) if equip_data else [],
        }
    
    equipped_items = {}
    for slot, records in equip.items():
        if slot.endswith('SaveRecord') and isinstance(records, list):
            slot_name = slot.replace('SaveRecord', '')
            for idx in records:
                if 0 <= idx < len(all_items):
                    item = all_items[idx]
                    if item.get('type') in [0, 1, 2, 3, 4]:
                        detail = get_item_detail(item, idx)
                        if slot_name == 'decoration':
                            if 'decorations' not in equipped_items:
                                equipped_items['decorations'] = []
                            equipped_items['decorations'].append(detail)
                        else:
                            equipped_items[slot_name] = detail
    
    items_by_type = {}
    for i, item in enumerate(all_items):
        t = item.get('type', 0)
        type_name = ITEM_TYPES.get(t, f'类型{t}')
        if type_name not in items_by_type:
            items_by_type[type_name] = []
        equip_data = item.get('equipmentData', {})
        items_by_type[type_name].append({
            'index': i,
            'name': item.get('name', '未知'),
            'itemLv': item.get('itemLv', 0),
            'rareLv': item.get('rareLv', 0),
            'type': t,
            'equipped': equip_data.get('equiped', False) if equip_data else False,
        })
    
    return jsonify({
        'money': items_data.get('money', 0),
        'weight': items_data.get('weight', 0),
        'maxWeight': items_data.get('maxWeight', 0),
        'totalItems': len(all_items),
        'equippedItems': equipped_items,
        'itemsByType': items_by_type,
    })

@app.route('/api/hero/<int:hero_id>/item/<int:item_idx>')
def api_hero_item_detail(hero_id, item_idx):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    items = hero.get('itemListData', {}).get('allItem', [])
    if not (0 <= item_idx < len(items)):
        return jsonify({'error': '物品索引无效'}), 400
    
    item = items[item_idx]
    equip_data = item.get('equipmentData', {})
    
    def parse_spe_data(data):
        result = []
        for k, v in data.items():
            result.append({'id': k, 'name': get_spe_attr_name(k), 'value': v})
        return result
    
    return jsonify({
        'index': item_idx,
        'name': item.get('name', '未知'),
        'itemID': item.get('itemID', 0),
        'type': item.get('type', 0),
        'typeName': ITEM_TYPES.get(item.get('type', 0), '未知'),
        'itemLv': item.get('itemLv', 0),
        'rareLv': item.get('rareLv', 0),
        'weight': item.get('weight', 0),
        'value': item.get('value', 0),
        'equipped': equip_data.get('equiped', False) if equip_data else False,
        'baseAddData': parse_spe_data(equip_data.get('baseAddData', {}).get('heroSpeAddData', {})) if equip_data else [],
        'extraAddData': parse_spe_data(equip_data.get('extraAddData', {}).get('heroSpeAddData', {})) if equip_data else [],
    })

@app.route('/api/hero/<int:hero_id>/item/<int:item_idx>', methods=['PUT'])
def api_hero_item_update(hero_id, item_idx):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    items = hero.get('itemListData', {}).get('allItem', [])
    if not (0 <= item_idx < len(items)):
        return jsonify({'error': '物品索引无效'}), 400
    
    try:
        req = request.get_json()
        item = items[item_idx]
        
        if 'field' in req:
            field = req['field']
            value = req['value']
            if field in ['itemLv', 'rareLv']:
                item[field] = int(value)
        
        if 'fieldName' in req and 'attrId' in req:
            field_name = req['fieldName']
            attr_id = str(req['attrId'])
            value = float(req.get('value', 0))
            
            if 'equipmentData' not in item:
                item['equipmentData'] = {
                    'enhanceLv': 0, 'littleType': 0, 'attriType': 0,
                    'baseAddData': {'heroSpeAddData': {}},
                    'extraAddData': {'heroSpeAddData': {}},
                    'equiped': False
                }
            
            equip_data = item['equipmentData']
            if field_name not in equip_data:
                equip_data[field_name] = {'heroSpeAddData': {}}
            if 'heroSpeAddData' not in equip_data[field_name]:
                equip_data[field_name]['heroSpeAddData'] = {}
            
            if value == 0:
                equip_data[field_name]['heroSpeAddData'].pop(attr_id, None)
            else:
                equip_data[field_name]['heroSpeAddData'][attr_id] = value
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/relations')
def api_hero_relations(hero_id):
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404

    def resolve_ids(ids):
        result = []
        for rid in ids:
            name = f'ID:{rid}'
            for h in hero_data:
                if h and h.get('heroID') == rid:
                    name = h.get('heroName', name)
                    break
            result.append({'id': rid, 'name': name})
        return result

    friends = resolve_ids(hero.get('Friends', []))
    haters = resolve_ids(hero.get('Haters', []))
    students = resolve_ids(hero.get('Students', []))
    teacher_id = hero.get('Teacher', -1)
    teacher = None
    if teacher_id >= 0:
        for h in hero_data:
            if h and h.get('heroID') == teacher_id:
                teacher = {'id': teacher_id, 'name': h.get('heroName', f'ID:{teacher_id}')}
                break

    lover_id = hero.get('Lover', -1)
    lover = None
    if lover_id >= 0:
        for h in hero_data:
            if h and h.get('heroID') == lover_id:
                lover = {'id': lover_id, 'name': h.get('heroName', f'ID:{lover_id}')}
                break

    return jsonify({
        'friends': friends,
        'haters': haters,
        'students': students,
        'teacher': teacher,
        'lover': lover,
    })

# ========== 好感度 API ==========

@app.route('/api/hero/<int:hero_id>/favor')
def api_hero_favor(hero_id):
    """获取角色好感度"""
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404

    favor = hero.get('favor', -999999.0)
    # 解析好感度状态
    if favor == -999999.0:
        status = 'unknown'
        status_text = '未知'
    elif favor >= 80:
        status = 'love'
        status_text = '挚爱'
    elif favor >= 60:
        status = 'close'
        status_text = '亲密'
    elif favor >= 40:
        status = 'friendly'
        status_text = '友善'
    elif favor >= 20:
        status = 'neutral_positive'
        status_text = '略有好感'
    elif favor >= 0:
        status = 'neutral'
        status_text = '中立'
    elif favor >= -20:
        status = 'neutral_negative'
        status_text = '略有不悦'
    elif favor >= -40:
        status = 'dislike'
        status_text = '厌恶'
    elif favor >= -60:
        status = 'hate'
        status_text = '憎恨'
    elif favor >= -80:
        status = 'enemy'
        status_text = '仇敌'
    else:
        status = 'nemesis'
        status_text = '死敌'

    return jsonify({
        'heroID': hero_id,
        'heroName': hero.get('heroName', '未知'),
        'favor': favor,
        'status': status,
        'statusText': status_text,
    })

@app.route('/api/hero/<int:hero_id>/favor', methods=['PUT'])
def api_hero_favor_update(hero_id):
    """设置角色好感度"""
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        value = float(req.get('favor', 0))
        modify_favor(hero, value)
        return jsonify({'success': True, 'favor': hero['favor']})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/relations', methods=['PUT'])
def api_hero_relations_update(hero_id):
    """更新人际关系"""
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        action = req.get('action')
        target_id = req.get('targetID')
        relation_type = req.get('type')

        if action == 'add':
            if relation_type == 'friend':
                add_friend(hero, target_id)
            elif relation_type == 'hater':
                add_hater(hero, target_id)
            elif relation_type == 'lover':
                set_lover(hero, target_id)
        elif action == 'remove':
            if relation_type == 'friend':
                remove_friend(hero, target_id)
            elif relation_type == 'hater':
                remove_hater(hero, target_id)
            elif relation_type == 'lover':
                set_lover(hero, -1)
        else:
            return jsonify({'error': '无效的操作'}), 400

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/heroes/favor')
def api_heroes_favor():
    """获取所有角色的好感度列表"""
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400

    result = []
    for hero in hero_data:
        if hero is None:
            continue
        favor = hero.get('favor', -999999.0)
        result.append({
            'heroID': hero.get('heroID'),
            'heroName': hero.get('heroName', '未知'),
            'favor': favor,
            'isUnknown': favor == -999999.0,
            'forceID': hero.get('belongForceID', -1),
            'forceName': FORCE_MAP.get(hero.get('belongForceID', -1), '无'),
        })
    return jsonify(result)

@app.route('/api/heroes/favor/batch', methods=['POST'])
def api_heroes_favor_batch():
    """批量设置好感度"""
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    try:
        req = request.get_json()
        value = float(req.get('favor', 0))
        mode = req.get('mode', 'all')  # all, team, force

        count = 0
        for hero in hero_data:
            if hero is None:
                continue
            if mode == 'all':
                modify_favor(hero, value)
                count += 1
            elif mode == 'team' and hero.get('inTeam', False):
                modify_favor(hero, value)
                count += 1
            elif mode == 'force':
                target_force = req.get('forceID')
                if hero.get('belongForceID') == target_force:
                    modify_favor(hero, value)
                    count += 1

        return jsonify({'success': True, 'count': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# ========== 物品管理 API ==========

@app.route('/api/hero/<int:hero_id>/item', methods=['POST'])
def api_hero_item_add(hero_id):
    """添加物品到角色背包"""
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        item = {
            'itemID': req.get('itemID', 0),
            'name': req.get('name', '新物品'),
            'type': req.get('type', 10),
            'subType': req.get('subType', 0),
            'itemLv': req.get('itemLv', 1),
            'rareLv': req.get('rareLv', 0),
            'weight': req.get('weight', 1.0),
            'value': req.get('value', 0),
            'isNew': True,
            'poisonNum': 0.0,
            'poisonNumDetected': False,
            'equipmentData': None,
            'medFoodData': None,
            'bookData': None,
            'treasureData': None,
            'materialData': None,
            'horseData': None,
        }
        add_item(hero, item)
        return jsonify({'success': True, 'item': item})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/hero/<int:hero_id>/item/<int:item_idx>', methods=['DELETE'])
def api_hero_item_delete(hero_id, item_idx):
    """删除物品"""
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    removed = remove_item(hero, item_idx)
    if removed is None:
        return jsonify({'error': '物品索引无效'}), 400
    return jsonify({'success': True, 'removed': removed.get('name', '未知物品')})

@app.route('/api/hero/<int:hero_id>/items/batch', methods=['POST'])
def api_hero_items_batch(hero_id):
    """批量操作物品"""
    if hero_data is None:
        return jsonify({'error': '存档未加载'}), 400
    hero = find_hero_by_id(hero_id)
    if hero is None:
        return jsonify({'error': '角色未找到'}), 404
    try:
        req = request.get_json()
        action = req.get('action')

        if action == 'remove_all_type':
            item_type = req.get('type')
            items = hero.get('itemListData', {}).get('allItem', [])
            original_count = len(items)
            hero['itemListData']['allItem'] = [i for i in items if i.get('type') != item_type]
            removed = original_count - len(hero['itemListData']['allItem'])
            return jsonify({'success': True, 'removed': removed})
        elif action == 'remove_duplicates':
            items = hero.get('itemListData', {}).get('allItem', [])
            seen_names = set()
            unique_items = []
            for item in items:
                name = item.get('name', '')
                if name not in seen_names:
                    seen_names.add(name)
                    unique_items.append(item)
            removed = len(items) - len(unique_items)
            hero['itemListData']['allItem'] = unique_items
            return jsonify({'success': True, 'removed': removed})
        else:
            return jsonify({'error': '无效的操作'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/items/types')
def api_items_types():
    """获取物品类型列表"""
    return jsonify([{'id': k, 'name': v} for k, v in ITEM_TYPES.items()])

# ========== 启动 ==========

def open_browser():
    """延迟打开浏览器"""
    import webbrowser
    import threading
    def _open():
        import time
        time.sleep(1.5)  # 等待服务器启动
        webbrowser.open('http://localhost:5000')
    threading.Thread(target=_open, daemon=True).start()

def get_resource_path(relative_path):
    """获取资源文件路径（兼容 PyInstaller 打包）"""
    try:
        # PyInstaller 打包后的路径
        import sys
        from pathlib import Path
        base_path = Path(sys._MEIPASS)
        return base_path / relative_path
    except Exception:
        # 开发环境路径
        from pathlib import Path
        return Path(__file__).parent / relative_path

if __name__ == '__main__':
    import sys
    import os
    from pathlib import Path

    # 切换工作目录到 exe 所在目录（打包后需要）
    if getattr(sys, 'frozen', False):
        os.chdir(Path(sys.executable).parent)

    print("=" * 50)
    print("  龙胤立志传 - Web 存档修改器")
    print("=" * 50)
    print()
    print("  服务器地址: http://localhost:5000")
    print("  按 Ctrl+C 停止服务器")
    print()

    # 检查必要文件
    if not os.path.exists('Hero'):
        print("  [提示] 当前目录未找到 Hero 存档文件")
        print("  [提示] 请将游戏存档文件 Hero 复制到此目录")
        print()

    # 自动打开浏览器（仅非调试模式）
    if not os.environ.get('FLASK_DEBUG'):
        open_browser()

    try:
        app.run(host='127.0.0.1', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n服务器已停止")