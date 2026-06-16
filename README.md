# 龙胤立志传存档修改器

用于修改游戏《龙胤立志传》存档的工具，提供 Web 图形界面和 REST API。

## 功能特性

- 角色属性编辑：基础属性、武学属性、技能属性
- 武功管理：查看、添加、删除、修改武功等级
- 装备物品：查看装备和背包物品
- 人际关系：好友、仇人、徒弟列表
- 批量操作：一键全属性满、全武功满级、治愈、复活
- 武功百科：查阅所有武功详细信息

## 快速开始

### Web 服务器

```bash
python3 web_server.py
```

访问 http://localhost:5000 打开 Web 界面。

### API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/heroes` | GET | 获取所有角色列表 |
| `/api/hero/<id>` | GET | 获取角色详情 |
| `/api/hero/<id>` | POST | 修改角色属性 |
| `/api/hero/<id>/skill` | POST | 添加武功 |
| `/api/hero/<id>/skill/<idx>` | DELETE | 删除武功 |
| `/api/hero/<id>/heal` | POST | 治愈角色 |
| `/api/hero/<id>/revive` | POST | 复活角色 |
| `/api/batch` | POST | 批量操作 |

## 项目结构

```
longying/
├── web_server.py           # Web 后端服务器 (Flask)
├── web/
│   ├── index.html          # 主界面 (角色编辑器)
│   ├── kungfu_wiki.html    # 武功百科
│   └── world.html          # 世界信息
├── skill_names.json        # 武功ID-名称映射
├── spe_attr_map.json       # 属性ID-名称映射
├── tag_names.json          # 标签ID-名称映射
├── talent_names.json       # 天赋ID-名称映射
├── kungfu_data.json        # 武功详细数据
├── PROJECT_DOC.md          # 项目技术文档
└── SAVE_DOC.md             # 存档格式文档
```

## 数据文件

| 文件 | 说明 |
|------|------|
| `skill_names.json` | 1051种武功的ID到名称映射 |
| `spe_attr_map.json` | 215种属性的ID到名称映射 |
| `tag_names.json` | 角色标签映射 |
| `talent_names.json` | 天赋名称映射 |
| `kungfu_data.json` | 武功详细信息（类型、效果等） |

## 属性对照表

### 基础属性
| 索引 | 名称 |
|------|------|
| 0 | 力道 |
| 1 | 灵巧 |
| 2 | 智力 |
| 3 | 意志 |
| 4 | 体质 |
| 5 | 经脉 |

### 武学属性
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

### 技能属性
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

## 注意事项

1. 修改前备份存档
2. 属性值建议不超过999
3. 存档文件使用UTF-8编码

## 许可证

MIT License
