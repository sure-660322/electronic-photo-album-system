# 电子相册系统

《软件工程》课程设计 —— 面向对象分析与设计，MVC 结构实现。

## 项目简介

基于 Web 的电子相册系统，采用 B/S 体系结构 + MVC 设计模式。普通用户可以注册、登录、创建和修改相册、上传和浏览照片、对照片发表评论；管理员可以维护相册类别。系统帮助用户对照片进行分类管理和分享。

- 需求分析成果：[Word 报告](docs/需求分析/电子相册系统_面向对象需求分析报告.docx)、[PDF 报告](docs/需求分析/电子相册系统_面向对象需求分析报告.pdf)、[答辩 PPT](docs/需求分析/电子相册系统_需求分析答辩.pptx)；正文与待确认事项见 [交付与验收记录](docs/需求分析/04_交付与验收记录.md)
- 报告图稿：见 [docs/图稿/](docs/图稿/)
- 答辩材料收集规则：见 [docs/答辩准备/README.md](docs/答辩准备/README.md)。报告与 PPT 已整合到 `docs/需求分析/`；贡献核定与真实试讲仍待完成，临时材料暂保留。

## 技术栈

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + TypeScript + Vite（开发期 `/api` 同源代理） |
| 后端 | Python + FastAPI（Uvicorn 运行），Pillow 生成缩略图 |
| 数据库 | PostgreSQL 17（Docker 容器部署） |
| ORM / 认证 | SQLAlchemy 2（映射 `docker/postgres/02-schema.sql` 既有表结构）；JWT（PyJWT + HttpOnly Cookie `album_session`），bcrypt 密码哈希 |

开发期整个系统运行于开发本机：FastAPI 本地启动，浏览器访问 `localhost`，数据库为本地 Docker 容器中的 PostgreSQL。**无需云服务器。**

## 本地开发数据库

首次启动时将 `.env.example` 复制为 `.env`，为 `ALBUM_DB_ADMIN_PASSWORD` 和 `ALBUM_DB_PASSWORD` 分别填写不同的随机密码。在项目根目录运行：

```powershell
docker compose up -d --build --wait db
```

应用连接地址为 `127.0.0.1:55432`，数据库名为 `electronic_photo_album`，账号为 `album_app`。应用密码取自 `.env` 的 `ALBUM_DB_PASSWORD`。端口冲突时修改 `.env` 的 `ALBUM_DB_PORT`。数据库数据保存在项目专用 Docker 命名卷中。首次创建数据卷时会自动创建六张空业务表，见 [建表脚本](docker/postgres/02-schema.sql)。

## 后端运行（FastAPI）

`.env` 中还需要填写后端会话配置 `ALBUM_JWT_SECRET`（不少于 32 个字符的随机字符串）等，字段见 `.env.example`。然后在 `backend/` 目录：

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端监听 `http://127.0.0.1:8000`，接口统一挂在 `/api` 前缀下。表结构由数据库容器初始化脚本创建，后端不自动建表，ORM 模型与建表脚本一一对应。

## 前端运行（Vue 3）

另开一个终端，在 `frontend/` 目录：

```powershell
cd frontend
npm install
npm run dev
```

浏览器访问 `http://localhost:5173`。开发服务器将 `/api` 代理到本机 8000 端口，会话 Cookie 作用于同一来源。

## 初始化演示数据

数据库与后端依赖就绪后，在 `backend/` 目录执行一次（可重复执行，已有数据不改动）：

```powershell
python -m app.seed
```

写入 4 个预置类别（风景、人物、生活、旅行）与 3 个演示账号：

| 账号 | 角色 | 密码（取自 `.env`） |
|------|------|---------------------|
| `demo_a` | 普通用户 | `ALBUM_DEMO_PASSWORD`（示例 `album-demo-123`） |
| `demo_b` | 普通用户 | `ALBUM_DEMO_PASSWORD` |
| `admin` | 管理员 | `ALBUM_ADMIN_PASSWORD`（示例 `album-admin-123`） |

## 中期答辩演示流程

1. `demo_a` 登录 → 我的相册 → 创建公开相册并上传 jpg/png/gif 图片，展示缩略图与照片详情。
2. `demo_a` 退出，`demo_b` 登录 → 浏览相册能看到 `demo_a` 的公开相册、缩略图与原图。
3. `demo_a` 把相册改为私有 → `demo_b` 刷新后，相册列表、照片详情、原图与缩略图链接全部返回 404；`demo_a` 本人仍可正常查看。
4. 上传超过 10MB 或格式不符的文件，展示“仅支持 jpg/png/gif，且不超过 10MB”的回退提示。

## 集成测试

`backend/tests/test_main_flow.py` 覆盖上述主流程与异常分支（数据库需已启动）：

```powershell
cd backend
python -m pytest
```

## 功能模块

| 模块 | 用例 |
|------|------|
| 账户管理 | 用户注册、用户登录 |
| 相册管理 | 创建相册、修改相册、相册类别管理（管理员） |
| 照片管理 | 上传图片、浏览照片 |
| 评论管理 | 对照片评论（含删除自己的评论，扩展流程） |

## 目录结构

```
电子相册系统/
├── README.md            ← 本文件
├── AGENTS.md            ← 给 AI 助手/协作者的项目说明
├── backend/             ← FastAPI 后端（app/ 应用包、tests/ 集成测试）
├── frontend/            ← Vue 3 + TS 前端（src/ 页面与路由，/api 同源代理）
├── docker/postgres/     ← PostgreSQL 容器构建与初始化 SQL（应用账号、六表结构）
├── docs/
│   ├── 需求分析/         ← 系统目标、模块划分、用例描述
│   ├── 交付/             ← 各成员交付（参考样板：1-账户管理-钟标）
│   ├── 图稿/             ← 报告用图（.drawio 源文件 + PNG）
│   │   └── 教学演示/      ← 绘图方法演示图（不入报告）
│   └── 绘图规范.md        ← 全组统一的画图要求
└── tools/               ← 图稿工具（figstyle.py 统一样式、render_drawio.py / postprocess_png.py、gen_drawio.py 等，见 tools/README.md）
```

## 协作约定（Git 同步范围）

**进 Git**：前后端源代码、建库与种子数据脚本（`seed.sql`）、演示用样例图片（`demo_photos/`）、本文档目录下所有文档。

**不进 Git**（加入 `.gitignore`）：`uploads/`（用户上传的照片）、数据库数据文件、`.env` 等本地配置。

**数据同步方式**：每人本地 Docker 中的 PostgreSQL 各自独立，通过执行同一份 `seed.sql` 保持一致；不互相传输数据库文件或压缩包。

## 当前进度

- [x] 需求梳理、系统目标定稿、功能模块划分（4 模块 8 用例）
- [x] 8 个用例的用例描述初稿
- [x] 技术选型与绘图规范确定（现行为 v2.1，见 `docs/绘图规范.md`）
- [x] 图 2-1 系统体系结构图、图 2-2 功能框架图（已按 v2.1 重出）
- [x] 阶段 2：各模块用例图 + 活动图（含图后说明文字）
- [x] 阶段 3：各模块类模型图 + 协作图
- [x] 绘图规范 v2.1 与账户管理模块样板重出（分支 `feat/unified-figure-style`）
- [x] 逻辑检查与视觉返修：其余三个模块及图 2-1、图 2-2 共 23 张图已重出，见 [返修检查记录](docs/图稿/返修检查记录.md)
- [ ] 阶段 4：非功能需求、分工与总结、43 页报告已整合；成员信息和贡献比例待确认（#24）
- [ ] 阶段 5：10 分钟主讲 PPT 已制作（16 页主讲 + 30 页隐藏备用图，含备注）；待真实计时试讲（#24）
- [ ] 系统实现与期末交付（源码 + SQL 脚本）：中期答辩主流程已落地——注册 / 登录 / 会话恢复、创建与修改相册（乐观锁）、上传图片（校验 + 缩略图 + 幂等重试）、浏览照片与公私权限联调（#37）；评论、点赞、类别管理与启动核对待后续任务

## 关键范围约定

严格按题目给定用例实现，**不新增功能**：不支持视频，不做点赞 / 关注 / 信息流 / 好友机制。
