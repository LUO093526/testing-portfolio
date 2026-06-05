# 第3天（6月5日）— 新增第一批用例

## 学到的东西

### 1. 今天写了什么

从 16 条用例扩充到 20 条，新增 4 条 + 补了 1 条遗漏：

| # | 用例 | 类型 | 输入 | 预期 | 实际结果 |
|---|------|------|------|------|---------|
| 1 | `test_create_empty_body` | 🔴 异常 | POST 不带 body | 400 | ✅ 400 |
| 2 | `test_create_empty_name` | 🟡 边界 | name="" | 201？400？ | ⚠️ 201，空名合法 |
| 3 | `test_create_negative_grade` | 🟡 边界 | grade="-1" | 201？400？ | ⚠️ 201，负年级合法 |
| 4 | `test_create_negative_score` | 🟡 边界 | score=-100 | 201？400？ | ⚠️ 201，负分合法 |
| 5 | `test_delete_nonexistent` | 🔴 异常 | DELETE 不存在ID | 404 | ✅ 404 |

### 2. 核心发现：API 的"两档校验"

写完这 4 条后发现了 API 的校验逻辑规律：

| 校验级别 | 检查什么 | 不检查什么 |
|---------|---------|-----------|
| **字段存在性** ✅ | name 字段在不在 JSON 里 | name 有没有意义 |
| **业务合法性** ❌ | — | 负数、空字符串、超长、XSS |

**结论**：这个 API 只做了"字段级校验"，没做"业务级校验"。真实项目里两种都要有，不然数据库会进脏数据。

> 🔑 **面试价值**：被问到"你发现过什么 bug"，可以直接说"API 接受了负数成绩和空姓名，属于缺少业务校验"。

### 3. 四个新用例的技术细节

#### 3.1 空 body（test_create_empty_body）

```python
r = requests.post(f"{BASE_URL}/api/students")  # 不传 json=
assert r.status_code == 400
```

**和 `test_create_missing_name` 的区别**：
- `missing_name`：传了 JSON 但缺少 name 字段 → 400
- `empty_body`：完全不传 JSON body → 400
- 两者报错原因不同，一个是"缺字段"，一个是"没 body"，要分别测

#### 3.2 空 name（test_create_empty_name）

```python
json={"name": "", "grade": "2026", "score": 80}
# 结果：201 Created，name="" 被原样存入
```

**意外发现**：`name=""` 和"不传 name"是两回事！
- 不传 → `missing_name` → 400（字段不存在）
- 传空串 → `empty_name` → 201（字段存在，值是空串）

这就是**等价类**的典型应用：同一个字段，不同的"空"也是不同的等价类。

#### 3.3 负数边界（grade / score）

```python
# grade 负数
json={"name": "测试", "grade": "-1", "score": 80}
# → 201 Created，grade="-1" 存入

# score 负数
json={"name": "测试", "grade": "2026", "score": -100}
# → 201 Created，score=-100 存入
```

**为什么不报错？** API 代码里 grade 和 score 是字符串/整数直接接收，没有写 `if score < 0: return 400`。这不一定是 bug（可能业务上允许负数），但作为测试工程师要**记录这个行为**，让产品和开发确认。

> 💡 真实工作里，这种"不确定是不是 bug"的行为要提 Bug Report 让 PM 决策，而不是自己假设。

#### 3.4 重复删除（test_delete_nonexistent）

```python
r = requests.delete(f"{BASE_URL}/api/students/99999")
assert r.status_code == 404
```

**测的是什么**：幂等性——同一个操作做两次，结果应该一致。
- 第一次删 → 200（或 204）
- 第二次删同一个 → 应该还是 404，而不是 500 崩溃

### 4. 测试数据清理的好习惯

今天写的用例里，`test_create_negative_grade` / `test_create_negative_score` / `test_create_empty_name` 都在最后做了清理：

```python
sid = r.json()["data"]["id"]
requests.delete(f"{BASE_URL}/api/students/{sid}")  # 用完就删
```

**为什么重要**：
- 测试用例不应该互相影响
- 这次测试创建的学生，下次跑还在数据库里，可能影响其他用例
- 真实项目里每个测试跑完要"恢复原状"

> 更好的做法是用 fixture 的 yield 后置清理，这次先记下，后面会学到。

---

## 今日过关检查

- [x] 自己写出了至少 2 条新用例（不是照抄的）
  - test_create_empty_body — 自己想的"完全不给 body"
  - test_create_empty_name — 自己想的"给字段但给空值"
  - test_create_negative_grade — 边界值负数场景
  - test_create_negative_score — 同上，score 维度
- [x] 20 条全部 PASSED
- [x] 有一条自己写的 commit message
  - `feat: API测试 16→20条，覆盖负数边界/空body/空name`
- [x] 知道 `git add .` 是干什么的
  - 把当前目录所有修改加入暂存区，`git commit` 只提交暂存区里的内容

---

## 今日总结

| 维度 | 收获 |
|------|------|
| 写用例 | 能独立写出异常输入、边界值、重复操作三类用例 |
| 发现能力 | 发现 API 不做业务校验（负数/空串直接入库） |
| 测试思维 | 理解"字段存在性校验"和"业务合法性校验"是两层 |
| 工程习惯 | 测试数据用完要清理，不给下次运行留坑 |
| Git | 提交信息写清楚"从哪到哪 + 覆盖了什么场景" |

---

## 明天（第4天）预告

> pytest mark 标记深入 + `pytest -m` 筛选运行 + HTML 测试报告
