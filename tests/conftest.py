"""
conftest.py — 项目全局测试配置

所有测试文件共享的 fixture、测试数据、前置逻辑统一放在这里。
pytest 会自动发现并加载本文件，无需手动 import。

使用方式：
    测试文件里直接写 fixture 名称作为参数即可，例如:
    def test_login(api_client, valid_user):
        ...
"""

import pytest
import requests
import os
import sys

# 确保 api 模块可导入
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ═══════════════════════════════════════════════════════════
# Flask 应用管理 fixture
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def app():
    """启动 Flask 测试服务器（整个测试会话只启动一次）"""
    from api.app import app as flask_app
    # TODO: 配置测试模式
    flask_app.config['TESTING'] = True
    return flask_app


@pytest.fixture(scope="session")
def base_url(app):
    """API 基础 URL"""
    return "http://127.0.0.1:5000"


# ═══════════════════════════════════════════════════════════
# 测试数据 fixture（第2周开始使用）
# ═══════════════════════════════════════════════════════════

@pytest.fixture
def valid_student():
    """合法用户数据"""
    return {
        "name": "测试学生",
        "grade": "2026",
        "score":88
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


# ═══════════════════════════════════════════════════════════
# API 客户端 fixture
# ═══════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def api_session():
    """全局 HTTP 会话（复用连接，加速测试）"""
    session = requests.Session()
    yield session
    session.close()


@pytest.fixture
def api_client(api_session, base_url):
    """API 客户端（无鉴权）"""
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






