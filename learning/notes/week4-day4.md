# 第4周 Day4 — systemd 服务管理

> 2026-06-25 周四 | 系统服务启停 · 开机自启 · journalctl 日志

---

## 今日学习内容

把 Flask API 做成系统服务，实现开机自启、崩溃自动重启、统一日志管理。

## 1. systemd 是什么

Linux 系统和服务管理器，PID=1（系统第一个进程）。管理所有后台服务。

**核心概念：**
| 概念 | 说明 |
|------|------|
| Unit | 最小管理单元（service/mount/socket...） |
| Service | 后台进程，systemd 管理其生命周期 |
| Target | 运行级别（multi-user.target = 多用户命令行模式） |

## 2. Unit 文件结构

```ini
[Unit]          # 元信息：描述、依赖
[Service]       # 进程控制：怎么启动、怎么重启
[Install]       # 安装信息：谁依赖我
```

**关键字段详解：**

### [Unit]
- `Description=` — 服务描述（`systemctl status` 会显示）
- `After=network.target` — 在网络就绪**之后**启动
- `Wants=` — 弱依赖（对方失败不影响我启动）

### [Service]
- `Type=simple` — 默认类型，主进程即服务进程
- `ExecStart=` — 启动命令（**必须用绝对路径**）
- `Restart=on-failure` — 仅在异常退出时重启
- `RestartSec=3s` — 等 3 秒再重启
- `StartLimitBurst=5` — 60秒内最多重启 5 次
- `StandardOutput=journal` — 日志输出到 journald

### [Install]
- `WantedBy=multi-user.target` — 多用户模式启动时自动启我

## 3. systemctl 命令速查

```bash
# 服务生命周期
sudo systemctl start flask-api       # 启动
sudo systemctl stop flask-api        # 停止
sudo systemctl restart flask-api     # 重启（停→启）
sudo systemctl reload flask-api      # 重载配置（不中断服务）
sudo systemctl status flask-api      # 查看状态

# 开机自启
sudo systemctl enable flask-api      # 设为开机自启
sudo systemctl disable flask-api     # 取消开机自启
sudo systemctl is-enabled flask-api  # 查看是否自启

# 列表查看
systemctl list-units --type=service  # 所有运行中的服务
systemctl list-unit-files | grep flask  # 所有已安装的单元文件
systemctl list-units --state=failed  # 查看失败的服务

# 重新加载 systemd（修改 unit 文件后执行）
sudo systemctl daemon-reload
```

## 4. journalctl 日志查看

```bash
# flask-api 专属日志
journalctl -u flask-api              # 全部日志
journalctl -u flask-api -f           # 实时跟踪（类似 tail -f）
journalctl -u flask-api --since today    # 今天的日志
journalctl -u flask-api -n 50        # 最后 50 行
journalctl -u flask-api -p err       # 只看错误级别

# 全局日志
journalctl -xe                        # 最近的系统日志（排错第一命令）
journalctl --since "10 min ago"       # 最近10分钟
journalctl -k                         # 只看内核日志
```

> 🎯 **面试场景："服务挂了你怎么查？"**
> 1. `systemctl status flask-api` — 看是不是挂了
> 2. `journalctl -u flask-api --since "10 min ago"` — 看出事前后的日志
> 3. `journalctl -u flask-api -p err` — 只看错误
> 4. `tail -100 /var/log/nginx/flask-error.log` — 交叉看 Nginx 日志

## 5. 部署步骤

```bash
# 1. 复制服务文件
sudo cp docs/flask-api.service /etc/systemd/system/

# 2. 重载 systemd
sudo systemctl daemon-reload

# 3. 启动并设为自启
sudo systemctl enable --now flask-api

# 4. 验证
systemctl status flask-api
curl http://127.0.0.1:5000/api/health
```

## 6. 常见状态码

| 状态 | 含义 |
|------|------|
| `active (running)` | 正在运行 ✅ |
| `inactive (dead)` | 已停止 |
| `failed` | 启动失败 ❌ |
| `activating` | 正在启动中... |
| `deactivating` | 正在停止中... |

## 7. ❌ 为什么不用 nohup &

| 方式 | 崩溃重启 | 开机自启 | 集中日志 | 资源限制 |
|------|---------|---------|---------|---------|
| `nohup &` | ❌ | ❌ | ❌ | ❌ |
| `systemd` | ✅ | ✅ | ✅ | ✅ |

> **面试能说：** "线上服务必须用 systemd 管理，因为进程挂了它能自动拉起来，日志统一进 journald，还能限制 CPU/内存"

## 自检

```
✅ 能说出 Unit 文件三个段的作用（Unit/Service/Install）
✅ 能写一个最小可用的 systemd service 文件
✅ 能说出 enable/start/status 三个命令的区别
✅ 能说出"服务挂了"排查三步骤（status → journalctl → tail log）
✅ 理解 Restart=on-failure 和 StartLimitBurst 的作用
```

## 产出物

- `docs/flask-api.service` — systemd 服务单元文件

---

> 📅 第4周 Day4 | systemd 服务管理 | 累计笔记 20篇
