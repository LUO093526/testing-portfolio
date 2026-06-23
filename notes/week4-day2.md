# 第4周 Day2 — 进程管理 & Shell 脚本实战（2026-06-23）

## 主题

Linux 进程生命周期管理 + Shell 脚本编程，核心产出是把 `run.sh` 从简陋的启停脚本升级为功能完整的环境管理工具。

---

## 一、进程管理

### 1.1 `ps` — 查看进程快照

```bash
ps aux            # 列出所有用户的所有进程（BSD 风格）
ps aux | grep flask   # 过滤出 Flask 相关进程
ps -ef            # System V 风格，输出格式略有不同
```

**关键列解读：**

| 列 | 含义 | 怎么用 |
|----|------|--------|
| PID | 进程 ID | kill 的目标；写 PID 文件的数据 |
| %CPU | CPU 占用百分比 | top 看实时，ps 看瞬时 |
| %MEM | 物理内存占用百分比 | 排查内存泄漏 |
| RSS | 实际物理内存(KB) | `ps -p $pid -o rss=` 精确取值 |
| STAT | 进程状态 | R=运行, S=睡眠, Z=僵尸, T=停止 |
| START/lstart | 启动时间 | `ps -p $pid -o lstart=` 看何时启动 |
| COMMAND | 命令行 | 区分多个同名进程 |

**常用组合：**
```bash
ps -p $pid -o rss=           # 只取内存值，用于脚本计算
ps -p $pid -o lstart=        # 取启动时间
ps -p $pid -o %cpu=          # 取 CPU 占用
ps -p $pid > /dev/null 2>&1  # 不关心输出，只检查进程是否存在（退出码 0/1）
```

**判断进程是否存在的可靠写法：**
```bash
if ps -p "$pid" > /dev/null 2>&1; then
    echo "进程存在"
else
    echo "进程不存在（或 PID 已回收）"
fi
```
> ⚠️ 不能只看 PID 文件是否存在——进程可能已死但 PID 文件残留（脏文件）。

### 1.2 `top` — 实时进程监控

```bash
top                 # 默认 3 秒刷新，按 CPU 排序
top -p $pid         # 只监控指定进程
top -u $username    # 只看某用户的进程
```

**交互快捷键：**
| 键 | 作用 |
|----|------|
| `1` | 展开/折叠每个 CPU 核心 |
| `M` | 按内存占用排序 |
| `P` | 按 CPU 占用排序 |
| `k` | 杀进程（输入 PID + 信号） |
| `q` | 退出 |

> `top` 适合"盯着看"实时变化；脚本里用 `ps` 取值。

### 1.3 `kill` — 向进程发信号

```bash
kill <PID>          # 默认发 SIGTERM(15)，礼貌请进程退出
kill -15 <PID>      # 同上，显式写法
kill -9 <PID>       # SIGKILL，内核强制杀，进程无法捕获/忽略
kill -l             # 列出所有信号（共 64 个）
```

**关键信号：**

| 信号 | 编号 | 含义 | 使用场景 |
|------|------|------|---------|
| SIGTERM | 15 | 终止（可捕获） | **首选**。给进程清理资源的机会 |
| SIGKILL | 9 | 强制终止（不可捕获） | 进程卡死、不响应 SIGTERM 时 |
| SIGHUP | 1 | 挂断 | 常用于让守护进程重读配置 |
| SIGINT | 2 | 中断 | Ctrl+C 发的就是这个 |
| SIGSTOP | 19 | 暂停（不可捕获） | 调试时暂停进程 |

**优雅停止策略（run.sh 采用）：**
```bash
kill "$pid"                    # 1. 先发 SIGTERM
for i in $(seq 1 10); do       # 2. 等最多 10 秒
    if ! ps -p "$pid" > /dev/null 2>&1; then
        echo "正常退出"
        return
    fi
    sleep 1
done
kill -9 "$pid"                 # 3. 超时 → 强制杀
```
> **面试会说：** 「线上永远先 kill -15，给 10 秒窗口，超时才 -9。直接 -9 可能导致数据丢失或连接未关闭。」

### 1.4 `pkill` / `pgrep` — 按名称操作

```bash
pkill -f "python3 app.py"      # 杀掉匹配命令行的所有进程
pkill -9 -f "python3 app.py"   # 强制杀
pgrep -f "python3 app.py"      # 只查 PID，不杀（安全预览）
```

**`kill` vs `pkill`：**
| | kill | pkill |
|------|------|-------|
| 目标 | 精确 PID | 进程名/命令行 |
| 风险 | 低（你明确知道杀哪个） | **高**（可能误杀同名进程） |
| 脚本场景 | ✅ 推荐（PID 文件配合） | ❌ 慎用 |

### 1.5 PID 文件机制

**要解决的问题：** 后台进程启动后，你记不住 PID；下次要停它，不知道发给谁。

**机制：**
```
启动时：echo $! > .api.pid        # $! 是上一条后台命令的 PID
停止时：pid=$(cat .api.pid); kill $pid
停止后：rm -f .api.pid            # 清理脏文件
```

**run.sh 采用的防御策略：**
1. 启动时检查 PID 文件是否存在且进程真的活着 → 防重复启动
2. 停止时检查 PID 进程是否真的在跑 → 不靠过期数据
3. `is_running()` 函数统一判断，消除重复代码

**PID 文件常见陷阱：**
- PID 被回收：旧 PID 文件还在，但进程早死了；新进程碰巧用了同一个 PID → `ps -p $pid` 能防这个
- 进程异常退出：`trap "rm -f $PID_FILE" EXIT` 可在脚本退出时自动清理

---

## 二、Shell 脚本编程

### 2.1 变量

```bash
# 定义（等号两边不能有空格！）
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$PROJECT_DIR/.api.pid"

# 命令替换 — 两种写法
pid=$(cat "$PID_FILE")          # 推荐：现代 $() 语法
pid=`cat "$PID_FILE"`           # 旧式：反引号，不推荐（难嵌套）

# 引号规则
"$VAR"     # 双引号：变量会展开，路径有空格也安全
'$VAR'     # 单引号：原样输出，变量不展开
${VAR}     # 花括号：变量名边界不清晰时用，如 ${VAR}_backup
```

**特殊变量：**
| 变量 | 含义 | run.sh 中的用法 |
|------|------|----------------|
| `$0` | 脚本自身路径 | `dirname "$0"` 定位项目根目录 |
| `$1` | 第一个参数 | 子命令分发 start/stop/restart/... |
| `$!` | 上一条后台命令的 PID | `python3 app.py &; echo $! > .pid` |
| `$?` | 上一条命令的退出码 | 0=成功 非0=失败 |
| `${1:-help}` | 参数缺省值 | 没传参数时默认 help |

### 2.2 条件判断

```bash
# if 语句 — 核心模式
if [ -f "$PID_FILE" ]; then        # 文件存在？
    ...
fi

if ps -p "$pid" > /dev/null 2>&1; then   # 进程存在？
    return 0   # 成功
fi
return 1       # 失败
```

**文件测试运算符：**
| 写法 | 含义 |
|------|------|
| `[ -f "$f" ]` | 是普通文件？ |
| `[ -d "$d" ]` | 是目录？ |
| `[ -x "$f" ]` | 有执行权限？ |
| `[ -s "$f" ]` | 文件非空？ |
| `[ -z "$s" ]` | 字符串为空？ |
| `[ -n "$s" ]` | 字符串非空？ |

**退出码即布尔值：**
```bash
# Unix 哲学：命令成功=0(真)，失败=非0(假)
is_running && echo "在跑"      # is_running 返回0时才执行echo
is_running || echo "没在跑"    # is_running 返回非0时才执行echo
```

### 2.3 循环

```bash
# 计数循环 — 等进程优雅退出
for i in $(seq 1 10); do
    if ! ps -p "$pid" > /dev/null 2>&1; then
        echo "第${i}秒退出"
        break
    fi
    sleep 1
done

# $(seq 1 10) 展开为 1 2 3 ... 10
```

### 2.4 函数

```bash
# 定义
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")   # local: 函数内局部变量
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        fi
    fi
    return 1
}

# 调用
if is_running; then
    echo "在跑"
fi
```

**函数返回值：** Shell 函数只能返回 0-255 的整数（退出码），不是 return 数据。返回数据用 `echo` + 命令替换 `$(func)`。

### 2.5 case 语句 — 子命令分发

```bash
case "${1:-help}" in
    start)    start ;;
    stop)     stop ;;
    restart)  restart ;;
    status)   status ;;
    test)     test_smoke ;;
    test-all) test_all ;;
    logs)     logs ;;
    help|*)
        echo "用法: ./run.sh {start|stop|restart|status|test|test-all|logs}"
        ;;
esac
```

**要点：**
- `"${1:-help}"` — 没传参数时默认为 help
- 每个分支以 `;;` 结束（Java 的 break）
- `help|*)` — | 是或，* 是通配（兜底）

### 2.6 其他语法要点

```bash
#!/bin/bash                     # shebang，指定解释器
set -e                          # 任何命令失败立即退出（防错误累积）
2>&1                            # 重定向 stderr 到 stdout（日志不丢）
2>/dev/null                     # 丢弃 stderr（不关心错误信息）
&                               # 放命令末尾 → 后台运行
&&                              # 前一条成功才执行后一条
||                              # 前一条失败才执行后一条
```

---

## 三、run.sh 升级：3 命令 → 7 命令

### 升级前
```
./run.sh start    # 启动
./run.sh stop     # 停止
./run.sh restart  # 重启
```

### 升级后
```
./run.sh start       # 启动 + 防重复 + 启动失败检测
./run.sh stop        # 停止：优雅(TERM)→10s超时→强制(KILL)
./run.sh restart     # 重启 = stop + sleep + start
./run.sh status      # 🆕 查看：PID/启动时间/CPU%/内存/并发实例数
./run.sh test        # 🆕 冒烟测试（只跑 smoke 标记的用例）
./run.sh test-all    # 🆕 全量测试 + HTML 报告
./run.sh logs        # 🆕 tail -f 实时日志
```

### 关键设计决策

| 问题 | 方案 | 为什么 |
|------|------|--------|
| 怎么知道服务在跑？ | PID 文件 + `ps -p` 双重校验 | 防脏 PID 文件 |
| 怎么防重复启动？ | `start()` 开头检查 `is_running` | 没必要跑两个实例 |
| 服务挂了怎么发现？ | 启动后 `sleep 2` 再检查 `is_running` | 避免闪退的假启动 |
| 优雅停止等多久？ | 等 10 秒 | 10秒够 Flask 处理完当前请求 |
| 彩色输出有什么？ | `\033[0;32m` 等 ANSI 转义码 | 终端里看得清楚 |

---

## 四、日志排查套路

### 4.1 `tail` — 看日志尾部

```bash
tail -n 50 api.log        # 最后 50 行
tail -f api.log           # 实时跟踪（Ctrl+C 退出）
tail -f api.log | grep ERROR   # 只看错误
```

### 4.2 `grep` — 搜索日志

```bash
grep "ERROR" api.log             # 含 ERROR 的行
grep -i "error" api.log          # 忽略大小写
grep -c "500" api.log            # 统计匹配行数
grep -B 2 -A 5 "ERROR" api.log  # 显示匹配行的前后 2/5 行（上下文）
grep "2026-06-23" api.log        # 只看今天的日志
```

### 4.3 `journalctl` — systemd 日志

```bash
journalctl -u nginx           # 只看 nginx 服务日志
journalctl -u nginx -f        # 实时跟踪（同 tail -f）
journalctl -u nginx --since "10 minutes ago"   # 最近 10 分钟
journalctl -u nginx -p err    # 只看 ERROR 及以上级别
```

### 4.4 排查"服务挂了"的标准流程

```
1. curl http://127.0.0.1:5000/api/health      ← 先确认真的挂了
2. systemctl status nginx                       ← 看 Nginx 状态
3. ./run.sh status                              ← 看 Flask 状态
4. tail -n 100 logs/api.log                     ← 看日志尾巴
5. tail -f logs/api.log & 然后 curl 触发请求    ← 实时抓错误
6. grep -B 5 "Traceback" logs/api.log           ← 找异常堆栈
```

> **面试会说：** 「线上排查我有固定套路——先确认症状(curl/status)，再看日志(tail/journalctl)，最后用 grep 搜关键错误。不会东敲一个西敲一个。」

---

## 五、产出物

1. **`run.sh`** — 7 命令环境管理脚本（start/stop/restart/status/test/test-all/logs）
2. **`notes/week4-day2.md`** — 本文档

---

## 六、自检

- [ ] 能说出 kill -15 和 kill -9 的区别，什么时候用哪个
- [ ] 能解释 PID 文件为什么要配合 `ps -p` 做双重校验
- [ ] Shell 变量赋值不能有空格、if [ 的方括号里必须加空格——都记住了
- [ ] run.sh 里的 `is_running()`、优雅停止循环、case 子命令分发都能说清楚
- [ ] 知道服务挂了从哪个命令开始排查（curl → status → tail → grep）

---

## 七、还模糊的地方

- `trap` 捕获信号做清理（EXIT/INT/TERM），run.sh 还没加
- `set -e` 和 `set -u` 的边界 case
- awk/sed 文本处理进阶（目前只会 `awk '{printf}'` 简单取值）
- `journalctl` 的过滤语法（`_PID=`, `_SYSTEMD_UNIT=` 等字段过滤）
