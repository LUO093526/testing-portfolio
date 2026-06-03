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

---

## 📅 第一阶段：pytest迁移 + 基础补充（现在-7月初，4周）

### 你已有的（不用学）
- [x] Python 基础 ✅
- [x] unittest 框架 ✅
- [x] Selenium Web自动化 ✅
- [x] JMeter 入门 ✅

### 要做的
- [ ] unittest → pytest 迁移：把 page_login_unittest.py 改写为 pytest
- [ ] 给 Flask API 写 20+ 条 pytest 用例（目前16条，加4条）
- [ ] Git 每日提交（保持绿点）
- [ ] 敲完 Linux L01-L04 练习

**检验标准：** 能用 pytest 独立写接口测试，GitHub 提交 20+ 次

---

## 📅 第二阶段：API测试深度 + JMeter深入（7-8月，暑假8周）

### pytest 测试框架
- [ ] fixture/conftest/parametrize/mark
- [ ] 测试报告：pytest-html, allure
- [ ] 数据驱动测试（用 Excel/JSON 做测试数据）
- [ ] 写 50+ 条自动化用例（覆盖你现在这个 Flask 项目）

### JMeter 进阶
- [ ] 参数化：CSV 数据驱动
- [ ] 断言：响应断言 + JSON 断言
- [ ] 混合场景设计：读多写少
- [ ] 看懂聚合报告：Avg/90%Line/Throughput/Error%
- [ ] 写一份正式的压测报告

### Linux 实操
- [ ] 用 Linux 搭一套测试环境：Nginx + MySQL + Flask 应用
- [ ] 配置 systemd 管理服务
- [ ] 查看日志：journalctl, tail, grep
- [ ] 写 Shell 脚本自动化环境部署

**检验标准：** GitHub 上有项目，push 代码自动跑测试并生成报告

---

## 📅 第三阶段：CI/CD + 作品集完善（9-10月，开学后）

### CI/CD
- [ ] GitHub Actions：push 自动跑 pytest
- [ ] allure 测试报告自动生成
- [ ] 了解 Jenkins 基础概念

### 作品集
- [ ] testing-portfolio 完善到 50+ 用例
- [ ] 写 2 份正式压测报告（PDF）
- [ ] README 写清楚：怎么测、测了什么、发现什么问题

**检验标准：** GitHub 项目有 CI badge，README 有截图，测试报告可查

---

## 📅 第四阶段：简历+面试（11月-12月）

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

1. ❌ 不要学太多框架（学 pytest 就够了，你的 unittest 经验已够用）
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
