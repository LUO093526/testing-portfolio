# 第4周 Day1 — Nginx + Flask 反向代理部署（2026-06-22）

## 主题

Linux 实操之 Nginx 反向代理，将 Flask API 通过 80 端口对外暴露。

## 学到的新概念

| 概念 | 一句话 |
|------|--------|
| **反向代理** | Nginx 收请求→转发给 Flask(:5000)→返回结果，客户端不知道 Flask 的存在 |
| **proxy_pass** | Nginx 的核心指令，指定转发目标地址 |
| **listen 80 default_server** | 让 Nginx 监听 80 端口，设为默认站点 |
| **proxy_set_header** | 转发时带上原始请求头（Host/X-Real-IP/X-Forwarded-For），后端才能知道真实来源 |
| **nginx -t** | 测试配置语法，改完配置先跑这个再 reload |
| **systemctl reload nginx** | 不中断服务的重载配置方式 |

## 架构

```
浏览器/curl → Nginx (:80) → Flask (:5000)
             反向代理        后端 API
```

## 产出物

1. `docs/deployment-guide.md` — 完整部署文档（安装→配置→验证→排错）
2. `docs/nginx-flask.conf` — 可复用的 Nginx 反向代理配置文件

## 验证结果

```bash
curl http://127.0.0.1:80/api/health  # 经 Nginx → Flask，全部接口正常
pytest tests/test_api.py -v           # 39 PASSED
```

## Day1 调整说明

本周原计划 Day1 是「文件/权限(chmod/chown)」，但该内容已于 6 月 13 日学校实训工单完成（10 个综合实训），故跳过，改为 Day3 的 Nginx+Flask 部署任务。

## 还模糊的地方

- proxy 超时参数调优（proxy_connect_timeout vs proxy_read_timeout 的具体场景）
- Nginx 日志格式自定义
- SSL/HTTPS 配置（后续补充）
