# 第3周第3天 — conftest.py 重构

> 📅 2026年6月17日（周三）| ⏱️ 约1小时

## 当天主题

**conftest.py 重构：公共逻辑抽离、fixture 依赖链**

## 学到的新概念

### 1. 单一数据源原则（Single Source of Truth）
- 所有测试数据集中在一个 `TestData` 类中管理
- 不再在多个文件里硬编码相同的测试账号密码
- 好处：改一处全改，数据一致性有保障

### 2. Fixture 依赖链
```
test_data → login_credentials → token_per_function → auth_headers → authenticated_client
```
每一层只做一件事，层层组合成最终需要的鉴权客户端。

### 3. 依赖链设计原则
- 宽 scope 不能依赖窄 scope（session 不能依赖 function）
- 每层只依赖紧邻的上一层
- 依赖链越清晰，排查问题越容易

### 4. scope 匹配规则
- `token_session`（session）用 `api_session`（session）而不是 `api_client`（function）
- 因为 function scope 比 session scope 窄，session fixture 不能依赖 function fixture

## 产出物

| 产出 | 详情 |
|------|------|
| conftest.py | 重构：新增 TestData 类、test_data/login_credentials/authenticated_client/sample_student fixture |
| test_api.py | 移除 sample_student fixture（已迁移到 conftest） |
| 测试验证 | 71/71 PASSED ✅ |
| Git commit | `e625a65` — refactor: conftest统一管理，建立fixture依赖链 |

## 还模糊的地方
- `authenticated_client` 实际使用场景还不多，后续测试可以多用它简化代码

## 明日预告
第3周第4天：用例扩充 30→35 — 异常场景、状态机测试
