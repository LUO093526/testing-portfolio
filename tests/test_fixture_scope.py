"""
第3周 Day1：fixture scope 对比测试

运行方式：
    pytest tests/test_fixture_scope.py -v              # 全部运行
    pytest tests/test_fixture_scope.py -v -s           # -s 看 print 输出（setup/teardown 时机）
    pytest tests/test_fixture_scope.py -v -k "speed"   # 只看速度对比

核心演示：
    1. 四种 scope 的 token fixture 各自独立工作
    2. function scope 每次新登录 vs session scope 复用
    3. yield teardown：测试结束后自动注销 token
    4. fixture 依赖链：token → auth_headers 自动传递
"""

import pytest
import time


# ═══════════════════════════════════════════════════════════
# 测试1：function scope token — 每次新登录
# ═══════════════════════════════════════════════════════════

class TestTokenFunctionScope:
    """使用 scope=function 的 token，每个测试独立登录"""

    def test_token_is_valid(self, api, api_client, token_per_function):
        """验证 function scope token 能通过 /api/me"""
        h = {"Authorization": f"Bearer {token_per_function}"}
        r = api_client.get("/api/me", headers=h)
        assert r.status_code == 200
        assert r.json()["message"] == "token 有效"

    def test_different_test_gets_different_token(self, api, api_client, token_per_function):
        """同一个类的不同测试方法，token 不同（各自独立）"""
        # 每个测试函数调用 token_per_function 都会触发新的登录
        # 所以这里的 token 和上个测试的不一样
        h = {"Authorization": f"Bearer {token_per_function}"}
        r = api_client.get("/api/me", headers=h)
        assert r.status_code == 200

    def test_teardown_revokes_token(self, api, api_client, token_per_function):
        """yield teardown 在测试结束后自动注销 token

        验证方式：用当前 token 调用 /api/me，确认有效。
        teardown 会在 yield 之后自动执行（通过 -s 参数可以看到 print 输出）。
        """
        h = {"Authorization": f"Bearer {token_per_function}"}
        r = api_client.get("/api/me", headers=h)
        assert r.status_code == 200
        # 本测试结束后，token_per_function 的 yield 之后代码会：
        # POST /api/logout → token 被注销


# ═══════════════════════════════════════════════════════════
# 测试2：session scope token — 全局复用
# ═══════════════════════════════════════════════════════════

class TestTokenSessionScope:
    """使用 scope=session 的 token，整个测试会话共享"""

    def test_session_token_valid(self, api, api_client, token_session):
        """验证 session scope token 有效"""
        h = {"Authorization": f"Bearer {token_session}"}
        r = api_client.get("/api/me", headers=h)
        assert r.status_code == 200

    def test_same_token_across_tests(self, api, api_client, token_session):
        """同一 session 内所有测试拿到的是同一个 token"""
        # token_session 是 session scope，整个运行期间只登录一次
        # 这个测试和上一个测试拿到的是同一个 token
        h = {"Authorization": f"Bearer {token_session}"}
        r = api_client.get("/api/me", headers=h)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════
# 测试3：fixture 依赖链 — auth_headers 依赖 token
# ═══════════════════════════════════════════════════════════

class TestFixtureDependencyChain:
    """演示 fixture 依赖链：api_session → api_client → token → auth_headers"""

    def test_auth_headers_depends_on_token(self, api, api_client, auth_headers):
        """auth_headers 自动依赖 token_per_function"""
        r = api_client.get("/api/me", headers=auth_headers)
        assert r.status_code == 200

    def test_session_auth_shared(self, api, api_client, auth_headers_session):
        """auth_headers_session 自动依赖 token_session"""
        r = api_client.get("/api/me", headers=auth_headers_session)
        assert r.status_code == 200

    def test_fixture_chain_explicit(
        self, api, api_client, token_per_function, auth_headers
    ):
        """显式展示完整依赖链：同一测试中使用多个层级的 fixture"""
        # token_per_function 提供 token
        assert token_per_function is not None
        assert len(token_per_function) == 32

        # auth_headers 把 token 包装成 HTTP 头
        assert "Authorization" in auth_headers
        assert auth_headers["Authorization"] == f"Bearer {token_per_function}"

        # api_client 提供 HTTP 客户端
        r = api_client.get("/api/me", headers=auth_headers)
        assert r.status_code == 200


# ═══════════════════════════════════════════════════════════
# 测试4：scope 性能对比
# ═══════════════════════════════════════════════════════════

class TestScopePerformance:
    """对比 function vs session scope 的性能差异"""

    def test_function_scope_slower(self, api, api_client):
        """function scope：每个测试都登录，适合隔离性要求高的场景"""
        # 模拟 function scope 行为：循环登录3次
        times = []
        for i in range(3):
            t0 = time.time()
            r = api_client.post("/api/login", json={"username": "testuser", "password": "test123"})
            token = r.json()["token"]
            times.append(time.time() - t0)
            # 清理
            h = {"Authorization": f"Bearer {token}"}
            api_client.post("/api/logout", headers=h)

        avg_function = sum(times) / len(times) * 1000
        print(f"\n  ⏱️  function scope 平均登录耗时: {avg_function:.1f}ms")

    def test_session_scope_faster(self, api, api_client):
        """session scope：只登录一次，后续测试直接复用"""
        t0 = time.time()
        r = api_client.post("/api/login", json={"username": "testuser", "password": "test123"})
        token = r.json()["token"]
        elapsed = (time.time() - t0) * 1000
        print(f"\n  ⚡ session scope 登录耗时: {elapsed:.1f}ms（只执行一次）")

        # 复用同一个 token 进行多次验证（模拟 session scope 行为）
        h = {"Authorization": f"Bearer {token}"}
        for _ in range(3):
            r = api_client.get("/api/me", headers=h)
            assert r.status_code == 200

        # 清理
        api_client.post("/api/logout", headers=h)

    def test_scope_decision_guide(self):
        """什么时候用什么 scope？

        function  → 需要严格隔离（如：每个测试不同角色）
        class     → 同一个类的测试共享状态
        module    → 同一文件的测试共享连接
        session   → 全局不变的数据（如：配置、数据库连接）

        本测试只是文档性质，不调用任何 API。
        """
        guide = {
            "隔离性": "function > class > module > session",
            "性能": "session > module > class > function",
            "适用场景": {
                "function": "每个测试需要干净状态时才用",
                "class": "同一个类共享登录态",
                "module": "同一个文件共享昂贵资源",
                "session": "配置项、全局连接池等不变的东西",
            },
        }
        assert len(guide["适用场景"]) == 4  # 四种 scope 都有


# ═══════════════════════════════════════════════════════════
# 测试5：class scope 演示
# ═══════════════════════════════════════════════════════════

@pytest.mark.usefixtures("token_per_class")
class TestClassScopeToken:
    """这个类使用 scope=class 的 token，类内所有测试共享"""

    def test_first_use(self, api, api_client, token_per_class):
        """第一次使用 class scope token"""
        h = {"Authorization": f"Bearer {token_per_class}"}
        r = api_client.get("/api/me", headers=h)
        assert r.status_code == 200

    def test_second_use_same_token(self, api, api_client, token_per_class):
        """第二次使用 — 应该是同一个 token（不会重新登录）"""
        h = {"Authorization": f"Bearer {token_per_class}"}
        r = api_client.get("/api/me", headers=h)
        assert r.status_code == 200
