# 第3天（6月4日）— 综合学习：JMeter + Linux

## JMeter：完整购物流程测试

### 流程概览

```
登录 → 搜索商品 → 查看详情 → 加入购物车 → 下单 → 支付
  │        │          │           │          │       │
  │   JSON提取器   正则提取器      │          │       │
  └──── token ─────────────────────┘          │       │
       msg → If Controller 判断登录成功才继续   │       │
```

### 涉及技术点

| 组件 | 作用 | 在哪用 |
|------|------|--------|
| HTTP Header Manager | 统一设置 Content-Type + token | 全局 |
| JSON Extractor | 提取登录返回的 token 和 msg | 登录接口 |
| If Controller | 判断 msg=="登录成功" 才继续后续请求 | 登录后 |
| Regex Extractor | 从商品详情提取 goods_id | 商品详情接口 |
| View Results Tree | 查看每个请求的响应 | 调试 |

### 接口链路

| # | 接口 | 方法 | 关键参数 |
|---|------|------|---------|
| 1 | /api/account/login | POST | account, password, client |
| 2 | /api/goods/getGoodsList | GET | keyword=晨光, page_no=1 |
| 3 | /api/goods/getGoodsDetail | GET | id=4 |
| 4 | /api/cart/add | POST | item_id, goods_num |
| 5 | /api/coupon/orderCoupon | POST | goods[{item_id, num}] |
| 6 | /api/order/buy?action=info | POST | goods, pay_way, address_id |
| 7 | /api/order/buy?action=submit | POST | 同上 action 改为 submit |

---

## Linux：用户与用户组权限（实训四）

### 实训1：root vs 普通用户

```
普通用户 mochen 在 / 下创建目录 → 权限不够
root 创建 /test_dir → 成功
mochen 删除 /test_dir → 权限不够
```

**结论**：root 拥有系统最高权限，普通用户只在自家目录有完整权限。

### 实训2：su 与 sudo

| 命令 | 切换后目录 |
|------|-----------|
| `su root` | 留在当前目录 |
| `su - root` | 跳到 /root |

`visudo` 配置免密 sudo 后，`sudo ls /root` 可绕过权限限制。

### 实训3：用户组管理

```bash
groupadd dev_group      # 创建组
getent group | grep dev  # 查询组
groupdel test_group     # 删除组
```

### 实训4：用户管理

```bash
useradd -G dev_group user01    # 创建用户并指定附加组
useradd user02                  # 创建用户不指定组
userdel user01                  # 删除用户（保留家目录）
userdel -r user02               # 删除用户+家目录
```

### 实训5：权限查看

```bash
ls -l   # 文件权限
ls -ld  # 目录本身权限
```

权限字符串：`-rwxr-xr--` → 第一位类型，后9位每3位一组（u/g/o）

### 实训6：rwx 对文件 vs 目录

| 权限 | 对文件 | 对目录 |
|------|--------|--------|
| r | 读取内容 | 列出文件名 |
| w | 修改内容 | 新建/删除文件 |
| x | 运行脚本 | cd 进入 |

### 实训7：chmod 字母法

```bash
chmod u=rwx,g=rx,o= work.txt    # 属主全权、属组读执行、其他无
chmod g+w,o+r work.txt           # 单独加权限
chmod -R u=rwx,g=rx,o= project/  # 递归设置
```

### 实训8：chmod 数字法

```
rwx = 4+2+1 = 7
rw- = 4+2+0 = 6
r-x = 4+0+1 = 5
r-- = 4+0+0 = 4
-wx = 0+2+1 = 3
--- = 0+0+0 = 0
```

练习：754、635、040、770、755

### 实训9：chown 归属

```bash
chown user01 owner.txt           # 改属主
chown :dev_group owner.txt       # 改属组
chown root:dev_group owner.txt   # 同时改
chown -R user01:dev_group data/  # 递归
```

### 实训10：综合实战 — 团队共享目录

```bash
groupadd team_group
useradd tom -G team_group
useradd jack -G team_group
mkdir /opt/team_dir
chown root:team_group /opt/team_dir
chmod 770 /opt/team_dir
# tom 创建文件 → jack 可编辑、可删除（同组有w权限）
```

---

## 今日总结

| 领域 | 收获 |
|------|------|
| JMeter | 完整电商流程：登录→搜索→详情→购物车→下单→支付，含提取器和条件判断 |
| Linux | 10个实训覆盖用户/组管理、权限(rwx/chmod/chown)、sudo、综合实战 |
| 和测试的关系 | JMeter测试电商接口 = API测试的延伸；Linux权限 = 搭测试环境的基础 |
