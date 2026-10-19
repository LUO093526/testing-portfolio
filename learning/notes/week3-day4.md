# 第3周 Day 4 (6/18) — 用例扩充：异常场景 + 状态机测试

## 主题
状态机测试 & 异常场景覆盖 — 让测试不只测"正常流程"

## 学到的新概念

### 1. 状态机测试
- **核心理念：** 不孤立测每个接口，而是测"状态流转链"
- **Token状态机：** 未登录 → 登录(token有效) → 注销(token无效) → 再次访问被拒
- **Student状态机：** 不存在 → 创建(存在) → 更新(修改) → 删除(不存在)
- 每条状态机测试至少覆盖3个状态跳变，验证每个状态下的行为

### 2. 幂等性测试
- 同一操作执行两次：第一次成功，第二次应返回预期错误(如404)
- 删除幂等：delete → 200, delete again → 404

### 3. 并发冲突模拟
- 同一资源快速连续更新 → 最后一次更新应生效
- 是简单版的 race condition 检测

### 4. 响应结构验证 (Schema Validation)
- 不只验证业务逻辑，还要验证响应格式一致性
- count 字段应与 data 数组长度一致
- token 长度应固定(32字符)

## 今日产出
- **新增9条测试用例**（test_api.py 29→39条）
- 新测试类：`TestTokenStateMachine`（3条）、`TestStudentStateMachine`（3条）、`TestResponseSchema`（3条）
- 全量80条 PASSED

## 还模糊的地方
- 真正的并发 race condition（多线程同时写同一资源）需要 threading 库，目前只是快速串行模拟
- 状态机覆盖度如何评估？需要更系统的状态图分析方法

## 关键代码片段
```python
# Token 完整生命周期
def test_token_full_lifecycle(self, api, api_client):
    # 登录 → 获取token
    r = api_client.post("/api/login", json={...})
    token = r.json()["token"]
    # 验证有效
    r = api_client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    # 注销
    api_client.post("/api/logout", headers=...)
    # 验证已失效
    r = api_client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401
```
