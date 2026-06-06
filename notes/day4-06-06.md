# 第1周第4天：pytest标记和HTML报告

日期：2026-06-06（周六）

## 今天学的

### 1. pytest mark 标记系统
给用例打上标签，可以按需筛选运行。

**5种标记：**
| 标记 | 数量 | 用途 |
|------|------|------|
| `smoke` 🏭 | 4条 | 冒烟 — 核心功能是否可用 |
| `crud` 🔄 | 8条 | 增删改查完整流程 |
| `exception` ⚠️ | 6条 | 异常输入处理（面试必问） |
| `boundary` 📏 | 4条 | 边界值测试 |
| `slow` 🐢 | 1条 | 耗时测试，可跳过 |

### 2. 标记注册
自定义标记必须在 `pytest.ini` 注册，否则会 `PytestUnknownMarkWarning`：
```ini
[pytest]
markers =
    smoke: 冒烟测试
    exception: 异常输入测试
```

### 3. `pytest -m` 筛选
```bash
pytest -m smoke            # 只跑冒烟
pytest -m "not slow"       # 跳过慢测试
pytest -m "smoke or crud"  # 冒烟 + CRUD（逻辑运算）
```

### 4. HTML 报告
```bash
pytest --html=reports/report.html --self-contained-html
```
- `--self-contained-html` = 单个文件，方便分享
- 报告含：总览、每条用例结果、耗时、环境信息

## 踩坑记录
- `pytest.ini` 里 `excepton` 拼错 → 应该是 `exception`
- `@pytest.mark.boudary` 拼错 → 应该是 `boundary`
- mark 必须在 pytest.ini 注册，否则 pytest 9.x 会告警

## 今日达标检查
- [x] 每条用例有合适的标记（smoke/crud/exception/boundary/slow）
- [x] 能说出5种标记的用途
- [x] 会用 `pytest -m smoke` 精确筛选
- [x] 能生成 `reports/report.html`
- [x] git commit

## 面试准备
```
"你怎么管理上百条用例？"
→ 用 pytest.mark 分类标记，smoke/regression/slow 分层跑

"CI里为什么不全跑？"
→ smoke先跑核心，full regression定时跑
```
