"""
conftest.py — 项目全局测试配置（第3周重构版）

所有测试文件共享的 fixture、测试数据、前置逻辑统一放在这里。
pytest 会自动发现并加载本文件，无需手动 import。

使用方式：
    测试文件里直接写 fixture 名称作为参数即可，例如:
    def test_login(api_client, valid_student):
        ...

═══════════════════════════════════════════════════
Fixture 依赖链（第3周核心）
═══════════════════════════════════════════════════

    test_data ──────────────────────────────────────────────┐
    │  session scope: 集中管理所有测试凭证和样本数据          │
    │  被依赖: valid_student, invalid_student, login_creds   │
    └───────────────────────────────────────────────────────┘
        │
        ▼
    api_session (session) ──→ api_client (function)
    │                             │
    │  全局 HTTP 会话               │  每个测试独立客户端
    │  复用 TCP 连接                │  封装 get/post/put/delete
    │                             │
    ▼                             ▼
    token_per_function ─────→ auth_headers (function)
    │  (function)                 │
    │  每次新登录拿 token          │  把 token 包成 Authorization 头
    │  yield → teardown 注销      │
    │                             │
    └─────────────────────────────┘
        │
        ▼
    authenticated_client (function)
    │  带鉴权的 API 客户端，组合 api_client + auth_headers
    │  一键发鉴权请求，不用每次手动拼 headers
    │
    ▼
    测试函数直接使用

    Scope 层级（宽→窄）:
        session  >  module  >  class  >  function
        (只能"窄依赖宽"，不能反过来)


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
from dataclasses import dataclass, field
from typing import Dict, List

# 确保 api 模块可导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# ═══════════════════════════════════════════════════════════
# 1. 集中测试数据层 — test_data（链的起点）
# ═══════════════════════════════════════════════════════════

@dataclass(frozen=True)
class TestData:
    """集中管理所有测试数据，单一数据源（Single Source of Truth）

    所有测试文件通过 test_data fixture 引用这里的数据，
    而不是各自硬编码。数据变更只需改这一处。
    """
    # ── 登录凭证 ──
    login_default: Dict[str, str] = field(default_factory=lambda: {
        "username": "testuser", "password": "test123"
    })
    login_admin: Dict[str, str] = field(default_factory=lambda: {
        "username": "admin", "password": "admin123"
    })
    login_users: List[Dict[str, str]] = field(default_factory=lambda: [
        {"username": "admin", "password": "admin123"},
        {"username": "testuser", "password": "test123"},
        {"username": "zhangsan", "password": "pass456"},
    ])
    login_invalid: List[Dict] = field(default_factory=lambda: [
        {"username": "admin", "password": "wrongpass"},
        {"username": "ghost", "password": "nope"},
    ])

    # ── 学生数据 ──
    student_valid: Dict = field(default_factory=lambda: {
        "name": "测试学生", "grade": "2026", "score": 88
    })
    student_invalid: Dict = field(default_factory=lambda: {
        "name": "", "grade": ""
    })
    student_missing_name: Dict = field(default_factory=lambda: {
        "grade": "2026", "score": 80
    })
    student_missing_grade: Dict = field(default_factory=lambda: {
        "name": "缺年级", "score": 80
    })

    # ── 边界值数据 ──
    boundary: Dict = field(default_factory=lambda: {
        "name_empty": "",
        "name_spaces": "   ",
        "name_numbers": "12345",
        "name_long": "测" * 100,
        "name_xss": "test<script>alert(1)</script>",
        "grade_empty": "",
        "grade_negative": "-1",
        "grade_nonexistent": "9999",
        "score_zero": 0,
        "score_negative": -100,
        "score_max": 999999,
        "score_string": "abc",
    })


@pytest.fixture(scope="session")
def test_data():
    """【依赖链起点】集中管理所有测试数据

    scope=session：测试数据在整个会话中不变，只创建一次。
    这是 fixture 依赖链的最上游 — 所有数据 fixture 都从这里取。

    依赖链: test_data → valid_student / invalid_student / login_creds → ...
    """
    return TestData()


# ── 派生数据 fixture（依赖 test_data）─────────────────────

@pytest.fixture(scope="session")
def login_credentials(test_data):
    """默认登录凭证（从 test_data 派生）"""
    return test_data.login_default


@pytest.fixture
def valid_student(test_data):
    """合法学生数据（从 test_data 派生，保持向后兼容）"""
    return dict(test_data.student_valid)


@pytest.fixture
def invalid_student(test_data):
    """非法学生数据（从 test_data 派生，保持向后兼容）"""
    return dict(test_data.student_invalid)


# ═══════════════════════════════════════════════════════════
# 2. Flask 应用管理层
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
# 3. HTTP 会话层 — api_session → api_client
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def api_session():
    """全局 HTTP 会话（复用 TCP 连接，加速测试）

    依赖链位置：第2层（被 api_client 依赖）

    yield 语法说明（第3周）：
        yield 之前的代码 = setup（创建 session）
        yield 之后的代码 = teardown（关闭 session，释放资源）
    """
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture
def api_client(api_session, base_url):
    """API 客户端（无鉴权）— 每个测试函数独立一份

    依赖链位置：第3层
    依赖: api_session (session), base_url (session)
    """
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
# 4. Token 管理层 — 四种 scope 对比
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def token_per_function(api_client, login_credentials):
    """【scope=function】每个测试函数都重新登录，获取新 token

    依赖链位置：第4层
    依赖: api_client (function), login_credentials (session)

    优点：隔离性最强，一个测试的 token 不会影响另一个
    缺点：每次都发 HTTP 请求，速度慢
    """
    r = api_client.post("/api/login", json=login_credentials)
    assert r.status_code == 200, f"登录失败: {r.json()}"
    token = r.json()["token"]

    yield token  # ← 把 token 交给测试函数

    # teardown：注销 token
    h = {"Authorization": f"Bearer {token}"}
    api_client.post("/api/logout", headers=h)


@pytest.fixture(scope="session")
def token_session(api_session, base_url, login_credentials):
    """【scope=session】整个测试会话只登录一次，所有测试共享同一个 token

    依赖链位置：第4层（session 分支）
    依赖: api_session (session), base_url (session), login_credentials (session)

    优点：性能最优，只发一次登录请求
    缺点：多个测试共用 token 可能互相干扰

    注意：session scope 不能用 function scope 的 api_client，
    必须直接使用 api_session + base_url。
    """
    r = api_session.post(
        f"{base_url}/api/login",
        json=login_credentials,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200, f"登录失败: {r.json()}"
    token = r.json()["token"]

    yield token

    # teardown（测试全部结束后执行）
    h = {"Authorization": f"Bearer {token}"}
    api_session.post(f"{base_url}/api/logout", headers=h)


@pytest.fixture(scope="class")
def token_per_class(api_session, base_url, login_credentials):
    """【scope=class】同一个测试类内共享一个 token

    依赖链位置：第4层（class 分支）
    """
    r = api_session.post(
        f"{base_url}/api/login",
        json=login_credentials,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200
    token = r.json()["token"]

    yield token

    h = {"Authorization": f"Bearer {token}"}
    api_session.post(f"{base_url}/api/logout", headers=h)


@pytest.fixture(scope="module")
def token_per_module(api_session, base_url, login_credentials):
    """【scope=module】同一个 .py 文件内共享一个 token

    依赖链位置：第4层（module 分支）
    """
    r = api_session.post(
        f"{base_url}/api/login",
        json=login_credentials,
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200
    token = r.json()["token"]

    yield token

    h = {"Authorization": f"Bearer {token}"}
    api_session.post(f"{base_url}/api/logout", headers=h)


# ═══════════════════════════════════════════════════════════
# 5. 鉴权层 — auth_headers（依赖 token）
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="function")
def auth_headers(token_per_function):
    """鉴权请求头（function scope，每个测试独立登录）

    依赖链位置：第5层
    依赖链: test_data → login_credentials → token_per_function → auth_headers
    """
    return {"Authorization": f"Bearer {token_per_function}"}


@pytest.fixture(scope="session")
def auth_headers_session(token_session):
    """鉴权请求头（session scope，全局复用）

    依赖链位置：第5层（session 分支）
    依赖链: test_data → login_credentials → token_session → auth_headers_session
    """
    return {"Authorization": f"Bearer {token_session}"}


# ═══════════════════════════════════════════════════════════
# 6. 便捷客户端层 — authenticated_client
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def authenticated_client(api_client, auth_headers):
    """【第3周新增】带鉴权的 API 客户端

    依赖链位置：第6层（链的终点）
    依赖链: test_data → login_credentials → api_client + token_per_function
            → auth_headers → authenticated_client

    使用方式：
        def test_something(authenticated_client):
            r = authenticated_client.get("/api/me")
            # 不需要手动传 headers，已自动带上 Authorization
    """
    class AuthApiClient:
        def __init__(self, client, headers):
            self._client = client
            self._headers = headers

        def get(self, path, **kwargs):
            kwargs.setdefault("headers", self._headers)
            return self._client.get(path, **kwargs)

        def post(self, path, **kwargs):
            kwargs.setdefault("headers", self._headers)
            return self._client.post(path, **kwargs)

        def put(self, path, **kwargs):
            kwargs.setdefault("headers", self._headers)
            return self._client.put(path, **kwargs)

        def delete(self, path, **kwargs):
            kwargs.setdefault("headers", self._headers)
            return self._client.delete(path, **kwargs)

    return AuthApiClient(api_client, auth_headers)


# ═══════════════════════════════════════════════════════════
# 7. 资源管理 fixture — sample_student
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def sample_student(api, api_client, valid_student):
    """创建一个测试用学生，测试完自动清理

    依赖链位置：测试资源层
    依赖: api (module), api_client (function), valid_student (function)

    用法：
        def test_something(sample_student):
            # sample_student = 刚创建的学生的 id
            r = api_client.get(f"/api/students/{sample_student}")
            ...

    从 test_api.py 迁移到 conftest.py（第3周Day3重构），
    所有测试文件现在可以共享这个 fixture。
    """
    r = api_client.post("/api/students", json=valid_student)
    assert r.status_code == 201, f"创建测试学生失败: {r.json()}"
    sid = r.json()["data"]["id"]

    yield sid  # ← 把学生 ID 交给测试函数

    # teardown：删除测试学生
    api_client.delete(f"/api/students/{sid}")


# ═══════════════════════════════════════════════════════════
# 8. 前置检查 fixture
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def api(api_session, base_url):
    """确保 API 服务已启动（module 级别，每个测试文件只检查一次）

    依赖链位置：独立前置检查层
    依赖: api_session (session), base_url (session)
    """
    try:
        r = api_session.get(f"{base_url}/api/health", timeout=3)
        assert r.status_code == 200
    except requests.ConnectionError:
        pytest.exit("❌ API 未启动！请先执行: python api/app.py")


# ═══════════════════════════════════════════════════════════
# 附：依赖链速查表
# ═══════════════════════════════════════════════════════════
#
#   test_data (session) ─────────────────────────────────
#       ├── login_credentials (session)
#       ├── valid_student (function)
#       └── invalid_student (function)
#                │
#   api_session (session) ──→ api_client (function)
#   base_url (session) ──────┘        │
#                                     ▼
#   login_credentials ──→ token_per_function (function)
#                                     │
#                                     ▼
#                         auth_headers (function) ──→ authenticated_client
#                         auth_headers_session ────→ (session 分支)
#
#   sample_student ←── api + api_client + valid_student
#
#   正确的依赖方向（scope 规则）:
#     窄 scope 可以依赖宽 scope ✅  (function 依赖 session)
#     宽 scope 不能依赖窄 scope ❌  (session 不能依赖 function)


# ═══════════════════════════════════════════════════════════
# 9. Selenium Web UI 配置（第3周Day5：Selenium pytest重构）
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def selenium_config():
    """Selenium Web UI 测试的集中配置（第3周Day5新增）

    所有 Web 测试通过此 fixture 引用配置，不再硬编码。
    包括：目标URL、测试账号、浏览器路径等。
    """
    return {
        "login_url": "http://124.223.155.95:8088/home/login/login.html",
        "valid_username": "18062031483",
        "valid_password": "mfm543200",
        "chromium_path": "/home/luo/.cache/ms-playwright/chromium-1223/chrome-linux64/chrome",
        "chromedriver_path": "/home/luo/.local/bin/chromedriver",
        "captcha_retry": 10,
        "accounts": [
            {"username": "18062031483", "password": "mfm543200", "desc": "主账号"},
            # 可扩展更多测试账号
        ],
        "invalid_accounts": [
            {"username": "wrong_user_123", "password": "mfm543200", "desc": "错误用户名"},
            {"username": "18062031483", "password": "wrongpassword", "desc": "错误密码"},
            {"username": "", "password": "mfm543200", "desc": "空用户名"},
            {"username": "18062031483", "password": "", "desc": "空密码"},
        ],
    }
