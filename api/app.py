"""学员管理系统 API — 为测试实战而生
GET    /api/students       — 学生列表（支持 ?name=&grade= 筛选）
GET    /api/students/<id>  — 单个学生
POST   /api/students       — 新增学生
PUT    /api/students/<id>  — 更新学生
DELETE /api/students/<id>  — 删除学生
GET    /api/health         — 健康检查
"""

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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
