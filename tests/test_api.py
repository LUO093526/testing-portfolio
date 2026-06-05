"""学员管理系统 API 自动化测试
运行方式:
    pytest tests/test_api.py -v                    # 基础运行
    pytest tests/test_api.py -v --html=reports/report.html  # 生成HTML报告
    pytest tests/test_api.py -v -m smoke           # 仅冒烟测试
    pytest tests/test_api.py -v -m "not slow"      # 跳过慢速测试
"""

import pytest
import requests

BASE_URL = "http://127.0.0.1:5000"


# ── Fixtures ──────────────────────────────────────────────

@pytest.fixture(scope="module")
def api():
    """确保 API 已启动"""
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=3)
        assert r.status_code == 200
    except requests.ConnectionError:
        pytest.exit("❌ API 未启动！请先执行: python api/app.py")


@pytest.fixture
def sample_student(api):
    """创建一个测试用学生，测试完自动清理"""
    r = requests.post(
        f"{BASE_URL}/api/students",
        json={"name": "测试学生", "grade": "2026", "score": 88},
    )
    assert r.status_code == 201
    sid = r.json()["data"]["id"]
    yield sid
    requests.delete(f"{BASE_URL}/api/students/{sid}")


# ── 冒烟测试 ──────────────────────────────────────────────

@pytest.mark.smoke
class TestHealthCheck:
    def test_health_returns_200(self, api):
        r = requests.get(f"{BASE_URL}/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.smoke
class TestStudentList:
    def test_list_returns_200_and_data(self, api):
        """GET /api/students 返回列表"""
        r = requests.get(f"{BASE_URL}/api/students")
        assert r.status_code == 200
        body = r.json()
        assert "count" in body
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_filter_by_name(self, api):
        """按姓名模糊筛选"""
        r = requests.get(f"{BASE_URL}/api/students?name=张")
        assert r.status_code == 200
        names = [s["name"] for s in r.json()["data"]]
        assert all("张" in n for n in names)

    def test_filter_by_grade(self, api):
        """按年级精确筛选"""
        r = requests.get(f"{BASE_URL}/api/students?grade=2025")
        assert r.status_code == 200
        grades = [s["grade"] for s in r.json()["data"]]
        assert all(g == "2025" for g in grades)


# ── CRUD 完整测试 ─────────────────────────────────────────

@pytest.mark.crud
class TestCreateStudent:
    def test_create_success(self, api):
        """正常新增"""
        r = requests.post(
            f"{BASE_URL}/api/students",
            json={"name": "新同学", "grade": "2026", "score": 95},
        )
        assert r.status_code == 201
        sid = r.json()["data"]["id"]
        # 清理
        requests.delete(f"{BASE_URL}/api/students/{sid}")

    def test_create_missing_name(self, api):
        """缺少必填字段应返回 400"""
        r = requests.post(f"{BASE_URL}/api/students", json={"grade": "2026"})
        assert r.status_code == 400
        assert "error" in r.json()

    def test_create_empty_body(self, api):
        """空请求体应返回 400"""
        r = requests.post(f"{BASE_URL}/api/students")
        assert r.status_code == 400

    def test_create_negative_grade(self, api):
        """grade传入负数应正常创建"""
        r = requests.post(
            f"{BASE_URL}/api/students",
            json={"name": "测试负数年级", "grade": "-1", "score": 80},
        )
        assert r.status_code == 201
        assert r.json()["data"]["grade"] == "-1"
        sid = r.json()["data"]["id"]
        # 清理
        requests.delete(f"{BASE_URL}/api/students/{sid}")

    def test_create_negative_score(self, api):
        """score传入负数应正常创建"""
        r = requests.post(
            f"{BASE_URL}/api/students",
            json={"name": "测试负分数", "grade": "2026", "score": -100},
        )
        assert r.status_code == 201
        assert r.json()["data"]["score"] == -100
        sid = r.json()["data"]["id"]
        # 清理
        requests.delete(f"{BASE_URL}/api/students/{sid}")

    def test_create_empty_name(self, api):
        """name为空字符串应正常创建"""
        r = requests.post(
            f"{BASE_URL}/api/students",
            json={"name": "", "grade": "2026", "score": 80},
        )
        assert r.status_code == 201
        assert r.json()["data"]["name"] == ""
        sid = r.json()["data"]["id"]
        # 清理
        requests.delete(f"{BASE_URL}/api/students/{sid}")


@pytest.mark.crud
class TestGetStudent:
    def test_get_existing(self, api, sample_student):
        """获取存在的学生"""
        r = requests.get(f"{BASE_URL}/api/students/{sample_student}")
        assert r.status_code == 200
        assert r.json()["data"]["name"] == "测试学生"

    def test_get_nonexistent(self, api):
        """获取不存在的学生应返回 404"""
        r = requests.get(f"{BASE_URL}/api/students/99999")
        assert r.status_code == 404


@pytest.mark.crud
class TestUpdateStudent:
    def test_update_success(self, api, sample_student):
        """正常更新"""
        r = requests.put(
            f"{BASE_URL}/api/students/{sample_student}",
            json={"score": 100},
        )
        assert r.status_code == 200
        assert r.json()["data"]["score"] == 100

    def test_update_nonexistent(self, api):
        """更新不存在的学生应返回 404"""
        r = requests.put(
            f"{BASE_URL}/api/students/99999",
            json={"score": 100},
        )
        assert r.status_code == 404

    def test_update_empty_body(self, api, sample_student):
        """更新时body为空应返回 400"""
        r = requests.put(f"{BASE_URL}/api/students/{sample_student}")
        assert r.status_code == 400
        assert "error" in r.json()


@pytest.mark.crud
class TestDeleteStudent:
    def test_delete_success(self, api):
        """正常删除"""
        r = requests.post(
            f"{BASE_URL}/api/students",
            json={"name": "待删除", "grade": "2026", "score": 60},
        )
        sid = r.json()["data"]["id"]
        r = requests.delete(f"{BASE_URL}/api/students/{sid}")
        assert r.status_code == 200
        # 再次获取应 404
        r = requests.get(f"{BASE_URL}/api/students/{sid}")
        assert r.status_code == 404

    def test_delete_nonexistent(self, api):
        """删除不存在学生应返回 404"""
        r = requests.delete(f"{BASE_URL}/api/students/99999")
        assert r.status_code == 404


# ── 数据验证测试 ──────────────────────────────────────────

class TestDataValidation:
    """接口文档里没写的，也要测"""

    def test_score_default_zero(self, api):
        """不传 score 时默认为 0"""
        r = requests.post(
            f"{BASE_URL}/api/students",
            json={"name": "无分数", "grade": "2026"},
        )
        assert r.status_code == 201
        sid = r.json()["data"]["id"]
        assert r.json()["data"]["score"] == 0
        requests.delete(f"{BASE_URL}/api/students/{sid}")

    def test_special_characters_in_name(self, api):
        """特殊字符处理"""
        r = requests.post(
            f"{BASE_URL}/api/students",
            json={"name": "test<script>alert(1)</script>", "grade": "2026"},
        )
        assert r.status_code == 201
        sid = r.json()["data"]["id"]
        requests.delete(f"{BASE_URL}/api/students/{sid}")


# ── 并发测试（简易）───────────────────────────────────────

class TestConcurrency:
    @pytest.mark.slow
    def test_rapid_create_delete(self, api):
        """快速连续操作不崩溃"""
        for i in range(10):
            r = requests.post(
                f"{BASE_URL}/api/students",
                json={"name": f"批量{i}", "grade": "2026"},
            )
            assert r.status_code == 201
        # 清理
        r = requests.get(f"{BASE_URL}/api/students?name=批量")
        for s in r.json()["data"]:
            requests.delete(f"{BASE_URL}/api/students/{s['id']}")
