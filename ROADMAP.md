# 🗺️ 测试工程师半年冲刺路线（大二→实习）v2

> ⚠️ 2026-06-03 修正：扫描D盘课程文件后发现你的真实水平远高于最初估计。
> 你已经在做 Selenium + unittest + ddddocr + PO 模式 + JMeter 了！

---

## 🎯 你的真实能力画像

| 技能 | 水平 | 证据 |
|------|------|------|
| Web自动化 | ⭐⭐⭐ | Selenium + unittest + ddddocr验证码 + PO模式 + 项目答辩 |
| API测试 | ⭐ | 基础requests，需加强pytest |
| JMeter | ⭐⭐ | 已装5.6.3，有备份测试计划，学过线程组/断言/参数化/关联 |
| Linux | ⭐⭐ | 有课程+作业+笔记，需加强实操 |
| 抓包 | ⭐⭐ | Fiddler已装，有使用笔记 |
| 工具链 | ⭐⭐⭐ | Apifox/Postman/Allure/phpStudy/JDK全装好了 |
| CI/CD | ⭐ | 尚未开始 |
| GitHub | ⭐ | 尚未开始 |

---

## ⏱️ 修正后时间线

```
6月 │7月 │8月 │9月 │10月 │11月 │12月→投简历实习
────┼────┼────┼────┼────┼────┼────────────
 pytest│ 整合 │ JMeter│ CI/CD│ 作品集│ 海投
 迁移  │ 项目 │ 深入  │ GitHub│ 简历  │ 面试
```

与原计划的关键区别：
- ❌ 跳过 Python基础（你已经在用了）
- ❌ 跳过 JMeter入门（你已装好，学过线程组/断言/参数化/关联）
- ✅ 重点：unittest→pytest迁移、API测试深度、CI/CD、GitHub作品集
────┼────┼────┼────┼────┼────┼────────────
 基础 │ 自动化 │ 性能  │ 项目 │ 简历 │ 海投
 Python│ pytest │ JMeter│ 作品集│ 面试 │ 面试
 接口  │ CI/CD  │ Linux │ 报告  │ 准备 │
```

---

## 📅 第一阶段：基础夯实（6月-7月中旬，6周）

### Python 测试脚本能力
- [ ] Python 基础：列表/字典/函数/异常处理
- [ ] requests 库：GET/POST/PUT/DELETE，header，token，json body
- [ ] JSON 解析和断言
- [ ] 用 Python 写 20 个接口测试脚本

### Linux 实操能力
- [ ] 用 Linux 搭一套测试环境：Nginx + MySQL + Flask 应用
- [ ] 配置 systemd 管理服务
- [ ] 查看日志：journalctl, tail, grep
- [ ] 写 Shell 脚本自动化环境部署

**检验标准：** 能独立用 Python 调通任意 REST API 并写断言

---

## 📅 第二阶段：自动化测试（7月中旬-9月，6周）

### pytest 测试框架
- [ ] fixture/conftest/parametrize/mark
- [ ] 测试报告：pytest-html, allure
- [ ] 数据驱动测试（用 Excel/JSON 做测试数据）
- [ ] 写 50+ 条自动化用例（覆盖你现在这个 Flask 项目）

### CI/CD 基础
- [ ] Git 工作流（commit/pr/merge）
- [ ] GitHub Actions：push 自动跑测试
- [ ] Jenkins 基础：拉代码→跑测试→发报告

**检验标准：** GitHub 上有项目，push 代码自动跑测试并生成报告

---

## 📅 第三阶段：性能测试深入（9月-10月，4周）

### JMeter 进阶
- [ ] 参数化：CSV 数据驱动
- [ ] 断言：响应断言 + JSON 断言
- [ ] 混合场景设计：读多写少
- [ ] 看懂聚合报告：Avg/90%Line/Throughput/Error%

### 性能分析
- [ ] Linux 服务器监控：top/htop/iostat/netstat
- [ ] 定位瓶颈：CPU 高还是 I/O 高？
- [ ] 写一份正式的压测报告（直接放简历里）

**检验标准：** 能独立完成一个系统的压测并写出合格报告

---

## 📅 第四阶段：项目作品集（10月-11月，4周）

在 GitHub 上打造 2 个作品：

### 作品1：API 自动化测试项目（你现在这个）
```
testing-portfolio/
├── api/              ← Flask REST API（被测系统）
├── tests/            ← pytest 自动化用例 50+
├── jmeter/           ← JMeter 压测脚本
├── reports/          ← 测试报告 HTML/PDF
└── .github/workflows ← CI 自动运行测试
```

### 作品2：实战项目随便挑一个
- 对 XX 开源项目写测试（如 RuoYi / 若依）
- 或者拿学校系统/校园 App 写接口测试
- 或者用 Postman 导出一套 Collection + 环境变量

**关键：README 写清楚你怎么测的、找到什么 bug、压测结论**

---

## 📅 第五阶段：简历+面试（11月-12月）

### 简历关键词（根据你实际学会的勾选）
```
√ Linux 系统管理、Shell 脚本
√ 接口测试：JMeter 参数化/断言/混合场景
√ 自动化测试：Python + pytest + requests + CI/CD
√ 测试报告编写
√ Git 协作
```

### 简历上的项目描述模板
> **学员管理系统 API 自动化测试**（个人项目）
> - 搭建 Flask REST API 作为被测系统，设计 16+ 条测试用例
> - 使用 pytest + requests 实现自动化回归测试，通过率 100%
> - 编写 JMeter 混合场景压测脚本（50/200并发），生成性能分析报告
> - 配置 GitHub Actions 实现 push 自动运行测试
> - 测试报告地址：github.com/你的ID/testing-portfolio

### 投递策略
- 目标：中小互联网公司、外包公司、软件测试岗
- 渠道：BOSS直聘 > 拉勾 > 实习僧 > 学校招聘会
- 数量：至少投 100 份，别玻璃心
- 底线薪资：一线城市实习 4-6K，转正 7-10K

---

## 📚 推荐资源（全免费）

| 内容 | 资源 |
|------|------|
| Python | B站"黑马程序员Python" |
| pytest | 官方文档 + B站"pytest全栈自动化测试" |
| JMeter | B站"JMeter性能测试入门到精通" |
| Linux | 鸟哥私房菜（在线免费）+ 你的WSL就是练习场 |
| 面试 | 牛客网刷测试面试题 |

---

## ⚠️ 别踩的坑

1. ❌ 不要学太多框架（只学 pytest，别碰 unittest/TestNG）
2. ❌ 不要追求"全栈"（别在简历写 React+Vue+Spring，测试岗不需要）
3. ❌ 不要等"学完再投"（11月就开始投，面试是最好的学习）
4. ✅ Python 往深学，面试必问：装饰器、生成器、上下文管理器
5. ✅ GitHub 必须绿，从现在开始每天至少一次 commit

---

## 🎯 今天的第一个 commit

```bash
cd ~/testing-portfolio
git init
git add .
git commit -m "feat: 初始化测试项目 — Flask API + pytest + JMeter"
```

做完这个 commit，你的测试之路就正式开始了。
