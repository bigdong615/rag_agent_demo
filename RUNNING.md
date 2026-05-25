# 运行指南(Running Guide)

本文档详细说明如何从零开始把 **RAG Agent Demo** 跑起来,包含每一步的
**命令、预期输出、常见错误排查**。

> 适用环境:macOS / Linux,Python 3.10+。Windows 用户把 `source .venv/bin/activate`
> 替换为 `.venv\Scripts\activate` 即可。

---

## 前置条件

| 项 | 要求 |
|---|---|
| Python | 3.10 或更高(建议 3.11) |
| pip | 最新版,`pip install --upgrade pip` |
| Anthropic API key | 必填,[console.anthropic.com](https://console.anthropic.com) 申请 |
| Tavily API key | 选填(Web 搜索工具用),[tavily.com](https://tavily.com) 免费注册 |
| 网络 | 第一次运行需要从 HuggingFace 下载 embedding 模型(约 90 MB) |

---

## Step 1 — 进入项目目录

```bash
cd rag_agent_demo
```

确认结构:
```bash
ls
# 应看到:README.md  cli.py  config.py  data/  requirements.txt  src/  tests/  ...
```

---

## Step 2 — 创建并激活虚拟环境

```bash
python -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows
```

**预期**:命令行提示符前面会出现 `(.venv)`。

---

## Step 3 — 安装依赖

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**预期**:无报错,最后一行是 `Successfully installed ...`。

**常见问题**:
- `chromadb` 安装慢/卡住 → 换国内源:`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
- macOS 上 `sentence-transformers` 报 torch 错误 → 单独装 CPU 版:`pip install torch --index-url https://download.pytorch.org/whl/cpu`

---

## Step 4 — 配置 API key

```bash
cp .env.example .env
```

用编辑器打开 `.env`,填入真实 key:

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxx
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxx
CLAUDE_MODEL=claude-sonnet-4-6
```

> **可选**:如果不需要 Web 搜索,`TAVILY_API_KEY` 可留空。
> Agent 调用 `search_web` 时会返回友好错误,Claude 会自动转用其他工具。

**验证 key 已加载**:
```bash
python -c "import config; print('OK' if config.ANTHROPIC_API_KEY else 'MISSING')"
```
预期输出:`OK`。

---

## Step 5 — 初始化 SQLite 示例数据

```bash
python data/init_db.py
```

**预期输出**:
```
Initialized /.../rag_agent_demo/data/sample.db
```

**验证**:
```bash
python -c "import sqlite3; c=sqlite3.connect('data/sample.db'); print(c.execute('SELECT COUNT(*) FROM employees').fetchone())"
# (5,)
```

---

## Step 6 — 索引文档到 ChromaDB

```bash
python -m src.ingestion
```

**预期输出**(首次会下载 embedding 模型,约 1~2 分钟):
```
Ingested 2 files → N chunks into /.../rag_agent_demo/chroma_db
```

**验证**:目录下会出现 `chroma_db/` 文件夹,里面有 SQLite 持久化文件。

**常见问题**:
- 下载 HuggingFace 模型失败 → 设置镜像:
  ```bash
  export HF_ENDPOINT=https://hf-mirror.com
  python -m src.ingestion
  ```

---

## Step 7 — 跑一遍单元测试(可选,推荐)

```bash
pytest tests/ -v
```

**预期**:5 个测试全绿(这些测试不调用 LLM,只验证工具本身)。
```
tests/test_agent.py::test_calculator_basic PASSED
tests/test_agent.py::test_calculator_invalid PASSED
tests/test_agent.py::test_sql_select_employees PASSED
tests/test_agent.py::test_sql_rejects_writes PASSED
tests/test_agent.py::test_sql_rejects_forbidden_keyword PASSED
```

如果测试报 `ModuleNotFoundError: No module named 'src'`,确认你在 `rag_agent_demo/`
目录下、并且虚拟环境已激活。

---

## Step 8a — 启动 CLI 模式

```bash
python cli.py
```

**预期**:
```
================================================================
 RockBot Agentic RAG — CLI
   Type your question and press Enter.
   Commands:  /reset  — clear chat history
              /quit   — exit
================================================================

>
```

**试一下这些问题**(会打印 verbose 的工具调用过程):

| 输入 | 触发工具 |
|------|---------|
| `RockBot Pro 多少钱?` | `search_documents` |
| `工程部最高工资是谁?` | `query_database` |
| `2024 年总营收是多少?` | `query_database` |
| `这个数字涨 15% 是多少?`(紧接上一问) | `calculate`(用到上下文) |
| `今天 Anthropic 发布了什么?` | `search_web`(需 Tavily key) |

输入 `/reset` 清除历史,`/quit` 退出。

---

## Step 8b — 启动 Web API 模式

新开一个终端(保留虚拟环境激活):

```bash
uvicorn src.api:app --reload
```

**预期**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Application startup complete.
```

打开浏览器访问 http://127.0.0.1:8000/docs 可以看到 Swagger UI。

### 用 curl 测试

**健康检查**:
```bash
curl http://localhost:8000/health
# {"status":"ok"}
```

**单次问答(无状态)**:
```bash
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "RockBot Pro 多少钱一个月?"}'
```

**多轮对话(带 session_id)**:
```bash
# 第一轮
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "工程部最高工资是多少?", "session_id": "user-001"}'

# 第二轮(引用上一轮结果)
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "那涨 15% 后是多少?", "session_id": "user-001"}'
```

**重置 session**:
```bash
curl -X POST http://localhost:8000/api/reset \
  -H "Content-Type: application/json" \
  -d '{"session_id": "user-001"}'
```

---

## 完整运行序列(一键复制)

下面这串命令可以在干净环境上一次跑完(填好 `.env` 后):

```bash
cd rag_agent_demo
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
# >>> 编辑 .env 填入 API key 后再继续 <<<
python data/init_db.py
python -m src.ingestion
pytest tests/ -v
python cli.py
```

---

## 常见错误排查

| 错误 | 原因 | 解决 |
|------|------|------|
| `RuntimeError: ANTHROPIC_API_KEY is not set` | `.env` 没填 / 没复制 | 检查 Step 4 |
| `No module named 'src'` | 没在 `rag_agent_demo/` 目录,或没激活 venv | `cd rag_agent_demo && source .venv/bin/activate` |
| `No relevant documents found.` 一直出现 | 没运行 ingestion | 执行 Step 6 |
| `sqlite3.OperationalError: no such table: employees` | 没运行 init_db | 执行 Step 5 |
| `Web search error: 401` | Tavily key 无效 | 重新申请并填入 `.env` |
| 模型下载卡住 | HuggingFace 网络问题 | `export HF_ENDPOINT=https://hf-mirror.com` |
| `port 8000 already in use` | 端口被占用 | `uvicorn src.api:app --port 8001` |

---

## 重新开始(清理状态)

```bash
rm -rf chroma_db data/sample.db
python data/init_db.py
python -m src.ingestion
```

---

## 下一步

- 把 `data/docs/` 替换成你自己的 PDF/Markdown(目前只支持 .md / .txt,
  PDF 需要在 `src/ingestion.py` 中加 `PyPDFLoader`)
- 改 `data/init_db.py` 接到真实数据库
- 在 `src/tools/` 下添加你自己的工具,然后加入 `src/tools/__init__.py` 的 `ALL_TOOLS`
- 把 `SYSTEM_PROMPT`(`src/agent.py`)改成符合你业务的人设
