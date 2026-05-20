const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  Header, Footer, AlignmentType, HeadingLevel, BorderStyle,
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

const doc = new Document({
  styles: { default: { document: { run: { font: "Microsoft YaHei", size: 21 } } } },
  sections: [{
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "学生积分管理系统 · 运维手册", font: "Microsoft YaHei", size: 18, color: "999999" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "第 ", font: "Microsoft YaHei", size: 18 }), new TextRun({ children: [PageNumber.CURRENT], font: "Microsoft YaHei", size: 18 }), new TextRun({ text: " 页", font: "Microsoft YaHei", size: 18 })] })] }) },
    children: [
      // 封面
      new Paragraph({ spacing: { before: 4000 }, alignment: AlignmentType.CENTER, children: [] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "学生积分管理系统", font: "Microsoft YaHei", bold: true, size: 52, color: "1E3A5F" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "v2.0", font: "Microsoft YaHei", size: 32, color: "666666" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 800, after: 100 }, children: [new TextRun({ text: "运维手册", font: "Microsoft YaHei", bold: true, size: 36, color: "2B579A" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "版本：v2.0  |  更新日期：2026-05-16", font: "Microsoft YaHei", size: 20, color: "999999" })] }),
      pb(),
      new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-3" }),
      pb(),

      // 第1章
      h1("第1章 系统架构"),
      h2("1.1 部署拓扑"),
      p("系统采用前后端一体化部署，由 Railway 平台托管。"),
      b("用户浏览器 ──HTTPS──▶ Railway Edge ──▶ FastAPI (uvicorn)"),
      b("                                              │"),
      b("                              ┌─────────────────┼─────────────────┐"),
      b("                              ▼                 ▼                 ▼"),
      b("                        /assets/*          /api/*           /admin-panel"),
      b("                     (gzip+缓存)        (业务API)         (管理后台)"),
      b("                              │"),
      b("                              ▼"),
      b("                     PostgreSQL (Railway 内网)"),
      h2("1.2 访问地址"),
      makeTable(["服务", "地址"], [
        ["教师端前端", "https://sps-production-6221.up.railway.app"],
        ["管理后台", "https://sps-production-6221.up.railway.app/admin-panel"],
        ["API 文档", "https://sps-production-6221.up.railway.app/docs"],
        ["健康检查", "https://sps-production-6221.up.railway.app/api/health"],
      ], [3000, 6026]),
      h2("1.3 性能优化"),
      makeTable(["优化项", "配置", "效果"], [
        ["gzip 预压缩", "vite-plugin-compression 构建时生成 .gz", "element-plus 832KB→311KB (-63%)"],
        ["代码分割", "manualChunks: element-plus / vendor", "首屏只需加载 index.js + vendor.js"],
        ["静态资源缓存", "Cache-Control: max-age=31536000, immutable", "浏览器长期缓存，减少重复请求"],
        ["index.html 不缓存", "Cache-Control: no-cache", "确保每次拿到最新资源引用"],
        ["terser 压缩", "drop_console + drop_debugger", "减小 JS 体积"],
      ], [2500, 3526, 3000]),
      pb(),

      // 第2章
      h1("第2章 日常运维"),
      h2("2.1 查看日志"),
      p("Railway 控制台 → 服务 → Deployments → 点击最新部署 → Logs。也可使用 CLI："),
      b("railway logs --tail"),
      h2("2.2 环境变量管理"),
      makeTable(["变量", "说明", "备注"], [
        ["DATABASE_URL", "PostgreSQL 连接串", "Railway 自动生成"],
        ["SECRET_KEY", "JWT 签名密钥", "建议 ≥ 32 位随机字符串"],
        ["PORT", "监听端口", "Railway 自动注入"],
        ["INIT_ADMIN_USER", "初始化管理员用户名", "一次性使用，创建后删除"],
        ["INIT_ADMIN_PASS", "初始化管理员密码", "一次性使用，创建后删除"],
      ], [3000, 3000, 3026]),
      p("设置环境变量：railway variables set KEY=VALUE"),
      p("查看环境变量：railway variables"),
      h2("2.3 数据库管理"),
      h3("通过管理后台"),
      p("访问 /admin-panel → 🗄️ 数据库管理，可对所有 8 张表进行可视化 CRUD 操作（分页、搜索、新增、编辑、删除）。password_hash 字段自动脱敏显示为 ***。"),
      h3("通过 Railway CLI"),
      b("railway connect postgres"),
      h2("2.4 数据备份"),
      h3("手动备份"),
      p("管理后台 → 💾 数据备份 → 下载备份文件。导出所有关键数据为 JSON 格式。"),
      h3("自动备份建议"),
      p("建议通过 Railway Cron 或外部定时任务，定期调用 /api/admin/backup 接口下载备份。"),
      h2("2.5 重新部署"),
      b("# 修改代码后重新部署"),
      b("cd frontend && npm run build"),
      b("rmdir /S /Q backend\\static && xcopy frontend\\dist backend\\static /E /I /Y"),
      b("cd backend && railway up"),
      pb(),

      // 第3章
      h1("第3章 管理后台"),
      h2("3.1 功能模块"),
      makeTable(["模块", "功能说明"], [
        ["📊 数据总览", "核心指标卡片（学生数/班级数/积分/勋章）、积分趋势折线图、最近登录、系统信息"],
        ["👥 用户管理", "用户列表、创建用户、删除用户、重置密码、设置账号有效期（+30天/+90天/+1年/永久）"],
        ["📋 登录日志", "按成功/失败筛选，显示 IP、时间、失败原因"],
        ["📈 积分日志", "最近积分操作记录"],
        ["🗄️ 数据库管理", "8 张表的可视化 CRUD（分页+搜索+新增+编辑+删除）"],
        ["💾 数据备份", "一键导出 JSON 备份文件"],
      ], [2500, 6526]),
      h2("3.2 数据库管理详情"),
      p("支持的表：users / classes / students / points_logs / points_rules / badges / student_badges / login_logs"),
      h3("安全措施"),
      p("• password_hash 字段显示为 ***，不可编辑"),
      p("• ID 和时间戳字段自动生成，不可编辑"),
      p("• 必填字段前端校验"),
      p("• 搜索对所有文本字段做模糊匹配（ILIKE）"),
      pb(),

      // 第4章
      h1("第4章 安全运维"),
      h2("4.1 安全头"),
      makeTable(["头部", "值", "作用"], [
        ["Content-Security-Policy", "script-src 'self' ...", "防止 XSS"],
        ["X-Content-Type-Options", "nosniff", "防止 MIME 嗅探"],
        ["X-Frame-Options", "DENY", "防止点击劫持"],
        ["X-XSS-Protection", "1; mode=block", "浏览器 XSS 过滤"],
        ["Referrer-Policy", "strict-origin-when-cross-origin", "限制 Referer"],
      ], [3000, 3026, 3000]),
      h2("4.2 登录安全"),
      p("• 图形验证码（数学题，每次登录生成"),
      p("• 登录失败 5 次锁定 15 分钟（内存计数器，重启清空）"),
      p("• 登录日志记录 IP、时间、结果、失败原因"),
      h2("4.3 密码策略"),
      p("• 最少 8 位，必须包含大写字母、小写字母和数字"),
      p("• bcrypt 哈希存储（salt 轮数自动）"),
      h2("4.4 账号有效期管理"),
      p("• 管理员可在管理后台为每个用户设置账号有效期"),
      p("• 支持快捷选项：+30天、+90天、+1年、永久有效"),
      p("• 过期账号无法登录（返回 403 错误，前端显示提示信息）"),
      p("• 已登录用户在过期后，任何 API 操作都会被强制踢出（返回登录页）"),
      p("• 每次 API 请求都在认证依赖（get_current_user）中实时检查过期状态"),
      p("• 有效期以 UTC 时间存储，前端自动转换为北京时间显示"),
      h2("4.5 管理员密码重置"),
      p("如忘记管理员密码，可通过环境变量重新初始化："),
      b("railway variables set INIT_ADMIN_USER=admin INIT_ADMIN_PASS=NewPass123"),
      b("railway up  # 触发重启，自动更新密码"),
      b("railway variables delete INIT_ADMIN_USER INIT_ADMIN_PASS  # 用完删除"),
      pb(),

      // 第5章
      h1("第5章 故障处理"),
      makeTable(["故障现象", "排查步骤", "解决方案"], [
        ["页面白屏", "1. 检查 Railway 部署日志\n2. 确认 static/ 目录存在", "重新构建前端并部署"],
        ["API 返回 500", "1. 查看 Railway 日志\n2. 检查 DATABASE_URL", "确认数据库连接正常"],
        ["gzip 未生效", "1. curl -H 'Accept-Encoding: gzip' 检查响应头", "确认 .gz 文件存在于 static/assets/"],
        ["管理后台加载失败", "1. 检查 /admin-assets/ 路径\n2. 检查 CSP 头", "确认 templates/static/ 目录完整"],
        ["账号提示已过期无法登录", "1. 确认管理员是否设置了有效期\n2. 检查服务器时间", "在管理后台续期或设为永久；或通过数据库重置 expires_at 为 NULL"],
        ["用户使用中突然被踢出", "确认账号有效期是否已到期", "在管理后台续期后，用户重新登录即可"],
        ["登录被锁定", "等待 15 分钟或重启服务", "内存计数器重启清空"],
      ], [2000, 3526, 3500]),
      pb(),

      // 第6章
      h1("第6章 监控与告警"),
      h2("6.1 健康检查"),
      p("GET /api/health 返回 { status: 'ok' }，可用于外部监控。"),
      h2("6.2 Railway 指标"),
      p("Railway 控制台提供 CPU、内存、网络流量等实时指标。"),
      h2("6.3 日志监控"),
      p("所有 uvicorn 日志输出到 stdout（已配置），Railway 自动收集。错误日志包含完整堆栈。"),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("../学生积分管理系统-运维手册.docx", buf);
  console.log("[OK] 运维手册已生成");
});
