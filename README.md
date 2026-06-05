 # 学员管理系统 API 自动化测试

 ![API Tests](https://github.com/LUO093526/testing-portfolio/actions/workflows/test.yml/badge.svg)

  ## 技术栈
  - Python 3.10 + Flask 3.x
  - pytest 9.0 + requests
  - JMeter 5.6

  ## 快速开始

  ### 启动API
  ./run.sh start

  ### 运行测试
  ./run.sh test        # 冒烟测试（4条）
  ./run.sh test-all    # 全部测试 + HTML报告
  ./run.sh test-crud   # CRUD测试

  ### 停止
  ./run.sh stop

  ### JMeter压测
  用JMeter打开 jmeter/student-api-load-test.jmx
  3个场景：基础负载(50并发) / 峰值压力(200并发) / 写操作(20并发)

  ## 测试覆盖
  - 冒烟测试：健康检查、列表、筛选
  - CRUD：新增/查询/更新/删除 + 异常场景
  - 数据验证：默认值、特殊字符
  - 并发测试：快速连续操作

  ## 报告
  运行测试后查看 reports/report.html
