#!/usr/bin/env python3
"""
龙胤立志传 - 武功修改器
支持修改所有角色的武功等级、突破属性
"""

import json
import shutil
import os
from datetime import datetime

# 加载武功名称映射
SKILL_NAMES = {}
if os.path.exists('skill_names.json'):
    with open('skill_names.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        for k, v in data.items():
            SKILL_NAMES[int(k)] = v

# 加载突破属性ID映射
SPE_ATTR_MAP = {}
if os.path.exists('spe_attr_map.json'):
    with open('spe_attr_map.json', 'r', encoding='utf-8') as f:
        SPE_ATTR_MAP = json.load(f)
else:
    # 默认映射（如果文件不存在）
    SPE_ATTR_MAP = {
        '0': '力道', '1': '灵巧', '2': '智力', '3': '意志', '4': '体质',
        '5': '经脉', '6': '内功', '7': '轻功', '8': '绝技', '9': '拳掌',
        '10': '剑法', '11': '刀法', '12': '长兵', '13': '奇门', '14': '射术',
        '57': '生命上限', '58': '体力上限', '59': '内力上限', '60': '伤害',
        '61': '护甲', '62': '护甲率', '63': '速度', '64': '命中', '65': '闪避',
        '66': '暴击', '67': '卸力', '68': '反击', '69': '压制', '70': '连击',
    }

def get_skill_name(skill_id):
    """获取武功名称"""
    if skill_id in SKILL_NAMES:
        return SKILL_NAMES[skill_id].get('name', f'未知({skill_id})')
    return f'未知({skill_id})'

def get_skill_type(skill_id):
    """获取武功类型"""
    if skill_id in SKILL_NAMES:
        return SKILL_NAMES[skill_id].get('type', '')
    return ''

def get_spe_attr_name(attr_id):
    """获取突破属性名称"""
    attr_key = str(attr_id)
    return SPE_ATTR_MAP.get(attr_key, f'属性{attr_id}')

# 基础属性名称
ATTR_NAMES = ['力道', '灵巧', '智力', '意志', '体质', '经脉']
# 武学属性名称
FIGHT_SKILL_NAMES = ['内功', '轻功', '绝技', '拳掌', '剑法', '刀法', '长兵', '奇门', '射术']
# 技能属性名称
LIVING_SKILL_NAMES = ['医术', '毒术', '学识', '口才', '采伐', '木植', '锻造', '炼丹', '烹饪']

def backup_file(filepath='Hero'):
    """备份存档文件"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    print(f"✓ 已备份到: {backup_path}")
    return backup_path

def load_data(filepath='Hero'):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data, filepath='Hero'):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)
    print(f"✓ 存档已保存: {filepath}")

def find_hero(data, identifier):
    """根据名字或ID查找角色"""
    for i, hero in enumerate(data):
        if hero.get('heroName') == identifier or str(hero.get('heroID')) == str(identifier):
            return i, hero
    return None, None

def find_hero_by_name(data, name):
    """根据名字查找角色"""
    return find_hero(data, name)

def list_heroes(data, limit=50):
    """列出所有角色"""
    print(f"\n{'='*70}")
    print(f"{'序号':<4} {'ID':<6} {'名字':<10} {'武功数':<6} {'在队':<4} {'死亡':<4}")
    print(f"{'='*70}")

    for i, hero in enumerate(data[:limit]):
        name = hero.get('heroName', '未知')
        hero_id = hero.get('heroID')
        skills_count = len(hero.get('kungfuSkills', []))
        in_team = '✓' if hero.get('inTeam') else ''
        dead = '✓' if hero.get('dead') else ''
        print(f"{i:<4} {hero_id:<6} {name:<10} {skills_count:<6} {in_team:<4} {dead:<4}")

    if len(data) > limit:
        print(f"... 共 {len(data)} 个角色")

def print_hero_brief(hero):
    """打印角色简要信息"""
    print(f"\n【{hero.get('heroName')} (ID:{hero.get('heroID')})】")
    print(f"  年龄: {hero.get('age')} | 性别: {'女' if hero.get('isFemale') else '男'}")
    print(f"  生命: {hero.get('hp', 0):.0f}/{hero.get('maxhp', 0):.0f}")
    print(f"  体力: {hero.get('power', 0):.0f}/{hero.get('maxPower', 0):.0f}")
    print(f"  内力: {hero.get('mana', 0):.0f}/{hero.get('maxMana', 0):.0f}")

    base_attri = hero.get('baseAttri', [0]*6)
    print(f"  属性: 力道{base_attri[0]:.0f} 灵巧{base_attri[1]:.0f} 智力{base_attri[2]:.0f} "
          f"意志{base_attri[3]:.0f} 体质{base_attri[4]:.0f} 经脉{base_attri[5]:.0f}")

def list_kungfu_skills(hero):
    """列出角色的所有武功"""
    skills = hero.get('kungfuSkills', [])
    print(f"\n【已学武功】共 {len(skills)} 门")
    print(f"{'序号':<4} {'ID':<5} {'武功名称':<12} {'类型':<6} {'等级':<4} {'装备':<4} {'突破属性'}")
    print("-" * 80)

    for i, skill in enumerate(skills):
        skill_id = skill.get('skillID')
        lv = skill.get('lv')
        equiped = '✓' if skill.get('equiped') else ''

        # 获取武功名称和类型
        skill_name = get_skill_name(skill_id)
        skill_type = get_skill_type(skill_id)

        # 显示特殊属性
        spe_data = skill.get('speUseData', {}).get('heroSpeAddData', {})
        spe_str = ', '.join([f"{get_spe_attr_name(k)}:{v}" for k, v in list(spe_data.items())[:2]])
        if len(spe_data) > 2:
            spe_str += '...'

        print(f"{i:<4} {skill_id:<5} {skill_name:<12} {skill_type:<6} {lv:<4} {equiped:<4} {spe_str}")

def print_skill_detail(skill):
    """打印武功详细信息"""
    skill_id = skill.get('skillID')
    skill_name = get_skill_name(skill_id)
    skill_type = get_skill_type(skill_id)

    print(f"\n{'='*50}")
    print(f"【武功详细信息】")
    print(f"{'='*50}")
    print(f"  武功名称: {skill_name}")
    print(f"  武功类型: {skill_type}")
    print(f"  skillID: {skill_id}")
    print(f"  等级 (lv): {skill.get('lv')}")
    print(f"  实战经验 (fightExp): {skill.get('fightExp')}")
    print(f"  理论经验 (bookExp): {skill.get('bookExp')}")
    print(f"  已装备 (equiped): {skill.get('equiped')}")
    print(f"  是否新学 (isNew): {skill.get('isNew')}")

    print(f"\n【装备加成 (speEquipData)】")
    spe_equip = skill.get('speEquipData', {}).get('heroSpeAddData', {})
    for k, v in spe_equip.items():
        print(f"    {get_spe_attr_name(k)}: {v}")

    print(f"\n【特殊属性 (speUseData)】")
    spe_use = skill.get('speUseData', {}).get('heroSpeAddData', {})
    for k, v in spe_use.items():
        print(f"    {get_spe_attr_name(k)}: {v}")

    print(f"\n【突破属性 (extraAddData)】")
    extra = skill.get('extraAddData', {}).get('heroSpeAddData', {})
    for k, v in extra.items():
        print(f"    {get_spe_attr_name(k)}: {v}")

    print(f"\n【伤害/自身/敌人加成】")
    print(f"  damageUseSpeAddValue: {skill.get('damageUseSpeAddValue')}")
    print(f"  selfUseSpeAddValue: {skill.get('selfUseSpeAddValue')}")
    print(f"  enemyUseSpeAddValue: {skill.get('enemyUseSpeAddValue')}")

def modify_skill_lv(skill, new_lv):
    """修改武功等级"""
    skill['lv'] = int(new_lv)
    return skill

def modify_skill_spe_data(skill, spe_type, attr_key, attr_value):
    """
    修改武功突破属性
    spe_type: 'speEquipData', 'speUseData', 'extraAddData'
    attr_key: 属性ID (如 '0'=力量, '57'=剑法精通)
    attr_value: 属性值
    """
    if spe_type not in skill:
        skill[spe_type] = {'heroSpeAddData': {}}
    if 'heroSpeAddData' not in skill[spe_type]:
        skill[spe_type]['heroSpeAddData'] = {}

    skill[spe_type]['heroSpeAddData'][str(attr_key)] = float(attr_value)
    return skill

def modify_skill_damage(skill, damage_val, self_val=0, enemy_val=0):
    """修改武功伤害加成"""
    skill['damageUseSpeAddValue'] = float(damage_val)
    skill['selfUseSpeAddValue'] = float(self_val)
    skill['enemyUseSpeAddValue'] = float(enemy_val)
    return skill

def modify_all_skills_max(hero, max_lv=10, max_damage=999):
    """将角色所有武功设为满级"""
    for skill in hero.get('kungfuSkills', []):
        skill['lv'] = max_lv
        skill['damageUseSpeAddValue'] = float(max_damage)

def add_skill_to_hero(hero, skill_id, lv=1):
    """给角色添加新武功"""
    new_skill = {
        'skillID': skill_id,
        'lv': lv,
        'fightExp': 0.0,
        'bookExp': 0.0,
        'equiped': False,
        'isNew': True,
        'belongHeroID': hero.get('heroID'),
        'speEquipData': {'heroSpeAddData': {}},
        'equipUseSpeAddValue': 0.0,
        'speUseData': {'heroSpeAddData': {}},
        'damageUseSpeAddValue': 0.0,
        'selfUseSpeAddValue': 0.0,
        'enemyUseSpeAddValue': 0.0,
        'extraAddData': {'heroSpeAddData': {}},
        'maxManaChanged': False
    }
    hero['kungfuSkills'].append(new_skill)
    return hero

def print_hero_attributes(hero):
    """打印角色完整属性"""
    print(f"\n{'='*70}")
    print(f"【{hero.get('heroName')}】完整属性")
    print(f"{'='*70}")

    # 生命/体力/内力
    print(f"\n【状态】")
    print(f"  生命: {hero.get('hp', 0):.0f}/{hero.get('maxhp', 0):.0f}")
    print(f"  体力: {hero.get('power', 0):.0f}/{hero.get('maxPower', 0):.0f}")
    print(f"  内力: {hero.get('mana', 0):.0f}/{hero.get('maxMana', 0):.0f}")

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

    # 技能属性
    print(f"\n【技能属性】 (基础值 / 总值 / 上限)")
    base_living = hero.get('baseLivingSkill', [0]*9)
    total_living = hero.get('totalLivingSkill', [0]*9)
    max_living = hero.get('maxLivingSkill', [0]*9)
    for i, name in enumerate(LIVING_SKILL_NAMES):
        base = base_living[i] if i < len(base_living) else 0
        total = total_living[i] if i < len(total_living) else 0
        max_val = max_living[i] if i < len(max_living) else 0
        print(f"  {name}: {base:.0f} / {total:.0f} / {max_val:.0f}")

def modify_living_skill(hero, skill_idx, new_value):
    """修改技能属性"""
    hero['baseLivingSkill'][skill_idx] = float(new_value)
    hero['totalLivingSkill'][skill_idx] = float(new_value)
    hero['maxLivingSkill'][skill_idx] = float(new_value)

def interactive_mode():
    """交互式修改模式"""
    print("\n" + "="*70)
    print("龙胤立志传 - 武功修改器")
    print("="*70)

    data = load_data()
    current_hero = None
    current_hero_idx = None

    while True:
        print("\n" + "-"*70)
        print("主菜单:")
        print("  1. 列出所有角色")
        print("  2. 选择角色 (输入名字或ID)")
        print("  3. 查看当前角色武功列表")
        print("  4. 查看武功详情")
        print("  5. 修改武功等级")
        print("  6. 修改武功突破属性")
        print("  7. 修改武功伤害加成")
        print("  8. 所有武功满级")
        print("  9. 给角色添加新武功")
        print("  10. 修改角色基础属性")
        print("  11. 修改角色武学属性")
        print("  12. 查看完整属性")
        print("  13. 修改技能属性")
        print("  s. 保存存档")
        print("  b. 备份存档")
        print("  0. 退出")
        print("-"*70)

        if current_hero:
            print(f"当前角色: {current_hero.get('heroName')} (ID:{current_hero.get('heroID')})")

        choice = input("\n请选择 [0-13/s/b]: ").strip().lower()

        if choice == '0':
            print("再见!")
            break

        elif choice == '1':
            list_heroes(data)

        elif choice == '2':
            identifier = input("输入角色名字或ID: ").strip()
            idx, hero = find_hero(data, identifier)
            if hero:
                current_hero_idx = idx
                current_hero = hero
                print_hero_brief(current_hero)
            else:
                print(f"✗ 未找到角色: {identifier}")

        elif choice == '3':
            if current_hero:
                list_kungfu_skills(current_hero)
            else:
                print("✗ 请先选择角色!")

        elif choice == '4':
            if not current_hero:
                print("✗ 请先选择角色!")
                continue
            skill_idx = input("输入武功序号: ").strip()
            try:
                skills = current_hero.get('kungfuSkills', [])
                skill = skills[int(skill_idx)]
                print_skill_detail(skill)
            except:
                print("✗ 无效的武功序号!")

        elif choice == '5':
            if not current_hero:
                print("✗ 请先选择角色!")
                continue
            skill_idx = input("输入武功序号: ").strip()
            new_lv = input("输入新等级 [1-10]: ").strip()
            try:
                skills = current_hero.get('kungfuSkills', [])
                skill = skills[int(skill_idx)]
                skill_id = skill.get('skillID')
                skill_name = get_skill_name(skill_id)
                modify_skill_lv(skill, int(new_lv))
                print(f"✓ 【{skill_name}】等级已改为 {new_lv}")
            except:
                print("✗ 输入无效!")

        elif choice == '6':
            if not current_hero:
                print("✗ 请先选择角色!")
                continue
            try:
                skill_idx = input("输入武功序号: ").strip()
                skills = current_hero.get('kungfuSkills', [])
                skill = skills[int(skill_idx)]
                skill_name = get_skill_name(skill.get('skillID'))

                print(f"\n正在修改【{skill_name}】的突破属性")

                print("\n属性类型:")
                print("  1. speEquipData (装备加成)")
                print("  2. speUseData (特殊属性)")
                print("  3. extraAddData (突破属性)")
                spe_type_choice = input("选择类型 [1-3]: ").strip()
                spe_types = {'1': 'speEquipData', '2': 'speUseData', '3': 'extraAddData'}
                spe_type = spe_types.get(spe_type_choice)

                if spe_type:
                    # 搜索属性
                    search = input("\n输入属性ID或名称(支持模糊搜索): ").strip()

                    attr_key = None
                    if search.isdigit():
                        attr_key = search
                    else:
                        # 模糊搜索
                        matches = []
                        for k, v in SPE_ATTR_MAP.items():
                            if search in v:
                                matches.append((k, v))

                        if len(matches) == 0:
                            print(f"✗ 未找到包含 '{search}' 的属性")
                            continue
                        elif len(matches) == 1:
                            attr_key, attr_name = matches[0]
                        else:
                            print(f"\n找到 {len(matches)} 个匹配的属性:")
                            for i, (k, v) in enumerate(matches[:20]):
                                print(f"  {i}. ID {k}: {v}")
                            if len(matches) > 20:
                                print(f"  ... 还有 {len(matches)-20} 个")
                            idx = int(input("\n选择序号: ").strip())
                            attr_key, attr_name = matches[idx]

                    attr_name = get_spe_attr_name(attr_key)
                    attr_value = input(f"输入【{attr_name}】的值: ").strip()
                    modify_skill_spe_data(skill, spe_type, attr_key, float(attr_value))
                    print(f"✓ 已修改【{attr_name}】= {attr_value}")
            except Exception as e:
                print(f"✗ 输入无效! {e}")

        elif choice == '7':
            if not current_hero:
                print("✗ 请先选择角色!")
                continue
            try:
                skill_idx = input("输入武功序号: ").strip()
                skills = current_hero.get('kungfuSkills', [])
                skill = skills[int(skill_idx)]

                damage = input("输入伤害加成 [默认999]: ").strip() or '999'
                self_val = input("输入自身加成 [默认0]: ").strip() or '0'
                enemy_val = input("输入敌人加成 [默认0]: ").strip() or '0'

                modify_skill_damage(skill, damage, self_val, enemy_val)
                print(f"✓ 已修改!")
            except:
                print("✗ 输入无效!")

        elif choice == '8':
            if not current_hero:
                print("✗ 请先选择角色!")
                continue
            confirm = input("确认将所有武功设为满级? (y/n): ").strip().lower()
            if confirm == 'y':
                modify_all_skills_max(current_hero)
                print("✓ 所有武功已满级!")

        elif choice == '9':
            if not current_hero:
                print("✗ 请先选择角色!")
                continue
            try:
                # 搜索武功
                search = input("输入武功ID或名称(支持模糊搜索): ").strip()

                # 如果是数字，直接使用
                if search.isdigit():
                    skill_id = int(search)
                    skill_name = get_skill_name(skill_id)
                else:
                    # 模糊搜索
                    matches = []
                    for sid, info in SKILL_NAMES.items():
                        if search in info.get('name', ''):
                            matches.append((sid, info['name']))

                    if len(matches) == 0:
                        print(f"✗ 未找到包含 '{search}' 的武功")
                        continue
                    elif len(matches) == 1:
                        skill_id, skill_name = matches[0]
                    else:
                        print(f"\n找到 {len(matches)} 个匹配的武功:")
                        for i, (sid, sname) in enumerate(matches[:20]):
                            print(f"  {i}. ID {sid}: {sname}")
                        if len(matches) > 20:
                            print(f"  ... 还有 {len(matches)-20} 个")
                        idx = int(input("\n选择序号: ").strip())
                        skill_id, skill_name = matches[idx]

                lv = input(f"输入【{skill_name}】等级 [默认1]: ").strip() or '1'
                add_skill_to_hero(current_hero, skill_id, int(lv))
                print(f"✓ 已添加【{skill_name}】!")
            except Exception as e:
                print(f"✗ 输入无效! {e}")

        elif choice == '10':
            if not current_hero:
                print("✗ 请先选择角色!")
                continue
            print("\n属性索引: 0=力道 1=灵巧 2=智力 3=意志 4=体质 5=经脉")
            try:
                attr_idx = int(input("输入属性索引 [0-5]: ").strip())
                new_val = float(input("输入新值: ").strip())
                current_hero['baseAttri'][attr_idx] = new_val
                current_hero['totalAttri'][attr_idx] = new_val
                current_hero['maxAttri'][attr_idx] = new_val
                print(f"✓ {ATTR_NAMES[attr_idx]} 已改为 {new_val}")
            except:
                print("✗ 输入无效!")

        elif choice == '11':
            if not current_hero:
                print("✗ 请先选择角色!")
                continue
            print("\n武学索引: 0=内功 1=轻功 2=绝技 3=拳掌 4=剑法 5=刀法 6=长兵 7=奇门 8=射术")
            try:
                attr_idx = int(input("输入武学索引 [0-8]: ").strip())
                new_val = float(input("输入新值: ").strip())
                current_hero['baseFightSkill'][attr_idx] = new_val
                current_hero['totalFightSkill'][attr_idx] = new_val
                current_hero['maxFightSkill'][attr_idx] = new_val
                print(f"✓ {FIGHT_SKILL_NAMES[attr_idx]} 已改为 {new_val}")
            except:
                print("✗ 输入无效!")

        elif choice == '12':
            if not current_hero:
                print("✗ 请先选择角色!")
                continue
            print_hero_attributes(current_hero)

        elif choice == '13':
            if not current_hero:
                print("✗ 请先选择角色!")
                continue
            print("\n技能索引: 0=医术 1=毒术 2=学识 3=口才 4=采伐 5=木植 6=锻造 7=炼丹 8=烹饪")
            try:
                attr_idx = int(input("输入技能索引 [0-8]: ").strip())
                new_val = float(input("输入新值: ").strip())
                modify_living_skill(current_hero, attr_idx, new_val)
                print(f"✓ {LIVING_SKILL_NAMES[attr_idx]} 已改为 {new_val}")
            except:
                print("✗ 输入无效!")

        elif choice == 's':
            backup_file('Hero')
            save_data(data, 'Hero')

        elif choice == 'b':
            backup_file('Hero')

if __name__ == '__main__':
    interactive_mode()
