# 第3周 Day1：Fixture 高级用法 — Scope & Yield

> 日期：2026-06-15 | 第3周第1天

---

## 一、四种 Scope 对比

| Scope | 创建时机 | 销毁时机 | 适用场景 |
|-------|---------|---------|---------|
| `function` | 每个测试函数前 | 测试函数结束后 | 需要严格隔离的数据（如：每个测试独立登录） |
| `class` | 测试类第一个方法前 | 类最后一个方法后 | 类内测试共享状态 |
| `module` | .py 文件第一个测试前 | 文件最后一个测试后 | 同一文件的测试共享连接 |
| `session` | pytest 运行开始时 | pytest 结束退出时 | 全局配置、数据库连接池等不变资源 |

### 选 scope 的决策规则

```
隔离性：function > class > module > session
性能：  session > module > class > function
```

**经验法则：**
- 不需要修改的数据 → `session`
- 每个测试文件共享的连接 → `module`
- 需要 `yield` 清理的资源 → `function`（确保每次清理）

---

## 二、代码实战

### 项目 token 管理（conftest.py）

项目中实现了 **四种 scope** 的登录 token fixture：

```python
# function scope — 每个测试独立登录，隔离性最强
@pytest.fixture(scope="function")
def token_per_function(api_client):
    r = api_client.post("/api/login", json=LOGIN_CREDENTIALS)
    token = r.json()["token"]
    yield token                    # ← 把 token 交给测试
    api_client.post("/api/logout") # ← teardown: 测试结束后注销

# session scope — 全局只登录一次，性能最优
@pytest.fixture(scope="session")
def token_session(api_session, base_url):
    r = api_session.post(f"{base_url}/api/login", json=LOGIN_CREDENTIALS)
    token = r.json()["token"]
    yield token                    # ← setup: 整个会话只执行一次
    api_session.post(f"{base_url}/api/logout") # ← teardown: 全部测试结束后执行
```

### 依赖链演示

```
api_session (session)
    ↓
api_client (function) ──→ token_per_function (function)
    │                           ↓
    │                     auth_headers (function)
    │
    └──→ base_url (session) ──→ token_session (session)
                                     ↓
                               auth_headers_session (session)
```

---

## 三、Yield / Teardown 机制

```
@pytest.fixture
def my_fixture():
    # ── SETUP ──
    resource = create_resource()
    
    yield resource  # ← 把 resource 传给测试函数
    
    # ── TEARDOWN ──
    resource.cleanup()  # 无论测试通过/失败都会执行
```

**关键点：**
1. `yield` 之前的代码 = **setup**（准备资源）
2. `yield` 返回的值 = 测试函数拿到的参数
3. `yield` 之后的代码 = **teardown**（清理资源）
4. 即使测试失败/报错，teardown 也**一定会执行**

**项目中已有的 yield 示例：**
- `api_session`: setup 创建 Session → teardown 关闭连接
- `token_per_function`: setup 登录 → teardown 注销 token
- `sample_student` (test_api.py): setup 创建学生 → teardown 删除学生

---

## 四、关键踩坑：Scope 依赖规则

pytest **不允许**宽 scope 依赖窄 scope：

```python
# ❌ 错误：class scope 的 fixture 不能用 function scope 的 fixture
@pytest.fixture(scope="class")
def token_per_class(api_client):  # api_client 是 function scope → ScopeMismatch!
    ...

# ✅ 正确：用同级别或更宽 scope 的 fixture
@pytest.fixture(scope="class")
def token_per_class(api_session, base_url):  # 都是 session scope → OK
    ...
```

**规则：只能"向上"依赖（窄 → 宽），不能"向下"依赖（宽 → 窄）**

```
function 可以依赖 → class / module / session
class    可以依赖 → module / session
module   可以依赖 → session
session  只能依赖 → session
```

---

## 五、测试验证

运行 `tests/test_fixture_scope.py`（13条新用例）：

```bash
# 看 scope 效果（-s 显示 print 输出）
pytest tests/test_fixture_scope.py -v -s

# 输出示例：
#   🔑 [session] 全局登录（整个会话只执行一次）...
#   🔑 [function] 正在登录...
#   🗑️  [function] 正在注销 token...
#   🗑️  [session] 正在注销全局 token...
```

**验证结论：**
- `token_per_function`：每个测试方法都触发登录+注销 ✅
- `token_session`：整个测试运行只登录一次，最后才注销 ✅
- `token_per_class`：只在类的第一个测试前登录，类结束后注销 ✅
- fixture 依赖链正常工作 ✅

---

## 六、面试映射

| 你做的事 | 面试对应问题 |
|---------|------------|
| 四种 scope token fixture | "pytest fixture 有哪几种 scope？你的项目里怎么选的？" |
| yield teardown 注销 token | "测试完成后怎么清理数据？" |
| fixture 依赖链 | "怎么避免测试数据重复创建？怎么管理 fixture 依赖？" |
| scope 选型决策 | "什么时候用 session scope？有什么风险？" |

---

> 下一篇：Day2 — parametrize 参数化
