# API 测试用例总表

> 基础：20条 → 当前：30条 | 更新时间：2026-06-11

---

## 一、健康检查（1条）

| ID | 用例 | 方法 | 分类 |
|----|------|------|------|
| 1 | test_health_returns_200 | 冒烟 | — |

---

## 二、列表查询（6条）

| ID | 用例 | 参数 | 预期 | 分类 |
|----|------|------|------|------|
| 2 | test_list_returns_200_and_data | 无 | 200, 返回count+data | 正常流程 |
| 3 | test_filter_by_name | ?name=张 | 200, 每条name含"张" | 等价类-有效 |
| 4 | test_filter_by_grade | ?grade=2025 | 200, 每条grade=2025 | 等价类-有效 |
| 5 | test_filter_by_name_and_grade | ?name=张&grade=2026 | 200, 两条件同时满足 | **正交法** |
| 6 | test_filter_by_empty_name | ?name= | 200, 返回全部 | 边界值 |
| 7 | test_filter_nonexistent_grade | ?grade=9999 | 200, count=0 | 等价类-无效 |

---

## 三、新增学生（11条）

| ID | 用例 | 关键参数 | 预期 | 分类 |
|----|------|---------|------|------|
| 8 | test_create_success | 正常三字段 | 201 | 正常流程 |
| 9 | test_create_missing_name | 缺name | 400 | 等价类-无效 |
| 10 | test_create_empty_body | 空body | 400 | 等价类-无效 |
| 11 | test_create_negative_grade | grade=-1 | 201, 接受 | 边界值 |
| 12 | test_create_negative_score | score=-100 | 201, 接受 | 边界值 |
| 13 | test_create_empty_name | name="" | 201, 接受 | 边界值 |
| 14 | test_create_long_name | name=100字 | 201, 接受 | 边界值 |
| 15 | test_create_huge_score | score=999999 | 201, 接受 | 边界值 |
| 16 | test_create_name_spaces | name="   " | 201, 接受 | 边界值 |
| 17 | test_create_score_string | score="abc" | 201, 接受（⚠️不推荐） | 等价类-无效 |
| 18 | test_create_grade_empty | grade="" | 201, 接受 | 边界值 |

---

## 四、查询/更新/删除（8条）

| ID | 用例 | 关键参数 | 预期 | 分类 |
|----|------|---------|------|------|
| 19 | test_get_existing | 存在的id | 200 | 正常流程 |
| 20 | test_get_nonexistent | id=99999 | 404 | 等价类-无效 |
| 21 | test_update_success | score=100 | 200 | 正常流程 |
| 22 | test_update_nonexistent | id=99999 | 404 | 等价类-无效 |
| 23 | test_update_empty_body | 空body | 400 | 等价类-无效 |
| 24 | test_update_score_string | score="not_a_number" | 200（⚠️不推荐） | 等价类-无效 |
| 25 | test_delete_success | 先建后删 | 200→404 | 正常流程 |
| 26 | test_delete_nonexistent | id=99999 | 404 | 等价类-无效 |

---

## 五、数据验证与并发（4条）

| ID | 用例 | 关键参数 | 预期 | 分类 |
|----|------|---------|------|------|
| 27 | test_score_default_zero | 不传score | 201, score=0 | 边界值 |
| 28 | test_special_characters_in_name | XSS脚本 | 201, 接受 | 边界值 |
| 29 | test_name_numbers_only | name="12345" | 201, 接受 | 边界值 |
| 30 | test_rapid_create_delete | 10次连续增删 | 全部200/201 | 并发 |

---

## 六、设计方法覆盖统计

| 方法 | 用例数 | 占比 |
|------|--------|------|
| 正常流程 | 5 | 17% |
| 等价类-有效 | 2 | 7% |
| 等价类-无效 | 10 | 33% |
| 边界值 | 10 | 33% |
| 正交法 | 1 | 3% |
| 冒烟 | 1 | 3% |
| 并发 | 1 | 3% |
| **合计** | **30** | 100% |
