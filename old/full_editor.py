#!/usr/bin/env python3
"""
龙胤立志传 - 完整存档修改器
支持修改角色所有属性、武功、装备、物品等
"""

import json
import shutil
import os
from datetime import datetime

# ========== 数据加载 ==========

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

# ========== 常量定义 ==========

# 基础属性名称
ATTR_NAMES = ['力道', '灵巧', '智力', '意志', '体质', '经脉']

# 武学属性名称
FIGHT_SKILL_NAMES = ['内功', '轻功', '绝技', '拳掌', '剑法', '刀法', '长兵', '奇门', '射术']

# 技能属性名称
LIVING_SKILL_NAMES = ['医术', '毒术', '学识', '口才', '采伐', '木植', '锻造', '炼丹', '烹饪']

# 性格映射
NATURE_MAP = {
    0: '仁善', 1: '正直', 2: '刚正', 3: '忠义', 4: '稳妥', 5: '温和',
    6: '平常', 7: '狡黠', 8: '乖张', 9: '叛逆', 10: '唯我', 11: '冷酷'
}

# 门派ID映射
FORCE_MAP = {
    0: '无', 1: '少林派', 2: '武当派', 3: '峨眉派', 4: '丐帮', 5: '华山派',
    6: '衡山派', 7: '青城派', 8: '点苍派', 9: '昆仑派', 10: '崆峒派',
    11: '天山派', 12: '雪山派', 13: '点星阁', 14: '五毒教', 15: '明教',
    16: '日月神教', 17: '红花会', 18: '天地会', 19: '六扇门', 20: '锦衣卫',
    21: '东厂', 22: '西厂', 23: '大理段氏', 24: '全真教', 25: '仙霞派',
    26: '茅山派', 27: '桃花岛', 28: '逍遥派', 29: '灵鹫宫'
}

# 装备槽位
EQUIPMENT_SLOTS = {
    'weaponSaveRecord': '武器',
    'armorSaveRecord': '护甲',
    'helmetSaveRecord': '头盔',
    'shoesSaveRecord': '鞋子',
    'decorationSaveRecord': '饰品'
}

# 物品类型
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

def save_data(data, filepath='Hero'):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False)

def get_skill_name(skill_id):
    if skill_id in SKILL_NAMES:
        return SKILL_NAMES[skill_id].get('name', f'未知({skill_id})')
    return f'未知({skill_id})'

def get_spe_attr_name(attr_id):
    return SPE_ATTR_MAP.get(str(attr_id), f'属性{attr_id}')

def get_force_name(force_id):
    return FORCE_MAP.get(force_id, f'未知门派({force_id})')

def get_nature_name(nature_id):
    return NATURE_MAP.get(nature_id, f'未知({nature_id})')

# ========== 显示函数 ==========

def print_hero_summary(hero, idx=None):
    """打印角色摘要"""
    name = hero.get('heroName', '未知')
    hero_id = hero.get('heroID')
    age = hero.get('age', '?')
    force_id = hero.get('belongForceID', -1)
    force_name = get_force_name(force_id)
    is_leader = '掌门' if hero.get('isLeader') else ''
    dead = ' [死亡]' if hero.get('dead') else ''
    in_team = ' [在队]' if hero.get('inTeam') else ''

    print(f"  {idx if idx is not None else '':<4} ID:{hero_id:<4} {name:<8} {age}岁 {force_name}{is_leader}{dead}{in_team}")

def print_hero_detail(hero):
    """打印角色详细信息"""
    name = hero.get('heroName', '未知')
    hero_id = hero.get('heroID')

    print(f"\n{'='*70}")
    print(f"【{name}】完整信息 (ID:{hero_id})")
    print(f"{'='*70}")

    # 基本信息
    print(f"\n【基本信息】")
    print(f"  姓名: {name}  姓氏: {hero.get('heroFamilyName', '')}")
    print(f"  年龄: {hero.get('age')}  性别: {'女' if hero.get('isFemale') else '男'}")
    print(f"  门派: {get_force_name(hero.get('belongForceID', -1))}", end='')
    if hero.get('isLeader'):
        print(' (掌门)', end='')
    print()
    print(f"  门派职位: {hero.get('forceJobID', -1)}  门派等级: {hero.get('heroForceLv', 0)}")
    print(f"  门派贡献: {hero.get('forceContribution', 0):.1f}")
    print(f"  性格: {get_nature_name(hero.get('nature', 6))}")

    # 状态
    print(f"\n【状态】")
    print(f"  生命: {hero.get('hp', 0):.0f}/{hero.get('maxhp', 0):.0f}")
    print(f"  体力: {hero.get('power', 0):.0f}/{hero.get('maxPower', 0):.0f}")
    print(f"  内力: {hero.get('mana', 0):.0f}/{hero.get('maxMana', 0):.0f}")
    print(f"  护甲: {hero.get('armor', 0):.1f}")
    injuries = []
    if hero.get('internalInjury', 0) > 0: injuries.append(f"内伤{hero.get('internalInjury'):.0f}")
    if hero.get('externalInjury', 0) > 0: injuries.append(f"外伤{hero.get('externalInjury'):.0f}")
    if hero.get('poisonInjury', 0) > 0: injuries.append(f"中毒{hero.get('poisonInjury'):.0f}")
    if injuries:
        print(f"  伤势: {', '.join(injuries)}")
    status = []
    if hero.get('dead'): status.append('死亡')
    if hero.get('inPrison'): status.append('入狱')
    if hero.get('rest'): status.append('休息')
    if status:
        print(f"  状态: {', '.join(status)}")

    # 基础属性
    print(f"\n【基础属性】 (基础/总值/上限)")
    base_attri = hero.get('baseAttri', [0]*6)
    total_attri = hero.get('totalAttri', [0]*6)
    max_attri = hero.get('maxAttri', [0]*6)
    for i, name in enumerate(ATTR_NAMES):
        b = base_attri[i] if i < len(base_attri) else 0
        t = total_attri[i] if i < len(total_attri) else 0
        m = max_attri[i] if i < len(max_attri) else 0
        print(f"  {name}: {b:.0f} / {t:.0f} / {m:.0f}")

    # 武学属性
    print(f"\n【武学属性】 (基础/总值/上限)")
    base_fight = hero.get('baseFightSkill', [0]*9)
    total_fight = hero.get('totalFightSkill', [0]*9)
    max_fight = hero.get('maxFightSkill', [0]*9)
    for i, name in enumerate(FIGHT_SKILL_NAMES):
        b = base_fight[i] if i < len(base_fight) else 0
        t = total_fight[i] if i < len(total_fight) else 0
        m = max_fight[i] if i < len(max_fight) else 0
        print(f"  {name}: {b:.0f} / {t:.0f} / {m:.0f}")

    # 技能属性
    print(f"\n【技能属性】 (基础/总值/上限)")
    base_living = hero.get('baseLivingSkill', [0]*9)
    total_living = hero.get('totalLivingSkill', [0]*9)
    max_living = hero.get('maxLivingSkill', [0]*9)
    for i, name in enumerate(LIVING_SKILL_NAMES):
        b = base_living[i] if i < len(base_living) else 0
        t = total_living[i] if i < len(total_living) else 0
        m = max_living[i] if i < len(max_living) else 0
        print(f"  {name}: {b:.0f} / {t:.0f} / {m:.0f}")

    # 声望荣誉
    print(f"\n【声望荣誉】")
    print(f"  声望: {hero.get('fame', 0):.0f}  恶名: {hero.get('badFame', 0):.0f}")
    print(f"  战斗分: {hero.get('fightScore', 0):.0f}")

    # 关系
    print(f"\n【人际关系】")
    friends = hero.get('Friends', [])
    haters = hero.get('Haters', [])
    students = hero.get('Students', [])
    teacher = hero.get('Teacher', -1)
    print(f"  好友: {len(friends)}人  仇人: {len(haters)}人  徒弟: {len(students)}人")
    if teacher >= 0:
        print(f"  师父ID: {teacher}")

    # 武功
    skills = hero.get('kungfuSkills', [])
    print(f"\n【武功】 共{len(skills)}门")
    equipped = [s for s in skills if s.get('equiped')]
    print(f"  已装备: {len(equipped)}门")

def print_kungfu_list(hero):
    """打印武功列表"""
    skills = hero.get('kungfuSkills', [])
    print(f"\n【武功列表】共 {len(skills)} 门")
    print(f"{'序号':<4} {'ID':<5} {'名称':<12} {'类型':<6} {'等级':<4} {'装备':<4} {'特殊属性'}")
    print("-" * 75)

    for i, skill in enumerate(skills):
        skill_id = skill.get('skillID')
        lv = skill.get('lv')
        equiped = '✓' if skill.get('equiped') else ''
        skill_name = get_skill_name(skill_id)
        skill_type = SKILL_NAMES.get(skill_id, {}).get('type', '') if skill_id in SKILL_NAMES else ''

        spe_data = skill.get('speUseData', {}).get('heroSpeAddData', {})
        spe_str = ', '.join([f"{get_spe_attr_name(k)}:{v}" for k, v in list(spe_data.items())[:2]])
        if len(spe_data) > 2:
            spe_str += '...'

        print(f"{i:<4} {skill_id:<5} {skill_name:<12} {skill_type:<6} {lv:<4} {equiped:<4} {spe_str}")

def print_skill_detail(skill):
    """打印武功详情"""
    skill_id = skill.get('skillID')
    skill_name = get_skill_name(skill_id)
    skill_type = SKILL_NAMES.get(skill_id, {}).get('type', '') if skill_id in SKILL_NAMES else ''

    print(f"\n{'='*55}")
    print(f"【{skill_name}】")
    print(f"{'='*55}")
    print(f"  类型: {skill_type}  ID: {skill_id}")
    print(f"  等级: {skill.get('lv')}")
    print(f"  实战经验: {skill.get('fightExp')}  理论经验: {skill.get('bookExp')}")
    print(f"  已装备: {skill.get('equiped')}  新学: {skill.get('isNew')}")

    print(f"\n【装备加成】")
    spe_equip = skill.get('speEquipData', {}).get('heroSpeAddData', {})
    if spe_equip:
        for k, v in spe_equip.items():
            print(f"  {get_spe_attr_name(k)}: {v}")
    else:
        print("  无")

    print(f"\n【特殊属性】")
    spe_use = skill.get('speUseData', {}).get('heroSpeAddData', {})
    if spe_use:
        for k, v in spe_use.items():
            print(f"  {get_spe_attr_name(k)}: {v}")
    else:
        print("  无")

    print(f"\n【突破属性】")
    extra = skill.get('extraAddData', {}).get('heroSpeAddData', {})
    if extra:
        for k, v in extra.items():
            print(f"  {get_spe_attr_name(k)}: {v}")
    else:
        print("  无")

    print(f"\n【伤害加成】")
    print(f"  伤害: {skill.get('damageUseSpeAddValue')}")
    print(f"  自身: {skill.get('selfUseSpeAddValue')}")
    print(f"  敌方: {skill.get('enemyUseSpeAddValue')}")

def print_equipment(hero):
    """打印装备"""
    print(f"\n【装备】")
    equip = hero.get('nowEquipment', {})
    for slot, name in EQUIPMENT_SLOTS.items():
        records = equip.get(slot, [])
        if records:
            print(f"  {name}: {records}")
        else:
            print(f"  {name}: 无")

def print_items(hero):
    """打印物品"""
    print(f"\n【物品】")
    items_data = hero.get('itemListData', {})
    money = items_data.get('money', 0)
    weight = items_data.get('weight', 0)
    max_weight = items_data.get('maxWeight', 0)
    all_items = items_data.get('allItem', [])

    print(f"  金钱: {money}")
    print(f"  负重: {weight:.1f}/{max_weight:.1f}")
    print(f"  物品数量: {len(all_items)}")

    # 按类型分类
    type_items = {}
    for item in all_items:
        t = item.get('type', 0)
        if t not in type_items:
            type_items[t] = []
        type_items[t].append(item)

    for t, items in sorted(type_items.items()):
        type_name = ITEM_TYPES.get(t, f'类型{t}')
        print(f"\n  [{type_name}] {len(items)}件")
        for item in items[:5]:
            name = item.get('name', '未知')
            lv = item.get('itemLv', 0)
            rare = item.get('rareLv', 0)
            print(f"    - {name} (等级{lv}, 品质{rare})")
        if len(items) > 5:
            print(f"    ... 还有{len(items)-5}件")

def print_relations(hero, data):
    """打印关系"""
    print(f"\n【人际关系】")

    # 好友
    friends = hero.get('Friends', [])
    if friends:
        print(f"\n  好友 ({len(friends)}人):")
        for fid in friends[:10]:
            for h in data:
                if h.get('heroID') == fid:
                    print(f"    - {h.get('heroName')} (ID:{fid})")
                    break
        if len(friends) > 10:
            print(f"    ... 还有{len(friends)-10}人")

    # 仇人
    haters = hero.get('Haters', [])
    if haters:
        print(f"\n  仇人 ({len(haters)}人):")
        for fid in haters[:10]:
            for h in data:
                if h.get('heroID') == fid:
                    print(f"    - {h.get('heroName')} (ID:{fid})")
                    break

    # 徒弟
    students = hero.get('Students', [])
    if students:
        print(f"\n  徒弟 ({len(students)}人):")
        for fid in students:
            for h in data:
                if h.get('heroID') == fid:
                    print(f"    - {h.get('heroName')} (ID:{fid})")
                    break

def print_tags(hero):
    """打印角色标签"""
    print(f"\n【角色标签】")
    tags = hero.get('heroTagData', [])
    if tags:
        for tag in tags:
            tag_id = tag.get('tagID')
            left_time = tag.get('leftTime', -1)
            time_str = '永久' if left_time < 0 else f'{left_time}天'
            print(f"  标签ID:{tag_id} ({time_str})")
    else:
        print("  无")

# ========== 修改函数 ==========

def modify_base_attr(hero, idx, value):
    """修改基础属性"""
    hero['baseAttri'][idx] = float(value)
    hero['totalAttri'][idx] = float(value)
    hero['maxAttri'][idx] = float(value)

def modify_fight_skill(hero, idx, value):
    """修改武学属性"""
    hero['baseFightSkill'][idx] = float(value)
    hero['totalFightSkill'][idx] = float(value)
    hero['maxFightSkill'][idx] = float(value)

def modify_living_skill(hero, idx, value):
    """修改技能属性"""
    hero['baseLivingSkill'][idx] = float(value)
    hero['totalLivingSkill'][idx] = float(value)
    hero['maxLivingSkill'][idx] = float(value)

def modify_status(hero, hp=None, power=None, mana=None):
    """修改状态值"""
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

def modify_skill_lv(skill, lv):
    """修改武功等级"""
    skill['lv'] = int(lv)

def modify_skill_spe(skill, spe_type, attr_id, value):
    """修改武功属性"""
    if spe_type not in skill:
        skill[spe_type] = {'heroSpeAddData': {}}
    if 'heroSpeAddData' not in skill[spe_type]:
        skill[spe_type]['heroSpeAddData'] = {}
    skill[spe_type]['heroSpeAddData'][str(attr_id)] = float(value)

def add_skill(hero, skill_id, lv=1):
    """添加武功"""
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
    """所有武功满级"""
    for skill in hero.get('kungfuSkills', []):
        skill['lv'] = lv
        skill['damageUseSpeAddValue'] = float(damage)

def remove_skill(hero, idx):
    """删除武功（更新所有装备索引）"""
    skills = hero.get('kungfuSkills', [])
    if not (0 <= idx < len(skills)):
        return None

    removed = skills.pop(idx)

    # 更新所有装备记录索引
    # 如果索引 > idx，则减1
    # 如果索引 == idx，则设为-1

    # 单个索引字段
    for field in ['internalSkillSaveRecord', 'dodgeSkillSaveRecord',
                  'uniqueSkillSaveRecord']:
        if field in hero:
            val = hero[field]
            if isinstance(val, int):
                if val == idx:
                    hero[field] = -1
                elif val > idx:
                    hero[field] = val - 1

    # 数组索引字段
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

def remove_skill_by_id(hero, skill_id):
    """根据ID删除武功"""
    skills = hero.get('kungfuSkills', [])
    for i, skill in enumerate(skills):
        if skill.get('skillID') == skill_id:
            return remove_skill(hero, i)
    return None

def modify_fame(hero, fame=None, bad_fame=None):
    """修改声望"""
    if fame is not None:
        hero['fame'] = float(fame)
    if bad_fame is not None:
        hero['badFame'] = float(bad_fame)

def modify_money(hero, money):
    """修改金钱"""
    if 'itemListData' not in hero:
        hero['itemListData'] = {'money': 0, 'weight': 0, 'maxWeight': 100, 'allItem': []}
    hero['itemListData']['money'] = int(money)

def heal_hero(hero):
    """治愈角色"""
    hero['hp'] = hero.get('maxhp', 999)
    hero['power'] = hero.get('maxPower', 999)
    hero['mana'] = hero.get('maxMana', 999)
    hero['internalInjury'] = 0.0
    hero['externalInjury'] = 0.0
    hero['poisonInjury'] = 0.0

def revive_hero(hero):
    """复活角色"""
    hero['dead'] = False
    heal_hero(hero)

def max_all_attrs(hero, value=999):
    """所有属性满"""
    for i in range(6):
        modify_base_attr(hero, i, value)
    for i in range(9):
        modify_fight_skill(hero, i, value)
        modify_living_skill(hero, i, value)
    modify_status(hero, value, value, value)

# ========== 主界面 ==========

def find_hero(data, identifier):
    """查找角色"""
    for i, h in enumerate(data):
        if h.get('heroName') == identifier or str(h.get('heroID')) == str(identifier):
            return i, h
    return None, None

def search_skill(name):
    """搜索武功"""
    matches = []
    for sid, info in SKILL_NAMES.items():
        if name.lower() in info.get('name', '').lower():
            matches.append((sid, info['name'], info.get('type', '')))
    return matches

def search_attr(name):
    """搜索属性"""
    matches = []
    for aid, aname in SPE_ATTR_MAP.items():
        if name in aname:
            matches.append((aid, aname))
    return matches

def interactive_mode():
    """交互式主界面"""
    data = load_data()
    hero = None
    hero_idx = None

    while True:
        print("\n" + "="*70)
        print("龙胤立志传 - 完整存档修改器")
        print("="*70)

        if hero:
            print(f"当前角色: {hero.get('heroName')} (ID:{hero.get('heroID')})")

        print("\n【角色管理】")
        print("  1. 列出所有角色")
        print("  2. 选择角色")
        print("  3. 查看完整信息")
        print("  4. 查看武功列表")
        print("  5. 查看装备物品")
        print("  6. 查看人际关系")

        print("\n【属性修改】")
        print("  10. 修改基础属性")
        print("  11. 修改武学属性")
        print("  12. 修改技能属性")
        print("  13. 修改状态(生命/体力/内力)")
        print("  14. 修改声望/恶名")
        print("  15. 修改金钱")
        print("  16. 一键全属性满")

        print("\n【武功修改】")
        print("  20. 查看武功详情")
        print("  21. 修改武功等级")
        print("  22. 修改武功属性")
        print("  23. 添加新武功")
        print("  24. 所有武功满级")
        print("  25. 删除武功")

        print("\n【特殊功能】")
        print("  30. 治愈角色")
        print("  31. 复活角色")
        print("  32. 查看角色标签")
        print("  33. 修改角色名字")

        print("\n【存档操作】")
        print("  s. 保存存档")
        print("  b. 备份存档")
        print("  0. 退出")

        choice = input("\n请选择: ").strip().lower()

        # 角色管理
        if choice == '1':
            print(f"\n{'='*70}")
            print("角色列表 (前50个)")
            print(f"{'='*70}")
            for i, h in enumerate(data[:50]):
                print_hero_summary(h, i)
            print(f"\n共 {len(data)} 个角色")

        elif choice == '2':
            identifier = input("输入角色名字或ID: ").strip()
            idx, h = find_hero(data, identifier)
            if h:
                hero_idx, hero = idx, h
                print_hero_summary(hero)
            else:
                print("未找到角色!")

        elif choice == '3':
            if hero:
                print_hero_detail(hero)
            else:
                print("请先选择角色!")

        elif choice == '4':
            if hero:
                print_kungfu_list(hero)
            else:
                print("请先选择角色!")

        elif choice == '5':
            if hero:
                print_equipment(hero)
                print_items(hero)
            else:
                print("请先选择角色!")

        elif choice == '6':
            if hero:
                print_relations(hero, data)
            else:
                print("请先选择角色!")

        # 属性修改
        elif choice == '10':
            if not hero: print("请先选择角色!"); continue
            print("\n基础属性: 0=力道 1=灵巧 2=智力 3=意志 4=体质 5=经脉")
            try:
                idx = int(input("选择属性: "))
                val = float(input("输入新值: "))
                modify_base_attr(hero, idx, val)
                print(f"✓ {ATTR_NAMES[idx]} 已改为 {val}")
            except: print("输入无效!")

        elif choice == '11':
            if not hero: print("请先选择角色!"); continue
            print("\n武学属性: 0=内功 1=轻功 2=绝技 3=拳掌 4=剑法 5=刀法 6=长兵 7=奇门 8=射术")
            try:
                idx = int(input("选择属性: "))
                val = float(input("输入新值: "))
                modify_fight_skill(hero, idx, val)
                print(f"✓ {FIGHT_SKILL_NAMES[idx]} 已改为 {val}")
            except: print("输入无效!")

        elif choice == '12':
            if not hero: print("请先选择角色!"); continue
            print("\n技能属性: 0=医术 1=毒术 2=学识 3=口才 4=采伐 5=木植 6=锻造 7=炼丹 8=烹饪")
            try:
                idx = int(input("选择属性: "))
                val = float(input("输入新值: "))
                modify_living_skill(hero, idx, val)
                print(f"✓ {LIVING_SKILL_NAMES[idx]} 已改为 {val}")
            except: print("输入无效!")

        elif choice == '13':
            if not hero: print("请先选择角色!"); continue
            print(f"\n当前: 生命{hero.get('hp'):.0f} 体力{hero.get('power'):.0f} 内力{hero.get('mana'):.0f}")
            try:
                hp = input("生命(回车跳过): ").strip()
                power = input("体力(回车跳过): ").strip()
                mana = input("内力(回车跳过): ").strip()
                modify_status(hero,
                    float(hp) if hp else None,
                    float(power) if power else None,
                    float(mana) if mana else None)
                print("✓ 状态已更新!")
            except: print("输入无效!")

        elif choice == '14':
            if not hero: print("请先选择角色!"); continue
            print(f"\n当前: 声望{hero.get('fame'):.0f} 恶名{hero.get('badFame'):.0f}")
            try:
                fame = input("声望(回车跳过): ").strip()
                bad = input("恶名(回车跳过): ").strip()
                modify_fame(hero,
                    float(fame) if fame else None,
                    float(bad) if bad else None)
                print("✓ 声望已更新!")
            except: print("输入无效!")

        elif choice == '15':
            if not hero: print("请先选择角色!"); continue
            print(f"\n当前金钱: {hero.get('itemListData', {}).get('money', 0)}")
            try:
                money = input("输入金钱: ").strip()
                modify_money(hero, int(money))
                print("✓ 金钱已更新!")
            except: print("输入无效!")

        elif choice == '16':
            if not hero: print("请先选择角色!"); continue
            val = input("属性值(默认999): ").strip() or '999'
            max_all_attrs(hero, float(val))
            print(f"✓ 所有属性已设为 {val}!")

        # 武功修改
        elif choice == '20':
            if not hero: print("请先选择角色!"); continue
            try:
                idx = int(input("武功序号: "))
                print_skill_detail(hero['kungfuSkills'][idx])
            except: print("输入无效!")

        elif choice == '21':
            if not hero: print("请先选择角色!"); continue
            try:
                idx = int(input("武功序号: "))
                lv = int(input("新等级(1-10): "))
                skill = hero['kungfuSkills'][idx]
                modify_skill_lv(skill, lv)
                print(f"✓ {get_skill_name(skill['skillID'])} 等级已改为 {lv}")
            except: print("输入无效!")

        elif choice == '22':
            if not hero: print("请先选择角色!"); continue
            try:
                idx = int(input("武功序号: "))
                skill = hero['kungfuSkills'][idx]
                print("\n属性类型: 1=装备加成 2=特殊属性 3=突破属性")
                t = input("选择: ").strip()
                types = {'1': 'speEquipData', '2': 'speUseData', '3': 'extraAddData'}
                spe_type = types.get(t)

                search = input("属性名称或ID: ").strip()
                if search.isdigit():
                    attr_id = search
                else:
                    matches = search_attr(search)
                    if not matches:
                        print("未找到属性!"); continue
                    for i, (aid, aname) in enumerate(matches[:10]):
                        print(f"  {i}. {aid}: {aname}")
                    sel = int(input("选择: "))
                    attr_id = matches[sel][0]

                val = float(input("属性值: "))
                modify_skill_spe(skill, spe_type, attr_id, val)
                print("✓ 已修改!")
            except Exception as e:
                print(f"错误: {e}")

        elif choice == '23':
            if not hero: print("请先选择角色!"); continue
            try:
                search = input("武功名称或ID: ").strip()
                if search.isdigit():
                    skill_id = int(search)
                else:
                    matches = search_skill(search)
                    if not matches:
                        print("未找到武功!"); continue
                    for i, (sid, sname, stype) in enumerate(matches[:10]):
                        print(f"  {i}. {sid}: {sname} ({stype})")
                    sel = int(input("选择: "))
                    skill_id = matches[sel][0]

                lv = int(input("等级(默认1): ") or '1')
                add_skill(hero, skill_id, lv)
                print(f"✓ 已添加 {get_skill_name(skill_id)}!")
            except Exception as e:
                print(f"错误: {e}")

        elif choice == '24':
            if not hero: print("请先选择角色!"); continue
            if input("确认所有武功满级? (y/n): ").lower() == 'y':
                all_skills_max(hero)
                print("✓ 所有武功已满级!")

        elif choice == '25':
            if not hero: print("请先选择角色!"); continue
            print_kungfu_list(hero)
            print()
            try:
                method = input("删除方式 (1=按序号 2=按武功名): ").strip()
                if method == '1':
                    idx = int(input("输入要删除的武功序号: "))
                    removed = remove_skill(hero, idx)
                    if removed:
                        print(f"✓ 已删除 {get_skill_name(removed['skillID'])}!")
                    else:
                        print("✗ 序号无效!")
                elif method == '2':
                    search = input("输入武功名称或ID: ").strip()
                    if search.isdigit():
                        skill_id = int(search)
                    else:
                        matches = search_skill(search)
                        if not matches:
                            print("未找到武功!"); continue
                        for i, (sid, sname, stype) in enumerate(matches[:10]):
                            print(f"  {i}. {sid}: {sname} ({stype})")
                        sel = int(input("选择: "))
                        skill_id = matches[sel][0]

                    # 查找并显示所有匹配的武功
                    skills = hero.get('kungfuSkills', [])
                    found = [(i, s) for i, s in enumerate(skills) if s.get('skillID') == skill_id]
                    if not found:
                        print("该角色未学此武功!")
                    elif len(found) == 1:
                        removed = remove_skill_by_id(hero, skill_id)
                        print(f"✓ 已删除 {get_skill_name(skill_id)}!")
                    else:
                        print(f"该武功学了{len(found)}次，删除第几个?")
                        for i, (idx, s) in enumerate(found):
                            print(f"  {i+1}. 序号{idx}, 等级{s.get('lv')}")
                        sel = int(input("选择: ")) - 1
                        if 0 <= sel < len(found):
                            remove_skill(hero, found[sel][0])
                            print(f"✓ 已删除!")
            except Exception as e:
                print(f"错误: {e}")

        # 特殊功能
        elif choice == '30':
            if not hero: print("请先选择角色!"); continue
            heal_hero(hero)
            print("✓ 角色已治愈!")

        elif choice == '31':
            if not hero: print("请先选择角色!"); continue
            revive_hero(hero)
            print("✓ 角色已复活!")

        elif choice == '32':
            if not hero: print("请先选择角色!"); continue
            print_tags(hero)

        elif choice == '33':
            if not hero: print("请先选择角色!"); continue
            new_name = input(f"新名字(当前:{hero.get('heroName')}): ").strip()
            if new_name:
                hero['heroName'] = new_name
                print("✓ 名字已修改!")

        # 存档操作
        elif choice == 's':
            backup_file('Hero')
            save_data(data, 'Hero')
            print("✓ 存档已保存!")

        elif choice == 'b':
            path = backup_file('Hero')
            print(f"✓ 已备份到: {path}")

        elif choice == '0':
            print("再见!")
            break

if __name__ == '__main__':
    interactive_mode()
