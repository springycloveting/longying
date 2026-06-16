# Handoff Document: Web编辑工具测试员

**会话ID**: e64a448a-d627-4b1e-8700-0d995ada45da  
**角色**: 测试员 (longying-tester)  
**房间**: longying (ce018947-b623-4468-ae02-b92132acc8e2)  
**日期**: 2026-06-15

---

## 项目概述

龙胤立志传存档修改器 - Web版

**项目路径**: `/home/v6/work/longying`

**技术栈**:
- 后端: Python Flask (web_server.py, 2120行)
- 前端: HTML/CSS/JS (web/index.html, 2300+行)
- 数据: JSON格式存档 (Hero, Save文件)

---

## 已完成工作

### 代码分析

对现有Web编辑工具进行了全面分析，包括：

1. **web_server.py 分析** (2120行)
   - Hero存档API (~1500行)
   - Save存档API (~700行)
   - 已实现50+个API端点

2. **web/index.html 分析** (2300+行)
   - 8个功能标签页
   - 现代化玻璃态UI设计
   - 完整的前端交互逻辑

3. **存档文件结构分析**
   - Hero文件: 角色数据数组
   - Save文件: 世界状态数据

### 关键发现

#### NPC好感度存储机制
```
位置: 每个Hero对象的favor字段
- 主角(heroID=0): favor=-999999 (特殊值)
- NPC: favor值表示对主角的好感度
- 示例: 姜映泉favor=100 → 对主角好感100
```

**当前状态**: 无API支持查看/修改favor字段

#### 物品管理现状
```
已有API:
- GET /api/hero/<id>/items - 物品列表
- GET /api/hero/<id>/item/<idx> - 物品详情
- PUT /api/hero/<id>/item/<idx> - 修改属性

缺失API:
- POST /api/hero/<id>/item - 新增物品
- DELETE /api/hero/<id>/item/<idx> - 删除物品
```

---

## 数据结构参考

### Hero关键字段
```json
{
  "heroID": 0,
  "heroName": "杨春",
  "favor": -999999.0,
  "Friends": [7, 4, 134],
  "Haters": [107, 106],
  "Lover": -1,
  "itemListData": {
    "money": 97760875,
    "weight": 610.5,
    "maxWeight": 623.0,
    "allItem": [...]
  },
  "nowEquipment": {
    "weaponSaveRecord": [],
    "armorSaveRecord": [],
    "helmetSaveRecord": [],
    "shoesSaveRecord": [],
    "decorationSaveRecord": []
  },
  "heroTagData": [
    {"tagID": 1, "leftTime": -1.0, "sourceHero": null}
  ],
  "baseAttri": [100, 100, 100, 100, 100, 100],
  "kungfuSkills": [...]
}
```

### 物品数据结构
```json
{
  "itemID": 1001,
  "type": 0,
  "name": "木剑",
  "itemLv": 1,
  "rareLv": 1,
  "weight": 1.0,
  "value": 100,
  "equipmentData": {
    "baseAddData": {
      "heroSpeAddData": {"1": 10.0, "2": 5.0}
    },
    "extraAddData": {
      "heroSpeAddData": {"3": 2.0}
    }
  }
}
```

### Save关键字段
```json
{
  "chapter": 1,
  "worldTime": {"year": 1, "month": 1, "day": 1},
  "Areas": [...],
  "Forces": [...],
  "ResourcePoints": [...],
  "governStorage": {...}
}
```

---

## 待实现功能

### 优先级高

#### 1. NPC好感度管理
**后端API**:
```
GET /api/hero/<id>/favor - 获取好感度
PUT /api/hero/<id>/favor - 修改好感度
GET /api/favors - 获取所有NPC对主角的好感度列表
```

**前端界面**:
- 新增"好感度"标签页
- 显示所有NPC好感度列表
- 支持筛选、排序
- 提供快捷修改按钮

**测试要点**:
- favor字段值范围 (-999999 到 999)
- 修改后存档保存验证
- 游戏内好感度显示验证

#### 2. 物品完整CRUD
**后端API**:
```
POST /api/hero/<id>/item - 新增物品
DELETE /api/hero/<id>/item/<idx> - 删除物品
PUT /api/hero/<id>/item/<idx>/move - 移动物品位置
```

**前端界面**:
- 物品添加模态框
- 物品删除确认
- 物品搜索筛选

**测试要点**:
- 新增物品后weight计算
- 删除物品后装备索引更新
- 负重上限验证

### 优先级中

#### 3. 存档属性深度解析
需分析的未知字段:
- `heroAIData`: AI行为数据
- `faceData`: 角色外貌数据
- `skinColorDark`, `skinID`, `skinLv`: 外观系统
- `manageAiHour`, `dailyAIManaged`: 日常管理
- Save中的`areaSpeAddData`: 区域特殊加成

#### 4. 物品位置调整
- 拖拽排序功能
- 索引直接修改

### 优先级低

#### 5. UI优化
- 物品搜索筛选增强
- 好感度可视化图表
- 批量修改功能

---

## 测试环境

### 存档文件位置
```
/home/v6/work/longying/LongYinLiZhiZhuan_Data/Save/
├── SaveSlot0/
│   ├── Hero
│   └── Save
├── SaveSlot1/
│   ├── Hero
│   └── Save
├── SaveSlot2/
│   ├── Hero
│   └── Save
└── SaveSlot10/
    ├── Hero
    └── Save
```

### 配置文件
```
/home/v6/work/longying/
├── skill_names.json - 武功名称映射
├── spe_attr_map.json - 特殊属性映射
├── talent_names.json - 天赋资质映射
└── tag_names.json - 天赋标签映射
```

### 运行测试
```bash
cd /home/v6/work/longying
python web_server.py
# 访问 http://localhost:5000
```

---

## 房间通信

**Session Gateway API**: http://127.0.0.1:8787/api/rooms/ce018947-b623-4468-ae02-b92132acc8e2/messages

**认证**: Bearer WeiLiu@7766

**发送消息示例**:
```bash
curl -X POST 'http://127.0.0.1:8787/api/rooms/ce018947-b623-4468-ae02-b92132acc8e2/messages' \
  -H 'Authorization: Bearer WeiLiu@7766' \
  -H 'Content-Type: application/json' \
  -d '{
    "fromSessionId": "e64a448a-d627-4b1e-8700-0d995ada45da",
    "text": "[DONE] 任务完成报告...",
    "target": {"mode": "room"},
    "metadata": {"source": "agent-result", "parentMessageId": "..."}
  }'
```

---

## 建议技能

1. **tdd** - 如果开发新功能，使用TDD方式开发，确保测试覆盖
2. **diagnose** - 如果发现bug，使用diagnose技能进行系统化调试
3. **codegraph_context** - 快速理解代码结构，避免重复读取文件

---

## 团队协作

- **@longying-planner**: 规划师，负责分析代码、制定实现计划
- **@longying-coder**: 开发者，负责实现后端API和前端界面
- **@longying-tester**: 测试员，负责功能测试和验证

---

## 后续步骤

1. 等待 @longying-coder 实现NPC好感度管理API
2. 测试好感度功能，验证:
   - API返回正确数据
   - 修改后存档保存成功
   - 游戏内好感度显示正确
3. 测试物品CRUD功能（待实现）
4. 进行端到端测试，验证实际游戏效果

---

## 注意事项

1. **存档备份**: 测试前务必备份存档
2. **索引更新**: 删除物品时需注意装备索引的更新
3. **值范围**: favor字段有特殊值(-999999)，修改时需注意
4. **游戏验证**: 存档修改后需在游戏中验证实际效果
