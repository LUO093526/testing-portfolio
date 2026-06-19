"""学员管理系统 API 自动化测试
运行方式:
    pytest tests/test_api.py -v                    # 基础运行
    pytest tests/test_api.py -v --html=reports/report.html  # 生成HTML报告
    pytest tests/test_api.py -v -m smoke           # 仅冒烟测试
    pytest tests/test_api.py -v -m "not slow"      # 跳过慢速测试
"""

import pytest


# ── 冒烟测试（快速验证核心功能是否可用）────────────────────
# 注：sample_student fixture 已迁移到 conftest.py（第3周Day3重构）

@pytest.mark.smoke
class TestHealthCheck:
    # 【冒烟】服务健康检查
    def test_health_returns_200(self, api, api_client):
        r = api_client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.smoke
class TestStudentList:
    # 【正常流程】列表能返回数据和count字段
    def test_list_returns_200_and_data(self, api, api_client):
        """GET /api/students 返回列表"""
        r = api_client.get("/api/students")
        assert r.status_code == 200
        body = r.json()
        assert "count" in body
        assert "data" in body
        assert isinstance(body["data"], list)

    # 【等价类-有效】按姓名模糊筛选
    def test_filter_by_name(self, api, api_client):
        """按姓名模糊筛选"""
        r = api_client.get("/api/students?name=张")
        assert r.status_code == 200
        names = [s["name"] for s in r.json()["data"]]
        assert all("张" in n for n in names)

    # 【正交法】同时按姓名+年级筛选（两因子组合）
    def test_filter_by_name_and_grade(self, api, api_client):
        """同时按姓名+年级筛选"""
        r = api_client.get("/api/students?name=张&grade=2026")
        assert r.status_code == 200
        students = r.json()["data"]
        # 验证每条结果：名字含"张" 且 年级为"2026"
        for s in students:
            assert "张" in s["name"]
            assert s["grade"] == "2026"

    # 【边界值】筛选参数name为空字符串
    def test_filter_by_empty_name(self, api, api_client):
        """name参数传空字符串"""
        r = api_client.get("/api/students?name=")
        assert r.status_code == 200
        # 空参数应返回全部数据（等同于不传name）
        assert "data" in r.json()

    # 【等价类-无效】筛选不存在的年级 → 返回空列表
    def test_filter_nonexistent_grade(self, api, api_client):
        """筛选一个不存在的年级"""
        r = api_client.get("/api/students?grade=9999")
        assert r.status_code == 200
        assert r.json()["count"] == 0  # 没有学生是这个年级

    # 【等价类-有效】按年级精确筛选
    def test_filter_by_grade(self, api, api_client):
        """按年级精确筛选"""
        r = api_client.get("/api/students?grade=2025")
        assert r.status_code == 200
        grades = [s["grade"] for s in r.json()["data"]]
        assert all(g == "2025" for g in grades)


# ── CRUD 增删改查完整测试 ───────────────────────────────────

@pytest.mark.crud
class TestCreateStudent:
    # 【正常流程】新增学生：必填字段齐全、返回201+id
    def test_create_success(self, api, api_client, valid_student):
        """正常新增"""
        r = api_client.post("/api/students", json=valid_student)
        assert r.status_code == 201
        sid = r.json()["data"]["id"]
        # 清理
        api_client.delete(f"/api/students/{sid}")

    # 【等价类-无效】缺少必填字段name → 400
    @pytest.mark.exception
    def test_create_missing_name(self, api, api_client):
        """缺少必填字段应返回 400"""
        r = api_client.post("/api/students", json={"grade": "2026"})
        assert r.status_code == 400
        assert "error" in r.json()

    # 【等价类-无效】空请求体 → 400
    @pytest.mark.exception
    def test_create_empty_body(self, api, api_client):
        """空请求体应返回 400"""
        r = api_client.post("/api/students")
        assert r.status_code == 400

    # 【边界值】grade传入负数（刚好小于有效范围）
    @pytest.mark.boundary
    def test_create_negative_grade(self, api, api_client):
        """grade传入负数应正常创建"""
        r = api_client.post(
            "/api/students",
            json={"name": "测试负数年级", "grade": "-1", "score": 80},
        )
        assert r.status_code == 201
        assert r.json()["data"]["grade"] == "-1"
        sid = r.json()["data"]["id"]
        api_client.delete(f"/api/students/{sid}")

    # 【边界值】score传入负数（刚好小于有效范围）
    @pytest.mark.boundary
    def test_create_negative_score(self, api, api_client):
        """score传入负数应正常创建"""
        r = api_client.post(
            "/api/students",
            json={"name": "测试负分数", "grade": "2026", "score": -100},
        )
        assert r.status_code == 201
        assert r.json()["data"]["score"] == -100
        sid = r.json()["data"]["id"]
        api_client.delete(f"/api/students/{sid}")

    # 【边界值】name为空字符串（值为空）
    @pytest.mark.boundary
    def test_create_empty_name(self, api, api_client):
        """name为空字符串应正常创建"""
        r = api_client.post(
            "/api/students",
            json={"name": "", "grade": "2026", "score": 80},
        )
        assert r.status_code == 201
        assert r.json()["data"]["name"] == ""
        sid = r.json()["data"]["id"]
        api_client.delete(f"/api/students/{sid}")

    # 【边界值】name传入超长字符串（100个字符）
    @pytest.mark.boundary
    def test_create_long_name(self, api, api_client):
        """name传入超长字符串"""
        long_name = "测" * 100  # 100个"测"字
        r = api_client.post(
            "/api/students",
            json={"name": long_name, "grade": "2026", "score": 80},
        )
        assert r.status_code == 201
        assert r.json()["data"]["name"] == long_name
        sid = r.json()["data"]["id"]
        api_client.delete(f"/api/students/{sid}")

    # 【边界值】score传入超大数值（刚好大于有效范围）
    @pytest.mark.boundary
    def test_create_huge_score(self, api, api_client):
        """score传入超大数值"""
        r = api_client.post(
            "/api/students",
            json={"name": "测试超大数", "grade": "2026", "score": 999999},
        )
        assert r.status_code == 201
        assert r.json()["data"]["score"] == 999999
        sid = r.json()["data"]["id"]
        api_client.delete(f"/api/students/{sid}")

    # 【边界值】name传入纯空格（非空但无实际内容）
    @pytest.mark.boundary
    def test_create_name_spaces(self, api, api_client):
        """name传入纯空格"""
        r = api_client.post(
            "/api/students",
            json={"name": "   ", "grade": "2026", "score": 80},
        )
        assert r.status_code == 201
        assert r.json()["data"]["name"] == "   "
        sid = r.json()["data"]["id"]
        api_client.delete(f"/api/students/{sid}")

    # 【等价类-无效】score传入字符串 → API接受但不推荐
    @pytest.mark.exception
    def test_create_score_string(self, api, api_client):
        """score传入字符串类型"""
        r = api_client.post(
            "/api/students",
            json={"name": "测试", "grade": "2026", "score": "abc"},
        )
        assert r.status_code == 201
        sid = r.json()["data"]["id"]
        api_client.delete(f"/api/students/{sid}")

    # 【边界值】grade传入空字符串
    @pytest.mark.boundary
    def test_create_grade_empty(self, api, api_client):
        """grade传入空字符串"""
        r = api_client.post(
            "/api/students",
            json={"name": "测试空年级", "grade": "", "score": 80},
        )
        assert r.status_code == 201
        assert r.json()["data"]["grade"] == ""
        sid = r.json()["data"]["id"]
        api_client.delete(f"/api/students/{sid}")


@pytest.mark.crud
class TestGetStudent:
    # 【正常流程】查询存在的学生 → 200+完整数据
    def test_get_existing(self, api, api_client, sample_student):
        """获取存在的学生"""
        r = api_client.get(f"/api/students/{sample_student}")
        assert r.status_code == 200
        assert r.json()["data"]["name"] == "测试学生"

    # 【等价类-无效】查询不存在的id → 404
    @pytest.mark.exception
    def test_get_nonexistent(self, api, api_client):
        """获取不存在的学生应返回 404"""
        r = api_client.get("/api/students/99999")
        assert r.status_code == 404


@pytest.mark.crud
class TestUpdateStudent:
    # 【正常流程】更新存在的学生 → 200+数据变更
    def test_update_success(self, api, api_client, sample_student):
        """正常更新"""
        r = api_client.put(
            f"/api/students/{sample_student}",
            json={"score": 100},
        )
        assert r.status_code == 200
        assert r.json()["data"]["score"] == 100

    # 【等价类-无效】更新不存在的id → 404
    @pytest.mark.exception
    def test_update_nonexistent(self, api, api_client):
        """更新不存在的学生应返回 404"""
        r = api_client.put(
            "/api/students/99999",
            json={"score": 100},
        )
        assert r.status_code == 404

    # 【等价类-无效】更新时body为空 → 400
    @pytest.mark.exception
    def test_update_empty_body(self, api, api_client, sample_student):
        """更新时body为空应返回 400"""
        r = api_client.put(f"/api/students/{sample_student}")
        assert r.status_code == 400
        assert "error" in r.json()

    # 【等价类-无效】更新score为字符串 → API接受但不推荐
    @pytest.mark.exception
    def test_update_score_string(self, api, api_client, sample_student):
        """更新时score传入字符串"""
        r = api_client.put(
            f"/api/students/{sample_student}",
            json={"score": "not_a_number"},
        )
        assert r.status_code == 200


@pytest.mark.crud
class TestDeleteStudent:
    # 【正常流程】删除存在的学生 → 200，再次查询返回404
    def test_delete_success(self, api, api_client, valid_student):
        """正常删除"""
        r = api_client.post("/api/students", json=valid_student)
        sid = r.json()["data"]["id"]
        r = api_client.delete(f"/api/students/{sid}")
        assert r.status_code == 200
        # 再次获取应 404
        r = api_client.get(f"/api/students/{sid}")
        assert r.status_code == 404

    # 【等价类-无效】删除不存在的id → 404
    @pytest.mark.exception
    def test_delete_nonexistent(self, api, api_client):
        """删除不存在学生应返回 404"""
        r = api_client.delete("/api/students/99999")
        assert r.status_code == 404


# ── 数据验证测试（文档没写但也要测的）───────────────────────

class TestDataValidation:
    """接口文档里没写的，也要测"""

    # 【边界值】score缺失 → 默认值0
    @pytest.mark.boundary
    def test_score_default_zero(self, api, api_client):
        """不传 score 时默认为 0"""
        r = api_client.post(
            "/api/students",
            json={"name": "无分数", "grade": "2026"},
        )
        assert r.status_code == 201
        sid = r.json()["data"]["id"]
        assert r.json()["data"]["score"] == 0
        api_client.delete(f"/api/students/{sid}")

    # 【边界值】name含XSS脚本特殊字符
    @pytest.mark.exception
    def test_special_characters_in_name(self, api, api_client):
        """特殊字符处理"""
        r = api_client.post(
            "/api/students",
            json={"name": "test<script>alert(1)</script>", "grade": "2026"},
        )
        assert r.status_code == 201
        sid = r.json()["data"]["id"]
        api_client.delete(f"/api/students/{sid}")

    # 【边界值】name为纯数字
    @pytest.mark.boundary
    def test_name_numbers_only(self, api, api_client):
        """name为纯数字"""
        r = api_client.post(
            "/api/students",
            json={"name": "12345", "grade": "2026", "score": 80},
        )
        assert r.status_code == 201
        assert r.json()["data"]["name"] == "12345"
        sid = r.json()["data"]["id"]
        api_client.delete(f"/api/students/{sid}")


# ── 并发测试（简易）───────────────────────────────────────

class TestConcurrency:
    # 【并发】连续快速增删10次不崩溃
    @pytest.mark.slow
    def test_rapid_create_delete(self, api, api_client):
        """快速连续操作不崩溃"""
        for i in range(10):
            r = api_client.post(
                "/api/students",
                json={"name": f"批量{i}", "grade": "2026"},
            )
            assert r.status_code == 201
        # 清理
        r = api_client.get("/api/students?name=批量")
        for s in r.json()["data"]:
            api_client.delete(f"/api/students/{s['id']}")


# ── 第3周Day4：状态机测试 ─────────────────────────────────

class TestTokenStateMachine:
    """Token 生命周期状态机测试
    状态流转: 未登录 → 已登录(token有效) → 已注销(token无效)
    """

    def test_token_full_lifecycle(self, api, api_client):
        """状态机：登录→验证有效→注销→验证无效
        完整走一遍 token 从创建到销毁的状态流转
        """
        # 状态1: 未登录 → 登录，获取 token
        r = api_client.post(
            "/api/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert r.status_code == 200
        token = r.json()["token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 状态2: token有效 → /api/me 应返回200
        r = api_client.get("/api/me", headers=headers)
        assert r.status_code == 200
        assert r.json()["message"] == "token 有效"

        # 状态3: 注销 → token 应失效
        r = api_client.post("/api/logout", headers=headers)
        assert r.status_code == 200
        assert "已注销" in r.json()["message"]

        # 状态4: token无效 → /api/me 应返回401
        r = api_client.get("/api/me", headers=headers)
        assert r.status_code == 401
        assert "token 无效" in r.json()["error"]

    @pytest.mark.exception
    def test_forged_token_rejected(self, api, api_client):
        """异常：伪造 token 应被拒绝"""
        headers = {"Authorization": "Bearer fake_token_never_existed_12345"}
        r = api_client.get("/api/me", headers=headers)
        assert r.status_code == 401
        assert "token 无效" in r.json()["error"]

    @pytest.mark.exception
    def test_missing_auth_header(self, api, api_client):
        """异常：不带 Authorization 头访问鉴权接口"""
        r = api_client.get("/api/me")
        assert r.status_code == 401
        assert "未提供 token" in r.json()["error"]


class TestStudentStateMachine:
    """Student 生命周期状态机测试
    状态流转: 不存在 → 已创建 → 已修改 → 已删除(不存在)
    """

    def test_student_full_lifecycle(self, api, api_client):
        """状态机：创建→查询→更新→再查询→删除→确认不存在
        覆盖学生从生到死的完整状态流转
        """
        # 状态1: 创建学生 → 应返回201+id
        r = api_client.post(
            "/api/students",
            json={"name": "状态机测试", "grade": "2026", "score": 75},
        )
        assert r.status_code == 201
        sid = r.json()["data"]["id"]
        assert sid > 0

        # 状态2: 查询刚创建的学生 → 应存在且数据完整
        r = api_client.get(f"/api/students/{sid}")
        assert r.status_code == 200
        data = r.json()["data"]
        assert data["name"] == "状态机测试"
        assert data["grade"] == "2026"
        assert data["score"] == 75

        # 状态3: 更新 → 数据应变更
        r = api_client.put(
            f"/api/students/{sid}",
            json={"score": 95, "grade": "2025"},
        )
        assert r.status_code == 200
        assert r.json()["data"]["score"] == 95
        assert r.json()["data"]["grade"] == "2025"

        # 状态4: 再次查询 → 确认更新后数据
        r = api_client.get(f"/api/students/{sid}")
        assert r.status_code == 200
        assert r.json()["data"]["score"] == 95

        # 状态5: 删除 → 应成功
        r = api_client.delete(f"/api/students/{sid}")
        assert r.status_code == 200

        # 状态6: 删除后再次查询 → 应404
        r = api_client.get(f"/api/students/{sid}")
        assert r.status_code == 404

    @pytest.mark.exception
    def test_idempotent_delete(self, api, api_client):
        """异常：幂等删除 — 删除同一学生两次，第二次应404"""
        # 创建
        r = api_client.post(
            "/api/students",
            json={"name": "幂等测试", "grade": "2026"},
        )
        assert r.status_code == 201
        sid = r.json()["data"]["id"]

        # 第一次删除 → 成功
        r = api_client.delete(f"/api/students/{sid}")
        assert r.status_code == 200

        # 第二次删除 → 应404（已不存在）
        r = api_client.delete(f"/api/students/{sid}")
        assert r.status_code == 404

    @pytest.mark.slow
    def test_concurrent_update_race(self, api, api_client):
        """并发：对同一学生连续快速更新 → 最后一次更新应生效"""
        # 创建
        r = api_client.post(
            "/api/students",
            json={"name": "并发更新测试", "grade": "2026", "score": 50},
        )
        assert r.status_code == 201
        sid = r.json()["data"]["id"]

        # 快速连续更新3次（模拟并发写入）
        for score in [60, 70, 80]:
            r = api_client.put(
                f"/api/students/{sid}",
                json={"score": score},
            )
            assert r.status_code == 200

        # 最终查询 → 最后一次更新应生效（score=80）
        r = api_client.get(f"/api/students/{sid}")
        assert r.status_code == 200
        assert r.json()["data"]["score"] == 80

        # 清理
        api_client.delete(f"/api/students/{sid}")


class TestResponseSchema:
    """响应结构验证 — 确保各接口返回格式一致"""

    def test_health_schema(self, api, api_client):
        """健康检查响应结构"""
        r = api_client.get("/api/health")
        assert r.status_code == 200
        body = r.json()
        assert "status" in body
        assert body["status"] == "ok"

    def test_login_success_schema(self, api, api_client):
        """登录成功响应结构"""
        r = api_client.post(
            "/api/login",
            json={"username": "admin", "password": "admin123"},
        )
        assert r.status_code == 200
        body = r.json()
        assert "token" in body
        assert "username" in body
        assert len(body["token"]) == 32

        # 清理：注销 token
        api_client.post(
            "/api/logout",
            headers={"Authorization": f"Bearer {body['token']}"},
        )

    def test_list_schema(self, api, api_client):
        """列表响应结构：必须有 count 和 data 字段"""
        r = api_client.get("/api/students")
        assert r.status_code == 200
        body = r.json()
        assert "count" in body
        assert "data" in body
        assert isinstance(body["count"], int)
        assert isinstance(body["data"], list)
        # count 应与 data 长度一致
        assert body["count"] == len(body["data"])
