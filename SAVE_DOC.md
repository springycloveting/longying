# 龙胤立志传存档修改器 - Save 文件字段解析

## 文件概述

Save 文件是世界存档，包含地图、门派、资源点、时间、剧情等世界状态数据。

## 顶级字段结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `chapter` | int | 当前章节 |
| `cityAreaID` | list[int] | 城市区域ID列表 |
| `villageAreaID` | list[int] | 村庄区域ID列表 |
| `forceAreaID` | list[int] | 门派区域ID列表 |
| `Areas` | list[dict] | 地区列表 (69个) |
| `Inns` | list[dict] | 客栈列表 (10个) |
| `ResourcePoints` | list[dict] | 资源点列表 (120个) |
| `Forces` | list[dict] | 门派列表 (30个) |
| `BigMapRandomEventDatas` | list[dict] | 大地图随机事件 |
| `AreaMapRandomEventDatas` | list[dict] | 区域地图随机事件 |
| `WorldEventDatasSaveRecord` | list[int] | 世界事件记录 |
| `WorldNewsDatas` | list[dict] | 世界新闻列表 |
| `MailDatas` | list[dict] | 邮件列表 |
| `worldTime` | dict | 世界时间 |
| `prisonData` | dict | 监狱数据 |
| `governStorage` | dict | 官府仓库 |
| `weaponResearchData` | dict | 武器研究数据 |
| `meditationData` | dict | 冥想数据 |
| `forceSpeResearchData` | dict | 门派特殊研究 |
| `speBookStorage` | dict | 特殊书籍仓库 |
| `plotHappened` | dict | 已发生剧情 |
| `missionFinished` | list[int] | 已完成任务 |
| `tutorialFinished` | list[str] | 已完成教程 |

## Areas 地区结构

### 地区基础信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `areaID` | int | 地区ID |
| `areaName` | string | 地区名称 |
| `areaStartLv` | int | 地区起始等级 |
| `spriteName` | string | 精灵名称 |
| `backgroundType` | string | 背景类型 |
| `backgroundSkinID` | int | 背景皮肤ID |
| `xScale` | float | X轴缩放 |
| `bigMapPos` | dict | 大地图位置 `{x, y}` |
| `areaType` | int | 地区类型 (0=城市, 1=村庄, 2=门派) |
| `mapWidth` | int | 地图宽度 |
| `mapHeight` | int | 地图高度 |
| `areaDetailDirty` | bool | 区域详情脏标记 |
| `areaInfoDirty` | bool | 区域信息脏标记 |

### 地区状态属性

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `maxPeople` | float | 最大人口 |
| `people` | float | 当前人口 |
| `safe` | float | 安全值 |
| `support` | float | 支持度 |
| `defence` | float | 防御值 |
| `belongForceID` | int | 所属门派ID |
| `insideHeros` | list[int] | 区域内角色ID列表 |
| `branchLeaderID` | int | 分支负责人ID |

### 资源相关

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `changeAreaState` | list[float] | 区域状态变化 `[繁荣, 治安, 民心, 人口]` |
| `changeAllAreaState` | list[float] | 全区域状态变化 |
| `changeResource` | list[float] | 资源变化 `[粮食, 木材, 石材, 铁矿, 布匹, 药材]` |
| `resourceValueRateBase` | list[float] | 资源产出率基础 |
| `resourceValueRateTemp` | list[float] | 资源产出率临时加成 |
| `connectAreaID` | list[int] | 连接区域ID |
| `nearAreaID` | list[int] | 相邻区域ID |
| `connectResourcePointID` | list[int] | 连接资源点ID |

### 资源类型索引

| 索引 | 名称 |
|------|------|
| 0 | 粮食 |
| 1 | 木材 |
| 2 | 石材 |
| 3 | 铁矿 |
| 4 | 布匹 |
| 5 | 药材 |

### 区域建筑与设施

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `areaTiles` | list[dict] | 地块数据 (15x15=225个) |
| `roadTiles` | list[int] | 道路地块索引 |
| `areaBranchDefenceLv` | list[int] | 分支防御等级 (5个) |
| `areaBranchDefenceUpgradeLeftTime` | list[int] | 分支防御升级剩余时间 |
| `areaTreasurePriceData` | list | 宝物价格数据 |
| `speProduct` | list[str] | 特产列表 |
| `autoBuild` | bool | 自动建造 |
| `autoBuildResourceRateLimit` | float | 自动建造资源率限制 |
| `autoBuildPriority` | int | 自动建造优先级 |

### 其他字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `areaSpeAddData` | dict | 区域特殊加成 |
| `recordLog` | list[str] | 记录日志 (最近30条) |
| `thisMonthManaged` | int | 本月管理次数 |
| `missionNumCount` | int | 任务计数 |
| `plotNumCount` | int | 剧情计数 |
| `areaInteractionTimeData` | dict | 区域交互时间数据 |

## areaTiles 地块结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | string/null | 名称 |
| `spriteName` | string | 精灵名称 (如 `Tile_GrayGround`) |
| `spriteRotateType` | int | 旋转类型 |
| `spriteFlipX` | bool | X轴翻转 |
| `spriteFlipY` | bool | Y轴翻转 |
| `building` | dict/null | 建筑数据 |
| `tileType` | int | 地块类型 (-1=空) |
| `areaRoadData` | dict/null | 道路数据 |
| `areaID` | int | 所属区域ID |
| `row` | int | 行号 |
| `column` | int | 列号 |

## areaRoadData 道路数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `areaID` | int | 所属区域ID |
| `roadLv` | int | 道路等级 |
| `upgradeTimeLeft` | int | 升级剩余时间 |

## building 建筑结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `buildingID` | int | 建筑ID |
| `lv` | int | 建筑等级 |
| `buildTimeLeft` | int | 建造剩余时间 |
| `upgradeTimeLeft` | int | 升级剩余时间 |
| `destroyTimeLeft` | int | 拆除剩余时间 |
| `noCancel` | bool | 不可取消 |
| `shopItemList` | dict | 商店物品列表 |
| `missionDatas` | list | 任务数据 |
| `produceRate` | float | 生产率 |
| `resourceStoreRate` | float | 资源存储率 |
| `areaID` | int | 所属区域ID |
| `belongHeroID` | int | 所属角色ID |
| `missionNumCount` | int | 任务计数 |
| `plotNumCount` | int | 剧情计数 |
| `enemyMonth` | int | 敌人月份 |

## Forces 门派结构

### 门派基础信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `forceID` | int | 门派ID |
| `forceName` | string | 门派名称 |
| `defaultSkinID` | int | 默认皮肤ID |
| `bigForce` | bool | 是否大门派 |
| `autoAddMember` | bool | 自动添加成员 |
| `forceStyle` | string | 门派风格 (中庸/正派/邪派) |
| `forceMaleRate` | float | 男性比例 |
| `forceLv` | int | 门派等级 |
| `mainAreaID` | int | 主区域ID |
| `masterForce` | int | 宗主门派ID (-1=无) |
| `servantForce` | list[int] | 附庸门派ID列表 |
| `leader` | int | 掌门角色ID |

### 门派成员与区域

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `ownAreasID` | list[int] | 拥有区域ID列表 |
| `ownResourcePointsID` | list[int] | 拥有资源点ID列表 |
| `ownHeros` | list[int] | 拥有角色ID列表 |
| `heroLvNum` | list[int] | 角色等级数量 `[低, 中, 高, ...]` |
| `totalSalary` | int | 总薪水 |
| `totalPopulation` | int | 总人口 |

### 门派资源

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `resourceStore` | list[float] | 资源存储 `[粮食, 木材, 石材, 铁矿, 布匹, 药材]` |
| `resourceStoreMax` | list[float] | 资源存储上限 |
| `resourceChange` | list[float] | 资源变化率 |
| `forceStorage` | dict | 门派仓库 |
| `forceStorageSelfDiscount` | float | 门派内购买折扣 |
| `forceStorageOtherDiscount` | float | 门派外购买折扣 |

### 门派关系

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `forceFavor` | list | 门派好感列表 |
| `forceFavorDict` | dict | 门派好感字典 `{门派ID: 好感值}` |
| `allyForce` | list[int] | 同盟门派ID列表 |
| `ForceStopWarTime` | dict | 停战时间 |

### 门派发展

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `kungfuSkillFocus` | list[int] | 武学侧重 (索引0-8对应武学类型) |
| `livingSkillFocus` | list[int] | 技能侧重 |
| `itemFocus` | list[float] | 物品侧重 |
| `forceFocus` | int | 门派侧重 |
| `nowResearchTech` | int | 当前研究科技ID |
| `techLvData` | list[dict] | 科技等级数据 (60个) |
| `techSpeAddData` | dict | 科技特殊加成 |
| `forceSpeAddData` | dict | 门派特殊加成 |

### 门派特殊建筑

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `speBuildingID` | int | 特殊建筑ID |
| `speFunctionDescribe` | string | 特殊功能描述 |

### 其他门派字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `bookWriterList` | list[dict] | 著书者列表 |
| `bookStorage` | dict | 书籍仓库 |
| `showRoomItems` | list | 展示物品 |
| `showRoomChangeFame` | float | 展示厅声望变化 |
| `forceJobSettingData` | dict | 门派职务设置 |
| `forceInteractionTimeData` | dict | 门派交互时间数据 |
| `playerOutForceContribution` | float | 玩家在门派贡献 |
| `thisMonthAttack` | bool | 本月是否攻击 |
| `thisMonthManaged` | int | 本月管理次数 |

## techLvData 科技等级

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `techID` | int | 科技ID |
| `lv` | int | 科技等级 |
| `researchPercent` | float | 研究进度百分比 |

## ResourcePoints 资源点结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `resourcePointID` | int | 资源点ID |
| `resourcePointTypeID` | int | 资源点类型ID |
| `resourcePointName` | string | 资源点名称 |
| `resourcePointFullName` | string | 资源点全名 |
| `spriteName` | string | 精灵名称 |
| `bigMapPos` | dict | 大地图位置 `{x, y}` |
| `belongForceID` | int | 所属门派ID |
| `connectAreaID` | int | 连接区域ID |
| `changeResource` | list[float] | 资源产出 `[粮食, 木材, 石材, 铁矿, 布匹, 药材]` |
| `resourceSpeAddData` | dict | 资源特殊加成 |
| `thisMonthExplored` | bool | 本月已探索 |
| `resourcePointDetailDirty` | bool | 资源点详情脏标记 |

## Inns 客栈结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `id` | int | 客栈ID |
| `innName` | string | 客栈名称 |
| `describe` | string | 客栈描述 |
| `shopItemList` | dict | 商店物品列表 |
| `bigMapPos` | dict | 大地图位置 `{x, y}` |
| `nearAreaID` | list[int] | 附近区域ID |
| `haveSpeEvent` | bool | 有特殊事件 |
| `plotNumCount` | int | 剧情计数 |
| `missionNumCount` | int | 任务计数 |

## worldTime 世界时间

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `year` | int | 年份 |
| `month` | int | 月份 (1-12) |
| `day` | int | 日期 (1-30) |

## prisonData 监狱数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `guardAlert` | float | 守卫警惕值 |
| `guardFavor` | float | 守卫好感值 |
| `prisonItemKeep` | dict | 扣押物品仓库 |
| `buyGuardCd` | float | 收买守卫冷却 |

## 物品/仓库通用结构

以下结构在多处使用: `governStorage`, `forceStorage`, `bookStorage`, `speBookStorage`, `shopItemList`, `prisonItemKeep` 等。

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `heroID` | int | 所属角色ID (-1=无) |
| `forceID` | int | 所属门派ID (-1=无) |
| `money` | int | 金钱 |
| `weight` | float | 当前负重 |
| `maxWeight` | float | 最大负重 (-1=无限制) |
| `allItem` | list[dict] | 所有物品列表 |

## Item 物品结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `itemID` | int | 物品ID |
| `type` | int | 物品类型 (见物品类型表) |
| `subType` | int | 子类型 |
| `name` | string | 名称 |
| `checkName` | string | 鉴定名称 |
| `describe` | string | 描述 |
| `value` | int | 价值 |
| `itemLv` | int | 物品等级 |
| `rareLv` | int | 品质等级 (0-5) |
| `weight` | float | 重量 |
| `isNew` | bool | 是否新物品 |
| `poisonNum` | float | 毒素量 |
| `poisonNumDetected` | bool | 毒素是否已检测 |
| `equipmentData` | dict/null | 装备数据 (武器/防具) |
| `medFoodData` | dict/null | 药品/食物数据 |
| `bookData` | dict/null | 秘籍数据 `{skillID: int}` |
| `treasureData` | dict/null | 宝物数据 |
| `materialData` | dict/null | 材料数据 |
| `horseData` | dict/null | 坐骑数据 |

### 物品类型表

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

## equipmentData 装备数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `enhanceLv` | int | 强化等级 |
| `littleType` | int | 小类型 |
| `attriType` | int | 属性类型 |
| `baseAddData` | dict | 基础加成 `{heroSpeAddData: {属性ID: 值}}` |
| `extraAddData` | dict | 额外加成 |
| `equiped` | bool | 是否已装备 |
| `animName` | string | 动画名称 |
| `equipPoisonData` | dict | 装备毒素数据 |
| `speEnhanceLv` | int | 特殊强化等级 |
| `speWeightLv` | int | 特殊重量等级 |

## medFoodData 药品/食物数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `enhanceLv` | int | 强化等级 |
| `changeHeroState` | dict | 角色状态变化 |
| `randomSpeAddValue` | int | 随机特殊加成值 |
| `extraAddData` | dict | 额外加成 |

### changeHeroState 结构

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `hp` | float | 生命变化 |
| `maxhp` | float | 最大生命变化 |
| `mana` | float | 内力变化 |
| `maxMana` | float | 最大内力变化 |
| `power` | float | 体力变化 |
| `maxPower` | float | 最大体力变化 |
| `externalInjury` | float | 外伤变化 |
| `internalInjury` | float | 内伤变化 |
| `poisonInjury` | float | 中毒变化 |
| `changeAttri` | list | 属性变化 |
| `charm` | float | 魅力变化 |
| `buffData` | dict | 增益数据 |

## horseData 坐骑数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `equiped` | bool | 是否已装备 |
| `speed` | float | 速度 |
| `power` | float | 体力 |
| `sprint` | float | 冲刺 |
| `resist` | float | 抗性 |
| `speedAdd` | float | 速度加成 |
| `powerAdd` | float | 体力加成 |
| `sprintAdd` | float | 冲刺加成 |
| `resistAdd` | float | 抗性加成 |
| `maxWeightAdd` | float | 最大负重加成 |
| `nowPower` | float | 当前体力 |
| `favorRate` | float | 好感率 |
| `sprintTimeLeft` | float | 冲刺剩余时间 |
| `sprintTimeCd` | float | 冲刺冷却 |

## treasureData 宝物数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `fullIdentified` | bool | 是否完全鉴定 |
| `identifyKnowledgeNeed` | float | 鉴定所需学识 |
| `treasureLv` | list[int] | 宝物等级 (4层) |
| `identifyDifficulty` | list[float] | 鉴定难度 (4层) |
| `identified` | list[bool] | 是否已鉴定 (4层) |
| `playerGuessTreasureLv` | list[list[int]] | 玩家猜测宝物等级 |

## weaponResearchData 武器研究数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `lv` | int | 研究等级 |
| `exp` | float | 研究经验 |
| `researchTarget` | dict | 研究目标物品 |
| `researchTargetBuff` | dict | 研究目标加成 |
| `leftTime` | int | 剩余时间 |

## meditationData 冥想数据

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `lv` | int | 冥想等级 |
| `exp` | float | 冥想经验 |
| `monthMeditationDay` | int | 本月冥想天数 |
| `meditationTreasure` | dict | 冥想宝物 |
| `treasureAddData` | dict | 宝物加成 |
| `treasureLeftTime` | int | 宝物剩余时间 |
| `meditationFood` | dict | 冥想食物 |
| `foodAddData` | dict | 食物加成 |
| `foodLeftTime` | int | 食物剩余时间 |
| `meditationMed` | dict | 冥想药物 |
| `medAddData` | dict | 药物加成 |
| `medLeftTime` | int | 药物剩余时间 |

## forceSpeResearchData 门派特殊研究

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `researchRate` | float | 研究速率 |
| `material` | dict | 材料 |
| `addDamageRate` | float | 伤害加成率 |
| `researchBuff` | dict | 研究增益 |
| `leftTime` | int | 剩余时间 |

## WorldNewsDatas 世界新闻

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `newsText` | string | 新闻内容 |
| `leftTime` | int | 剩余时间 |

## MailDatas 邮件

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `mailTitle` | string | 邮件标题 |
| `mailText` | string | 邮件内容 |
| `mailTime` | dict | 邮件时间 `{year, month, day}` |
| `important` | bool | 是否重要 |
| `noticed` | bool | 是否已通知 |
| `autoDestroyTime` | int | 自动销毁时间 |
| `notImportant` | bool | 是否不重要 |

## infos 信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `infoType` | int | 信息类型 |
| `infotime` | dict | 信息时间 `{year, month, day}` |
| `infoText` | string | 信息内容 |

## worldPlotEventStartData 世界剧情事件

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `name` | string | 事件名称 |
| `difficulty` | float | 难度 |
| `plotID` | int | 剧情ID |
| `triggerType` | int | 触发类型 |
| `triggerTargetID` | string | 触发目标ID |
| `startLeftDay` | int | 开始剩余天数 |
| `targetEventSaveRecord` | int | 目标事件记录 |
| `targetEvent` | dict/null | 目标事件 |
| `noAutoDestroy` | bool | 不自动销毁 |
| `outtimeCallSpeFuc` | string | 超时调用特殊功能 |
| `notImportant` | bool | 是否不重要 |

## plotHappened 已发生剧情

字典结构，键为剧情ID，值为发生时间列表：

```json
{
  "剧情ID": [{"year": 1, "month": 1, "day": 1}, ...]
}
```

## playerBookWriter 玩家著书

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `lv` | int | 著书等级 |
| `bookWriterType` | int | 著书类型 |
| `bookWriterHeroID` | int | 著书角色ID |
| `targetBookData` | dict/null | 目标书籍数据 |
| `combineBookData` | dict/null | 组合书籍数据 |
| `targetSkillData` | dict/null | 目标武功数据 |
| `workStarted` | bool | 是否开始工作 |
| `workPercent` | float | 工作进度百分比 |

## skinUnlockData 皮肤解锁

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `skinID` | int | 皮肤ID |
| `skinLvUnlocked` | list[bool] | 皮肤等级解锁状态 (6级) |

## customDifficultyData 自定义难度

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `customDifficultyLv` | dict | 自定义难度等级设置 |

## 其他游戏状态字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `cheating` | bool | 是否作弊中 |
| `cheated` | bool | 是否曾作弊 |
| `gameMode` | int | 游戏模式 |
| `gameDifficulty` | int | 游戏难度 |
| `relaxMode` | bool | 休闲模式 |
| `hour` | float | 当前小时 |
| `TimeDifficulty` | float | 时间难度 |
| `forceMeetingStarted` | bool | 门派会议已开始 |
| `forcePartyStarted` | bool | 门派宴会已开始 |
| `forceMeetingMissedTime` | int | 门派会议错过次数 |
| `playerBetrayForceBadTime` | int | 玩家叛出门派次数 |
| `playerGetTeacherTime` | int | 玩家拜师次数 |
| `playerServantForceTime` | int | 玩家附庸门派时间 |
| `openLeaveForce` | bool | 开放离开门派 |
| `openForceBuilding` | bool | 开放门派建筑 |
| `openForceAttackResource` | bool | 开放门派攻击资源点 |
| `openForceAttackArea` | bool | 开放门派攻击区域 |
| `openForceAttackBasement` | bool | 开放门派攻击基地 |

## 每月次数限制字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `monthCatchBadFamePlayerTime` | int | 本月通缉恶名玩家次数 |
| `monthGambleTime` | int | 本月赌博次数 |
| `monthPartyTime` | int | 本月宴会次数 |
| `monthForcePartyTime` | int | 本月门派宴会次数 |
| `monthDoctorTime` | int | 本月看病次数 |
| `monthPerformForMoneyTime` | int | 本月卖艺次数 |
| `monthCoachTime` | int | 本月指点次数 |
| `monthAttackMartialClubTime` | int | 本月攻击武馆次数 |
| `monthSpeReduceBadFameTime` | int | 本月特殊减少恶名次数 |
| `monthSpeAddFameTime` | int | 本月特殊增加声望次数 |
| `monthSpeGetTalentPointTime` | int | 本月特殊获取天赋点次数 |
| `monthChallengeTime` | int | 本月挑战次数 |
| `monthBuyAreaInfoTime` | int | 本月购买区域信息次数 |
| `monthGiveMoneyToGovernTime` | int | 本月给官府钱次数 |
| `monthBreakEquipTime` | int | 本月破坏装备次数 |
| `monthKillTime` | int | 本月击杀次数 |
| `monthFreshBountyTime` | int | 本月刷新悬赏次数 |
| `monthFreshAuctionTime` | int | 本月刷新拍卖次数 |
| `monthLeaderInteractOtherForceTime` | int | 本月掌门与其他门派交互次数 |

## 统计字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `finishForceMissionCount` | int | 完成门派任务数 |
| `totalFightCount` | int | 总战斗次数 |
| `totalWinFightCount` | int | 总胜利次数 |
| `totalEnemyKilled` | int | 总击杀敌人 |
| `totalBadFame` | float | 总恶名 |
| `studyFightWithGreatHeroSingleWinNum` | int | 切磋单挑胜利数 |
| `studyFightWithGreatHeroMultiWinNum` | int | 切磋群战胜利数 |
| `studyFightWithGreatHeroFinalWinNum` | int | 切磋最终胜利数 |
| `totalHeroMeet` | int | 总相遇角色数 |

## 特殊加成数据格式

游戏中多处使用 `heroSpeAddData` 格式存储属性加成：

```json
{
  "heroSpeAddData": {
    "属性ID": 加成值,
    "66": 0.1,  // 暴击+10%
    "60": 0.2   // 伤害+20%
  }
}
```

### 常用属性ID参考

| ID | 名称 | ID | 名称 |
|----|------|-----|------|
| 0-5 | 基础属性 (力道/灵巧/智力/意志/体质/经脉) | 60 | 伤害 |
| 6-14 | 武学属性 | 61 | 护甲 |
| 57 | 生命上限 | 63 | 速度 |
| 58 | 体力上限 | 64 | 命中 |
| 59 | 内力上限 | 65 | 闪避 |
| 66 | 暴击 | 70 | 连击 |
| 67 | 卸力 | 71 | 招架 |
| 68 | 反击 | 72 | 破甲 |
| 69 | 压制 | 73 | 穿透 |

## 注意事项

1. **存档编码** - Save 文件使用 UTF-8 编码的 JSON 格式
2. **数值类型** - 多数数值为 float 类型，注意精度问题
3. **脏标记** - 多处 `*Dirty` 字段用于标记数据是否需要同步
4. **时间字段** - 时间统一使用 `{year, month, day}` 格式
5. **ID映射** - 门派ID、角色ID等与 Hero 文件中的ID对应
6. **列表索引** - 资源、属性等多用数组索引，注意顺序
