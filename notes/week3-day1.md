# 第3周 Day1 — fixture高级用法

> 📅 2026年6月15日（周一） | ⏱️ 约1.5小时 | commit `64e601b`

## 核心知识点

### Fixture 四种 Scope

| Scope | 创建时机 | 销毁时机 | 适用场景 |
|-------|---------|---------|---------|
| `function` | 每个测试函数前 | 测试函数结束后 | 需要严格隔离（默认） |
| `class` | 测试类第一个方法前 | 类最后一个方法后 | 类内共享登录态 |
| `module` | 模块第一个测试前 | 模块最后一个测试后 | 文件内共享昂贵资源 |
| `session` | 整个测试会话开始 | 所有测试结束后 | 全局配置、连接池 |

**关键规则：** 宽 scope 只能用更宽 scope 的 fixture。比如 session scope 的 fixture 不能依赖 function scope 的 fixture（否则报 `ScopeMismatch`）。

### yield / teardown 机制

```python
@pytest.fixture
def my_fixture():
    # === setup === (yield 之前)
    resource = create_resource()
    yield resource
    # === teardown === (yield 之后)
    resource.cleanup()
```

**核心理解：**
- `yield` 之前的代码 = setup（准备环境）
- `yield` 之后 = teardown（清理环境，即使测试失败也会执行）
- `yield` 的值传给测试函数使用

### Fixture 依赖链

```
api_session (session) → api_client (function) → token_per_function (function) → auth_headers (function)
                                                    ↓
                                              token_session (session) → auth_headers_session (session)
```

pytest 自动解析依赖：测试函数声明了 `auth_headers`，pytest 会自动先执行 `api_session` → `api_client` → `token_per_function` → 最后才是 `auth_headers`。

## 实战产出

### 1. API 端点新增（api/app.py）
- `POST /api/login` — 用户登录，返回 SHA256 token
- `GET /api/me` — 验证 token 有效性
- `POST /api/logout` — 注销 token

### 2. conftest.py 重构
- `token_per_function`（scope=function）— 每个测试独立登录+自动注销
- `token_per_class`（scope=class）— 类内共享
- `token_per_module`（scope=module）— 文件内共享
- `token_session`（scope=session）— 全局复用
- `auth_headers` / `auth_headers_session` — 依赖链封装

### 3. 测试验证（test_fixture_scope.py，13条）
- TestTokenFunctionScope：验证 function scope 隔离性
- TestTokenSessionScope：验证 session scope 复用
- TestFixtureDependencyChain：验证依赖链自动解析
- TestScopePerformance：function vs session 性能对比
- TestClassScopeToken：class scope 共享验证

**全部13条 PASSED ✅**

## 遇到的坑

### ScopeMismatch 错误
**问题：** `token_per_class` 最初用了 `api_client`（function scope），pytest 报错 `ScopeMismatch: you tried to access the function scoped fixture api_client from a class scoped request object`

**解决：** class/module/session scope 的 fixture 不能依赖 function scope 的 fixture。改为直接使用 `api_session`（session scope）+ `base_url`（session scope）。

**教训：** 设计 fixture 依赖链时，scope 只能同级或更宽，不能反过来。

## 面试映射

| 你做的事 | 面试对应 |
|---------|---------|
| fixture 4种 scope | "pytest的fixture有哪几种scope？你项目中怎么用的？" |
| yield teardown | "测试完成后怎么清理数据？" |
| fixture 依赖链 | "多个fixture之间有依赖关系怎么处理？" |
| ScopeMismatch | "遇到过pytest的ScopeMismatch吗？怎么解决的？" ← 加分项 |

## 下一步
- Day2（6/16 周二）：parametrize参数化 — 数据驱动、批量测试数据
