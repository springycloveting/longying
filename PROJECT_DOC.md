# 龙胤立志传存档修改器 - 项目文档

## 项目概述

本项目是一个用于修改游戏《龙胤立志传》存档的工具，支持 WEB 图形界面和 CLI 命令行两种模式。

## 文件结构

```
Y:\longying\
├── Hero                      # 主存档文件 (JSON格式，角色数据)
├── Save                      # 世界存档文件
├── TempHero                  # 临时角色存档
├── Info                      # 存档信息
│
├── skill_names.json          # 武功ID→名称映射 (1051种武功)
├── spe_attr_map.json         # 特殊属性ID→名称映射 (215种属性)
│
├── save_editor_gui.py        # GUI图形界面版 (PyQt6)
├── full_editor.py            # CLI完整修改器
├── kungfu_editor.py          # CLI武功专用修改器
├── save_parser.py            # 基础解析工具
│
├── run.sh / run.bat          # 启动脚本
├── run_direct.bat            # Windows直接运行脚本
├── build_exe.sh / build_exe.bat  # 打包脚本
│
└── README.md                 # 使用说明
```

## 数据文件格式

### skill_names.json - 武功映射

```json
{
  "1": {"name": "太祖长拳", "type": "拳掌"},
  "2": {"name": "罗汉拳", "type": "拳掌"},
  "100": {"name": "追魂夺命剑", "type": "剑法"},
  ...
}
```

**字段说明:**
- Key: 武功ID (字符串)
- `name`: 武功中文名称
- `type`: 武功类型 (拳掌/剑法/刀法/内功/轻功/绝技/长兵/奇门/射术)

### spe_attr_map.json - 特殊属性映射

```json
{
  "0": "力道",
  "1": "灵巧",
  "2": "智力",
  "57": "生命上限",
  "60": "伤害",
  "66": "暴击",
  ...
}
```

**字段说明:**
- Key: 属性ID (字符串)
- Value: 属性中文名称

## Hero 存档文件结构

### 角色基础信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `heroName` | string | 角色姓名 |
| `heroID` | int | 角色唯一ID |
| `heroFamilyName` | string | 姓氏 |
| `age` | int | 年龄 |
| `isFemale` | bool | 是否女性 |
| `dead` | bool | 是否死亡 |
| `inTeam` | bool | 是否在队伍中 |
| `nature` | int | 性格ID (见性格映射表) |
| `belongForceID` | int | 所属门派ID (见门派映射表) |
| `isLeader` | bool | 是否掌门 |

### 状态属性

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `hp` | float | 当前生命 |
| `maxhp` | float | 最大生命 |
| `realMaxHp` | float | 真实最大生命 |
| `power` | float | 当前体力 |
| `maxPower` | float | 最大体力 |
| `realMaxPower` | float | 真实最大体力 |
| `mana` | float | 当前内力 |
| `maxMana` | float | 最大内力 |
| `realMaxMana` | float | 真实最大内力 |
| `armor` | float | 护甲值 |
| `internalInjury` | float | 内伤程度 |
| `externalInjury` | float | 外伤程度 |
| `poisonInjury` | float | 中毒程度 |
| `inPrison` | bool | 是否入狱 |
| `rest` | bool | 是否休息中 |

### 基础属性 (数组索引 0-5)

```python
hero['baseAttri'] = [力道, 灵巧, 智力, 意志, 体质, 经脉]
hero['totalAttri'] = [...]  # 总值(含加成)
hero['maxAttri'] = [...]    # 上限值
```

| 索引 | 名称 |
|------|------|
| 0 | 力道 |
| 1 | 灵巧 |
| 2 | 智力 |
| 3 | 意志 |
| 4 | 体质 |
| 5 | 经脉 |

### 武学属性 (数组索引 0-8)

```python
hero['baseFightSkill'] = [内功, 轻功, 绝技, 拳掌, 剑法, 刀法, 长兵, 奇门, 射术]
hero['totalFightSkill'] = [...]  # 总值
hero['maxFightSkill'] = [...]    # 上限值
```

| 索引 | 名称 |
|------|------|
| 0 | 内功 |
| 1 | 轻功 |
| 2 | 绝技 |
| 3 | 拳掌 |
| 4 | 剑法 |
| 5 | 刀法 |
| 6 | 长兵 |
| 7 | 奇门 |
| 8 | 射术 |

### 技能属性 (数组索引 0-8)

```python
hero['baseLivingSkill'] = [医术, 毒术, 学识, 口才, 采伐, 木植, 锻造, 炼丹, 烹饪]
hero['totalLivingSkill'] = [...]  # 总值
hero['maxLivingSkill'] = [...]    # 上限值
```

| 索引 | 名称 |
|------|------|
| 0 | 医术 |
| 1 | 毒术 |
| 2 | 学识 |
| 3 | 口才 |
| 4 | 采伐 |
| 5 | 木植 |
| 6 | 锻造 |
| 7 | 炼丹 |
| 8 | 烹饪 |

### 声望金钱

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `fame` | float | 声望值 |
| `badFame` | float | 恶名值 |
| `fightScore` | float | 战斗分 |
| `itemListData.money` | int | 金钱 |

### 武功数据

```python
hero['kungfuSkills'] = [
    {
        'skillID': 100,           # 武功ID
        'lv': 10,                 # 等级 (1-10)
        'fightExp': 0.0,          # 实战经验
        'bookExp': 0.0,           # 理论经验
        'equiped': True,          # 是否已装备
        'isNew': False,           # 是否新学
        'belongHeroID': 0,        # 所属角色ID
        'speEquipData': {         # 装备加成
            'heroSpeAddData': {'66': 0.1}  # 暴击+10%
        },
        'speUseData': {           # 特殊属性
            'heroSpeAddData': {}
        },
        'extraAddData': {         # 突破属性
            'heroSpeAddData': {}
        },
        'damageUseSpeAddValue': 0.0,   # 伤害加成
        'selfUseSpeAddValue': 0.0,     # 自身加成
        'enemyUseSpeAddValue': 0.0,    # 敌方加成
        'maxManaChanged': False
    },
    ...
]
```

### 装备索引 (重要！)

删除武功时必须更新这些索引：

```python
hero['internalSkillSaveRecord']    # 内功索引 (int)
hero['dodgeSkillSaveRecord']       # 轻功索引 (int)
hero['uniqueSkillSaveRecord']      # 绝技索引 (int)
hero['attackSkillSaveRecord']      # 攻击武功索引 (list[int])
```

**删除武功时的索引更新规则:**
- 被删索引 == 当前索引 → 设为 -1
- 被删索引 < 当前索引 → 索引值减 1

### 人际关系

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `Friends` | list[int] | 好友角色ID列表 |
| `Haters` | list[int] | 仇人角色ID列表 |
| `Students` | list[int] | 徒弟角色ID列表 |
| `Teacher` | int | 师父角色ID |

### 物品数据

```python
hero['itemListData'] = {
    'money': 10000,           # 金钱
    'weight': 50.0,           # 当前负重
    'maxWeight': 150.0,       # 最大负重
    'allItem': [              # 所有物品
        {
            'name': '玄铁重剑',
            'type': 0,        # 物品类型
            'itemLv': 5,      # 物品等级
            'rareLv': 3       # 品质等级
        },
        ...
    ]
}
```

**物品类型:**
| type | 类型 |
|------|------|
| 0 | 武器 |
| 1 | 护甲 |
| 2 | 头盔 |
| 3 | 鞋子 |
| 4 | 饰品 |
| 5 | 药品 |
| 6 | 坐骑 |
| 7 | 秘籍 |
| 8 | 材料 |
| 9 | 宝物 |
| 10 | 杂项 |

## 映射表

### 门派映射 (FORCE_MAP)

| ID | 门派 | ID | 门派 |
|----|------|-----|------|
| 0 | 无 | 15 | 明教 |
| 1 | 少林派 | 16 | 日月神教 |
| 2 | 武当派 | 17 | 红花会 |
| 3 | 峨眉派 | 18 | 天地会 |
| 4 | 丐帮 | 19 | 六扇门 |
| 5 | 华山派 | 20 | 锦衣卫 |
| 6 | 衡山派 | 21 | 东厂 |
| 7 | 青城派 | 22 | 西厂 |
| 8 | 点苍派 | 23 | 大理段氏 |
| 9 | 昆仑派 | 24 | 全真教 |
| 10 | 崆峒派 | 25 | 仙霞派 |
| 11 | 天山派 | 26 | 茅山派 |
| 12 | 雪山派 | 27 | 桃花岛 |
| 13 | 点星阁 | 28 | 逍遥派 |
| 14 | 五毒教 | 29 | 灵鹫宫 |

### 性格映射 (NATURE_MAP)

| ID | 性格 | ID | 性格 |
|----|------|-----|------|
| 0 | 仁善 | 6 | 平常 |
| 1 | 正直 | 7 | 狡黠 |
| 2 | 刚正 | 8 | 乖张 |
| 3 | 忠义 | 9 | 叛逆 |
| 4 | 稳妥 | 10 | 唯我 |
| 5 | 温和 | 11 | 冷酷 |

### 常用特殊属性ID

| ID | 名称 | ID | 名称 |
|----|------|-----|------|
| 0-5 | 基础属性 | 60 | 伤害 |
| 6-14 | 武学属性 | 61 | 护甲 |
| 57 | 生命上限 | 63 | 速度 |
| 58 | 体力上限 | 64 | 命中 |
| 59 | 内力上限 | 65 | 闪避 |
| 66 | 暴击 | 70 | 连击 |
| 67 | 卸力 | 71 | 招架 |
| 68 | 反击 | 72 | 破甲 |
| 69 | 压制 | 73 | 穿透 |

## 关键代码说明

### 删除武功函数 (重要！)

```python
def remove_skill(hero, idx):
    """删除武功并更新装备索引"""
    skills = hero.get('kungfuSkills', [])
    if not (0 <= idx < len(skills)):
        return None

    removed = skills.pop(idx)

    # 更新单个索引字段
    for field in ['internalSkillSaveRecord', 'dodgeSkillSaveRecord', 'uniqueSkillSaveRecord']:
        if field in hero:
            val = hero[field]
            if isinstance(val, int):
                if val == idx:
                    hero[field] = -1
                elif val > idx:
                    hero[field] = val - 1

    # 更新数组索引字段
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
```

### 修改属性函数

```python
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
```



## 注意事项

1. **删除武功必须更新索引** - 否则会导致装备错乱
2. **保存前先备份** - 程序会自动创建带时间戳的备份
3. **属性值不要过大** - 建议不超过999，否则可能游戏异常
4. **JSON编码UTF-8** - 存档文件使用UTF-8编码
5. **浮点数处理** - 存档中数值多为float类型

## 

## 数据来源

武功名称和特殊属性ID从 Unity 游戏资源提取：

```
LongYinLiZhiZhuan_Data/
├── streamingassets/
│   └── configdata/
│       ├── kungfudata.bytes      # 武功配置 (CSV格式)
│       └── speadddatabase.bytes  # 特殊属性配置 (CSV格式)
```

提取脚本参考 `full_editor.py` 中的相关代码。
