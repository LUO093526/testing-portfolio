# 第3周 Day2 — parametrize参数化

> 📅 2026年6月16日（周二） | ⏱️ 约1.5小时 | commit `acc5f72`

## 核心知识点

### `@pytest.mark.parametrize` 语法
```python
@pytest.mark.parametrize("参数名1,参数名2", [
    pytest.param(值1, 值2, id="用例名"),
    ...
])
def test_xxx(param1, param2):
    ...
```

**关键理解：**
- 一组数据 → 自动生成一条独立测试用例
- `pytest -v` 输出中每条 parametrize 组合都显示为独立一行
- 一条失败不阻塞其他条（不像 for 循环第一条失败就全停）
- `pytest.param(..., id="名称")` 给每条用例起可读名字

### parametrize vs for 循环

| | parametrize | for 循环 |
|---|---|---|
| 失败隔离 | ✅ 一条失败其他继续 | ❌ 第一条失败全停 |
| 可读性 | ✅ `-v` 显示每条名字 | ❌ 不知道哪个数据失败 |
| 选择性执行 | ✅ `-k "关键词"` 筛选 | ❌ 只能全跑 |
| 报告统计 | ✅ 每条独立计数 | ❌ 只算一条 |

## 实战产出

### 1. 登录接口 parametrize（10组）
- 正常登录 ×3: admin/testuser/zhangsan
- 密码错误 ×3: wrongpass/空密码/跨用户密码
- 空值 ×2: 空用户名/空请求体
- 安全测试 ×2: XSS用户名/SQL注入式密码

### 2. 注册接口 parametrize（10组）
- 正常注册 ×3: 完整字段/仅必填/满分
- 必填缺失 ×2: 缺name/缺grade
- 边界值 ×3: score=0/score=-1/score=999999
- 特殊场景 ×2: name空字符串/name超长100字

### 3. 进阶：叠加 parametrize（6条）
- 2个用户名 × 3种密码 = 笛卡尔积自动生成6条

### 4. parametrize + fixture 组合（2条）
- 有效token / 无效token 配合 token_per_function fixture

**总计：28条新用例，全部PASSED ✅**

## 面试映射

| 你做的事 | 面试对应 |
|---------|---------|
| 登录10组+注册10组 parametrize | "你怎么避免写重复用例？" → 参数化 |
| 叠加 parametrize 笛卡尔积 | "多条件组合怎么高效覆盖？" |
| parametrize + fixture 协作 | "参数化和fixture怎么配合？" |
| 用 id 参数命名每条用例 | "用例多了怎么管理可读性？" |

## 还模糊的地方
- ~~叠加 parametrize 的笛卡尔积会不会爆炸？~~ 已理解：只适合2-3个维度各2-3个值，多了用正交法
- conftest 里能不能放 parametrize 数据？→ 明天 Day3 重构时可以试

## 下一步
- Day3（6/17 周三）：conftest.py 重构 — 公共逻辑抽离、依赖链
