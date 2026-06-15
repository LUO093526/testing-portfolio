"""
conftest.py — 项目全局测试配置

所有测试文件共享的 fixture、测试数据、前置逻辑统一放在这里。
pytest 会自动发现并加载本文件，无需手动 import。

使用方式：
    测试文件里直接写 fixture 名称作为参数即可，例如:
    def test_login(api_client, valid_user):
        ...

Fixture Scope 说明（第3周）：
    function — 每个测试函数新建一份（默认，隔离性最强）
    class    — 同一个测试类内所有方法共享一份
    module   — 同一个 .py 文件内所有测试共享一份
    session  — 整个 pytest 运行期间只创建一次（性能最优）
"""

import pytest
import requests
import os
import sys
import time

# 确保 api 模块可导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ═══════════════════════════════════════════════════════════
# Flask 应用管理 fixture
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def app():
    """启动 Flask 测试服务器（整个测试会话只启动一次）"""
    from api.app import app as flask_app
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture(scope="session")
def base_url(app):
    """API 基础 URL"""
    return "http://127.0.0.1:5000"


# ═══════════════════════════════════════════════════════════
# API 客户端 fixture（底层 — 被上层 fixture 依赖）
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def api_session():
    """全局 HTTP 会话（复用 TCP 连接，加速测试）

    yield 语法说明（第3周）：
        yield 之前的代码 = setup（创建 session）
        yield 之后的代码 = teardown（关闭 session，释放资源）
    """
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture
def api_client(api_session, base_url):
    """API 客户端（无鉴权）— 每个测试函数独立一份"""
    class ApiClient:
        def __init__(self, session, base):
            self.session = session
            self.base = base

        def get(self, path, **kwargs):
            return self.session.get(f"{self.base}{path}", **kwargs)

        def post(self, path, **kwargs):
            return self.session.post(f"{self.base}{path}", **kwargs)

        def put(self, path, **kwargs):
            return self.session.put(f"{self.base}{path}", **kwargs)

        def delete(self, path, **kwargs):
            return self.session.delete(f"{self.base}{path}", **kwargs)

    return ApiClient(api_session, base_url)


# ═══════════════════════════════════════════════════════════
# 第3周核心：Token 管理 fixture（四种 scope 对比）
# ═══════════════════════════════════════════════════════════

# 登录凭证（硬编码，与 api/app.py 的 VALID_USERS 保持一致）
LOGIN_CREDENTIALS = {"username": "testuser", "password": "test123"}


@pytest.fixture(scope="function")
def token_per_function(api_client):
    """【scope=function】每个测试函数都重新登录，获取新 token

    优点：隔离性最强，一个测试的 token 不会影响另一个
    缺点：每次都发 HTTP 请求，速度慢

    yield 说明：
        yield token      ← 把 token 交给测试函数使用
        /api/logout      ← 测试结束后注销 token（teardown）
    """
    print(f"\n  🔑 [function] 正在登录...")  # pytest -s 可见
    r = api_client.post("/api/login", json=LOGIN_CREDENTIALS)
    assert r.status_code == 200, f"登录失败: {r.json()}"
    token = r.json()["token"]

    # ── yield 之前 = setup ──
    yield token
    # ── yield 之后 = teardown ──

    print(f"  🗑️  [function] 正在注销 token...")
    h = {"Authorization": f"Bearer {token}"}
    api_client.post("/api/logout", headers=h)


@pytest.fixture(scope="session")
def token_session(api_session, base_url):
    """【scope=session】整个测试会话只登录一次，所有测试共享同一个 token

    优点：性能最优，只发一次登录请求
    缺点：多个测试共用 token 可能互相干扰

    这里直接用 api_session 而非 api_client，
    因为 api_client 是 function scope，session scope 的 fixture 不能用 function scope 的 fixture。
    """
    print(f"\n  🔑 [session] 全局登录（整个会话只执行一次）...")
    r = api_session.post(
        f"{base_url}/api/login",
        json=LOGIN_CREDENTIALS,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200, f"登录失败: {r.json()}"
    token = r.json()["token"]

    # ── setup ──
    yield token
    # ── teardown（测试全部结束后执行）──

    print(f"\n  🗑️  [session] 正在注销全局 token...")
    h = {"Authorization": f"Bearer {token}"}
    api_session.post(f"{base_url}/api/logout", headers=h)


@pytest.fixture(scope="class")
def token_per_class(api_session, base_url):
    """【scope=class】同一个测试类内共享一个 token

    在 class 和 session 之间折中：一个类的测试共享登录态

    注意：class scope 的 fixture 不能用 function scope 的 api_client，
    必须用 session scope 的 api_session + base_url（pytest scope 规则：
    宽 scope 只能依赖更宽 scope 的 fixture）。
    """
    print(f"\n  🔑 [class] 类级登录...")
    r = api_session.post(
        f"{base_url}/api/login",
        json=LOGIN_CREDENTIALS,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200
    token = r.json()["token"]

    yield token

    print(f"  🗑️  [class] 正在注销类级 token...")
    h = {"Authorization": f"Bearer {token}"}
    api_session.post(f"{base_url}/api/logout", headers=h)


@pytest.fixture(scope="module")
def token_per_module(api_session, base_url):
    """【scope=module】同一个 .py 文件内共享一个 token

    比 session 隔离性好，比 function 性能好。
    同样不能用 api_client（function scope），直接用 api_session。
    """
    print(f"\n  🔑 [module] 模块级登录...")
    r = api_session.post(
        f"{base_url}/api/login",
        json=LOGIN_CREDENTIALS,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200
    token = r.json()["token"]

    yield token

    print(f"  🗑️  [module] 正在注销模块级 token...")
    h = {"Authorization": f"Bearer {token}"}
    api_session.post(f"{base_url}/api/logout", headers=h)


# ═══════════════════════════════════════════════════════════
# 鉴权 Headers fixture（依赖 token fixture）
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def auth_headers(token_per_function):
    """鉴权请求头（function scope，每个测试独立登录）

    依赖链：api_session → api_client → token_per_function → auth_headers
    这就是 fixture 依赖链的演示。
    """
    return {"Authorization": f"Bearer {token_per_function}"}


@pytest.fixture(scope="session")
def auth_headers_session(token_session):
    """鉴权请求头（session scope，全局复用）

    依赖链：api_session → token_session → auth_headers_session
    """
    return {"Authorization": f"Bearer {token_session}"}


# ═══════════════════════════════════════════════════════════
# 测试数据 fixture（第2周开始使用）
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def valid_student():
    """合法用户数据"""
    return {
        "name": "测试学生",
        "grade": "2026",
        "score": 88
    }


@pytest.fixture
def invalid_student():
    """非法用户数据（用于异常测试）"""
    return {
        "name": "",
        "grade": ""
    }


# ═══════════════════════════════════════════════════════════
# 前置检查 fixture
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def api(api_session, base_url):
    """确保 API 服务已启动（module 级别，每个测试文件只检查一次）"""
    try:
        r = api_session.get(f"{base_url}/api/health", timeout=3)
        assert r.status_code == 200
    except requests.ConnectionError:
        pytest.exit("❌ API 未启动！请先执行: python api/app.py")
