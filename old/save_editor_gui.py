#!/usr/bin/env python3
"""
龙胤立志传 - 存档修改器 GUI版
基于 PyQt6，可打包为 EXE
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
    QTabWidget, QSplitter, QListWidget, QListWidgetItem, QGroupBox,
    QGridLayout, QSpinBox, QDoubleSpinBox, QMessageBox, QFileDialog,
    QDialog, QComboBox, QCheckBox, QHeaderView, QFrame, QScrollArea,
    QToolBar, QStatusBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPalette, QAction

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

# Apple 风格颜色
COLORS = {
    'bg': '#f5f5f7',
    'sidebar_bg': '#ffffff',
    'card_bg': '#ffffff',
    'border': '#d2d2d7',
    'text': '#1d1d1f',
    'text_secondary': '#86868b',
    'primary': '#0071e3',
    'success': '#34c759',
    'danger': '#ff3b30',
    'warning': '#ff9500',
    'hp': '#34c759',
    'power': '#0071e3',
    'mana': '#af52de',
}

# ========== 数据加载 ==========

def get_app_dir():
    """获取应用程序目录"""
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent

def load_json_data(filename):
    """加载 JSON 数据文件"""
    app_dir = get_app_dir()
    filepath = app_dir / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

# 加载武功名称
SKILL_NAMES = {}
skill_data = load_json_data('skill_names.json')
for k, v in skill_data.items():
    SKILL_NAMES[int(k)] = v

# 加载属性映射
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

def get_nature_name(nature_id):
    return NATURE_MAP.get(nature_id, f'未知({nature_id})')

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
    # 更新装备索引
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
    def __init__(self, title, color, current, maximum):
        super().__init__()
        self.setFixedHeight(100)
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg']};
                border-radius: 10px;
            }}
            QLabel {{
                border: none;
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 12px; font-weight: 500;")
        layout.addWidget(title_label)

        self.value_label = QLabel(f"{int(current)}")
        self.value_label.setStyleSheet(f"color: {color}; font-size: 28px; font-weight: 700;")
        layout.addWidget(self.value_label)

        edit_layout = QHBoxLayout()
        self.current_spin = QSpinBox()
        self.current_spin.setRange(0, 99999)
        self.current_spin.setValue(int(current))
        self.current_spin.setFixedWidth(70)
        self.current_spin.setStyleSheet(f"background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 4px;")

        self.max_spin = QSpinBox()
        self.max_spin.setRange(0, 99999)
        self.max_spin.setValue(int(maximum))
        self.max_spin.setFixedWidth(70)
        self.max_spin.setStyleSheet(f"background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 4px;")

        edit_layout.addWidget(self.current_spin)
        sep = QLabel("/")
        sep.setStyleSheet(f"color: {COLORS['text_secondary']};")
        edit_layout.addWidget(sep)
        edit_layout.addWidget(self.max_spin)
        edit_layout.addStretch()
        layout.addLayout(edit_layout)

        # 进度条
        bar = QFrame()
        bar.setFixedHeight(4)
        bar.setStyleSheet(f"background: #e5e5ea; border-radius: 2px;")
        fill = QFrame(bar)
        fill.setStyleSheet(f"background: {color}; border-radius: 2px;")
        pct = min(100, int(current / max(maximum, 1) * 100))
        fill.setGeometry(0, 0, int(bar.width() * pct / 100), 4)
        layout.addWidget(bar)

    def get_values(self):
        return self.current_spin.value(), self.max_spin.value()

class AttrEdit(QFrame):
    """属性编辑控件"""
    valueChanged = pyqtSignal()

    def __init__(self, name, value, max_value=None, show_max=False):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background: {COLORS['bg']};
                border-radius: 8px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 10)

        name_label = QLabel(name)
        name_label.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; font-weight: 500;")
        name_label.setFixedWidth(50)
        layout.addWidget(name_label)

        self.spin = QSpinBox()
        self.spin.setRange(0, 9999)
        self.spin.setValue(int(value))
        self.spin.setFixedWidth(60)
        self.spin.setStyleSheet(f"background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 4px; text-align: center;")
        self.spin.valueChanged.connect(self.valueChanged.emit)
        layout.addWidget(self.spin)

        if show_max and max_value is not None:
            sep = QLabel(f"/")
            sep.setStyleSheet(f"color: {COLORS['text_secondary']};")
            layout.addWidget(sep)

            self.max_spin = QSpinBox()
            self.max_spin.setRange(0, 9999)
            self.max_spin.setValue(int(max_value))
            self.max_spin.setFixedWidth(50)
            self.max_spin.setStyleSheet(f"background: white; border: 1px solid {COLORS['border']}; border-radius: 6px; padding: 4px;")
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

        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入武功名称或ID...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 10px 12px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background: white;
                font-size: 14px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
        """)
        self.search_input.textChanged.connect(self.search_skills)
        layout.addWidget(self.search_input)

        # 结果列表
        self.result_list = QListWidget()
        self.result_list.setStyleSheet(f"""
            QListWidget {{
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background: white;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-bottom: 1px solid #f5f5f7;
            }}
            QListWidget::item:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
        """)
        layout.addWidget(self.result_list)

        # 等级选择
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

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(80, 32)
        cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['bg']};
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                color: {COLORS['text']};
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: #e8e8ed;
            }}
        """)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

        add_btn = QPushButton("添加")
        add_btn.setFixedSize(80, 32)
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                border: none;
                border-radius: 8px;
                color: white;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: #0077ed;
            }}
        """)
        add_btn.clicked.connect(self.accept_skill)
        btn_layout.addWidget(add_btn)
        layout.addLayout(btn_layout)

        # 初始加载
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
        self.apply_style()

    def setup_ui(self):
        # 中心部件
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧边栏
        self.setup_sidebar(main_layout)

        # 右侧主区域
        self.setup_main_area(main_layout)

        # 工具栏
        self.setup_toolbar()

        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

    def setup_sidebar(self, parent_layout):
        sidebar = QFrame()
        sidebar.setFixedWidth(260)
        sidebar.setStyleSheet(f"background: {COLORS['sidebar_bg']}; border-right: 1px solid {COLORS['border']};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题
        header = QFrame()
        header.setStyleSheet(f"background: #fafafa; border-bottom: 1px solid {COLORS['border']};")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("角色列表")
        title.setStyleSheet(f"color: {COLORS['text_secondary']}; font-size: 13px; font-weight: 600;")
        header_layout.addWidget(title)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索角色...")
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 12px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background: white;
            }}
            QLineEdit:focus {{
                border-color: {COLORS['primary']};
            }}
        """)
        self.search_input.textChanged.connect(self.filter_characters)
        header_layout.addWidget(self.search_input)
        layout.addWidget(header)

        # 角色列表
        self.char_list = QListWidget()
        self.char_list.setStyleSheet(f"""
            QListWidget {{
                border: none;
                background: white;
            }}
            QListWidget::item {{
                padding: 10px 12px;
                border-bottom: 1px solid #f5f5f7;
            }}
            QListWidget::item:selected {{
                background: {COLORS['primary']};
                color: white;
            }}
            QListWidget::item:hover {{
                background: #f5f5f7;
            }}
            QListWidget::item:selected:hover {{
                background: {COLORS['primary']};
            }}
        """)
        self.char_list.currentRowChanged.connect(self.select_character)
        layout.addWidget(self.char_list)

        parent_layout.addWidget(sidebar)

    def setup_main_area(self, parent_layout):
        main_frame = QFrame()
        main_frame.setStyleSheet(f"background: {COLORS['bg']};")

        layout = QVBoxLayout(main_frame)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 顶部信息栏
        header = QFrame()
        header.setStyleSheet(f"background: white; border-bottom: 1px solid {COLORS['border']};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 12, 20, 12)

        title = QLabel("龙胤立志传 存档修改器")
        title.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COLORS['text']};")
        header_layout.addWidget(title)

        self.current_char_label = QLabel()
        self.current_char_label.setStyleSheet(f"background: {COLORS['bg']}; padding: 6px 14px; border-radius: 20px;")
        header_layout.addWidget(self.current_char_label)
        header_layout.addStretch()

        self.save_btn = QPushButton("保存修改")
        self.save_btn.setFixedSize(90, 32)
        self.save_btn.clicked.connect(self.save_file)
        header_layout.addWidget(self.save_btn)

        layout.addWidget(header)

        # Tab部件
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: none;
                background: {COLORS['bg']};
            }}
            QTabBar::tab {{
                background: white;
                padding: 12px 16px;
                color: {COLORS['text_secondary']};
                border-bottom: 2px solid transparent;
            }}
            QTabBar::tab:selected {{
                color: {COLORS['primary']};
                border-bottom-color: {COLORS['primary']};
            }}
            QTabBar::tab:hover {{
                color: {COLORS['text']};
            }}
        """)

        # 基本属性页
        self.setup_basic_tab()
        # 武功技能页
        self.setup_skills_tab()
        # 物品装备页
        self.setup_items_tab()
        # 人际关系页
        self.setup_relations_tab()
        # 工具页
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

        for text, callback in [
            ("一键全属性满", self.max_all_attrs),
            ("治愈角色", self.heal_hero),
            ("复活角色", self.revive_hero),
            ("金钱满", self.max_money),
            ("声望满", self.max_fame),
        ]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white;
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 10px 16px;
                    color: {COLORS['text']};
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: {COLORS['bg']};
                    border-color: {COLORS['text_secondary']};
                }}
            """)
            btn.clicked.connect(callback)
            quick_layout.addWidget(btn)
        quick_layout.addStretch()

        quick_group.layout().addLayout(quick_layout)
        layout.addWidget(quick_group)

        # 状态
        status_group = self.create_card("状态")
        status_layout = QHBoxLayout()
        status_layout.setSpacing(16)

        self.hp_card = StatusCard("生命", COLORS['hp'], 100, 100)
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
        base_layout.setSpacing(10)

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
        fight_layout.setSpacing(10)

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
        living_layout.setSpacing(10)

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

        # 工具栏
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        self.skill_search = QLineEdit()
        self.skill_search.setPlaceholderText("搜索武功...")
        self.skill_search.setStyleSheet(f"""
            QLineEdit {{
                padding: 8px 12px;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                background: white;
            }}
        """)
        self.skill_search.textChanged.connect(self.filter_skills)
        toolbar_layout.addWidget(self.skill_search)

        add_btn = QPushButton("添加武功")
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }}
        """)
        add_btn.clicked.connect(self.add_skill)
        toolbar_layout.addWidget(add_btn)

        max_btn = QPushButton("全部满级")
        max_btn.setStyleSheet(f"""
            QPushButton {{
                background: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }}
        """)
        max_btn.clicked.connect(self.all_skills_max)
        toolbar_layout.addWidget(max_btn)

        layout.addWidget(toolbar)

        # 武功表格
        self.skill_table = QTableWidget()
        self.skill_table.setColumnCount(6)
        self.skill_table.setHorizontalHeaderLabels(["武功名称", "类型", "等级", "装备", "特殊属性", "操作"])
        self.skill_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.skill_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.skill_table.setShowGrid(False)
        self.skill_table.setStyleSheet(f"""
            QTableWidget {{
                background: white;
                border: 1px solid {COLORS['border']};
                border-radius: 12px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid #f5f5f7;
            }}
            QHeaderView::section {{
                background: #fafafa;
                padding: 10px 12px;
                border: none;
                border-bottom: 1px solid {COLORS['border']};
                color: {COLORS['text_secondary']};
                font-weight: 500;
            }}
        """)
        layout.addWidget(self.skill_table)

        self.tabs.addTab(page, "武功技能")

    def setup_items_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # 装备
        equip_group = self.create_card("装备")
        self.equip_grid = QGridLayout()
        self.equip_grid.setSpacing(10)
        equip_group.layout().addLayout(self.equip_grid)
        layout.addWidget(equip_group)

        # 物品
        items_group = self.create_card("物品栏")
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(4)
        self.items_table.setHorizontalHeaderLabels(["名称", "类型", "等级", "品质"])
        self.items_table.setStyleSheet(f"""
            QTableWidget {{
                background: white;
                border: 1px solid {COLORS['border']};
                border-radius: 8px;
            }}
        """)
        items_group.layout().addWidget(self.items_table)
        layout.addWidget(items_group)

        layout.addStretch()
        self.tabs.addTab(page, "物品装备")

    def setup_relations_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # 好友
        friends_group = self.create_card("好友")
        self.friends_list = QListWidget()
        self.friends_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg']};
                border: none;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 16px;
                margin: 2px;
                border: 1px solid {COLORS['success']};
                color: {COLORS['success']};
            }}
        """)
        friends_group.layout().addWidget(self.friends_list)
        layout.addWidget(friends_group)

        # 仇人
        haters_group = self.create_card("仇人")
        self.haters_list = QListWidget()
        self.haters_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg']};
                border: none;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 16px;
                margin: 2px;
                border: 1px solid {COLORS['danger']};
                color: {COLORS['danger']};
            }}
        """)
        haters_group.layout().addWidget(self.haters_list)
        layout.addWidget(haters_group)

        # 徒弟
        students_group = self.create_card("徒弟")
        self.students_list = QListWidget()
        self.students_list.setStyleSheet(f"""
            QListWidget {{
                background: {COLORS['bg']};
                border: none;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-radius: 16px;
                margin: 2px;
                border: 1px solid {COLORS['primary']};
                color: {COLORS['primary']};
            }}
        """)
        students_group.layout().addWidget(self.students_list)
        layout.addWidget(students_group)

        layout.addStretch()
        self.tabs.addTab(page, "人际关系")

    def setup_tools_tab(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)

        # 批量操作
        batch_group = self.create_card("批量操作")
        batch_layout = QHBoxLayout()

        for text, callback in [
            ("所有角色属性满", self.batch_max_attrs),
            ("所有角色武功满级", self.batch_max_skills),
            ("治愈所有角色", self.batch_heal),
            ("复活所有死亡角色", self.batch_revive),
        ]:
            btn = QPushButton(text)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: white;
                    border: 1px solid {COLORS['border']};
                    border-radius: 8px;
                    padding: 10px 16px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background: {COLORS['bg']};
                }}
            """)
            btn.clicked.connect(callback)
            batch_layout.addWidget(btn)
        batch_layout.addStretch()
        batch_group.layout().addLayout(batch_layout)
        layout.addWidget(batch_group)

        # 存档信息
        info_group = self.create_card("存档信息")
        info_layout = QGridLayout()
        info_layout.setSpacing(10)

        self.info_labels = {}
        for i, (key, label) in enumerate([
            ("version", "存档版本"),
            ("count", "角色总数"),
            ("time", "保存时间"),
        ]):
            lbl = QLabel(f"{label}: -")
            lbl.setStyleSheet(f"color: {COLORS['text']};")
            info_layout.addWidget(lbl, 0, i)
            self.info_labels[key] = lbl

        info_group.layout().addLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        self.tabs.addTab(page, "工具")

    def create_card(self, title):
        """创建卡片组件"""
        group = QFrame()
        group.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 1px solid {COLORS['border']};
            }}
        """)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 15px; font-weight: 600; color: {COLORS['text']};")
        layout.addWidget(title_label)

        return group

    def setup_toolbar(self):
        toolbar = QToolBar()
        toolbar.setStyleSheet(f"""
            QToolBar {{
                background: white;
                border-bottom: 1px solid {COLORS['border']};
                padding: 4px;
            }}
        """)
        self.addToolBar(toolbar)

        open_action = QAction("打开存档", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        backup_action = QAction("备份存档", self)
        backup_action.triggered.connect(self.backup_file)
        toolbar.addAction(backup_action)

    def apply_style(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background: {COLORS['bg']};
            }}
            QPushButton {{
                font-size: 13px;
            }}
            QLabel {{
                font-size: 13px;
            }}
        """)

        # 保存按钮样式
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 8px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                background: #0077ed;
            }}
        """)

    # ========== 文件操作 ==========

    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(
            self, "打开存档文件", str(get_app_dir()), "存档文件 (Hero Hero.*);;所有文件 (*)"
        )
        if filepath:
            self.load_file(filepath)

    def load_file(self, filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            self.data = json.loads(content)

            # 验证数据
            if self.data is None:
                raise ValueError("文件内容为空")
            if not isinstance(self.data, list):
                raise ValueError(f"存档格式错误: 期望数组，得到 {type(self.data).__name__}")
            if len(self.data) == 0:
                raise ValueError("存档中没有角色数据")

            # 检查第一个角色是否有效
            if self.data[0] is None:
                raise ValueError("第一个角色数据无效")

            self.save_path = filepath
            self.refresh_character_list()
            self.status_bar.showMessage(f"已加载: {filepath} (共 {len(self.data)} 个角色)")

        except FileNotFoundError:
            QMessageBox.critical(self, "错误", f"文件不存在: {filepath}")
        except json.JSONDecodeError as e:
            QMessageBox.critical(self, "错误", f"JSON解析失败: {e}")
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

        # 先保存当前角色数据
        self.save_current_hero()

        # 备份
        backup_file(self.save_path)

        # 保存
        with open(self.save_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False)

        self.modified = False
        self.status_bar.showMessage(f"存档已保存: {self.save_path}")
        QMessageBox.information(self, "成功", "存档保存成功!")

    # ========== 角色操作 ==========

    def refresh_character_list(self):
        self.char_list.clear()
        if not self.data:
            return
        for i, hero in enumerate(self.data):
            if hero is None:
                continue
            name = hero.get('heroName', '未知')
            hero_id = hero.get('heroID', '?')
            force = get_force_name(hero.get('belongForceID', -1))

            item = QListWidgetItem(f"{name} (ID:{hero_id}) · {force}")

            if hero.get('dead'):
                item.setForeground(QColor(COLORS['text_secondary']))

            item.setData(Qt.ItemDataRole.UserRole, i)
            self.char_list.addItem(item)

        if self.char_list.count() > 0:
            self.char_list.setCurrentRow(0)

    def filter_characters(self, text):
        for i in range(self.char_list.count()):
            item = self.char_list.item(i)
            visible = text.lower() in item.text().lower()
            item.setHidden(not visible)

    def select_character(self, row):
        if row < 0 or row >= len(self.data):
            return

        # 保存上一个角色
        if self.current_hero:
            self.save_current_hero()

        self.hero_idx = row
        self.current_hero = self.data[row]
        self.load_hero_data()

    def load_hero_data(self):
        """加载角色数据到界面"""
        if not self.current_hero:
            return

        hero = self.current_hero

        # 更新标题
        name = hero.get('heroName', '未知')
        hero_id = hero.get('heroID', '?')
        force = get_force_name(hero.get('belongForceID', -1))
        leader = "掌门" if hero.get('isLeader') else ""
        dead = " [死亡]" if hero.get('dead') else ""

        self.current_char_label.setText(f"当前角色: {name}{dead} | {force}{leader}")

        # 状态
        hp = hero.get('hp', 0)
        maxhp = hero.get('maxhp', 100)
        self.hp_card.current_spin.setValue(int(hp))
        self.hp_card.max_spin.setValue(int(maxhp))

        power = hero.get('power', 0)
        maxPower = hero.get('maxPower', 100)
        self.power_card.current_spin.setValue(int(power))
        self.power_card.max_spin.setValue(int(maxPower))

        mana = hero.get('mana', 0)
        maxMana = hero.get('maxMana', 100)
        self.mana_card.current_spin.setValue(int(mana))
        self.mana_card.max_spin.setValue(int(maxMana))

        # 基础属性
        base_attri = hero.get('baseAttri', [0]*6)
        max_attri = hero.get('maxAttri', [0]*6)
        for i, attr in enumerate(self.base_attrs):
            attr.spin.setValue(int(base_attri[i] if i < len(base_attri) else 0))
            attr.set_max_value(max_attri[i] if i < len(max_attri) else 0)

        # 武学属性
        base_fight = hero.get('baseFightSkill', [0]*9)
        max_fight = hero.get('maxFightSkill', [0]*9)
        for i, attr in enumerate(self.fight_attrs):
            attr.spin.setValue(int(base_fight[i] if i < len(base_fight) else 0))
            attr.set_max_value(max_fight[i] if i < len(max_fight) else 0)

        # 技能属性
        base_living = hero.get('baseLivingSkill', [0]*9)
        max_living = hero.get('maxLivingSkill', [0]*9)
        for i, attr in enumerate(self.living_attrs):
            attr.spin.setValue(int(base_living[i] if i < len(base_living) else 0))
            attr.set_max_value(max_living[i] if i < len(max_living) else 0)

        # 声望金钱
        self.fame_edit.spin.setValue(int(hero.get('fame', 0)))
        self.bad_fame_edit.spin.setValue(int(hero.get('badFame', 0)))
        money = hero.get('itemListData', {}).get('money', 0)
        self.money_edit.spin.setValue(int(money))

        # 武功
        self.refresh_skill_table()

        # 关系
        self.refresh_relations()

        # 存档信息
        self.info_labels['count'].setText(f"角色总数: {len(self.data)}")

    def save_current_hero(self):
        """保存当前界面数据到角色"""
        if not self.current_hero:
            return

        hero = self.current_hero

        # 状态
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

        # 基础属性
        for i, attr in enumerate(self.base_attrs):
            modify_base_attr(hero, i, attr.spin.value())
            if attr.has_max():
                hero['maxAttri'][i] = float(attr.max_spin.value())

        # 武学属性
        for i, attr in enumerate(self.fight_attrs):
            modify_fight_skill(hero, i, attr.spin.value())
            if attr.has_max():
                hero['maxFightSkill'][i] = float(attr.max_spin.value())

        # 技能属性
        for i, attr in enumerate(self.living_attrs):
            modify_living_skill(hero, i, attr.spin.value())
            if attr.has_max():
                hero['maxLivingSkill'][i] = float(attr.max_spin.value())

        # 声望金钱
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

            # 操作按钮
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 4, 4, 4)
            btn_layout.setSpacing(4)

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
            visible = text.lower() in name_item.text().lower()
            self.skill_table.setRowHidden(i, not visible)

    def add_skill(self):
        if not self.current_hero:
            QMessageBox.warning(self, "警告", "请先选择角色")
            return

        dialog = SkillSearchDialog(self)
        if dialog.exec():
            if dialog.selected_skill:
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
        skill_name = get_skill_name(skill.get('skillID'))

        # 简单编辑对话框
        dialog = QDialog(self)
        dialog.setWindowTitle(f"编辑武功 - {skill_name}")
        dialog.setFixedSize(400, 300)

        layout = QVBoxLayout(dialog)

        # 等级
        lv_layout = QHBoxLayout()
        lv_layout.addWidget(QLabel("等级:"))
        lv_spin = QSpinBox()
        lv_spin.setRange(1, 10)
        lv_spin.setValue(skill.get('lv', 1))
        lv_layout.addWidget(lv_spin)
        lv_layout.addStretch()
        layout.addLayout(lv_layout)

        # 伤害加成
        dmg_layout = QHBoxLayout()
        dmg_layout.addWidget(QLabel("伤害加成:"))
        dmg_spin = QDoubleSpinBox()
        dmg_spin.setRange(0, 9999)
        dmg_spin.setValue(skill.get('damageUseSpeAddValue', 0))
        dmg_layout.addWidget(dmg_spin)
        dmg_layout.addStretch()
        layout.addLayout(dmg_layout)

        # 按钮
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
            skill['damageUseSpeAddValue'] = dmg_spin.value()
            self.refresh_skill_table()
            self.modified = True

    def delete_skill(self, idx):
        if not self.current_hero:
            return

        skills = self.current_hero.get('kungfuSkills', [])
        if idx >= len(skills):
            return

        skill_name = get_skill_name(skills[idx].get('skillID'))

        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除【{skill_name}】吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
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

        # 好友
        friends = hero.get('Friends', [])
        self.friends_list.clear()
        for fid in friends:
            for h in self.data:
                if h.get('heroID') == fid:
                    self.friends_list.addItem(h.get('heroName', f'ID:{fid}'))
                    break

        # 仇人
        haters = hero.get('Haters', [])
        self.haters_list.clear()
        for fid in haters:
            for h in self.data:
                if h.get('heroID') == fid:
                    self.haters_list.addItem(h.get('heroName', f'ID:{fid}'))
                    break

        # 徒弟
        students = hero.get('Students', [])
        self.students_list.clear()
        for fid in students:
            for h in self.data:
                if h.get('heroID') == fid:
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
        reply = QMessageBox.question(
            self, "确认",
            "确定将所有角色属性设为999吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for hero in self.data:
                max_all_attrs(hero, 999)
            self.load_hero_data()
            self.modified = True
            self.status_bar.showMessage("所有角色属性已满")

    def batch_max_skills(self):
        reply = QMessageBox.question(
            self, "确认",
            "确定将所有角色武功设为满级吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            for hero in self.data:
                all_skills_max(hero)
            self.refresh_skill_table()
            self.modified = True
            self.status_bar.showMessage("所有角色武功已满级")

    def batch_heal(self):
        for hero in self.data:
            if not hero.get('dead'):
                heal_hero(hero)
        self.load_hero_data()
        self.modified = True
        self.status_bar.showMessage("所有角色已治愈")

    def batch_revive(self):
        count = 0
        for hero in self.data:
            if hero.get('dead'):
                revive_hero(hero)
                count += 1
        self.refresh_character_list()
        self.load_hero_data()
        self.modified = True
        self.status_bar.showMessage(f"已复活 {count} 个角色")

    # ========== 窗口事件 ==========

    def closeEvent(self, event):
        if self.modified:
            reply = QMessageBox.question(
                self, "确认退出",
                "有未保存的修改，确定要退出吗?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        event.accept()


def main():
    app = QApplication(sys.argv)

    # 设置全局字体
    font = QFont()
    font.setFamily("-apple-system, BlinkMacSystemFont, 'SF Pro Display', 'PingFang SC', sans-serif")
    font.setPointSize(13)
    app.setFont(font)

    window = SaveEditorWindow()
    window.show()

    # 尝试自动加载存档
    app_dir = get_app_dir()
    hero_path = app_dir / 'Hero'
    if hero_path.exists():
        window.load_file(str(hero_path))

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
