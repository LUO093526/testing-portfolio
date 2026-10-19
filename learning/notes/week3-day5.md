# 第3周 Day 5 (6/19) — Selenium pytest重构：conftest + parametrize

## 主题
把 Selenium Web UI 测试真正融入 pytest 框架 — conftest 共享配置 + parametrize 数据驱动

## 重构内容

### 1. Selenium 配置集中化
- **原来：** 硬编码 `LOGIN_URL`、`VALID_USERNAME`、`VALID_PASSWORD`、`CHROMIUM_PATH`、`CHROMEDRIVER_PATH`
- **现在：** 统一放入 conftest 的 `selenium_config` fixture（scope=session）
- 好处：路径/账号变更只改一处，所有 Web 测试自动生效

### 2. parametrize 参数化
- 正向登录：`@parametrize` 驱动多组有效账号 → 可扩展
- 反向登录：4组错误数据（错用户名/错密码/空用户名/空密码）→ 以前只测1种
- 每组数据显示为独立用例名，失败一目了然

### 3. pytest 标记体系
- 新增 `@pytest.mark.web` 标记（pytest.ini 已注册）
- 保留 `@pytest.mark.selenium` 兼容旧命令
- `pytest -m web` → 只跑7条 UI 用例
- `pytest -m "not (selenium or web)"` → 跳过 UI，只跑 API

### 4. conftest 依赖注入
- `driver` fixture 从 `selenium_config` 读取浏览器路径
- `logged_in_driver` fixture 从 `selenium_config` 读取账号密码
- 测试函数只关心"我要什么"，不关心"从哪来"

## Fixture 依赖链（新增 Selenium 分支）
```
selenium_config (session) ──────────────────────┐
    │                                            │
    ├── driver (class) ← chromium_path          │
    │       │                                    │
    │       └── logged_in_driver (class) ← username/password
    │                                            │
    └── 测试函数直接引用 config 读配置
```

## 今日产出
- 重构 `test_login_pytest.py`：6个旧测试 → 7个新测试（含4组 parametrize）
- conftest 新增 `selenium_config` fixture
- pytest.ini 注册 `web` 标记
- `pytest -m web` 可正确收集7条测试

## 面试映射
| 做的事 | 面试对应 |
|--------|---------|
| conftest 共享 Selenium 配置 | "Selenium 测试怎么管理配置？" |
| parametrize 多组登录 | "登录页面你测了多少种情况？" |
| pytest -m web 分类运行 | "怎么区分 UI 测试和 API 测试？" |

## 还模糊的地方
- Selenium 需要外部网站（124.223.155.95:8088），本地跑时会因网络/验证码 skip → 需确认 CI 环境如何处理
- ddddocr 验证码识别准确率有限，是否有更好方案？
