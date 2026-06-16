# 龙胤立志传 Web 编辑器 - 开发交接文档

**生成时间**: 2025-06-15
**会话主题**: NPC 好感度调整与物品管理功能开发

---

## 项目概述

龙胤立志传存档修改器，基于 Flask 后端 + HTML/CSS/JS 前端的 Web 应用。用于修改游戏存档中的角色属性、武功、物品等数据。

**技术栈**:
- 后端: Python Flask (`web_server.py`)
- 前端: 单页 HTML (`web/index.html`)
- 测试: Python unittest (`test_api.py`)

---

## 已完成功能

### 1. NPC 好感度系统

**数据结构**:
- `hero['favor']` - 角色 ID 对玩家好感度
- `-999999` = 未知状态（未互动）
- `-100 到 100` = 正常好感度范围

**好感度状态分级**:
| 范围 | 状态 | 颜色 |
|------|------|------|
| >= 80 | 挚爱 | #ff1493 |
| 60-79 | 亲密 | #ff69b4 |
| 40-59 | 友善 | #4caf50 |
| 20-39 | 略有好感 | #8bc34a |
| 0-19 | 中立 | #9e9e9e |
| -20 到 -1 | 略有不悦 | #ff9800 |
| -40 到 -21 | 厌恶 | #ff5722 |
| -60 到 -41 | 憎恨 | #f44336 |
| -80 到 -61 | 仇敌 | #c62828 |
| < -80 | 死敌 | #8b0000 |

**API 端点**:
- `GET /api/hero/<hero_id>/favor` - 获取好感度
- `PUT /api/hero/<hero_id>/favor` - 设置好感度
- `GET /api/heroes/favor` - 获取所有角色好感度
- `POST /api/heroes/favor/batch` - 批量设置好感度

**后端函数** (`web_server.py`):
```python
modify_favor(hero, value)  # 修改好感度，自动限制范围
add_friend(hero, friend_id)
remove_friend(hero, friend_id)
add_hater(hero, hater_id)
set_lover(hero, lover_id)
```

### 2. 物品管理系统

**API 端点**:
- `POST /api/hero/<hero_id>/item` - 添加物品
- `DELETE /api/hero/<hero_id>/item/<idx>` - 删除物品
- `POST /api/hero/<hero_id>/items/batch` - 批量操作
- `GET /api/items/types` - 物品类型列表

**后端函数** (`web_server.py`):
```python
add_item(hero, item)      # 添加物品并更新负重
remove_item(hero, idx)    # 删除物品并更新负重
modify_item(hero, idx, field, value)  # 修改物品属性
```

**批量操作支持**:
- `remove_all_type` - 按类型删除物品
- `remove_duplicates` - 删除重复物品

### 3. 前端界面更新

**人际关系 Tab** (`loadRelationsTab()`):
- 显示当前好感度状态（颜色编码）
- 手动输入好感值修改
- 快捷按钮：重置/满好感/满厌恶
- 所有角色好感度列表（可筛选）
- 批量设置好感度弹窗

**物品管理增强**:
- 物品详情弹窗添加删除按钮
- 批量操作：按类型删除、删除重复

---

## 测试

**测试文件**: `test_api.py`
**测试数量**: 38 个

运行测试:
```bash
python3 test_api.py
```

测试覆盖:
- `TestHeroFavorAPI` - 好感度 API 测试
- `TestHeroFavorFunctions` - 好感度函数测试
- `TestFavorStatusClassification` - 好感度状态分类测试
- `TestHeroItemAPI` - 物品 API 测试
- `TestItemWeightManagement` - 物品负重管理测试
- `TestHeroRelationsAPI` - 人际关系 API 测试

---

## 项目文件结构

```
/home/v6/work/longying/
├── web_server.py          # Flask 后端 (已修改)
├── test_api.py            # 单元测试 (新增)
├── web/
│   └── index.html         # 前端界面 (已修改)
├── Hero                   # 角色存档文件
├── Save                   # 世界存档文件
├── skill_names.json       # 武功名称映射
├── spe_attr_map.json      # 属性名称映射
├── tag_names.json         # 天赋标签映射
├── PROJECT_DOC.md         # 项目文档
└── SAVE_DOC.md            # 存档结构文档
```

---

## 关键数据结构

### Hero 存档关键字段

```python
hero = {
    'heroID': int,           # 角色唯一ID
    'heroName': str,         # 角色名称
    'favor': float,          # 对玩家好感度 (-999999=未知)
    'Friends': [int],        # 好友ID列表
    'Haters': [int],         # 仇人ID列表
    'Lover': int,            # 恋人ID (-1=无)
    'itemListData': {
        'money': int,
        'weight': float,
        'maxWeight': float,
        'allItem': [...]     # 物品列表
    }
}
```

### 物品类型映射

```python
ITEM_TYPES = {
    0: '武器', 1: '护甲', 2: '头盔', 3: '鞋子', 4: '饰品',
    5: '药品', 6: '坐骑', 7: '秘籍', 8: '材料', 9: '宝物', 10: '杂项'
}
```

---

## 后续开发建议

### 可选增强功能

1. **好感度关系管理**
   - 添加/移除好友、仇人的 UI 操作
   - 设置恋人功能

2. **物品创建**
   - 添加物品的完整 UI（目前只有 API）

3. **数据持久化**
   - 添加修改历史记录
   - 支持撤销操作

### 建议的 Skills

- `tdd` - 继续使用 TDD 流程开发新功能
- `code-review` - 代码审查
- `simplify` - 代码简化优化
- `verify` - 启动服务器验证功能

---

## 启动服务器

```bash
cd /home/v6/work/longying
python3 web_server.py
```

服务器地址: `http://localhost:5000`

---

## 注意事项

1. 所有修改遵循 TDD 流程（先写测试，再写实现）
2. 好感度值会自动限制在有效范围内
3. 删除物品会自动更新负重
4. 前端使用内联 JavaScript，无外部依赖
5. 存档保存前会自动备份
