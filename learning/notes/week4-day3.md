# 第4周 Day3 — Nginx 配置深入

> 2026-06-24 周三 | 日志 · 安全头 · Gzip · 限流

---

## 今日学习内容

Day1 完成了基础的 Nginx 反向代理（:80 → Flask :5000）。今天深入配置，让 Nginx 更接近生产环境。

## 1. 自定义日志格式

```nginx
log_format timing '$remote_addr - [$time_local] '
                  '"$request" $status $body_bytes_sent '
                  'rt=$request_time uct=$upstream_connect_time '
                  'uht=$upstream_header_time';
```

**关键变量：**
| 变量 | 含义 |
|------|------|
| `$request_time` | 从收到请求到发完响应的总时间（秒） |
| `$upstream_connect_time` | Nginx 连接到 Flask 的耗时 |
| `$upstream_header_time` | Flask 返回响应头的耗时 |

> **面试能说：** "我在 Nginx 配置了 timing 日志格式，记录请求耗时和上游响应时间，方便定位慢接口"

## 2. 安全响应头

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;         # 防点击劫持
add_header X-Content-Type-Options "nosniff" always;      # 防MIME嗅探
add_header X-XSS-Protection "1; mode=block" always;      # 防XSS
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

- `always` 参数：即使错误响应（404/500）也加上这些头
- 这些都是 OWASP 推荐的安全基线

## 3. Gzip 压缩

```nginx
gzip on;
gzip_comp_level 5;          # 压缩级别（1-9，5是平衡点）
gzip_min_length 256;        # 小于256字节不压（压了反而变大）
gzip_types application/json text/plain;
gzip_proxied any;           # 代理请求也压缩
```

**为什么重要：** JSON 响应压缩后体积减少 70-90%，接口响应更快。

## 4. 限流 (rate limiting)

```nginx
# 全局定义限流区：每个IP每秒10请求
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# 在 location 中应用
limit_req zone=api_limit burst=20 nodelay;
```

**三个参数：**
- `rate=10r/s` — 每秒最多 10 个请求（平均）
- `burst=20` — 允许瞬时突发 20 个
- `nodelay` — 突发请求立即处理，不排队

> **面试能说：** "我在 Nginx 配了 rate limiting，防止接口被刷爆。每 IP 每秒 10 个请求，允许突发 20 个"

## 5. upstream 连接池

```nginx
upstream flask_backend {
    server 127.0.0.1:5000 max_fails=3 fail_timeout=30s;
    keepalive 16;   # 保持16个空闲连接
}
```

- `max_fails=3`：连续失败3次后标记为不可用
- `fail_timeout=30s`：30秒后重试
- `keepalive 16`：连接池复用，减少 TCP 握手开销

## 自检

```
✅ 能说出 Nginx 日志中 request_time 和 upstream_connect_time 的区别
✅ 能列出至少 4 个安全响应头及其作用
✅ 能解释 rate=10r/s burst=20 nodelay 三个参数
✅ 理解 upstream keepalive 的作用
```

## 产出物

- `docs/nginx-flask-enhanced.conf` — 生产增强版 Nginx 配置

## 关键收获

**Nginx 不只是"转发"，它可以：**
1. 记录详细的请求耗时日志（排错利器）
2. 加安全头（防常见 Web 攻击）
3. 压缩响应（省带宽、加速）
4. 限流（保护后端不被刷爆）
5. 连接池复用（减少 Flask 压力）

> 💡 面试官问"你怎么部署测试环境的"→ 把这几条说出来，比只说"我配了反向代理"强10倍。
