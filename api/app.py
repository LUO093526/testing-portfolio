"""学员管理系统 API — 为测试实战而生
GET    /api/students       — 学生列表（支持 ?name=&grade= 筛选）
GET    /api/students/<id>  — 单个学生
POST   /api/students       — 新增学生
PUT    /api/students/<id>  — 更新学生
DELETE /api/students/<id>  — 删除学生
GET    /api/health         — 健康检查
POST   /api/login          — 登录（返回 token，第3周新增）
"""

import time
import hashlib
from flask import Flask, request, jsonify

app = Flask(__name__)

# 内存数据库
students = [
    {"id": 1, "name": "张三", "grade": "2024", "score": 85},
    {"id": 2, "name": "李四", "grade": "2024", "score": 72},
    {"id": 3, "name": "王五", "grade": "2025", "score": 90},
]
next_id = 4


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/students", methods=["GET"])
def list_students():
    name = request.args.get("name")
    grade = request.args.get("grade")
    result = students
    if name:
        result = [s for s in result if name in s["name"]]
    if grade:
        result = [s for s in result if s["grade"] == grade]
    return jsonify({"count": len(result), "data": result})


@app.route("/api/students/<int:sid>", methods=["GET"])
def get_student(sid):
    s = next((s for s in students if s["id"] == sid), None)
    if s is None:
        return jsonify({"error": "学生不存在"}), 404
    return jsonify({"data": s})


@app.route("/api/students", methods=["POST"])
def create_student():
    body = request.get_json(force=True, silent=True)
    if not body or "name" not in body or "grade" not in body:
        return jsonify({"error": "name 和 grade 为必填字段"}), 400
    global next_id
    s = {"id": next_id, "name": body["name"], "grade": body["grade"], "score": body.get("score", 0)}
    next_id += 1
    students.append(s)
    return jsonify({"data": s}), 201


@app.route("/api/students/<int:sid>", methods=["PUT"])
def update_student(sid):
    s = next((s for s in students if s["id"] == sid), None)
    if s is None:
        return jsonify({"error": "学生不存在"}), 404
    body = request.get_json(force=True, silent=True)
    if not body:
        return jsonify({"error": "请求体为空"}), 400
    s["name"] = body.get("name", s["name"])
    s["grade"] = body.get("grade", s["grade"])
    s["score"] = body.get("score", s["score"])
    return jsonify({"data": s})


@app.route("/api/students/<int:sid>", methods=["DELETE"])
def delete_student(sid):
    s = next((s for s in students if s["id"] == sid), None)
    if s is None:
        return jsonify({"error": "学生不存在"}), 404
    students.remove(s)
    return jsonify({"message": f"学生 {sid} 已删除"})


# ── 第3周新增：登录鉴权端点 ──────────────────────────────

# 合法用户表（硬编码，演示用）
VALID_USERS = {
    "admin": "admin123",
    "testuser": "test123",
    "zhangsan": "pass456",
}

# 已签发的 token 集合（用于 /api/me 验证）
_active_tokens = set()


def _make_token(username: str) -> str:
    """生成简单 token：时间戳 + 用户名 的 SHA256 前16位"""
    raw = f"{username}:{time.time()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


@app.route("/api/login", methods=["POST"])
def login():
    """用户登录，返回 token"""
    body = request.get_json(force=True, silent=True)
    if not body:
        return jsonify({"error": "请求体为空"}), 400

    username = body.get("username", "")
    password = body.get("password", "")

    if not username or not password:
        return jsonify({"error": "username 和 password 为必填字段"}), 400

    if username not in VALID_USERS or VALID_USERS[username] != password:
        return jsonify({"error": "用户名或密码错误"}), 401

    token = _make_token(username)
    _active_tokens.add(token)
    return jsonify({"token": token, "username": username}), 200


@app.route("/api/me", methods=["GET"])
def me():
    """验证 token 有效性（第3周 fixture teardown 演示）"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "未提供 token"}), 401

    token = auth[len("Bearer "):]

    if token not in _active_tokens:
        return jsonify({"error": "token 无效或已注销"}), 401

    return jsonify({"message": "token 有效", "token": token}), 200


@app.route("/api/logout", methods=["POST"])
def logout():
    """注销 token（模拟 token 失效）"""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "未提供 token"}), 401

    token = auth[len("Bearer "):]
    _active_tokens.discard(token)
    return jsonify({"message": "已注销"}), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
