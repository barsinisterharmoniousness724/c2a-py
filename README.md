# Cursor2API Python

这是 `cursor2api` 的 **Python / FastAPI 最小实现版本**。

提供一个更轻量、便于阅读和二次开发的 Python 版本。

## 当前实现范围

- FastAPI 服务入口：[`main.py`](./main.py)
- 启动脚本：[`start_py.py`](./start_py.py)
- Claude Code 兼容路由：
  - `POST /v1/messages`
  - `POST /messages`
  - `POST /v1/messages/count_tokens`
  - `POST /messages/count_tokens`
  - `GET /v1/models`
  - `GET /health`
- 最小能力包括：
  - Anthropic Messages 请求转 Cursor `/api/chat`
  - 基础 system prompt 清洗
  - 工具定义注入
  - `json action` 工具块解析
  - 基础身份文本清洗
  - Claude Code 可识别的非流式/流式响应格式

## 项目结构

```text
py/
├── main.py            # FastAPI 入口
├── start_py.py        # 本目录下的启动脚本
├── config.py          # 环境变量配置
├── schemas.py         # Anthropic 请求/响应相关模型
├── converter.py       # 请求转换、工具注入、json action 解析
├── cursor_client.py   # 向 Cursor /api/chat 发起请求
├── constants.py       # 拒绝检测、身份清洗规则
├── requirements.txt   # pip 依赖
└── pyproject.toml     # Python 项目元数据
```

## 安装

### 方式一：使用 pip

```bash
pip install -r requirements.txt
```

### 方式二：使用 uv

```bash
uv sync
```

## 启动

在 `py/` 目录下运行：

```bash
python start_py.py
```

默认监听：

```text
http://0.0.0.0:8000
```

也可以直接使用 uvicorn：

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `HOST` | 监听地址 | `0.0.0.0` |
| `PORT` | 服务端口 | `8000` |
| `RELOAD` | 是否开启热重载 | `false` |
| `CURSOR_CHAT_API` | 上游 Cursor 接口地址 | `https://cursor.com/api/chat` |
| `CURSOR_MODEL` | 转发时使用的模型名 | `claude-4-5` |
| `REQUEST_TIMEOUT` | 请求超时秒数 | `90` |
| `AUTH_TOKEN` | 代理自身鉴权 token，多个可逗号分隔 | 空 |
| `SANITIZE_RESPONSE` | 是否清洗身份相关文本 | `true` |
| `TOOLS_PASSTHROUGH` | 是否使用工具透传模式 | `false` |
| `TOOLS_DISABLED` | 是否禁用工具注入 | `false` |
| `USER_AGENT` | 转发请求时的浏览器 UA | 内置 Chrome UA |

## Docker 部署

### 方式一：使用预构建镜像（推荐）

无需克隆代码，直接拉取 GitHub Container Registry 中的镜像运行。

**1. 准备配置文件**

```bash
curl -O https://raw.githubusercontent.com/wuyao4/c2a-py/master/.env.example
cp .env.example .env
```

编辑 `.env`，至少修改 `AUTH_TOKEN`：

```bash
AUTH_TOKEN=your-secret-token
```

**2. 下载 compose 文件并启动**

```bash
curl -O https://raw.githubusercontent.com/wuyao4/c2a-py/master/docker-compose.yml
docker compose up -d
```

服务默认监听 `http://localhost:3010`。

**3. 指定版本（可选）**

```bash
C2A_VERSION=1.2.3 docker compose up -d
```

### 方式二：本地构建镜像

克隆代码后自行构建：

```bash
git clone https://github.com/wuyao4/c2a-py.git
cd c2a-py
cp .env.example .env  # 按需修改
docker compose build
docker compose up -d
```

### 常用命令

```bash
# 查看运行状态
docker compose ps

# 实时查看日志
docker compose logs -f

# 停止服务
docker compose down

# 更新到最新镜像
docker compose pull && docker compose up -d
```

### 健康检查

服务启动后可访问以下端点确认运行正常：

```bash
curl http://localhost:3010/health
```

---

## Claude Code 使用方式

服务启动后，可将 Claude Code 指向本代理：

```bash
export ANTHROPIC_BASE_URL=http://localhost:8000
```

如果你配置了 `AUTH_TOKEN`，还需要同时设置：

```bash
export ANTHROPIC_API_KEY=your-token
```

## 免责声明 / Disclaimer

1. 本目录下的 Python / FastAPI 代码仅供学习、研究、协议分析与接口调试使用。
2. 该实现并非 Cursor 官方项目，也不代表 Cursor、Anysphere、Anthropic 或其他任何服务提供方的官方立场。
3. 使用本项目可能违反相关平台服务条款，也可能导致账号限制、账号封禁、访问策略调整或其他不可预期后果。
4. 请勿将本项目用于任何违法违规用途，包括但不限于滥用接口、规避平台限制、批量攻击、数据窃取或其他侵害第三方权益的行为。
5. 作者及贡献者不对因使用、修改、部署、传播本代码而导致的任何直接或间接损失承担责任，所有风险由使用者自行承担。
