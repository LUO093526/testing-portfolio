# 第3周总结：pytest 框架深入（6/15-21）

> 本周从「会写测试」进阶到「会用框架」。pytest 的深度 = 面试区分度。

---

## 本周完成总览

| 天 | 日期 | 主题 | 产出 | 状态 |
|----|------|------|------|------|
| 1 | 6/15 | fixture 高级用法 | 四种 scope + yield/teardown | ✅ |
| 2 | 6/16 | parametrize 参数化 | 28条参数化用例，数据驱动 | ✅ |
| 3 | 6/17 | conftest.py 重构 | fixture 依赖链、消除重复 | ✅ |
| 4 | 6/18 | 用例扩充 30→87 | 状态机+Schema 验证 | ✅ |
| 5 | 6/19 | Selenium pytest 重构 | conftest + parametrize + web mark | ✅ |
| 6 | 6/20 | 查漏补缺 | 周总结+进度更新 | ✅ |

---

## 核心能力提升

### 1. Fixture Scope 四级（Day1）
- **function**: 每个测试独立，隔离性最强，最慢
- **class**: 类内共享，UI 测试常用
- **module**: 文件内共享，API 前置检查
- **session**: 全局唯一，测试数据/HTTP 会话
- **关键规则**: 窄 scope 能依赖宽 scope，反之不行

### 2. Parametrize 参数化（Day2）
- 一个装饰器替代 N 个重复函数
- 登录 10 组 + 注册 10 组 + 异常 8 组 = 28 条参数化用例
- 每组在 pytest 输出中独立显示，失败精确定位

### 3. Fixture 依赖链（Day3）
```
test_data(session) → login_credentials → token_per_function → auth_headers → authenticated_client
                 → valid_student → api_client + sample_student
```
- 集中管理、自动注入、消除硬编码
- conftest.py 从 150 行增长到 480 行（含详细注释）

### 4. 状态机测试（Day4）
- Token 生命周期: 未登录 → 有效 → 注销 → 失效
- Student 生命周期: 不存在 → 创建 → 更新 → 删除 → 不存在
- 新增响应 Schema 验证（count 一致性、token 长度）
- 用例数从 30 飙升到 87（含参数化展开）

### 5. Selenium 融入 pytest（Day5）
- conftest 管理 Selenium 配置（URL/账号/浏览器路径）
- parametrize 驱动 4 组错误登录场景
- `@pytest.mark.web` 标记，`pytest -m web` 独立运行

---

## 数据看板

| 指标 | 本周初 | 本周末 | 变化 |
|------|--------|--------|------|
| API 测试用例 | 30 | **87** | +57 🔥 |
| GitHub commits | 10 | **16** | +6 |
| 学习笔记 | 10 | **16** | +6 |
| 连续打卡 | 7 天 | **15 天** | +8 |
| 代码行数 | ~800 | **1972** | +1172 |

> 用例数爆炸是因为 parametrize 展开：28 组参数化 = 28 条独立用例。

---

## 面试自检

- [x] 能说清楚 fixture scope 4 个级别区别，以及各自使用场景
- [x] 至少有 2 个 parametrize 用例（实际 28 条）
- [x] conftest.py 里有共享 fixture 且有一条完整依赖链
- [x] 87 条 API 测试全部通过
- [x] Selenium Web UI 用例已重构为 pytest 格式（conftest + parametrize + mark）
- [x] 本周 6 次 commit

### 面试模拟问答

**Q: "pytest 的 fixture 机制你用过吗？"**
A: 用过。我在项目中实现了 4 种 scope 的 fixture。function scope 用于每个测试独立的 token，session scope 用于全局测试数据和 HTTP 会话复用。关键点是窄 scope 可以依赖宽 scope，但不能反向。我还用 yield 实现了 setup/teardown 模式——yield 前准备资源，yield 后清理。

**Q: "你怎么避免写重复用例？"**
A: 用 parametrize 装饰器。比如登录接口，我准备了 10 组数据（正常 3 组 + 密码错 3 组 + 空值 2 组 + 特殊字符 2 组），一个测试函数就覆盖了 10 种情况。每组在 pytest 输出中独立显示，失败能精确定位到哪组数据。

**Q: "你的测试数据怎么管理？"**
A: 统一放在 conftest.py 里。顶层是 TestData 这个 dataclass（session scope），所有账号密码、合法/非法数据、边界值全在这里。然后通过 fixture 依赖链逐层派生——login_credentials → token → auth_headers → authenticated_client。这样数据变更只改一处，所有测试自动生效。

**Q: "Selenium 测试怎么和 pytest 结合？"**
A: 我把 Web 测试也纳入了 pytest 框架。conftest 里用 selenium_config fixture 管理 URL 和账号（session scope），driver fixture 自动读取配置创建浏览器实例（class scope 复用）。登录测试用 parametrize 驱动多组错误场景，加了 @pytest.mark.web 标记，可以用 pytest -m web 单独跑。

---

## 还模糊的地方

1. **Selenium 外部依赖**：测试依赖外网服务器 124.223.155.95:8088，5 条 UI 用例因网络/验证码失败。需要确认 CI 环境如何处理
2. **并发测试**：当前只是快速串行模拟并发冲突，真正的多线程 race condition 需要用 threading 库
3. **状态机覆盖度**：如何系统评估状态图覆盖？需要更形式化的方法

---

## 下周预告：第4周 Linux 实操（6/22-28）

- Day1 跳过（学校已掌握 useradd/chmod/chown）
- 直入 Nginx+Flask 部署
- systemd 服务管理
- 日志排查实战（journalctl/tail/grep）
- 目标：第 1 个月 GitHub 全绿（28 天）
