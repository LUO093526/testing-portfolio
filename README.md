# 简易用户管理 API 测试平台

![API Tests](https://github.com/LUO093526/testing-portfolio/actions/workflows/test.yml/badge.svg)

> 12周测试工程师学习计划配套实战项目 | 2026.06 — 2026.08

## 项目简介

独立完成的全流程 API 测试项目。核心接口包括**登录、用户注册、用户查询/修改、分页列表查询、用户状态启停** 5 大模块。

## 技术栈

| 层次 | 技术 | 说明 |
|------|------|------|
| 被测系统 | Python Flask 3.x | 自建 REST API 服务 |
| 接口自动化 | pytest 9.0 + requests | 50+ 条自动化测试用例 |
| Web 自动化 | Selenium + pytest | 后台管理 UI 测试 |
| 性能测试 | JMeter 5.6 | CSV 参数化压测 + 混合场景 |
| 测试报告 | pytest-html + Allure | 可视化报告 |
| CI/CD | GitHub Actions | push 自动跑测试 |
| 环境 | WSL2 + Linux + Nginx | 测试环境部署 |

## 项目结构

```
testing-portfolio/
├── api/                    # Flask API 被测系统
│   └── app.py
├── tests/                  # 自动化测试
│   ├── conftest.py         # 全局 fixture + 测试数据
│   ├── test_api.py         # 接口自动化用例
│   └── test_login_pytest.py # Web UI 用例
├── data/                   # 测试数据文件
│   └── test_data.xlsx      # Excel 数据驱动
├── docs/                   # 文档
│   ├── api-spec.md         # 接口说明
│   ├── testcase-table.md   # 用例总表
│   ├── equivalent-class-analysis.md
│   ├── boundary-value-analysis.md
│   └── orthogonal-analysis.md
├── jmeter_script/          # JMeter 脚本 + 压测报告
├── reports/                # 测试报告
├── logs/                   # 运行日志
├── notes/                  # 学习笔记
├── .github/workflows/      # CI 配置
└── README.md
```

## 快速开始

### 启动 API 服务
```bash
./run.sh start
```

### 运行测试
```bash
./run.sh test         # 冒烟测试
./run.sh test-all     # 全部测试 + HTML 报告
pytest -m smoke       # 只跑冒烟用例
pytest -m "not slow"  # 跳过慢用例
```

### 生成测试报告
```bash
pytest --html=reports/report.html                    # HTML 报告
pytest --alluredir=allure-results && allure serve .   # Allure 报告
```

### 停止服务
```bash
./run.sh stop
```

## 测试覆盖（累计 50+ 条）

| 类型 | 数量 | 方法 |
|------|------|------|
| 功能测试 | 20+ | 等价类 + 边界值 |
| 异常测试 | 15+ | 无效输入、token 异常 |
| 边界值测试 | 10+ | 刚好等于/小于/大于 |
| 正交组合 | 5+ | 多条件排列精简 |
| 并发测试 | JMeter | CSV 参数化 100 用户 |

## 学习路线

```
第1周 ✅ 读懂代码 → 第2周 🔴 测试设计 → 第3周 pytest深入 → 第4周 Linux实操
→ 第5-6周 API深度 → 第7-8周 JMeter深入 → 第9-10周 CI/CD → 第11-12周 求职
```

详见 [`LEARNING-PLAN.md`](./LEARNING-PLAN.md) 和 [`PROGRESS.md`](./PROGRESS.md)

## 关键指标

| 指标 | 当前 | 目标 |
|------|------|------|
| API 测试用例 | 20 | 50+ |
| GitHub Commits | 3 | 60+ |
| 学习笔记 | 4 | 40+ |
| 连续打卡 | 4 天 | 84 天 |

---

> 🤖 本项目全程使用 Claude Code 辅助学习：AI = 导师 → 副驾驶 → 协作者
