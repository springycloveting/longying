#!/usr/bin/env python3
"""
龙胤立志传存档解析与修改工具
游戏存档文件: Hero, Save, TempHero, Info
"""

import json
import os
import shutil
from datetime import datetime

# 属性名称映射
ATTR_NAMES = ['力量', '灵巧', '智力', '意志', '体质', '经脉']
FIGHT_SKILL_NAMES = ['内力', '轻功', '绝技', '拳法', '剑法', '刀法', '枪法', '奇门', '射术']

def backup_file(filepath):
    """备份存档文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    return backup_path

def load_hero_data(filepath='Hero'):
    """加载 Hero 存档"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_hero_data(data, filepath='Hero'):
    """保存 Hero 存档"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def find_hero_by_name(data, name):
    """根据名字查找角色"""
    for i, hero in enumerate(data):
        if hero.get('heroName') == name:
            return i, hero
    return None, None

def print_hero_info(hero):
    """打印角色详细信息"""
    print(f"\n{'='*50}")
    print(f"角色: {hero.get('heroName', '未知')}")
    print(f"{'='*50}")

    # 基本信息
    print(f"\n【基本信息】")
    print(f"  ID: {hero.get('heroID')}")
    print(f"  年龄: {hero.get('age', 'N/A')}")
    print(f"  性别: {'女' if hero.get('isFemale') else '男'}")
    print(f"  所属门派ID: {hero.get('belongForceID')}")
    print(f"  门派职位: {hero.get('forceJobID', 'N/A')}")
    print(f"  门派贡献: {hero.get('forceContribution', 'N/A')}")
    print(f"  声望: {hero.get('fame', 'N/A')}")
    print(f"  恶名: {hero.get('badFame', 'N/A')}")
    print(f"  正义值: {hero.get('goodKungfuSkillName', 'N/A')}")

    # 生命/内力
    print(f"\n【生命与内力】")
    print(f"  生命: {hero.get('hp', 'N/A')} / {hero.get('maxhp', 'N/A')}")
    print(f"  内力: {hero.get('power', 'N/A')} / {hero.get('maxPower', 'N/A')}")
    print(f"  真气: {hero.get('mana', 'N/A')} / {hero.get('maxMana', 'N/A')}")

    # 基础属性
    print(f"\n【基础属性】 (基础值 / 总值 / 上限)")
    base_attri = hero.get('baseAttri', [0]*6)
    total_attri = hero.get('totalAttri', [0]*6)
    max_attri = hero.get('maxAttri', [0]*6)

    for i, name in enumerate(ATTR_NAMES):
        base = base_attri[i] if i < len(base_attri) else 0
        total = total_attri[i] if i < len(total_attri) else 0
        max_val = max_attri[i] if i < len(max_attri) else 0
        print(f"  {name}: {base:.0f} / {total:.0f} / {max_val:.0f}")

    # 武学属性
    print(f"\n【武学属性】 (基础值 / 总值 / 上限)")
    base_fight = hero.get('baseFightSkill', [0]*9)
    total_fight = hero.get('totalFightSkill', [0]*9)
    max_fight = hero.get('maxFightSkill', [0]*9)

    for i, name in enumerate(FIGHT_SKILL_NAMES):
        base = base_fight[i] if i < len(base_fight) else 0
        total = total_fight[i] if i < len(total_fight) else 0
        max_val = max_fight[i] if i < len(max_fight) else 0
        print(f"  {name}: {base:.0f} / {total:.0f} / {max_val:.0f}")

    # 武功技能
    print(f"\n【已学武功】")
    kungfu_skills = hero.get('kungfuSkills', [])
    for skill in kungfu_skills[:10]:  # 只显示前10个
        print(f"  - {skill}")
    if len(kungfu_skills) > 10:
        print(f"  ... 共 {len(kungfu_skills)} 门武功")

    # 物品
    print(f"\n【物品栏】")
    items = hero.get('itemListData', [])
    print(f"  物品数量: {len(items)}")

    return hero

def modify_attribute(hero, attr_type, attr_index, new_value):
    """
    修改属性
    attr_type: 'baseAttri' 或 'baseFightSkill'
    attr_index: 属性索引 (0-5 属性, 0-8 武学)
    new_value: 新值
    """
    if attr_type == 'baseAttri':
        fields = ['baseAttri', 'totalAttri', 'maxAttri']
    elif attr_type == 'baseFightSkill':
        fields = ['baseFightSkill', 'totalFightSkill', 'maxFightSkill']
    else:
        raise ValueError(f"未知的属性类型: {attr_type}")

    for field in fields:
        if field in hero:
            hero[field][attr_index] = float(new_value)

    return hero

def modify_all_attributes_max(hero, max_value=999):
    """将所有属性和武学设置为最大值"""
    # 修改基础属性
    hero['baseAttri'] = [float(max_value)] * 6
    hero['totalAttri'] = [float(max_value)] * 6
    hero['maxAttri'] = [float(max_value)] * 6

    # 修改武学属性
    hero['baseFightSkill'] = [float(max_value)] * 9
    hero['totalFightSkill'] = [float(max_value)] * 9
    hero['maxFightSkill'] = [float(max_value)] * 9

    # 修改生命内力
    hero['hp'] = float(max_value)
    hero['maxhp'] = float(max_value)
    hero['realMaxHp'] = float(max_value)
    hero['power'] = float(max_value)
    hero['maxPower'] = float(max_value)
    hero['realMaxPower'] = float(max_value)
    hero['mana'] = float(max_value)
    hero['maxMana'] = float(max_value)
    hero['realMaxMana'] = float(max_value)

    return hero

def main():
    print("=" * 60)
    print("龙胤立志传 存档解析工具")
    print("=" * 60)

    # 加载存档
    data = load_hero_data()

    # 查找主角
    idx, hero = find_hero_by_name(data, '杨春')

    if hero:
        print_hero_info(hero)
    else:
        print("\n未找到主角杨春，显示第一个角色信息：")
        print_hero_info(data[0])

    print("\n" + "=" * 60)
    print("使用方法示例：")
    print("=" * 60)
    print("""
# Python 交互式修改示例：

from save_parser import *

# 加载存档
data = load_hero_data()

# 找到主角
idx, hero = find_hero_by_name(data, '杨春')

# 修改单个属性（属性索引：0力量 1灵巧 2智力 3意志 4体质 5经脉）
modify_attribute(hero, 'baseAttri', 0, 999)  # 力量改为999

# 修改单个武学（武学索引：0内力 1轻功 2绝技 3拳法 4剑法 5刀法 6枪法 7奇门 8射术）
modify_attribute(hero, 'baseFightSkill', 0, 999)  # 内力改为999

# 一键全满
modify_all_attributes_max(hero, 999)

# 保存存档（会自动备份）
backup_file('Hero')
save_hero_data(data, 'Hero')
""")

if __name__ == '__main__':
    main()
