const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageNumber, PageBreak, TableOfContents
} = require("docx");

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };
const cellMargins = { top: 80, bottom: 80, left: 120, right: 120 };
const PAGE_WIDTH = 9026;

function hCell(text, width) {
  return new TableCell({ borders, width: { size: width, type: WidthType.DXA }, shading: { fill: "2B579A", type: ShadingType.CLEAR }, margins: cellMargins, verticalAlign: "center", children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Microsoft YaHei", size: 20 })] })] });
}
function cell(text, width, opts = {}) {
  return new TableCell({ borders, width: { size: width, type: WidthType.DXA }, margins: cellMargins, shading: opts.shade ? { fill: "F2F7FB", type: ShadingType.CLEAR } : undefined, children: [new Paragraph({ children: [new TextRun({ text, font: "Microsoft YaHei", size: 20, ...(opts.bold ? { bold: true } : {}) })] })] });
}
function h1(t) { return new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 360, after: 200 }, children: [new TextRun({ text: t, font: "Microsoft YaHei", bold: true, size: 32, color: "1E3A5F" })] }); }
function h2(t) { return new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 160 }, children: [new TextRun({ text: t, font: "Microsoft YaHei", bold: true, size: 28, color: "2B579A" })] }); }
function h3(t) { return new Paragraph({ heading: HeadingLevel.HEADING_3, spacing: { before: 200, after: 120 }, children: [new TextRun({ text: t, font: "Microsoft YaHei", bold: true, size: 24, color: "3B7DD8" })] }); }
function p(t) { return new Paragraph({ spacing: { after: 120, line: 360 }, children: [new TextRun({ text: t, font: "Microsoft YaHei", size: 21 })] }); }
function b(t) { return new Paragraph({ spacing: { after: 80, line: 360 }, indent: { left: 420 }, children: [new TextRun({ text: t, font: "Consolas", size: 20, color: "333333" })] }); }
function pb() { return new Paragraph({ children: [new PageBreak()] }); }

function makeTable(headers, rows, widths) {
  const headerRow = new TableRow({ children: headers.map((h, i) => hCell(h, widths[i])) });
  const dataRows = rows.map((row, ri) => new TableRow({ children: row.map((c, ci) => cell(c, widths[ci], { shade: ri % 2 === 1 })) }));
  return new Table({ width: { size: PAGE_WIDTH, type: WidthType.DXA }, rows: [headerRow, ...dataRows] });
}

function coverPage() {
  return [
    new Paragraph({ spacing: { before: 4000 }, alignment: AlignmentType.CENTER, children: [] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "学生积分管理系统", font: "Microsoft YaHei", bold: true, size: 52, color: "1E3A5F" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "v2.0", font: "Microsoft YaHei", size: 32, color: "666666" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 800, after: 100 }, children: [new TextRun({ text: "开发手册", font: "Microsoft YaHei", bold: true, size: 36, color: "2B579A" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "（含部署指南）", font: "Microsoft YaHei", size: 24, color: "888888" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "版本：v2.0  |  更新日期：2026-05-10", font: "Microsoft YaHei", size: 20, color: "999999" })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "技术栈：Vue 3 + FastAPI + PostgreSQL", font: "Microsoft YaHei", size: 20, color: "999999" })] }),
    pb(),
  ];
}

const doc = new Document({
  styles: { default: { document: { run: { font: "Microsoft YaHei", size: 21 } } } },
  sections: [{
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "学生积分管理系统 · 开发手册", font: "Microsoft YaHei", size: 18, color: "999999" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "第 ", font: "Microsoft YaHei", size: 18 }), new TextRun({ children: [PageNumber.CURRENT], font: "Microsoft YaHei", size: 18 }), new TextRun({ text: " 页", font: "Microsoft YaHei", size: 18 })] })] }) },
    children: [
      ...coverPage(),
      new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-3" }),
      pb(),

      // ── 第1章 ──
      h1("第1章 项目概述"),
      h2("1.1 项目简介"),
      p("学生积分管理系统是一套面向教师的班级管理工具，通过游戏化积分机制激励学生。系统采用前后端分离架构，支持多班级管理、学生积分记录、勋章颁发、课堂工具（随机点名/计时器/分组/积分抽奖）等功能。管理后台独立部署，提供数据可视化和数据库 CRUD 操作。"),
      h2("1.2 技术栈"),
      makeTable(["层级", "技术", "版本", "说明"], [
        ["前端框架", "Vue 3", "3.4+", "Composition API + SFC"],
        ["构建工具", "Vite", "6.x", "HMR + 代码分割 + gzip 预压缩"],
        ["UI 组件库", "Element Plus", "2.x", "按需引入，中文支持"],
        ["状态管理", "Pinia", "2.x", "轻量级，支持持久化"],
        ["后端框架", "FastAPI", "0.110+", "异步路由，自动文档"],
        ["ORM", "SQLAlchemy (async)", "2.0+", "异步会话，模型声明式"],
        ["数据库", "PostgreSQL", "15", "Railway 托管"],
        ["部署平台", "Railway", "-", "CLI 部署，自动 HTTPS"],
      ], [1800, 2200, 1500, 3526]),
      h2("1.3 系统架构"),
      p("前后端一体化部署：Vue 3 构建产物（含 .gz 预压缩文件）复制到 backend/static/，由 FastAPI 统一提供服务。后端同时托管独立的管理后台页面（/admin-panel）。"),
      b("用户浏览器 → HTTPS → Railway Edge → FastAPI"),
      b("  ├─ /assets/*     → 静态文件（gzip 优先 + 长期缓存）"),
      b("  ├─ /api/*        → 业务 API 路由"),
      b("  ├─ /admin-panel  → 管理后台（独立 HTML/JS）"),
      b("  └─ /*            → SPA 兜底 → index.html"),
      pb(),

      // ── 第2章 ──
      h1("第2章 环境搭建"),
      h2("2.1 开发环境要求"),
      makeTable(["工具", "版本要求", "用途"], [
        ["Node.js", "≥ 18", "前端构建与依赖管理"],
        ["Python", "≥ 3.11", "后端运行"],
        ["PostgreSQL", "≥ 14", "数据库（开发可用 SQLite）"],
        ["Railway CLI", "最新", "部署"],
      ], [2500, 2000, 4526]),
      h2("2.2 本地启动"),
      h3("后端"),
      b("cd backend"),
      b("pip install -r requirements.txt"),
      b("uvicorn app.main:app --reload --port 8000"),
      h3("前端"),
      b("cd frontend"),
      b("npm install"),
      b("npm run dev"),
      p("Vite 开发服务器会自动将 /api 请求代理到后端 localhost:8000。"),
      h2("2.3 环境变量"),
      makeTable(["变量名", "说明", "示例"], [
        ["DATABASE_URL", "PostgreSQL 连接串", "postgresql+asyncpg://user:pass@host/db"],
        ["SECRET_KEY", "JWT 签名密钥", "随机 32 位字符串"],
        ["INIT_ADMIN_USER", "首次启动自动创建管理员（一次性）", "admin"],
        ["INIT_ADMIN_PASS", "管理员密码", "YourSecurePass1"],
      ], [3000, 3000, 3026]),
      pb(),

      // ── 第3章 ──
      h1("第3章 后端核心模块"),
      h2("3.1 目录结构"),
      b("backend/app/"),
      b("  ├── main.py          # 应用入口、中间件、路由注册、gzip 静态服务"),
      b("  ├── config.py         # 环境变量配置"),
      b("  ├── database.py       # 异步引擎与会话工厂"),
      b("  ├── models/           # SQLAlchemy 模型（User/Class/Student/Badge/PointsLog）"),
      b("  ├── schemas/          # Pydantic 请求/响应模型（含 XSS 过滤、密码强度校验）"),
      b("  ├── routes/           # API 路由（auth/classes/students/badges/leaderboard/admin）"),
      b("  ├── utils/            # 工具模块"),
      b("  │   ├── auth.py       # JWT + bcrypt 密码哈希"),
      b("  │   ├── deps.py       # 依赖注入（get_current_user）"),
      b("  │   ├── security.py   # CSP 安全头中间件"),
      b("  │   ├── exceptions.py # 全局异常处理器（隐藏 SQL 错误细节）"),
      b("  │   └── login_security.py # 图形验证码 + 登录锁定 + 登录日志"),
      b("  ├── templates/        # 管理后台独立页面"),
      b("  │   ├── admin.html    # 管理后台 HTML（自包含深色主题）"),
      b("  │   └── static/       # 管理后台 JS/CSS（自托管 Vue/axios）"),
      b("  └── static/           # 前端构建产物（含 .gz 预压缩）"),
      h2("3.2 数据库模型"),
      makeTable(["表名", "模型类", "关键字段", "说明"], [
        ["users", "User", "id, username, password_hash, display_name, expires_at", "教师账户（含账号有效期）"],
        ["classes", "Class", "id, name, owner_id, is_active", "班级"],
        ["students", "Student", "id, name, student_no, points, level, pet_type, class_id", "学生"],
        ["points_logs", "PointsLog", "id, student_id, points, reason, category, operator_id", "积分记录"],
        ["points_rules", "PointsRule", "id, name, points, category, icon, owner_id", "积分规则"],
        ["badges", "Badge", "id, name, icon, description, owner_id", "勋章定义"],
        ["student_badges", "StudentBadge", "id, student_id, badge_id, awarded_by", "学生勋章关联"],
        ["login_logs", "LoginLog", "id, username, ip_address, success, fail_reason", "登录日志"],
      ], [1800, 2000, 3226, 2000]),
      h2("3.3 安全机制"),
      h3("密码安全"),
      p("bcrypt 哈希存储，密码强度校验（≥8位，含大小写字母和数字）。"),
      h3("登录安全"),
      p("图形验证码（数学题，Python PIL 生成）、登录失败锁定（5次失败锁15分钟，内存计数器）、登录日志记录。"),
      h3("输入安全"),
      p("XSS 过滤（学生/积分 Schema 的 field_validator）、SQL 注入防护（SQLAlchemy 参数化查询）、积分范围限制（-1000~1000）。"),
      h3("响应安全"),
      p("CSP 内容安全策略（管理后台路径放宽 unsafe-eval）、X-Content-Type-Options、X-Frame-Options、X-XSS-Protection、Referrer-Policy。全局异常处理器隐藏数据库错误细节。"),
      h2("3.4 管理后台"),
      p("管理后台完全独立于前端教师端，通过 /admin-panel 访问。使用自托管的 Vue 3 CDN 脚本，深色主题。"),
      h3("API 端点"),
      makeTable(["方法", "路径", "说明"], [
        ["GET", "/api/admin/stats", "系统统计概览"],
        ["GET", "/api/admin/users", "用户列表"],
        ["POST", "/api/admin/users", "创建用户"],
        ["DELETE", "/api/admin/users/{id}", "删除用户"],
        ["POST", "/api/admin/users/{id}/reset-password", "重置密码"],
        ["PUT", "/api/admin/users/{id}/expiry", "设置用户账号有效期"],
        ["GET", "/api/admin/login-logs", "登录日志"],
        ["GET", "/api/admin/points-logs", "积分日志"],
        ["POST", "/api/admin/backup", "数据备份下载"],
        ["GET", "/api/admin/db/tables", "获取所有表结构"],
        ["GET", "/api/admin/db/{table}", "分页查询表数据（支持搜索）"],
        ["POST", "/api/admin/db/{table}", "新增记录"],
        ["PUT", "/api/admin/db/{table}/{id}", "更新记录"],
        ["DELETE", "/api/admin/db/{table}/{id}", "删除记录"],
      ], [1500, 4526, 3000]),
      pb(),

      // ── 第4章 ──
      h1("第4章 前端核心模块"),
      h2("4.1 目录结构"),
      b("frontend/src/"),
      b("  ├── main.js              # 入口（Element Plus + Pinia + Router）"),
      b("  ├── api/index.js          # Axios 实例 + 请求/响应拦截器"),
      b("  ├── router/index.js       # 路由配置（懒加载）"),
      b("  ├── stores/               # Pinia Store（auth/class）"),
      b("  ├── components/"),
      b("  │   ├── AppLayout.vue     # 响应式布局（桌面侧边栏 + 移动端抽屉）"),
      b("  │   └── SidebarContent.vue # 侧边栏菜单组件"),
      b("  ├── views/"),
      b("  │   ├── Dashboard.vue     # 班级总览 + 统计卡片"),
      b("  │   ├── Students.vue      # 学生管理（手机端卡片列表）"),
      b("  │   ├── StudentDetail.vue # 学生详情 + 积分时间线"),
      b("  │   ├── Leaderboard.vue   # 排行榜"),
      b("  │   ├── Badges.vue        # 勋章管理"),
      b("  │   ├── Tools.vue         # 课堂工具（随机点名/计时器/分组/积分抽奖/积分兑换/积分提醒）"),
      b("  │   ├── PointsLogs.vue    # 积分日志（分页查询班级积分变动）"),
      b("  │   ├── Classes.vue       # 班级管理"),
      b("  │   ├── Settings.vue      # 系统设置"),
      b("  │   └── Login.vue         # 登录页（含验证码）"),
      b("  └── assets/styles/main.css # 全局响应式样式"),
      h2("4.2 性能优化"),
      h3("代码分割"),
      p("Vite rollupOptions.manualChunks 将 element-plus 和 vendor（vue/vue-router/pinia/axios）拆为独立 chunk，各页面组件懒加载。"),
      h3("gzip 预压缩"),
      p("vite-plugin-compression 在构建时自动生成 .gz 文件。后端检测 Accept-Encoding: gzip 请求头，优先返回压缩版本。element-plus 从 832KB 压缩到 311KB。"),
      h3("静态资源缓存"),
      p("assets 文件设 Cache-Control: public, max-age=31536000, immutable（浏览器长期缓存）。index.html 设为 no-cache 确保每次拿到最新资源引用。"),
      h3("构建压缩"),
      p("terser 压缩，移除 console.log 和 debugger。"),
      h2("4.3 响应式设计"),
      makeTable(["断点", "适配策略"], [
        ["< 480px（超小屏）", "Badge 网格 2 列、按钮字号缩小"],
        ["< 768px（手机）", "侧边栏变为抽屉、统计卡片 2 列、表格横向滚动、弹窗 95% 宽度"],
        ["768px ~ 1023px（平板）", "侧边栏自动折叠、主内容 padding 缩小"],
        ["≥ 1024px（桌面）", "完整侧边栏 + 主内容区"],
      ], [3000, 6026]),
      h2("4.4 课堂工具"),
      p("Tools.vue 包含四个工具，均支持手机端使用："),
      makeTable(["工具", "功能", "说明"], [
        ["🎲 随机点名", "公平随机抽取学生", "支持多轮不重复，动画滚动效果"],
        ["⏱️ 计时器", "课堂倒计时", "预设 1/3/5 分钟，支持暂停/重置"],
        ["👥 随机分组", "均衡分组", "设置组数，随机分配学生"],
        ["🎰 积分抽奖", "消耗积分抽奖激励", "可编辑奖项（名称/说明/颜色/权重），存 localStorage，支持添加/删除奖项"],
        ["🎁 积分兑换", "积分兑换实物奖品", "预设奖品可编辑（localStorage），选择学生+奖品自动扣减积分"],
        ["🔔 积分提醒", "阈值达标检测", "设定积分阈值，一键检查达标学生列表"],
      ], [2000, 2500, 4526]),
      pb(),

      // ── 第5章 ──
      h1("第5章 部署"),
      h2("5.1 部署流程"),
      p("使用 Railway CLI 直接部署（因国内 GitHub 推送受限）："),
      b("# 1. 构建前端"),
      b("cd frontend && npm run build"),
      b(""),
      b("# 2. 复制构建产物到后端"),
      b("rmdir /S /Q backend\\static"),
      b("xcopy frontend\\dist backend\\static /E /I /Y"),
      b(""),
      b("# 3. 部署到 Railway"),
      b("cd backend"),
      b("railway up"),
      h2("5.2 Railway 配置"),
      makeTable(["配置项", "值"], [
        ["项目 ID", "be4ed1ea-f2bb-4169-8a29-8779398d93ac"],
        ["后端服务 ID", "0b36e499-fc12-4850-89dd-0392dd03242c"],
        ["PostgreSQL 服务 ID", "4c6424ef-6e17-4547-9242-ddf2c4760e5b"],
        ["环境 ID", "2e416499-6004-40e6-a051-8d6b28204cb3"],
        ["后端 API 域名", "https://sps-production-6221.up.railway.app"],
        ["管理后台", "https://sps-production-6221.up.railway.app/admin-panel"],
      ], [3000, 6026]),
      h2("5.3 关键问题与解决方案"),
      makeTable(["问题", "解决方案"], [
        ["$PORT 变量未展开", "startCommand 使用 bash -c 包装"],
        ["bcrypt 版本冲突", "requirements.txt 固定 bcrypt==4.0.1"],
        ["Railway rootDirectory 冲突", "清除 rootDirectory，从 backend/ 目录上传"],
        ["管理后台 CSP 阻止脚本", "自托管 Vue/axios 脚本 + 放宽 unsafe-eval"],
        ["无法连接 Railway 内网数据库", "环境变量 INIT_ADMIN_USER/PASS 启动时自动创建管理员"],
        ["gzip 未生效", "移除 StaticFiles 挂载，统一走 catch-all 路由检测 .gz"],
      ], [4000, 5026]),
      pb(),

      // ── 第6章 ──
      h1("第6章 测试账号"),
      makeTable(["用途", "用户名", "密码", "地址"], [
        ["教师端", "teacher", "123456", "https://sps-production-6221.up.railway.app"],
        ["管理后台", "admin", "Zty256310x", "https://sps-production-6221.up.railway.app/admin-panel"],
      ], [2000, 2000, 2526, 2500]),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("../学生积分管理系统-开发手册.docx", buf);
  console.log("[OK] 开发手册已生成");
});
