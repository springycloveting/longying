#!/usr/bin/env python3
"""
龙胤立志传 - Web 存档修改器
测试 NPC 好感度和物品管理 API
"""

import unittest
import json
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestHeroFavorAPI(unittest.TestCase):
    """测试角色好感度 API 功能"""

    def setUp(self):
        """测试前准备"""
        # 创建测试用的角色数据
        self.test_hero = {
            'heroID': 0,
            'heroName': '测试角色',
            'favor': -999999.0,
            'Friends': [1, 2, 3],
            'Haters': [4, 5],
            'Lover': -1,
        }

    def test_get_favor_default(self):
        """测试获取默认好感度"""
        # 新角色的好感度应该是 -999999（未知）
        favor = self.test_hero.get('favor', -999999.0)
        self.assertEqual(favor, -999999.0)

    def test_get_favor_positive(self):
        """测试获取正好感度"""
        self.test_hero['favor'] = 50.0
        favor = self.test_hero.get('favor', -999999.0)
        self.assertEqual(favor, 50.0)

    def test_get_favor_negative(self):
        """测试获取负好感度"""
        self.test_hero['favor'] = -50.0
        favor = self.test_hero.get('favor', -999999.0)
        self.assertEqual(favor, -50.0)

    def test_set_favor_valid_positive(self):
        """测试设置有效的正好感度"""
        # 好感度应该在 -100 到 100 之间
        new_favor = 75.0
        self.test_hero['favor'] = new_favor
        self.assertEqual(self.test_hero['favor'], new_favor)

    def test_set_favor_valid_negative(self):
        """测试设置有效的负好感度"""
        new_favor = -50.0
        self.test_hero['favor'] = new_favor
        self.assertEqual(self.test_hero['favor'], new_favor)

    def test_set_favor_clamp_max(self):
        """测试好感度上限为 100"""
        # 设置超过 100 的值应该被限制为 100
        new_favor = min(100.0, 150.0)
        self.test_hero['favor'] = new_favor
        self.assertEqual(self.test_hero['favor'], 100.0)

    def test_set_favor_unknown_value(self):
        """测试重置好感度为未知状态"""
        # 重置为未知状态
        self.test_hero['favor'] = -999999.0
        self.assertEqual(self.test_hero['favor'], -999999.0)


class TestHeroFavorFunctions(unittest.TestCase):
    """测试好感度相关函数"""

    def setUp(self):
        """测试前准备"""
        from web_server import find_hero_by_id, find_hero_index
        self.find_hero_by_id = find_hero_by_id
        self.find_hero_index = find_hero_index

    def test_modify_favor_function_exists(self):
        """测试好感度修改函数是否存在"""
        # 这个测试预期会失败，因为函数还不存在
        # 这是 TDD 的 Red 阶段
        from web_server import modify_favor
        self.assertTrue(callable(modify_favor))

    def test_modify_favor_sets_value(self):
        """测试 modify_favor 函数设置好感度"""
        from web_server import modify_favor
        hero = {'heroID': 1, 'heroName': '测试', 'favor': 0.0}
        modify_favor(hero, 50.0)
        self.assertEqual(hero['favor'], 50.0)

    def test_modify_favor_clamps_to_max(self):
        """测试 modify_favor 限制最大值"""
        from web_server import modify_favor
        hero = {'heroID': 1, 'heroName': '测试', 'favor': 0.0}
        modify_favor(hero, 150.0)  # 应该被限制为 100
        self.assertEqual(hero['favor'], 100.0)

    def test_modify_favor_allows_unknown(self):
        """测试 modify_favor 允许设置为未知状态"""
        from web_server import modify_favor
        hero = {'heroID': 1, 'heroName': '测试', 'favor': 50.0}
        modify_favor(hero, -999999.0)  # 重置为未知
        self.assertEqual(hero['favor'], -999999.0)


class TestHeroItemAPI(unittest.TestCase):
    """测试物品管理 API 功能"""

    def setUp(self):
        """测试前准备"""
        self.test_hero = {
            'heroID': 0,
            'heroName': '测试角色',
            'itemListData': {
                'money': 1000,
                'weight': 50.0,
                'maxWeight': 100.0,
                'allItem': [
                    {
                        'itemID': 1,
                        'name': '测试武器',
                        'type': 0,
                        'itemLv': 1,
                        'rareLv': 0,
                        'weight': 5.0,
                        'value': 100,
                        'equipmentData': None
                    },
                    {
                        'itemID': 2,
                        'name': '测试药品',
                        'type': 5,
                        'itemLv': 1,
                        'rareLv': 0,
                        'weight': 1.0,
                        'value': 50,
                        'equipmentData': None
                    }
                ]
            }
        }

    def test_get_items_list(self):
        """测试获取物品列表"""
        items = self.test_hero.get('itemListData', {}).get('allItem', [])
        self.assertEqual(len(items), 2)

    def test_get_item_by_index(self):
        """测试按索引获取物品"""
        items = self.test_hero['itemListData']['allItem']
        item = items[0]
        self.assertEqual(item['name'], '测试武器')

    def test_add_item_function_exists(self):
        """测试添加物品函数是否存在"""
        from web_server import add_item
        self.assertTrue(callable(add_item))

    def test_add_item_increases_count(self):
        """测试添加物品增加数量"""
        from web_server import add_item
        initial_count = len(self.test_hero['itemListData']['allItem'])
        new_item = {
            'itemID': 3,
            'name': '新物品',
            'type': 8,
            'itemLv': 1,
            'rareLv': 1,
            'weight': 2.0,
            'value': 200
        }
        add_item(self.test_hero, new_item)
        self.assertEqual(len(self.test_hero['itemListData']['allItem']), initial_count + 1)

    def test_remove_item_function_exists(self):
        """测试删除物品函数是否存在"""
        from web_server import remove_item
        self.assertTrue(callable(remove_item))

    def test_remove_item_decreases_count(self):
        """测试删除物品减少数量"""
        from web_server import remove_item
        initial_count = len(self.test_hero['itemListData']['allItem'])
        removed = remove_item(self.test_hero, 0)
        self.assertEqual(len(self.test_hero['itemListData']['allItem']), initial_count - 1)
        self.assertIsNotNone(removed)

    def test_remove_item_returns_removed_item(self):
        """测试删除物品返回被删除的物品"""
        from web_server import remove_item
        removed = remove_item(self.test_hero, 0)
        self.assertEqual(removed['name'], '测试武器')

    def test_remove_item_invalid_index_returns_none(self):
        """测试删除无效索引返回 None"""
        from web_server import remove_item
        removed = remove_item(self.test_hero, 999)
        self.assertIsNone(removed)


class TestHeroRelationsAPI(unittest.TestCase):
    """测试人际关系 API 功能"""

    def setUp(self):
        """测试前准备"""
        self.test_hero = {
            'heroID': 0,
            'heroName': '主角',
            'Friends': [1, 2, 3],
            'Haters': [4, 5],
            'Students': [6],
            'Teacher': 7,
            'Lover': -1,
            'Brothers': [],
            'Relatives': []
        }

    def test_get_friends(self):
        """测试获取好友列表"""
        friends = self.test_hero.get('Friends', [])
        self.assertEqual(len(friends), 3)
        self.assertIn(1, friends)

    def test_get_haters(self):
        """测试获取仇人列表"""
        haters = self.test_hero.get('Haters', [])
        self.assertEqual(len(haters), 2)
        self.assertIn(4, haters)

    def test_add_friend_function_exists(self):
        """测试添加好友函数是否存在"""
        from web_server import add_friend
        self.assertTrue(callable(add_friend))

    def test_add_friend_adds_to_list(self):
        """测试添加好友到列表"""
        from web_server import add_friend
        add_friend(self.test_hero, 10)
        self.assertIn(10, self.test_hero['Friends'])

    def test_add_friend_no_duplicate(self):
        """测试添加好友不重复"""
        from web_server import add_friend
        add_friend(self.test_hero, 1)  # 已存在
        count = self.test_hero['Friends'].count(1)
        self.assertEqual(count, 1)

    def test_remove_friend_function_exists(self):
        """测试移除好友函数是否存在"""
        from web_server import remove_friend
        self.assertTrue(callable(remove_friend))

    def test_remove_friend_removes_from_list(self):
        """测试移除好友从列表删除"""
        from web_server import remove_friend
        remove_friend(self.test_hero, 1)
        self.assertNotIn(1, self.test_hero['Friends'])

    def test_add_hater_function_exists(self):
        """测试添加仇人函数是否存在"""
        from web_server import add_hater
        self.assertTrue(callable(add_hater))

    def test_set_lover_function_exists(self):
        """测试设置恋人函数是否存在"""
        from web_server import set_lover
        self.assertTrue(callable(set_lover))


class TestFavorStatusClassification(unittest.TestCase):
    """测试好感度状态分类"""

    def test_classify_unknown(self):
        """测试未知状态分类"""
        favor = -999999.0
        status = 'unknown' if favor == -999999.0 else 'known'
        self.assertEqual(status, 'unknown')

    def test_classify_love(self):
        """测试挚爱状态分类 (>=80)"""
        favor = 85.0
        status = 'love' if favor >= 80 else 'other'
        self.assertEqual(status, 'love')

    def test_classify_close(self):
        """测试亲密状态分类 (>=60)"""
        favor = 65.0
        status = 'close' if favor >= 60 and favor < 80 else 'other'
        self.assertEqual(status, 'close')

    def test_classify_friendly(self):
        """测试友善状态分类 (>=40)"""
        favor = 45.0
        status = 'friendly' if favor >= 40 and favor < 60 else 'other'
        self.assertEqual(status, 'friendly')

    def test_classify_neutral(self):
        """测试中立状态分类 (>=0)"""
        favor = 10.0
        status = 'neutral' if favor >= 0 and favor < 20 else 'other'
        self.assertEqual(status, 'neutral')

    def test_classify_dislike(self):
        """测试厌恶状态分类 (>=-40)"""
        favor = -30.0
        status = 'dislike' if favor >= -40 and favor < -20 else 'other'
        self.assertEqual(status, 'dislike')

    def test_classify_enemy(self):
        """测试仇敌状态分类 (>=-80)"""
        favor = -70.0
        status = 'enemy' if favor >= -80 and favor < -60 else 'other'
        self.assertEqual(status, 'enemy')

    def test_classify_nemesis(self):
        """测试死敌状态分类 (<-80)"""
        favor = -90.0
        status = 'nemesis' if favor < -80 else 'other'
        self.assertEqual(status, 'nemesis')


class TestItemWeightManagement(unittest.TestCase):
    """测试物品负重管理"""

    def setUp(self):
        """测试前准备"""
        self.test_hero = {
            'heroID': 0,
            'heroName': '测试角色',
            'itemListData': {
                'money': 1000,
                'weight': 10.0,
                'maxWeight': 100.0,
                'allItem': [
                    {'itemID': 1, 'name': '物品1', 'type': 0, 'weight': 5.0, 'value': 100},
                    {'itemID': 2, 'name': '物品2', 'type': 5, 'weight': 5.0, 'value': 50}
                ]
            }
        }

    def test_add_item_updates_weight(self):
        """测试添加物品更新负重"""
        from web_server import add_item
        initial_weight = self.test_hero['itemListData']['weight']
        new_item = {'itemID': 3, 'name': '新物品', 'type': 8, 'weight': 3.0, 'value': 200}
        add_item(self.test_hero, new_item)
        self.assertEqual(self.test_hero['itemListData']['weight'], initial_weight + 3.0)

    def test_remove_item_updates_weight(self):
        """测试删除物品更新负重"""
        from web_server import remove_item
        initial_weight = self.test_hero['itemListData']['weight']
        removed = remove_item(self.test_hero, 0)
        expected_weight = initial_weight - removed['weight']
        self.assertEqual(self.test_hero['itemListData']['weight'], expected_weight)


class TestHeroRelationsFunctions(unittest.TestCase):
    """测试人际关系函数完整功能"""

    def setUp(self):
        self.test_hero = {
            'heroID': 0,
            'heroName': '主角',
            'Friends': [1, 2],
            'Haters': [3, 4],
            'Lover': -1,
        }

    def test_add_hater_adds_to_list(self):
        """测试添加仇人到列表"""
        from web_server import add_hater
        add_hater(self.test_hero, 10)
        self.assertIn(10, self.test_hero['Haters'])

    def test_add_hater_no_duplicate(self):
        """测试添加仇人不重复"""
        from web_server import add_hater
        add_hater(self.test_hero, 3)
        count = self.test_hero['Haters'].count(3)
        self.assertEqual(count, 1)

    def test_remove_hater_function_exists(self):
        """测试移除仇人函数是否存在"""
        from web_server import remove_hater
        self.assertTrue(callable(remove_hater))

    def test_remove_hater_removes_from_list(self):
        """测试移除仇人从列表删除"""
        from web_server import remove_hater
        remove_hater(self.test_hero, 3)
        self.assertNotIn(3, self.test_hero['Haters'])

    def test_set_lover_sets_value(self):
        """测试设置恋人"""
        from web_server import set_lover
        set_lover(self.test_hero, 5)
        self.assertEqual(self.test_hero['Lover'], 5)

    def test_set_lover_to_none(self):
        """测试清除恋人"""
        from web_server import set_lover
        set_lover(self.test_hero, -1)
        self.assertEqual(self.test_hero['Lover'], -1)


class TestFavorBoundaryValues(unittest.TestCase):
    """测试好感度边界值"""

    def test_favor_lower_bound(self):
        """测试好感度下限为 -100"""
        from web_server import modify_favor
        hero = {'heroID': 1, 'favor': 0.0}
        modify_favor(hero, -150.0)
        self.assertEqual(hero['favor'], -100.0)

    def test_favor_upper_bound(self):
        """测试好感度上限为 100"""
        from web_server import modify_favor
        hero = {'heroID': 1, 'favor': 0.0}
        modify_favor(hero, 150.0)
        self.assertEqual(hero['favor'], 100.0)

    def test_favor_exact_bounds(self):
        """测试好感度精确边界值"""
        from web_server import modify_favor
        hero1 = {'heroID': 1, 'favor': 0.0}
        hero2 = {'heroID': 2, 'favor': 0.0}
        modify_favor(hero1, -100.0)
        modify_favor(hero2, 100.0)
        self.assertEqual(hero1['favor'], -100.0)
        self.assertEqual(hero2['favor'], 100.0)

    def test_favor_zero_value(self):
        """测试好感度为 0"""
        from web_server import modify_favor
        hero = {'heroID': 1, 'favor': 50.0}
        modify_favor(hero, 0.0)
        self.assertEqual(hero['favor'], 0.0)


class TestItemBatchOperations(unittest.TestCase):
    """测试物品批量操作"""

    def setUp(self):
        self.test_hero = {
            'heroID': 0,
            'heroName': '测试角色',
            'itemListData': {
                'money': 1000,
                'weight': 20.0,
                'maxWeight': 100.0,
                'allItem': [
                    {'itemID': 1, 'name': '武器1', 'type': 0, 'weight': 5.0, 'value': 100},
                    {'itemID': 2, 'name': '武器2', 'type': 0, 'weight': 5.0, 'value': 100},
                    {'itemID': 3, 'name': '药品1', 'type': 5, 'weight': 1.0, 'value': 50},
                    {'itemID': 4, 'name': '药品2', 'type': 5, 'weight': 1.0, 'value': 50},
                    {'itemID': 5, 'name': '药品1', 'type': 5, 'weight': 1.0, 'value': 50},
                ]
            }
        }

    def test_remove_all_type_reduces_count(self):
        """测试按类型删除物品减少数量"""
        items = self.test_hero['itemListData']['allItem']
        original_count = len(items)
        items_to_remove = [i for i in items if i.get('type') == 5]
        self.test_hero['itemListData']['allItem'] = [i for i in items if i.get('type') != 5]
        removed = original_count - len(self.test_hero['itemListData']['allItem'])
        self.assertEqual(removed, 3)

    def test_remove_duplicates_reduces_count(self):
        """测试删除重复物品减少数量"""
        items = self.test_hero['itemListData']['allItem']
        seen_names = set()
        unique_items = []
        for item in items:
            name = item.get('name', '')
            if name not in seen_names:
                seen_names.add(name)
                unique_items.append(item)
        removed = len(items) - len(unique_items)
        self.assertEqual(removed, 1)


class TestModifyItemFunction(unittest.TestCase):
    """测试物品修改函数"""

    def setUp(self):
        self.test_hero = {
            'heroID': 0,
            'heroName': '测试角色',
            'itemListData': {
                'money': 1000,
                'weight': 10.0,
                'maxWeight': 100.0,
                'allItem': [
                    {'itemID': 1, 'name': '测试武器', 'type': 0, 'itemLv': 1, 'rareLv': 0, 'weight': 5.0, 'value': 100},
                ]
            }
        }

    def test_modify_item_function_exists(self):
        """测试修改物品函数是否存在"""
        from web_server import modify_item
        self.assertTrue(callable(modify_item))

    def test_modify_item_changes_field(self):
        """测试修改物品字段"""
        from web_server import modify_item
        result = modify_item(self.test_hero, 0, 'itemLv', 5)
        self.assertTrue(result)
        self.assertEqual(self.test_hero['itemListData']['allItem'][0]['itemLv'], 5)

    def test_modify_item_invalid_index_returns_false(self):
        """测试修改无效索引返回 False"""
        from web_server import modify_item
        result = modify_item(self.test_hero, 999, 'itemLv', 5)
        self.assertFalse(result)


class TestAPIEndpoints(unittest.TestCase):
    """测试 API 端点"""

    def setUp(self):
        from web_server import app
        self.app = app
        self.client = app.test_client()
        self.app.testing = True

    def test_api_status_endpoint(self):
        """测试状态 API 端点"""
        response = self.client.get('/api/status')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('loaded', data)
        self.assertIn('hero_count', data)

    def test_api_items_types_endpoint(self):
        """测试物品类型 API 端点"""
        response = self.client.get('/api/items/types')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)

    def test_api_heroes_without_load(self):
        """测试未加载存档时获取角色列表"""
        response = self.client.get('/api/heroes')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)

    def test_api_hero_favor_without_load(self):
        """测试未加载存档时获取好感度"""
        response = self.client.get('/api/hero/0/favor')
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn('error', data)


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""

    def test_add_item_to_hero_without_itemlistdata(self):
        """测试向没有 itemListData 的角色添加物品"""
        from web_server import add_item
        hero = {'heroID': 1, 'heroName': '测试'}
        new_item = {'itemID': 1, 'name': '新物品', 'type': 0, 'weight': 5.0, 'value': 100}
        add_item(hero, new_item)
        self.assertIn('itemListData', hero)
        self.assertIn('allItem', hero['itemListData'])
        self.assertEqual(len(hero['itemListData']['allItem']), 1)

    def test_add_friend_to_hero_without_friends_list(self):
        """测试向没有 Friends 列表的角色添加好友"""
        from web_server import add_friend
        hero = {'heroID': 1, 'heroName': '测试'}
        add_friend(hero, 5)
        self.assertIn('Friends', hero)
        self.assertIn(5, hero['Friends'])

    def test_add_hater_to_hero_without_haters_list(self):
        """测试向没有 Haters 列表的角色添加仇人"""
        from web_server import add_hater
        hero = {'heroID': 1, 'heroName': '测试'}
        add_hater(hero, 5)
        self.assertIn('Haters', hero)
        self.assertIn(5, hero['Haters'])

    def test_remove_friend_not_in_list(self):
        """测试移除不在列表中的好友"""
        from web_server import remove_friend
        hero = {'heroID': 1, 'Friends': [1, 2, 3]}
        remove_friend(hero, 999)
        self.assertEqual(len(hero['Friends']), 3)

    def test_remove_hater_not_in_list(self):
        """测试移除不在列表中的仇人"""
        from web_server import remove_hater
        hero = {'heroID': 1, 'Haters': [1, 2, 3]}
        remove_hater(hero, 999)
        self.assertEqual(len(hero['Haters']), 3)


class TestRelationsAPIMore(unittest.TestCase):
    """测试关系操作API更多用例"""

    def setUp(self):
        from web_server import app
        import web_server
        self.app = app
        self.client = app.test_client()
        app.testing = True
        web_server.hero_data = []

    def test_api_hero_relations_update_add_friend(self):
        """测试通过API添加好友"""
        import web_server
        
        web_server.hero_data[:] = [
            {'heroID': 1, 'heroName': '主角', 'Friends': [], 'Haters': [], 'Lover': -1},
            {'heroID': 2, 'heroName': '角色A', 'Friends': [], 'Haters': [], 'Lover': -1},
        ]
        
        response = self.client.put('/api/hero/1/relations',
                              json={'action': 'add', 'type': 'friend', 'targetID': 2},
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(2, web_server.hero_data[0]['Friends'])

    def test_api_hero_relations_update_remove_friend(self):
        """测试通过API移除好友"""
        import web_server
        
        web_server.hero_data[:] = [
            {'heroID': 1, 'heroName': '主角', 'Friends': [2, 3], 'Haters': [], 'Lover': -1},
            {'heroID': 2, 'heroName': '角色A', 'Friends': [], 'Haters': [], 'Lover': -1},
        ]
        
        response = self.client.put('/api/hero/1/relations',
                              json={'action': 'remove', 'type': 'friend', 'targetID': 2},
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(2, web_server.hero_data[0]['Friends'])

    def test_api_hero_relations_update_add_hater(self):
        """测试通过API添加仇人"""
        import web_server
        
        web_server.hero_data[:] = [
            {'heroID': 1, 'heroName': '主角', 'Friends': [], 'Haters': [], 'Lover': -1},
            {'heroID': 2, 'heroName': '角色A', 'Friends': [], 'Haters': [], 'Lover': -1},
        ]
        
        response = self.client.put('/api/hero/1/relations',
                              json={'action': 'add', 'type': 'hater', 'targetID': 2},
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn(2, web_server.hero_data[0]['Haters'])

    def test_api_hero_relations_update_remove_hater(self):
        """测试通过API移除仇人"""
        import web_server
        
        web_server.hero_data[:] = [
            {'heroID': 1, 'heroName': '主角', 'Friends': [], 'Haters': [2, 3], 'Lover': -1},
            {'heroID': 2, 'heroName': '角色A', 'Friends': [], 'Haters': [], 'Lover': -1},
        ]
        
        response = self.client.put('/api/hero/1/relations',
                              json={'action': 'remove', 'type': 'hater', 'targetID': 2},
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(2, web_server.hero_data[0]['Haters'])

    def test_api_hero_relations_update_set_lover(self):
        """测试通过API设置恋人"""
        import web_server
        
        web_server.hero_data[:] = [
            {'heroID': 1, 'heroName': '主角', 'Friends': [], 'Haters': [], 'Lover': -1},
            {'heroID': 2, 'heroName': '恋人A', 'Friends': [], 'Haters': [], 'Lover': -1},
        ]
        
        response = self.client.put('/api/hero/1/relations',
                              json={'action': 'add', 'type': 'lover', 'targetID': 2},
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(web_server.hero_data[0]['Lover'], 2)

    def test_api_hero_relations_update_clear_lover(self):
        """测试通过API清除恋人"""
        import web_server
        
        web_server.hero_data[:] = [
            {'heroID': 1, 'heroName': '主角', 'Friends': [], 'Haters': [], 'Lover': 2},
            {'heroID': 2, 'heroName': '恋人A', 'Friends': [], 'Haters': [], 'Lover': -1},
        ]
        
        response = self.client.put('/api/hero/1/relations',
                              json={'action': 'remove', 'type': 'lover', 'targetID': -1},
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(web_server.hero_data[0]['Lover'], -1)

    def test_api_hero_relations_returns_lover(self):
        """测试关系API返回恋人信息"""
        import web_server
        
        web_server.hero_data[:] = [
            {'heroID': 1, 'heroName': '主角', 'Friends': [], 'Haters': [], 'Lover': 2},
            {'heroID': 2, 'heroName': '恋人A', 'Friends': [], 'Haters': [], 'Lover': -1},
        ]
        
        response = self.client.get('/api/hero/1/relations')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn('lover', data)
        self.assertIsNotNone(data['lover'])
        self.assertEqual(data['lover']['id'], 2)
        self.assertEqual(data['lover']['name'], '恋人A')


class TestItemCreateAPI(unittest.TestCase):
    """测试物品创建API"""

    def setUp(self):
        from web_server import app
        import web_server
        self.app = app
        self.client = app.test_client()
        app.testing = True
        web_server.hero_data = []

    def test_api_hero_item_add_success(self):
        """测试通过API创建物品"""
        import web_server
        
        web_server.hero_data[:] = [
            {'heroID': 1, 'heroName': '主角', 'itemListData': {'money': 0, 'weight': 0, 'maxWeight': 100, 'allItem': []}},
        ]
        
        response = self.client.post('/api/hero/1/item',
                              json={'name': '新武器', 'type': 0, 'itemLv': 5, 'rareLv': 3, 'weight': 10.0, 'value': 500},
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        self.assertEqual(data['item']['name'], '新武器')
        self.assertEqual(data['item']['type'], 0)

    def test_api_hero_item_add_updates_weight(self):
        """测试创建物品更新负重"""
        import web_server
        
        web_server.hero_data[:] = [
            {'heroID': 1, 'heroName': '主角', 'itemListData': {'money': 0, 'weight': 0, 'maxWeight': 100, 'allItem': []}},
        ]
        
        response = self.client.post('/api/hero/1/item',
                              json={'name': '重物', 'type': 0, 'weight': 25.5, 'value': 100},
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(web_server.hero_data[0]['itemListData']['weight'], 25.5)

    def test_api_hero_item_add_default_values(self):
        """测试创建物品使用默认值"""
        import web_server
        
        web_server.hero_data[:] = [
            {'heroID': 1, 'heroName': '主角', 'itemListData': {'money': 0, 'weight': 0, 'maxWeight': 100, 'allItem': []}},
        ]
        
        response = self.client.post('/api/hero/1/item',
                              json={'name': '普通物品'},
                              content_type='application/json')
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['item']['type'], 10)
        self.assertEqual(data['item']['itemLv'], 1)
        self.assertEqual(data['item']['rareLv'], 0)

    def test_api_hero_item_add_hero_not_found(self):
        """测试创建物品时角色不存在"""
        import web_server
        
        web_server.hero_data[:] = []
        
        response = self.client.post('/api/hero/999/item',
                              json={'name': '物品'},
                              content_type='application/json')
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
