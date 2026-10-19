# 第2周第5天：测试数据管理 conftest

日期：2026-06-12（周五）

## 今天学的

### 1. conftest.py 的作用
- pytest 自动发现：同目录及子目录的测试文件自动加载
- 管理全局测试数据：账号密码、token、用户数据统一存放
- 封装公共前置逻辑：自动登录、准备测试用户

### 2. 实际操作
把散落在 `test_api.py` 里的硬编码数据全部抽出来：

| 创建的 fixture | 作用 |
|---------------|------|
| `valid_user` | 正常测试用户数据 |
| `invalid_user` | 异常测试用户数据 |
| `admin_user` | 管理员用户数据 |
| `auth_headers` | 自动登录获取 token |
| `test_student` | 预创建的测试学生 |
| `base_url` | API 地址统一配置 |

### 3. fixture ≠ 写测试用例
fixture 的角色是**管理数据 + 管理前置逻辑**，它不写测试逻辑，而是把准备好的"原料"注入给测试用例。

### 4. 产出
- `tests/conftest.py` — 8 个 fixture
- 30 条用例全部改用 fixture，不再硬编码
- `pytest tests/test_api.py -v` 30/30 ✅
- git commit：`79d6d7c`

## 今日达标检查
- [x] conftest.py 里至少有 3 个数据 fixture
- [x] 至少 5 条用例不再硬编码测试数据
- [x] 30 条全部通过
- [x] git commit
- [x] 第2周达标 ✅
