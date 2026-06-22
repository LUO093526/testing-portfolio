# Nginx + Flask 部署指南

> 用户管理 API 测试平台 | WSL (Ubuntu) | 2026-06-22

---

## 1. 架构概览

```
浏览器/curl → Nginx (:80) → Flask (:5000)
             反向代理         后端 API
```

Nginx 作为反向代理，接收外部请求并转发给 Flask 应用。好处：
- 不需要暴露 Flask 端口
- Nginx 可处理静态文件、缓存、限流
- 更接近生产环境

---

## 2. 环境

| 组件 | 版本 |
|------|------|
| WSL | Ubuntu (Windows Subsystem for Linux) |
| Nginx | 1.18.0 |
| Python | 3.x |
| Flask | 3.1.3 |

---

## 3. 安装 Nginx

```bash
sudo apt-get update
sudo apt-get install -y nginx
```

验证安装：
```bash
nginx -v              # 查看版本
sudo nginx -t         # 测试配置语法
```

---

## 4. Nginx 配置

### 4.1 配置文件位置

```
/etc/nginx/sites-available/default   ← 站点配置
/etc/nginx/sites-enabled/default     ← 启用站点的软链接
```

### 4.2 反向代理配置

```nginx
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name localhost;

    # 反向代理：API 请求 → Flask
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_connect_timeout 10s;
        proxy_read_timeout 30s;
    }

    # 默认静态页面
    location / {
        root /var/www/html;
        index index.html index.htm;
    }
}
```

### 4.3 部署配置

```bash
# 备份原配置
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.bak

# 替换为新配置
sudo cp docs/nginx-flask.conf /etc/nginx/sites-available/default

# 测试语法
sudo nginx -t

# 重载配置
sudo nginx -s reload
```

---

## 5. 启动/停止

```bash
# 启动 Flask API
cd /home/luo/testing-portfolio
python3 api/app.py &          # 后台启动

# 或使用项目脚本
./run.sh start

# 启动/重载/停止 Nginx
sudo nginx                     # 启动
sudo nginx -s reload           # 重载配置（不中断服务）
sudo nginx -s stop             # 停止
```

---

## 6. 验证

```bash
# 直连 Flask（端口 5000）
curl http://127.0.0.1:5000/api/health

# 经 Nginx 代理（端口 80）
curl http://127.0.0.1/api/health

# 测试完整接口
curl http://127.0.0.1/api/students
curl http://127.0.0.1/api/students/1
curl -X POST http://127.0.0.1/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 7. 常见问题

### 7.1 `bind() to 0.0.0.0:80 failed`

> 端口 80 已被占用（Nginx 已在运行）

```bash
sudo nginx -s reload    # 重载配置即可，无需重新启动
```

### 7.2 `Connection refused`

> Nginx 未启动

```bash
sudo nginx              # 启动 Nginx
```

### 7.3 代理返回 404

> 确认 Nginx 已重载配置：`sudo nginx -s reload`

### 7.4 Flask 未启动导致 502

```bash
python3 api/app.py &
```

---

## 8. 配置备份

原默认配置已备份至：
- `/etc/nginx/sites-available/default.bak`

项目配置存于：
- `docs/nginx-flask.conf`

---

> 📅 部署日期：2026-06-22 | 第4周 Day1 | Nginx+Flask 部署
