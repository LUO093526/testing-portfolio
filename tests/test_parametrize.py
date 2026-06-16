"""pytest parametrize 参数化 — 第3周Day2

核心概念：
    @pytest.mark.parametrize("参数名", [数据列表])
    一组数据 → 自动生成一条独立用例，避免手写重复代码。

运行方式：
    pytest tests/test_parametrize.py -v              # 查看每组数据显示为独立用例
    pytest tests/test_parametrize.py -v -k "login"   # 只跑登录相关
    pytest tests/test_parametrize.py -v -k "create"  # 只跑注册相关

面试价值：
    "你怎么避免写重复用例？" → 用 parametrize 一组数据驱动 N 条用例
    "登录接口你测了多少种情况？" → 能报出具体数字：10组参数化数据
"""

import pytest


# ═══════════════════════════════════════════════════════════
# 一、登录接口 parametrize — 10组数据
# ═══════════════════════════════════════════════════════════

LOGIN_TEST_DATA = [
    # ── 正常场景：正确用户名+正确密码 ──
    # id 参数让每条用例有可读的名字（而非默认的 test_login[login_data0]）
    pytest.param(
        {"username": "admin", "password": "admin123"},
        200, "登录成功，返回token",
        id="正常-admin登录",
    ),
    pytest.param(
        {"username": "testuser", "password": "test123"},
        200, "登录成功，返回token",
        id="正常-testuser登录",
    ),
    pytest.param(
        {"username": "zhangsan", "password": "pass456"},
        200, "登录成功，返回token",
        id="正常-zhangsan登录",
    ),

    # ── 密码错误场景：正确用户名 + 错误密码 ──
    pytest.param(
        {"username": "admin", "password": "wrongpass"},
        401, "用户名或密码错误",
        id="异常-admin密码错误",
    ),
    pytest.param(
        {"username": "testuser", "password": "admin123"},
        401, "用户名或密码错误",
        id="异常-testuser密码错误",
    ),
    pytest.param(
        {"username": "zhangsan", "password": ""},
        400, "username 和 password 为必填字段",
        id="边界-密码为空字符串",
    ),

    # ── 空值/缺失场景 ──
    pytest.param(
        {"username": "", "password": "test123"},
        400, "username 和 password 为必填字段",
        id="边界-用户名为空",
    ),
    pytest.param(
        {},
        400, "请求体为空",
        id="边界-空请求体",
    ),

    # ── 特殊字符/异常输入 ──
    pytest.param(
        {"username": "<script>alert(1)</script>", "password": "test123"},
        401, "用户名或密码错误",
        id="安全-XSS用户名",
    ),
    pytest.param(
        {"username": "admin", "password": "'; DROP TABLE users;--"},
        401, "用户名或密码错误",
        id="安全-SQL注入式密码",
    ),
]


@pytest.mark.parametrize("payload,expected_status,expected_msg", LOGIN_TEST_DATA)
def test_login_parametrize(api_client, payload, expected_status, expected_msg):
    """登录接口参数化：10组数据覆盖正常/异常/边界/安全场景

    每组数据生成一条独立用例，pytest -v 输出中可见10条不同名字的测试。
    一条失败不影响其他条继续执行。
    """
    r = api_client.post("/api/login", json=payload)
    assert r.status_code == expected_status, \
        f"期望 {expected_status}，实际 {r.status_code}，响应: {r.json()}"

    body = r.json()
    if expected_status == 200:
        # 成功登录必须返回 token 和 username
        assert "token" in body, f"缺少 token 字段: {body}"
        assert len(body["token"]) == 32, f"token 长度应为32: {len(body['token'])}"
        assert body["username"] == payload["username"]
    else:
        # 失败场景验证错误消息中包含关键字
        assert expected_msg in body.get("error", ""), \
            f"错误消息应包含 '{expected_msg}'，实际: {body.get('error', '')}"


# ═══════════════════════════════════════════════════════════
# 二、用户注册（新增学生）接口 parametrize — 10组数据
# ═══════════════════════════════════════════════════════════

CREATE_TEST_DATA = [
    # ── 正常注册：合法数据 ──
    pytest.param(
        {"name": "张三", "grade": "2026", "score": 85},
        201, "正常-完整字段",
        id="正常-完整字段",
    ),
    pytest.param(
        {"name": "李四", "grade": "2025"},
        201, "正常-仅必填字段(score默认0)",
        id="正常-仅必填字段",
    ),
    pytest.param(
        {"name": "王五", "grade": "2024", "score": 100},
        201, "正常-score满分",
        id="正常-score满分",
    ),

    # ── 必填字段缺失 ──
    pytest.param(
        {"grade": "2026", "score": 80},
        400, "name 和 grade 为必填字段",
        id="异常-缺少name字段",
    ),
    pytest.param(
        {"name": "缺年级", "score": 80},
        400, "name 和 grade 为必填字段",
        id="异常-缺少grade字段",
    ),

    # ── 边界值：score ──
    pytest.param(
        {"name": "边界测试0", "grade": "2026", "score": 0},
        201, "边界-score为0",
        id="边界-score=0",
    ),
    pytest.param(
        {"name": "边界测试-1", "grade": "2026", "score": -1},
        201, "边界-score为负数",
        id="边界-score=-1",
    ),
    pytest.param(
        {"name": "边界测试大数", "grade": "2026", "score": 999999},
        201, "边界-score超大数",
        id="边界-score=999999",
    ),

    # ── 特殊字符/边界 name ──
    pytest.param(
        {"name": "", "grade": "2026", "score": 80},
        201, "边界-name为空字符串",
        id="边界-name空字符串",
    ),
    pytest.param(
        {"name": "测" * 100, "grade": "2026", "score": 80},
        201, "边界-name超长100字",
        id="边界-name超长100字",
    ),
]


@pytest.mark.parametrize("payload,expected_status,desc", CREATE_TEST_DATA)
def test_create_student_parametrize(api_client, payload, expected_status, desc):
    """学生注册接口参数化：10组数据覆盖正常/异常/边界场景

    每组数据生成一条独立用例。创建成功后自动清理。
    验证点：状态码、必要字段存在性。
    """
    r = api_client.post("/api/students", json=payload)
    assert r.status_code == expected_status, \
        f"[{desc}] 期望 {expected_status}，实际 {r.status_code}，响应: {r.json()}"

    body = r.json()
    if expected_status == 201:
        # 成功创建：验证返回数据包含 id 和原始字段
        assert "data" in body, f"缺少 data 字段: {body}"
        data = body["data"]
        assert "id" in data, f"缺少 id: {data}"
        assert data["name"] == payload["name"], \
            f"name 不匹配: 期望'{payload['name']}' 实际'{data['name']}'"
        assert data["grade"] == payload["grade"]
        expected_score = payload.get("score", 0)
        assert data["score"] == expected_score, \
            f"score 不匹配: 期望{expected_score} 实际{data['score']}"

        # 清理：删除刚创建的学生
        api_client.delete(f"/api/students/{data['id']}")
    else:
        # 失败场景：验证错误消息
        assert "error" in body, f"应包含 error 字段: {body}"


# ═══════════════════════════════════════════════════════════
# 三、进阶：parametrize 叠加 — 组合多个参数
# ═══════════════════════════════════════════════════════════

# pytest 支持多个 parametrize 装饰器叠加，自动做笛卡尔积
# 例如下面：2个用户名 × 3个状态 = 6条用例

@pytest.mark.parametrize("username", [
    pytest.param("admin", id="用户=admin"),
    pytest.param("testuser", id="用户=testuser"),
])
@pytest.mark.parametrize("password_scenario", [
    pytest.param("admin123", id="密码正确"),
    pytest.param("wrong", id="密码错误"),
    pytest.param("", id="密码为空"),
])
def test_login_combination(api_client, username, password_scenario):
    """叠加 parametrize 演示 — 2×3=6条用例自动生成

    多 parametrize 叠加 = 笛卡尔积。适合"每个参数独立变化"的场景。
    本例：2个用户 × 3种密码 = 6条用例
    """
    payload = {"username": username, "password": password_scenario}
    r = api_client.post("/api/login", json=payload)

    if password_scenario == "admin123":
        # admin 的密码是 admin123，testuser 的密码是 test123
        if username == "admin":
            assert r.status_code == 200
            assert "token" in r.json()
        else:
            assert r.status_code == 401
    elif password_scenario == "wrong":
        assert r.status_code == 401
    elif password_scenario == "":
        assert r.status_code == 400


# ═══════════════════════════════════════════════════════════
# 四、parametrize 配合 fixture — 用 token 鉴权后的请求
# ═══════════════════════════════════════════════════════════

ME_CHECK_DATA = [
    pytest.param(True, 200, "token有效", id="正常-有效token"),
    pytest.param(False, 401, "token无效或已注销", id="异常-无效token"),
]


@pytest.mark.parametrize("use_valid_token,expected_status,expected_msg", ME_CHECK_DATA)
def test_me_with_parametrize(
    api_client, token_per_function, use_valid_token, expected_status, expected_msg
):
    """parametrize + fixture 组合：token 验证接口

    演示 parametrize 和 fixture 可以无缝协作：
    - token_per_function 是 Day1 的 fixture（scope=function）
    - parametrize 提供两组场景：有效token / 无效token
    """
    if use_valid_token:
        headers = {"Authorization": f"Bearer {token_per_function}"}
    else:
        headers = {"Authorization": "Bearer invalid_token_12345"}

    r = api_client.get("/api/me", headers=headers)
    assert r.status_code == expected_status, \
        f"期望 {expected_status}，实际 {r.status_code}: {r.json()}"


# ═══════════════════════════════════════════════════════════
# 五、批量数据：用 parametrize 替代 for 循环
# ═══════════════════════════════════════════════════════════
#
# ❌ 坏写法（不推荐）：
#   def test_many_logins(api_client):
#       for user, pwd in [("a","1"), ("b","2"), ...]:
#           r = api_client.post("/api/login", json=...)
#           assert r.status_code == 200
#   → 问题：第一个用户失败就全部停止，且不知道哪个失败
#
# ✅ 好写法（推荐）：
#   @pytest.mark.parametrize(...)
#   def test_login(api_client, payload, ...):
#       ...
#   → 优势：每条独立、失败不阻塞、pytest -v 清楚显示每条结果
