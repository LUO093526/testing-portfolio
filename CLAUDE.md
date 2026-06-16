# testing-portfolio — 测试工程师学习项目

> 12周学习计划 | 6/3-8/23 | [`LEARNING-PLAN.md`](./LEARNING-PLAN.md) | [`PROGRESS.md`](./PROGRESS.md)

## 项目上下文
- **项目：** 简易用户管理 API 测试平台（Flask + pytest + JMeter + CI/CD）
- **用户：** 大二软件技术，2026年底实习，目标是初级测试工程师
- **当前进度：** 第2周第1天（6/8周一），等价类深入
- **关键原则：** AI辅助但不替代思考；所有产出落地到本项目；每天 commit

## 高频操作
```bash
./run.sh start          # 启动 Flask API
pytest tests/ -v        # 跑全部测试
pytest -m smoke         # 只跑冒烟
./run.sh stop           # 停止服务
git log --oneline       # 查看提交历史
```

---

# 技能自动触发规则 — 全 54 技能分类

> 匹配到触发条件时，**必须先调用 Skill 工具**，再给文字回答。
> 一个回合只触发最匹配的 1 个。吃不准就不触发。

---

## 🧠 思考与决策（10 技能）

| 技能 | 触发词/场景 |
|------|-----------|
| `5whys` | 「为什么出错」「根因」「深层原因」「bug 怎么来的」；反复出现的问题 |
| `ooda` | 「怎么选」「方案对比」「决策」「选 A 还是 B」；多个选项犹豫 |
| `socratic` | 「为什么这样设计」「这个需求合理吗」「深层假设是什么」；质疑需求 |
| `premortem` | 「上线前」「发布风险」「可能出什么问题」「万一失败」；重大操作前 |
| `postmortem` | 「复盘」「事故分析」「故障回顾」「这次出了什么问题」 |
| `redteam` | 「安全漏洞」「怎么被攻击」「有什么弱点」「绕过方式」；review 代码安全 |
| `retro` | 「回顾这周」「总结本周」「Sprint 回顾」「改进点」；周期性反思 |
| `moscow` | 「优先级」「先做哪个」「P0/P1」「哪些最重要」；一堆事排不开 |
| `brainstorming` | 「新功能」「创意想法」「做个什么东西」；任何创造性工作前 |
| `self-evolve` | 「进化」「升级」「自我改进」「能力评估」「检查新能力」 |

---

## 💻 写代码（6 技能）

| 技能 | 触发词/场景 |
|------|-----------|
| `test-driven-development` | 「写功能」「实现」「加个接口」「新特性」；写任何新代码前 |
| `software-engineer` | 架构评审、代码质量标准、多模块设计；team-executor 自动分配 |
| `implement-issue` | 「处理 issue #N」「做这个 issue」；给 issue 编号或 URL |
| `systematic-debugging` | 「报错了」「挂了」「不工作」「bug」；任何异常/失败/意外行为 |
| `verification-before-completion` | 声称「完成了」「修好了」「通过了」之前 | 自动验证 |
| `using-git-worktrees` | 「开始新功能」「开分支开发」；需要隔离工作区 |

---

## 🧪 测试（1 技能）

| 技能 | 触发词/场景 |
|------|-----------|
| `webapp-testing` | 「测一下页面」「截图」「浏览器调试」「前端验证」；Playwright 操作 |

---

## 📋 项目流程（8 技能）

| 技能 | 触发词/场景 |
|------|-----------|
| `writing-plans` | 「做个计划」「怎么实现」「设计方案」；多步骤任务，动手前 |
| `executing-plans` | 已有书面计划要执行，需要 review checkpoint |
| `finishing-a-development-branch` | 「做完了」「代码写好了，怎么合并」；实现完成、测试通过 |
| `dispatching-parallel-agents` | 「同时做 A 和 B」；2+ 独立任务无依赖 |
| `subagent-driven-development` | 执行有多任务并行需求的实现计划 |
| `team-executor` | 「构建这个」「做这个项目」「帮我实现」；大段需求描述需要分解 |
| `requesting-code-review` | 「检查一下代码」「review 一下」；完成任务后、合并前 |
| `receiving-code-review` | 收到 code review 反馈后、实施建议前 |

---

## 📄 文档与办公（6 技能）

| 技能 | 触发词/场景 |
|------|-----------|
| `docx` | 「Word 文档」「.docx」「报告文档」「出个报告」；任何 Word 文件操作 |
| `pptx` | 「PPT」「幻灯片」「演示文稿」「.pptx」「deck」「做 presentation」 |
| `pdf` | 「PDF」「.pdf」；提取/合并/拆分/加水印/填表/OCR |
| `xlsx` | 「Excel」「表格」「.xlsx」「.csv」「电子表格」；数据清洗/公式/图表 |
| `doc-coauthoring` | 「写文档」「写提案」「写技术说明」「写决策记录」；结构化文档协作 |
| `internal-comms` | 「写周报」「状态更新」「公告」「通知」「内部邮件」 |

---

## 🎨 设计与创意（9 技能）

| 技能 | 触发词/场景 |
|------|-----------|
| `frontend-design` | 「做个网页」「前端」「界面」「dashboard」「landing page」；Web UI |
| `canvas-design` | 「做海报」「设计图」「艺术」「静态设计」；PNG/PDF 视觉作品 |
| `logo-studio` | 「Logo」「图标」「brand mark」「app icon」「品牌标识」 |
| `brand-guidelines` | 「品牌色」「公司配色」「设计规范」；需要 Anthropic 或指定品牌风格 |
| `theme-factory` | 「换个主题」「配色方案」「风格」；给已有作品套皮肤 |
| `creative-director` | 「品牌创意」「网站创意方向」「UI 概念」「视觉策略」 |
| `web-artifacts-builder` | 复杂 React/Tailwind/shadcn 前端 artifact（非简单单页 HTML） |
| `algorithmic-art` | 「生成艺术」「算法艺术」「粒子」「流场」；代码生成艺术作品 |
| `slack-gif-creator` | 「做个 GIF」「动图」「动画表情」；Slack 优化的 GIF |

---

## 🤖 AI 多媒体生成（9 技能）

| 技能 | 触发词/场景 |
|------|-----------|
| `image-generation` | 「生成图片」「画个…」「AI 绘画」「根据描述生成图」 |
| `image-edit` | 「修改图片」「P 一下」「图片变体」「编辑图像」 |
| `image-understand` | 「图片里有什么」「识别图片」「OCR」「分析这张图」 |
| `video-generation` | 「生成视频」「AI 视频」「根据文本生成视频」 |
| `video-understand` | 「分析视频」「视频里有什么」「提取视频帧」 |
| `video-storyboard` | 「视频脚本」「分镜」「广告剧本」「故事板」「品牌视频」 |
| `VLM` | 「看图聊天」「图片+文字问答」；视觉语言多模态对话 |
| `agent-media` | 「UGC 视频」「终端生成视频」；用 agent-media CLI |
| `image-generation` | 复用 — 也覆盖「画图」「AI 绘图」「图片创作」 |

---

## 🔧 技能与基础设施（5 技能）

| 技能 | 触发词/场景 |
|------|-----------|
| `skill-creator` | 「创建技能」「新建 skill」「优化技能描述」；管理技能生命周期 |
| `writing-skills` | 「写个技能」「编辑 skill」；新建/修改/验证技能 |
| `using-superpowers` | 每次会话启动自动注入；不需要手动触发 |
| `claude-api` | 「Claude API」「Anthropic SDK」「模型版本」「prompt caching」 |
| `mcp-builder` | 「MCP server」「新建 MCP」「集成外部 API 到 Claude」 |

---

## 🏠 专用工具（1 技能）

| 技能 | 触发词/场景 |
|------|-----------|
| `homework-collector` | 「收作业」「QQ 群作业」；自动化收集 QQ 群作业 |

---

## 触发铁律

1. **先 Skill，后文字** — 匹配到条件时，Skill 调用在第一个
2. **一问一技能** — 每回合只触发最匹配的 1 个
3. **不确定不触发** — 吃不准就正常回答，宁漏勿滥
4. **不存在就模拟** — 技能未安装时，用自然语言按该框架思考（如「我用五问法…」）
5. **TDD 铁律** — 写新功能/改代码，先触发 `test-driven-development`，先写测试再写实现
6. **Debug 铁律** — 遇到 bug/报错/异常，先触发 `systematic-debugging`，不要直接猜原因
7. **完成前验证** — 声称完成/修复/通过前，必须触发 `verification-before-completion` 跑验证
