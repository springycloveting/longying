#!/usr/bin/env python3
"""
龙胤立志传存档修改器 - 交互式命令行工具
"""

import json
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
    print(f"✓ 已备份到: {backup_path}")
    return backup_path

def load_hero_data(filepath='Hero'):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_hero_data(data, filepath='Hero'):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"✓ 存档已保存: {filepath}")

def find_hero_by_name(data, name):
    for i, hero in enumerate(data):
        if hero.get('heroName') == name:
            return i, hero
    return None, None

def print_hero_summary(hero):
    """打印角色属性摘要"""
    print(f"\n{'='*60}")
    print(f"角色: {hero.get('heroName', '未知')} (ID: {hero.get('heroID')})")
    print(f"{'='*60}")

    base_attri = hero.get('baseAttri', [0]*6)
    total_attri = hero.get('totalAttri', [0]*6)
    max_attri = hero.get('maxAttri', [0]*6)

    print("\n【基础属性】基础值/总值/上限")
    for i, name in enumerate(ATTR_NAMES):
        print(f"  {i}. {name}: {base_attri[i]:.0f} / {total_attri[i]:.0f} / {max_attri[i]:.0f}")

    base_fight = hero.get('baseFightSkill', [0]*9)
    total_fight = hero.get('totalFightSkill', [0]*9)
    max_fight = hero.get('maxFightSkill', [0]*9)

    print("\n【武学属性】基础值/总值/上限")
    for i, name in enumerate(FIGHT_SKILL_NAMES):
        print(f"  {i}. {name}: {base_fight[i]:.0f} / {total_fight[i]:.0f} / {max_fight[i]:.0f}")

    print(f"\n【生命/内力/真气】")
    print(f"  生命: {hero.get('hp', 0):.0f} / {hero.get('maxhp', 0):.0f}")
    print(f"  内力: {hero.get('power', 0):.0f} / {hero.get('maxPower', 0):.0f}")
    print(f"  真气: {hero.get('mana', 0):.0f} / {hero.get('maxMana', 0):.0f}")

def modify_attribute(hero, attr_type, attr_index, new_value):
    """修改属性"""
    if attr_type == 'attri':
        hero['baseAttri'][attr_index] = float(new_value)
        hero['totalAttri'][attr_index] = float(new_value)
        hero['maxAttri'][attr_index] = float(new_value)
    elif attr_type == 'fight':
        hero['baseFightSkill'][attr_index] = float(new_value)
        hero['totalFightSkill'][attr_index] = float(new_value)
        hero['maxFightSkill'][attr_index] = float(new_value)

def modify_all_max(hero, value=999):
    """将所有属性设为指定值"""
    for i in range(6):
        modify_attribute(hero, 'attri', i, value)
    for i in range(9):
        modify_attribute(hero, 'fight', i, value)

    hero['hp'] = float(value)
    hero['maxhp'] = float(value)
    hero['realMaxHp'] = float(value)
    hero['power'] = float(value)
    hero['maxPower'] = float(value)
    hero['realMaxPower'] = float(value)
    hero['mana'] = float(value)
    hero['maxMana'] = float(value)
    hero['realMaxMana'] = float(value)

def modify_hp_mp(hero, value=9999):
    """修改生命和内力"""
    hero['hp'] = float(value)
    hero['maxhp'] = float(value)
    hero['realMaxHp'] = float(value)
    hero['power'] = float(value)
    hero['maxPower'] = float(value)
    hero['realMaxPower'] = float(value)
    hero['mana'] = float(value)
    hero['maxMana'] = float(value)
    hero['realMaxMana'] = float(value)

def interactive_mode():
    """交互式修改模式"""
    print("\n" + "="*60)
    print("龙胤立志传 存档修改器")
    print("="*60)

    # 加载存档
    data = load_hero_data()
    idx, hero = find_hero_by_name(data, '杨春')

    if not hero:
        print("未找到主角杨春!")
        return

    while True:
        print_hero_summary(hero)

        print("\n" + "-"*60)
        print("修改选项:")
        print("  1. 修改单个基础属性 (力量/灵巧/智力/意志/体质/经脉)")
        print("  2. 修改单个武学属性 (内力/轻功/绝技/拳法等)")
        print("  3. 一键全属性满 (999)")
        print("  4. 修改生命/内力/真气上限")
        print("  5. 保存存档")
        print("  6. 备份存档")
        print("  0. 退出")
        print("-"*60)

        choice = input("\n请选择操作 [0-6]: ").strip()

        if choice == '0':
            print("再见!")
            break

        elif choice == '1':
            print("\n选择要修改的属性:")
            for i, name in enumerate(ATTR_NAMES):
                print(f"  {i}. {name}")
            idx_input = input("输入属性编号 [0-5]: ").strip()
            try:
                attr_idx = int(idx_input)
                if 0 <= attr_idx < 6:
                    new_val = input(f"输入新的 {ATTR_NAMES[attr_idx]} 值: ").strip()
                    modify_attribute(hero, 'attri', attr_idx, float(new_val))
                    print(f"✓ {ATTR_NAMES[attr_idx]} 已修改为 {new_val}")
            except:
                print("✗ 输入无效!")

        elif choice == '2':
            print("\n选择要修改的武学:")
            for i, name in enumerate(FIGHT_SKILL_NAMES):
                print(f"  {i}. {name}")
            idx_input = input("输入武学编号 [0-8]: ").strip()
            try:
                attr_idx = int(idx_input)
                if 0 <= attr_idx < 9:
                    new_val = input(f"输入新的 {FIGHT_SKILL_NAMES[attr_idx]} 值: ").strip()
                    modify_attribute(hero, 'fight', attr_idx, float(new_val))
                    print(f"✓ {FIGHT_SKILL_NAMES[attr_idx]} 已修改为 {new_val}")
            except:
                print("✗ 输入无效!")

        elif choice == '3':
            confirm = input("确认将所有属性设为999? (y/n): ").strip().lower()
            if confirm == 'y':
                modify_all_max(hero, 999)
                print("✓ 所有属性已设为999!")

        elif choice == '4':
            val = input("输入生命/内力/真气上限值 [默认9999]: ").strip()
            val = float(val) if val else 9999
            modify_hp_mp(hero, val)
            print(f"✓ 生命/内力/真气已修改为 {val}")

        elif choice == '5':
            backup_file('Hero')
            save_hero_data(data, 'Hero')
            print("✓ 存档已保存!")

        elif choice == '6':
            backup_file('Hero')

if __name__ == '__main__':
    interactive_mode()
