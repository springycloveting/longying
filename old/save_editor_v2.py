#!/usr/bin/env python3
"""
龙胤立志传 - 存档修改器 GUI版 v2
采用简洁风格设计，基于 PyQt6
"""

import sys
import os
import json
import shutil
from datetime import datetime
from pathlib import Path

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QTabWidget, QListWidget, QListWidgetItem,
    QGridLayout, QSpinBox, QDoubleSpinBox, QMessageBox, QFileDialog,
    QDialog, QHeaderView, QFrame, QScrollArea, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor

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

# 绿色主题颜色
COLORS = {
    'ink': '#17211d',
    'muted': '#6f7b75',
    'accent': '#276c58',
    'accent_deep': '#1c5142',
    'bg': '#e9efec',
    'card_bg': '#ffffff',
    'border': '#d2d2d7',
    'text': '#1d1d1f',
    'text_secondary': '#86868b',
    'primary': '#276c58',
    'success': '#388160',
    'power': '#3d7189',
    'mana': '#755f96',
    'danger': '#b85048',
}

# ========== 数据加载 ==========

def get_app_dir():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def load_json_data(filename):
    app_dir = get_app_dir()
    filepath = app_dir / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

SKILL_NAMES = {}
skill_data = load_json_data('skill_names.json')
for k, v in skill_data.items():
    SKILL_NAMES[int(k)] = v

SPE_ATTR_MAP = load_json_data('spe_attr_map.json')

# ========== 工具函数 ==========

def get_skill_name(skill_id):
    if skill_id in SKILL_NAMES:
        return SKILL_NAMES[skill_id].get('name', f'未知({skill_id})')
    return f'未知({skill_id})'

def get_skill_type(skill_id):
    if skill_id in SKILL_NAMES:
        return SKILL_NAMES[skill_id].get('type', '')
    return ''

def get_spe_attr_name(attr_id):
    return SPE_ATTR_MAP.get(str(attr_id), f'属性{attr_id}')

def get_force_name(force_id):
    return FORCE_MAP.get(force_id, f'未知({force_id})')

def backup_file(filepath):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = f"{filepath}.backup_{timestamp}"
    shutil.copy2(filepath, backup_path)
    return backup_path

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

def all_skills_max(hero, lv=10, damage=999):
    for skill in hero.get('kungfuSkills', []):
        skill['lv'] = lv
        skill['damageUseSpeAddValue'] = float(damage)

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

# ========== 自定义控件 ==========

class StatusCard(QFrame):
    """状态卡片"""
    def __init__(self, title, color, current=100, maximum=100):
        super().__init__()
        self.color = color
        self.setFixedHeight(110)
        self.setStyleSheet(f"QFrame {{ background: #f5f5f7; border: 1px solid {COLORS['border']}; border-radius: 10px; }}")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(6)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px; font-weight: 500;")
        layout.addWidget(title_label)

        self.value_label = QLabel(f"{int(current)}")
        self.value_label.setStyleSheet(f"color: {color}; font-size: 26px; font-weight: 700;")
        layout.addWidget(self.value_label)

        edit_layout = QHBoxLayout()
        edit_layout.setSpacing(4)
        
        self.current_spin = QSpinBox()
        self.current_spin.setRange(0, 999999)
        self.current_spin.setValue(int(current))
        self.current_spin.setFixedWidth(70)
        self.current_spin.setStyleSheet(f"QSpinBox {{ background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 4px 8px; }}")
        edit_layout.addWidget(self.current_spin)
        
        sep = QLabel("/")
        sep.setStyleSheet(f"color: {COLORS['muted']};")
        edit_layout.addWidget(sep)
        
        self.max_spin = QSpinBox()
        self.max_spin.setRange(0, 999999)
        self.max_spin.setValue(int(maximum))
        self.max_spin.setFixedWidth(70)
        self.max_spin.setStyleSheet(self.current_spin.styleSheet())
        edit_layout.addWidget(self.max_spin)
        edit_layout.addStretch()
        layout.addLayout(edit_layout)

    def get_values(self):
        return self.current_spin.value(), self.max_spin.value()

class AttrEdit(QFrame):
    """属性编辑控件"""
    valueChanged = pyqtSignal()

    def __init__(self, name, value=0, max_value=None, show_max=False):
        super().__init__()
        self.setStyleSheet(f"QFrame {{ background: #f5f5f7; border: 1px solid {COLORS['border']}; border-radius: 8px; }}")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)
        layout.setSpacing(4)

        # 属性名
        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {COLORS['muted']}; font-size: 12px; font-weight: 500;")
        name_label.setFixedWidth(32)
        layout.addWidget(name_label)

        # 值输入框
        self.spin = QSpinBox()
        self.spin.setRange(0, 9999)
        self.spin.setValue(int(value))
        self.spin.setFixedWidth(55)
        self.spin.setStyleSheet(f"QSpinBox {{ background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 2px; }}")
        self.spin.valueChanged.connect(self.valueChanged.emit)
        layout.addWidget(self.spin)

        # 最大值
        if show_max and max_value is not None:
            sep = QLabel("/")
            sep.setStyleSheet(f"color: {COLORS['muted']}; font-size: 10px;")
            layout.addWidget(sep)
            self.max_spin = QSpinBox()
            self.max_spin.setRange(0, 9999)
            self.max_spin.setValue(int(max_value))
            self.max_spin.setFixedWidth(45)
            self.max_spin.setStyleSheet(self.spin.styleSheet())
            layout.addWidget(self.max_spin)
            self._has_max = True
        else:
            self._has_max = False
            layout.addStretch()

    def get_value(self):
        return self.spin.value()

    def has_max(self):
        return self._has_max

    def set_max_value(self, value):
        if self._has_max and hasattr(self, 'max_spin'):
            self.max_spin.setValue(int(value))

class SkillSearchDialog(QDialog):
    """武功搜索对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加武功")
        self.setFixedSize(450, 400)
        self.selected_skill = None

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入武功名称或ID...")
        self.search_input.setStyleSheet(f"QLineEdit {{ padding: 10px; border: 1px solid {COLORS['border']}; border-radius: 8px; background: white; }}")
        self.search_input.textChanged.connect(self.search_skills)
        layout.addWidget(self.search_input)

        self.result_list = QListWidget()
        self.result_list.setStyleSheet(f"QListWidget {{ border: 1px solid {COLORS['border']}; border-radius: 8px; background: white; }}")
        layout.addWidget(self.result_list)

        level_layout = QHBoxLayout()
        level_label = QLabel("等级:")
        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 10)
        self.level_spin.setValue(1)
        self.level_spin.setFixedWidth(80)
        level_layout.addWidget(level_label)
        level_layout.addWidget(self.level_spin)
        level_layout.addStretch()
        layout.addLayout(level_layout)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(80, 32)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        add_btn = QPushButton("添加")
        add_btn.setFixedSize(80, 32)
        add_btn.setStyleSheet(f"QPushButton {{ background: {COLORS['primary']}; color: white; border-radius: 8px; }}")
        add_btn.clicked.connect(self.accept_skill)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)
        self.search_skills("")

    def search_skills(self, text):
        self.result_list.clear()
        text = text.lower()
        count = 0
        for sid, info in SKILL_NAMES.items():
            name = info.get('name', '')
            skill_type = info.get('type', '')
            if text in name.lower() or text in str(sid):
                item = QListWidgetItem(f"{name} ({skill_type}) [ID:{sid}]")
                item.setData(Qt.ItemDataRole.UserRole, sid)
                self.result_list.addItem(item)
                count += 1
                if count >= 100:
                    break

    def accept_skill(self):
        current = self.result_list.currentItem()
        if current:
            self.selected_skill = current.data(Qt.ItemDataRole.UserRole)
            self.selected_level = self.level_spin.value()
            self.accept()

# ========== 主窗口 ==========

class SaveEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("龙胤立志传 - 存档修改器")
        self.setMinimumSize(1100, 750)

        self.data = []
        self.current_hero = None
        self.hero_idx = None
        self.save_path = None
        self.modified = False

        self.setup_ui()

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.setup_sidebar(main_layout)
        self.setup_main_area(main_layout)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def setup_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"QFrame {{ background: white; border-right: 1px solid {COLORS['border']}; }}")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 品牌
        brand_layout = QHBoxLayout()
        brand_mark = QLabel("胤")
        brand_mark.setStyleSheet(f"QLabel {{ background: {COLORS['primary']}; color: white; border-radius: 10px; padding: 6px; font-size: 16px; font-weight: bold; }}")
        brand_layout.addWidget(brand_mark)
        brand_name = QLabel("龙胤立志传")
        brand_name.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {COLORS['ink']};")
        brand_layout.addWidget(brand_name)
        brand_layout.addStretch()
        layout.addLayout(brand_layout)

        # 搜索
        list_title = QLabel("角色列表")
        list_title.setStyleSheet(f"font-size: 12px; color: {COLORS['muted']}; font-weight: 500;")
        layout.addWidget(list_title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索角色...")
        self.search_input.setStyleSheet(f"QLineEdit {{ padding: 8px; border: 1px solid {COLORS['border']}; border-radius: 8px; background: #f5f5f7; }}")
        self.search_input.textChanged.connect(self.filter_characters)
        layout.addWidget(self.search_input)

        # 角色列表
        self.char_list = QListWidget()
        self.char_list.setStyleSheet(f"QListWidget {{ border: none; background: transparent; }} QListWidget::item {{ padding: 10px; border-radius: 8px; }} QListWidget::item:selected {{ background: {COLORS['primary']}; color: white; }}")
        self.char_list.currentRowChanged.connect(self.select_character)
        layout.addWidget(self.char_list)

        parent_layout.addWidget(sidebar)

    def setup_main_area(self, parent_layout):
        main_frame = QFrame()
        main_frame.setStyleSheet(f"QFrame {{ background: {COLORS['bg']}; }}")

        layout = QVBoxLayout(main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部
        header = QFrame()
        header.setStyleSheet(f"QFrame {{ background: white; border-bottom: 1px solid {COLORS['border']}; }}")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 12, 20, 12)

        title = QLabel("龙胤立志传 存档修改器")
        title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['ink']};")
        header_layout.addWidget(title)

        self.current_char_label = QLabel()
        self.current_char_label.setStyleSheet(f"QLabel {{ background: #f5f5f7; padding: 6px 14px; border-radius: 20px; }}")
        header_layout.addWidget(self.current_char_label)
        header_layout.addStretch()

        self.open_btn = QPushButton("打开存档")
        self.open_btn.setFixedSize(90, 32)
        self.open_btn.setStyleSheet(f"QPushButton {{ background: #f5f5f7; border: 1px solid {COLORS['border']}; border-radius: 8px; }}")
        self.open_btn.clicked.connect(self.open_file)
        header_layout.addWidget(self.open_btn)

        self.backup_btn = QPushButton("备份存档")
        self.backup_btn.setFixedSize(90, 32)
        self.backup_btn.setStyleSheet(self.open_btn.styleSheet())
        self.backup_btn.clicked.connect(self.backup_file)
        header_layout.addWidget(self.backup_btn)

        self.save_btn = QPushButton("保存修改")
        self.save_btn.setFixedSize(90, 32)
        self.save_btn.setStyleSheet(f"QPushButton {{ background: {COLORS['primary']}; color: white; border-radius: 8px; }}")
        self.save_btn.clicked.connect(self.save_file)
        header_layout.addWidget(self.save_btn)

        layout.addWidget(header)

        # Tab
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"QTabWidget::pane {{ border: none; background: {COLORS['bg']}; }} QTabBar::tab {{ background: white; padding: 12px 16px; color: {COLORS['muted']}; border-bottom: 2px solid transparent; }} QTabBar::tab:selected {{ color: {COLORS['primary']}; border-bottom-color: {COLORS['primary']}; }}")

        self.setup_basic_tab()
        self.setup_skills_tab()
        self.setup_items_tab()
        self.setup_relations_tab()
        self.setup_tools_tab()

        layout.addWidget(self.tabs)
        parent_layout.addWidget(main_frame)

    def setup_basic_tab(self):
        page = QWidget()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(page)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # 快捷操作
        quick_group = self.create_card("快捷操作")
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(8)
        for text, callback in [("一键全属性满", self.max_all_attrs), ("治愈角色", self.heal_hero), ("复活角色", self.revive_hero), ("金钱满", self.max_money), ("声望满", self.max_fame)]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"QPushButton {{ background: white; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 10px 16px; }}")
            btn.clicked.connect(callback)
            quick_layout.addWidget(btn)
        quick_layout.addStretch()
        quick_group.layout().addLayout(quick_layout)
        layout.addWidget(quick_group)

        # 状态
        status_group = self.create_card("状态")
        status_layout = QHBoxLayout()
        status_layout.setSpacing(16)
        self.hp_card = StatusCard("生命", COLORS['success'], 100, 100)
        self.power_card = StatusCard("体力", COLORS['power'], 100, 100)
        self.mana_card = StatusCard("内力", COLORS['mana'], 100, 100)
        status_layout.addWidget(self.hp_card)
        status_layout.addWidget(self.power_card)
        status_layout.addWidget(self.mana_card)
        status_group.layout().addLayout(status_layout)
        layout.addWidget(status_group)

        # 基础属性
        base_group = self.create_card("基础属性")
        base_layout = QGridLayout()
        base_layout.setSpacing(12)
        base_layout.setColumnStretch(0, 1)
        base_layout.setColumnStretch(1, 1)
        base_layout.setColumnStretch(2, 1)
        self.base_attrs = []
        for i, name in enumerate(ATTR_NAMES):
            attr = AttrEdit(name, 0, show_max=True)
            self.base_attrs.append(attr)
            base_layout.addWidget(attr, i // 3, i % 3)
        base_group.layout().addLayout(base_layout)
        layout.addWidget(base_group)

        # 武学属性
        fight_group = self.create_card("武学属性")
        fight_layout = QGridLayout()
        fight_layout.setSpacing(12)
        fight_layout.setColumnStretch(0, 1)
        fight_layout.setColumnStretch(1, 1)
        fight_layout.setColumnStretch(2, 1)
        self.fight_attrs = []
        for i, name in enumerate(FIGHT_SKILL_NAMES):
            attr = AttrEdit(name, 0, show_max=True)
            self.fight_attrs.append(attr)
            fight_layout.addWidget(attr, i // 3, i % 3)
        fight_group.layout().addLayout(fight_layout)
        layout.addWidget(fight_group)

        # 技能属性
        living_group = self.create_card("技能属性")
        living_layout = QGridLayout()
        living_layout.setSpacing(12)
        living_layout.setColumnStretch(0, 1)
        living_layout.setColumnStretch(1, 1)
        living_layout.setColumnStretch(2, 1)
        self.living_attrs = []
        for i, name in enumerate(LIVING_SKILL_NAMES):
            attr = AttrEdit(name, 0, show_max=True)
            self.living_attrs.append(attr)
            living_layout.addWidget(attr, i // 3, i % 3)
        living_group.layout().addLayout(living_layout)
        layout.addWidget(living_group)

        # 其他信息
        other_group = self.create_card("其他信息")
        other_layout = QGridLayout()
        other_layout.setSpacing(10)
        self.fame_edit = AttrEdit("声望", 0)
        self.bad_fame_edit = AttrEdit("恶名", 0)
        self.money_edit = AttrEdit("金钱", 0)
        self.money_edit.spin.setRange(0, 9999999)
        self.money_edit.spin.setFixedWidth(80)
        other_layout.addWidget(self.fame_edit, 0, 0)
        other_layout.addWidget(self.bad_fame_edit, 0, 1)
        other_layout.addWidget(self.money_edit, 0, 2)
        other_group.layout().addLayout(other_layout)
        layout.addWidget(other_group)

        layout.addStretch()
        self.tabs.addTab(scroll, "基本属性")

    def setup_skills_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)
        self.skill_search = QLineEdit()
        self.skill_search.setPlaceholderText("搜索武功...")
        self.skill_search.setStyleSheet(f"QLineEdit {{ padding: 8px; border: 1px solid {COLORS['border']}; border-radius: 8px; background: white; }}")
        self.skill_search.textChanged.connect(self.filter_skills)
        toolbar_layout.addWidget(self.skill_search)
        add_btn = QPushButton("添加武功")
        add_btn.setStyleSheet(f"QPushButton {{ background: {COLORS['primary']}; color: white; border-radius: 8px; padding: 8px 16px; }}")
        add_btn.clicked.connect(self.add_skill)
        toolbar_layout.addWidget(add_btn)
        max_btn = QPushButton("全部满级")
        max_btn.setStyleSheet(f"QPushButton {{ background: white; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 8px 16px; }}")
        max_btn.clicked.connect(self.all_skills_max)
        toolbar_layout.addWidget(max_btn)
        layout.addWidget(toolbar)

        self.skill_table = QTableWidget()
        self.skill_table.setColumnCount(6)
        self.skill_table.setHorizontalHeaderLabels(["武功名称", "类型", "等级", "装备", "特殊属性", "操作"])
        self.skill_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.skill_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.skill_table.setShowGrid(False)
        self.skill_table.setStyleSheet(f"QTableWidget {{ background: white; border: 1px solid {COLORS['border']}; border-radius: 12px; }}")
        layout.addWidget(self.skill_table)
        self.tabs.addTab(page, "武功技能")

    def setup_items_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        equip_group = self.create_card("装备")
        self.equip_grid = QGridLayout()
        equip_group.layout().addLayout(self.equip_grid)
        layout.addWidget(equip_group)
        items_group = self.create_card("物品栏")
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["名称", "类型", "等级", "品质"])
        items_group.layout().addWidget(self.items_table)
        layout.addWidget(items_group)
        layout.addStretch()
        self.tabs.addTab(page, "物品装备")

    def setup_relations_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        friends_group = self.create_card("好友")
        self.friends_list = QListWidget()
        self.friends_list.setStyleSheet(f"QListWidget {{ background: transparent; border: none; }} QListWidget::item {{ padding: 6px 12px; border-radius: 16px; border: 1px solid {COLORS['success']}; color: {COLORS['success']}; }}")
        friends_group.layout().addWidget(self.friends_list)
        layout.addWidget(friends_group)
        haters_group = self.create_card("仇人")
        self.haters_list = QListWidget()
        self.haters_list.setStyleSheet(f"QListWidget {{ background: transparent; border: none; }} QListWidget::item {{ padding: 6px 12px; border-radius: 16px; border: 1px solid {COLORS['danger']}; color: {COLORS['danger']}; }}")
        haters_group.layout().addWidget(self.haters_list)
        layout.addWidget(haters_group)
        students_group = self.create_card("徒弟")
        self.students_list = QListWidget()
        self.students_list.setStyleSheet(f"QListWidget {{ background: transparent; border: none; }} QListWidget::item {{ padding: 6px 12px; border-radius: 16px; border: 1px solid {COLORS['primary']}; color: {COLORS['primary']}; }}")
        students_group.layout().addWidget(self.students_list)
        layout.addWidget(students_group)
        layout.addStretch()
        self.tabs.addTab(page, "人际关系")

    def setup_tools_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        batch_group = self.create_card("批量操作")
        batch_layout = QHBoxLayout()
        for text, callback in [("所有角色属性满", self.batch_max_attrs), ("所有角色武功满级", self.batch_max_skills), ("治愈所有角色", self.batch_heal), ("复活所有死亡角色", self.batch_revive)]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"QPushButton {{ background: white; border: 1px solid {COLORS['border']}; border-radius: 8px; padding: 10px 16px; }}")
            btn.clicked.connect(callback)
            batch_layout.addWidget(btn)
        batch_layout.addStretch()
        batch_group.layout().addLayout(batch_layout)
        layout.addWidget(batch_group)
        info_group = self.create_card("存档信息")
        info_layout = QGridLayout()
        self.info_labels = {}
        for i, (key, label) in enumerate([("version", "存档版本"), ("count", "角色总数"), ("time", "保存时间")]):
            lbl = QLabel(f"{label}: -")
            info_layout.addWidget(lbl, 0, i)
            self.info_labels[key] = lbl
        info_group.layout().addLayout(info_layout)
        layout.addWidget(info_group)
        layout.addStretch()
        self.tabs.addTab(page, "工具")

    def create_card(self, title):
        group = QFrame()
        group.setStyleSheet(f"QFrame {{ background: white; border-radius: 12px; border: 1px solid {COLORS['border']}; }}")
        layout = QVBoxLayout(group)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {COLORS['ink']};")
        layout.addWidget(title_label)
        return group

    # ========== 文件操作 ==========

    def open_file(self):
        # 检查是否有real/Save目录
        app_dir = get_app_dir()
        save_dir = app_dir / 'real' / 'Save'
        if not save_dir.exists():
            save_dir = app_dir
        
        filepath, _ = QFileDialog.getOpenFileName(
            self, "打开存档文件", 
            str(save_dir), 
            "存档文件 (Hero);;所有文件 (*)"
        )
        if filepath:
            self.load_file(filepath)

    def load_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            if not isinstance(self.data, list) or len(self.data) == 0:
                raise ValueError("存档格式错误")
            self.data = [h for h in self.data if h is not None]
            self.save_path = filepath
            self.refresh_character_list()
            self.status_bar.showMessage(f"已加载: {filepath} (共 {len(self.data)} 个角色)")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"加载失败: {e}")

    def backup_file(self):
        if self.save_path:
            backup_path = backup_file(self.save_path)
            self.status_bar.showMessage(f"已备份到: {backup_path}")
        else:
            QMessageBox.warning(self, "警告", "请先打开存档文件")

    def save_file(self):
        if not self.save_path:
            QMessageBox.warning(self, "警告", "请先打开存档文件")
            return
        self.save_current_hero()
        backup_file(self.save_path)
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False)
        self.modified = False
        self.status_bar.showMessage(f"存档已保存")
        QMessageBox.information(self, "成功", "存档保存成功!")

    # ========== 角色操作 ==========

    def refresh_character_list(self):
        self.char_list.clear()
        for i, hero in enumerate(self.data):
            if hero is None:
                continue
            name = hero.get('heroName', '未知')
            hero_id = hero.get('heroID', '?')
            force = get_force_name(hero.get('belongForceID', -1))
            item = QListWidgetItem(f"{name} (ID:{hero_id}) · {force}")
            item.setData(Qt.ItemDataRole.UserRole, i)
            if hero.get('dead'):
                item.setForeground(QColor(COLORS['muted']))
            self.char_list.addItem(item)
        if self.char_list.count() > 0:
            self.char_list.setCurrentRow(0)

    def filter_characters(self, text):
        for i in range(self.char_list.count()):
            item = self.char_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def select_character(self, row):
        if row < 0 or row >= len(self.data):
            return
        if self.current_hero:
            self.save_current_hero()
        self.hero_idx = row
        self.current_hero = self.data[row]
        self.load_hero_data()

    def load_hero_data(self):
        if not self.current_hero:
            return
        hero = self.current_hero
        name = hero.get('heroName', '未知')
        force = get_force_name(hero.get('belongForceID', -1))
        leader = "掌门" if hero.get('isLeader') else ""
        dead = " [死亡]" if hero.get('dead') else ""
        self.current_char_label.setText(f"当前角色: {name}{dead} | {force}{leader}")

        hp = hero.get('hp', 0)
        maxhp = hero.get('maxhp', 100)
        self.hp_card.current_spin.setValue(int(hp))
        self.hp_card.max_spin.setValue(int(maxhp))
        self.hp_card.value_label.setText(str(int(hp)))

        power = hero.get('power', 0)
        maxPower = hero.get('maxPower', 100)
        self.power_card.current_spin.setValue(int(power))
        self.power_card.max_spin.setValue(int(maxPower))
        self.power_card.value_label.setText(str(int(power)))

        mana = hero.get('mana', 0)
        maxMana = hero.get('maxMana', 100)
        self.mana_card.current_spin.setValue(int(mana))
        self.mana_card.max_spin.setValue(int(maxMana))
        self.mana_card.value_label.setText(str(int(mana)))

        base_attri = hero.get('baseAttri', [0]*6)
        max_attri = hero.get('maxAttri', [0]*6)
        for i, attr in enumerate(self.base_attrs):
            attr.spin.setValue(int(base_attri[i] if i < len(base_attri) else 0))
            attr.set_max_value(max_attri[i] if i < len(max_attri) else 0)

        base_fight = hero.get('baseFightSkill', [0]*9)
        max_fight = hero.get('maxFightSkill', [0]*9)
        for i, attr in enumerate(self.fight_attrs):
            attr.spin.setValue(int(base_fight[i] if i < len(base_fight) else 0))
            attr.set_max_value(max_fight[i] if i < len(max_fight) else 0)

        base_living = hero.get('baseLivingSkill', [0]*9)
        max_living = hero.get('maxLivingSkill', [0]*9)
        for i, attr in enumerate(self.living_attrs):
            attr.spin.setValue(int(base_living[i] if i < len(base_living) else 0))
            attr.set_max_value(max_living[i] if i < len(max_living) else 0)

        self.fame_edit.spin.setValue(int(hero.get('fame', 0)))
        self.bad_fame_edit.spin.setValue(int(hero.get('badFame', 0)))
        self.money_edit.spin.setValue(int(hero.get('itemListData', {}).get('money', 0)))

        self.refresh_skill_table()
        self.refresh_relations()
        self.info_labels['count'].setText(f"角色总数: {len(self.data)}")

    def save_current_hero(self):
        if not self.current_hero:
            return
        hero = self.current_hero
        hp, maxhp = self.hp_card.get_values()
        power, maxPower = self.power_card.get_values()
        mana, maxMana = self.mana_card.get_values()
        modify_status(hero, hp, power, mana)
        hero['maxhp'] = float(maxhp)
        hero['realMaxHp'] = float(maxhp)
        hero['maxPower'] = float(maxPower)
        hero['realMaxPower'] = float(maxPower)
        hero['maxMana'] = float(maxMana)
        hero['realMaxMana'] = float(maxMana)
        for i, attr in enumerate(self.base_attrs):
            modify_base_attr(hero, i, attr.spin.value())
            if attr.has_max():
                hero['maxAttri'][i] = float(attr.max_spin.value())
        for i, attr in enumerate(self.fight_attrs):
            modify_fight_skill(hero, i, attr.spin.value())
            if attr.has_max():
                hero['maxFightSkill'][i] = float(attr.max_spin.value())
        for i, attr in enumerate(self.living_attrs):
            modify_living_skill(hero, i, attr.spin.value())
            if attr.has_max():
                hero['maxLivingSkill'][i] = float(attr.max_spin.value())
        modify_fame(hero, self.fame_edit.spin.value(), self.bad_fame_edit.spin.value())
        modify_money(hero, self.money_edit.spin.value())
        self.modified = True

    # ========== 武功操作 ==========

    def refresh_skill_table(self):
        skills = self.current_hero.get('kungfuSkills', [])
        self.skill_table.setRowCount(len(skills))
        for i, skill in enumerate(skills):
            skill_id = skill.get('skillID')
            name = get_skill_name(skill_id)
            skill_type = get_skill_type(skill_id)
            lv = skill.get('lv', 1)
            equipped = "✓" if skill.get('equiped') else ""
            spe_data = skill.get('speUseData', {}).get('heroSpeAddData', {})
            spe_str = ', '.join([f"{get_spe_attr_name(k)}:{v:.2f}" for k, v in list(spe_data.items())[:2]])
            self.skill_table.setItem(i, 0, QTableWidgetItem(name))
            self.skill_table.setItem(i, 1, QTableWidgetItem(skill_type))
            self.skill_table.setItem(i, 2, QTableWidgetItem(str(lv)))
            self.skill_table.setItem(i, 3, QTableWidgetItem(equipped))
            self.skill_table.setItem(i, 4, QTableWidgetItem(spe_str))
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            edit_btn = QPushButton("编辑")
            edit_btn.setFixedSize(50, 24)
            edit_btn.clicked.connect(lambda checked, idx=i: self.edit_skill(idx))
            btn_layout.addWidget(edit_btn)
            del_btn = QPushButton("删除")
            del_btn.setFixedSize(50, 24)
            del_btn.setStyleSheet(f"background: {COLORS['danger']}; color: white;")
            del_btn.clicked.connect(lambda checked, idx=i: self.delete_skill(idx))
            btn_layout.addWidget(del_btn)
            self.skill_table.setCellWidget(i, 5, btn_widget)

    def filter_skills(self, text):
        for i in range(self.skill_table.rowCount()):
            name_item = self.skill_table.item(i, 0)
            if name_item:
                self.skill_table.setRowHidden(i, text.lower() not in name_item.text().lower())

    def add_skill(self):
        if not self.current_hero:
            QMessageBox.warning(self, "警告", "请先选择角色")
            return
        dialog = SkillSearchDialog(self)
        if dialog.exec() and dialog.selected_skill:
            add_skill(self.current_hero, dialog.selected_skill, dialog.selected_level)
            self.refresh_skill_table()
            self.modified = True
            self.status_bar.showMessage(f"已添加: {get_skill_name(dialog.selected_skill)}")

    def edit_skill(self, idx):
        if not self.current_hero:
            return
        skills = self.current_hero.get('kungfuSkills', [])
        if idx >= len(skills):
            return
        skill = skills[idx]
        dialog = QDialog(self)
        dialog.setWindowTitle(f"编辑武功 - {get_skill_name(skill.get('skillID'))}")
        dialog.setFixedSize(300, 150)
        layout = QVBoxLayout(dialog)
        lv_layout = QHBoxLayout()
        lv_layout.addWidget(QLabel("等级:"))
        lv_spin = QSpinBox()
        lv_spin.setRange(1, 10)
        lv_spin.setValue(skill.get('lv', 1))
        lv_layout.addWidget(lv_spin)
        lv_layout.addStretch()
        layout.addLayout(lv_layout)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        cancel = QPushButton("取消")
        cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(cancel)
        save = QPushButton("保存")
        save.setStyleSheet(f"background: {COLORS['primary']}; color: white;")
        save.clicked.connect(dialog.accept)
        btn_layout.addWidget(save)
        layout.addLayout(btn_layout)
        if dialog.exec():
            skill['lv'] = lv_spin.value()
            self.refresh_skill_table()
            self.modified = True

    def delete_skill(self, idx):
        if not self.current_hero:
            return
        skills = self.current_hero.get('kungfuSkills', [])
        if idx >= len(skills):
            return
        skill_name = get_skill_name(skills[idx].get('skillID'))
        if QMessageBox.question(self, "确认删除", f"确定要删除【{skill_name}】吗?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            remove_skill(self.current_hero, idx)
            self.refresh_skill_table()
            self.modified = True
            self.status_bar.showMessage(f"已删除: {skill_name}")

    def all_skills_max(self):
        if not self.current_hero:
            return
        all_skills_max(self.current_hero)
        self.refresh_skill_table()
        self.modified = True
        self.status_bar.showMessage("所有武功已满级")

    # ========== 关系操作 ==========

    def refresh_relations(self):
        if not self.current_hero:
            return
        hero = self.current_hero
        self.friends_list.clear()
        for fid in hero.get('Friends', []):
            for h in self.data:
                if h and h.get('heroID') == fid:
                    self.friends_list.addItem(h.get('heroName', f'ID:{fid}'))
                    break
        self.haters_list.clear()
        for fid in hero.get('Haters', []):
            for h in self.data:
                if h and h.get('heroID') == fid:
                    self.haters_list.addItem(h.get('heroName', f'ID:{fid}'))
                    break
        self.students_list.clear()
        for fid in hero.get('Students', []):
            for h in self.data:
                if h and h.get('heroID') == fid:
                    self.students_list.addItem(h.get('heroName', f'ID:{fid}'))
                    break

    # ========== 快捷操作 ==========

    def max_all_attrs(self):
        if not self.current_hero:
            return
        max_all_attrs(self.current_hero, 999)
        self.load_hero_data()
        self.modified = True
        self.status_bar.showMessage("所有属性已满")

    def heal_hero(self):
        if not self.current_hero:
            return
        heal_hero(self.current_hero)
        self.load_hero_data()
        self.modified = True
        self.status_bar.showMessage("角色已治愈")

    def revive_hero(self):
        if not self.current_hero:
            return
        revive_hero(self.current_hero)
        self.load_hero_data()
        self.modified = True
        self.status_bar.showMessage("角色已复活")

    def max_money(self):
        if not self.current_hero:
            return
        modify_money(self.current_hero, 999999)
        self.load_hero_data()
        self.modified = True
        self.status_bar.showMessage("金钱已满")

    def max_fame(self):
        if not self.current_hero:
            return
        modify_fame(self.current_hero, 99999, 0)
        self.load_hero_data()
        self.modified = True
        self.status_bar.showMessage("声望已满")

    # ========== 批量操作 ==========

    def batch_max_attrs(self):
        if QMessageBox.question(self, "确认", "确定将所有角色属性设为999吗?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            for hero in self.data:
                if hero:
                    max_all_attrs(hero, 999)
            self.load_hero_data()
            self.modified = True
            self.status_bar.showMessage("所有角色属性已满")

    def batch_max_skills(self):
        if QMessageBox.question(self, "确认", "确定将所有角色武功设为满级吗?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            for hero in self.data:
                if hero:
                    all_skills_max(hero)
            self.refresh_skill_table()
            self.modified = True
            self.status_bar.showMessage("所有角色武功已满级")

    def batch_heal(self):
        for hero in self.data:
            if hero and not hero.get('dead'):
                heal_hero(hero)
        self.load_hero_data()
        self.modified = True
        self.status_bar.showMessage("所有角色已治愈")

    def batch_revive(self):
        count = 0
        for hero in self.data:
            if hero and hero.get('dead'):
                revive_hero(hero)
                count += 1
        self.refresh_character_list()
        self.load_hero_data()
        self.modified = True
        self.status_bar.showMessage(f"已复活 {count} 个角色")

    def closeEvent(self, event):
        if self.modified:
            if QMessageBox.question(self, "确认退出", "有未保存的修改，确定要退出吗?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No:
                event.ignore()
                return
        event.accept()


def main():
    app = QApplication(sys.argv)
    font = QFont()
    font.setFamily("Microsoft YaHei, PingFang SC, sans-serif")
    font.setPointSize(13)
    app.setFont(font)
    window = SaveEditorWindow()
    window.show()
    
    # 尝试自动加载存档
    app_dir = get_app_dir()
    
    # 优先检查 real/Save/SaveSlot0/Hero
    hero_path = app_dir / 'real' / 'Save' / 'SaveSlot0' / 'Hero'
    if not hero_path.exists():
        # 其次检查 Hero
        hero_path = app_dir / 'Hero'
    
    if hero_path.exists():
        window.load_file(str(hero_path))
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()