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
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: "学生积分管理系统 · 用户使用手册", font: "Microsoft YaHei", size: 18, color: "999999" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "第 ", font: "Microsoft YaHei", size: 18 }), new TextRun({ children: [PageNumber.CURRENT], font: "Microsoft YaHei", size: 18 }), new TextRun({ text: " 页", font: "Microsoft YaHei", size: 18 })] })] }) },
    children: [
      // 封面
      new Paragraph({ spacing: { before: 4000 }, alignment: AlignmentType.CENTER, children: [] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "学生积分管理系统", font: "Microsoft YaHei", bold: true, size: 52, color: "1E3A5F" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: "v2.0", font: "Microsoft YaHei", size: 32, color: "666666" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 800, after: 100 }, children: [new TextRun({ text: "用户使用手册", font: "Microsoft YaHei", bold: true, size: 36, color: "2B579A" })] }),
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "版本：v2.0  |  更新日期：2026-05-10", font: "Microsoft YaHei", size: 20, color: "999999" })] }),
      pb(),
      new TableOfContents("目录", { hyperlink: true, headingStyleRange: "1-3" }),
      pb(),

      // 第1章
      h1("第1章 快速开始"),
      h2("1.1 访问系统"),
      p("在浏览器中打开系统地址即可使用，支持电脑和手机端。"),
      b("电脑端：https://class-pet-v2-production.up.railway.app"),
      b("手机端：同上地址，自动适配手机屏幕"),
      h2("1.2 登录"),
      p("1. 打开系统地址，进入登录页面"),
      p("2. 输入用户名和密码"),
      p("3. 完成验证码计算（如 41 - 9 = ? 填写 32）"),
      p("4. 点击「登录」按钮"),
      p("注意：连续输错密码 5 次将被锁定 15 分钟，请确认密码正确后再试。"),
      h2("1.3 首次使用"),
      p("登录后建议按以下顺序操作："),
      p("① 班级管理 → 创建班级"),
      p("② 学生管理 → 添加学生"),
      p("③ 开始使用积分、勋章、课堂工具等功能"),
      pb(),

      // 第2章
      h1("第2章 班级管理"),
      h2("2.1 创建班级"),
      p("侧边栏 → 班级管理 → 点击「新建班级」按钮 → 填写班级名称和描述 → 确认。"),
      h2("2.2 切换班级"),
      p("桌面端：侧边栏顶部的班级下拉框可切换当前班级。"),
      p("手机端：打开侧边栏 → 点击顶部班级名称切换。"),
      h2("2.3 编辑/删除"),
      p("在班级管理页面，点击班级卡片上的编辑或删除按钮。删除班级会同时删除该班级下的所有学生数据，请谨慎操作。"),
      pb(),

      // 第3章
      h1("第3章 学生管理"),
      h2("3.1 添加学生"),
      p("侧边栏 → 学生管理 → 点击「添加学生」→ 填写学号、姓名、选择宠物类型。"),
      h2("3.2 批量导入"),
      p("支持两种批量导入方式："),
      h3("文本批量导入"),
      p("点击「批量导入」→ 在文本框中每行输入一个学生（格式：学号,姓名,萌宠类型），点击导入。"),
      h3("Excel 批量导入"),
      p("点击「批量导入」→ 切换到「Excel 导入」标签 → 上传 .xlsx 文件。系统会自动识别列名（支持中英文），预览数据后确认导入。"),
      p("支持的列名：学号/编号/No、姓名/名字/Name、萌宠/宠物类型/Pet。萌宠类型支持中文（猫/狗/兔/熊猫/企鹅）和英文（cat/dog/rabbit/panda/penguin）。"),
      h2("3.2 积分操作"),
      p("在学生列表中点击学生 → 进入学生详情页 → 点击「加分」或「减分」按钮 → 选择积分规则或手动输入积分和原因。"),
      makeTable(["操作", "说明"], [
        ["➕ 加分", "选择预设规则或自定义积分值和原因"],
        ["➖ 减分", "输入扣分值和原因，积分下限为 0"],
        ["📝 积分记录", "查看该学生所有积分变动历史"],
      ], [2000, 7026]),
      h2("3.3 宠物系统"),
      p("每个学生可选择一个萌宠角色（🐱猫/🐶狗/🐰兔/🐼熊猫/🐧企鹅），积分累积可提升宠物等级。"),
      h2("3.4 手机端适配"),
      p("手机端学生列表自动切换为卡片布局，点击卡片进入详情。表格横向可滚动。"),
      pb(),

      // 第4章
      h1("第4章 积分系统"),
      h2("4.1 积分规则"),
      p("侧边栏 → 积分规则 → 管理预设的积分规则（如「回答问题 +5」「未交作业 -10」）。"),
      p("每个规则包含：名称、积分值、类型（奖励/惩罚）、图标。"),
      h2("4.2 积分操作"),
      p("在学生详情页或学生列表中，选择规则后一键加分/减分。也可自定义积分值。"),
      h2("4.3 积分范围"),
      p("单次积分操作范围：-1000 ~ +1000。总积分最低为 0。"),
      pb(),

      // 第5章
      h1("第5章 勋章系统"),
      h2("5.1 创建勋章"),
      p("侧边栏 → 勋章管理 → 点击「创建勋章」→ 填写名称、选择图标、填写描述。"),
      h2("5.2 颁发勋章"),
      p("在勋章卡片上点击「颁发」→ 选择要颁发的学生 → 确认。一个学生可获得多个不同勋章。"),
      h2("5.3 管理勋章"),
      p("可编辑勋章名称/描述，或删除勋章（会同时撤销所有已颁发记录）。"),
      pb(),

      // 第6章
      h1("第6章 课堂工具"),
      p("侧边栏 → 课堂工具，包含六个实用工具："),
      makeTable(["工具", "功能", "说明"], [
        ["🎲 随机点名", "公平随机抽取学生", "支持多轮不重复，动画滚动效果"],
        ["⏱️ 计时器", "课堂倒计时", "预设 1/3/5 分钟，支持暂停/重置"],
        ["👥 随机分组", "均衡分组", "设置组数，随机分配学生"],
        ["🎰 积分抽奖", "消耗积分抽奖激励", "可编辑奖项，支持添加/删除/权重调整"],
        ["🎁 积分兑换", "积分兑换实物奖品", "预设奖品可编辑，选择学生+奖品自动扣减积分"],
        ["🔔 积分提醒", "阈值达标检测", "设定积分阈值，一键查看达标学生"],
      ], [2000, 2500, 4526]),
      h2("6.1 🎲 随机点名"),
      p("点击「随机点名」→ 点击「开始抽取」→ 系统随机滚动学生名单 → 最终停在一个学生上。支持多轮不重复。"),
      h2("6.2 ⏱️ 计时器"),
      p("预设 1分钟/3分钟/5分钟，也可自定义时间。支持开始、暂停、重置。"),
      h2("6.3 👥 随机分组"),
      p("设置分几组 → 点击「开始分组」→ 系统随机将当前班级学生均衡分配到各组。"),
      h2("6.4 🎰 积分抽奖"),
      p("消耗指定积分参与抽奖，激励学生积极性。"),
      h3("抽奖规则"),
      p("• 每次消耗指定积分（默认 10 分，可调整）"),
      p("• 只有积分足够的学生才能参与"),
      p("• 中奖后自动加积分，未中奖扣除消耗积分"),
      h3("自定义奖项"),
      p("点击「✏️ 编辑奖项」可自定义奖项配置："),
      makeTable(["字段", "说明", "示例"], [
        ["名称", "奖项显示名称", "🥇 一等奖"],
        ["奖励说明", "中奖后的奖励描述", "积分 ×3"],
        ["颜色", "显示颜色（十六进制）", "#f59e0b"],
        ["权重", "中奖概率（百分比）", "5 表示 5% 概率"],
      ], [2000, 3526, 3500]),
      p("支持添加新奖项、删除奖项（至少保留 2 个），权重总和建议为 100%。奖项配置保存在浏览器本地，刷新不丢失。"),
      h2("6.5 🎁 积分兑换"),
      p("学生用积分兑换实物奖品，培养积分管理意识。"),
      h3("操作步骤"),
      p("1. 点击「积分兑换」打开工具"),
      p("2. 从下拉菜单选择学生（显示当前积分）"),
      p("3. 选择奖品（显示所需积分）"),
      p("4. 点击「兑换」，系统自动检查积分是否充足并扣减"),
      h3("管理奖品"),
      p("点击「✏️ 添加奖品」可新增奖品（名称+所需积分），支持删除和修改。预设奖品：文具套装(50分)、笔记本(30分)、铅笔礼包(20分)。奖品配置保存在浏览器本地。"),
      h2("6.6 🔔 积分提醒"),
      p("一键检查积分达到指定阈值的学生，方便发放奖励或表扬。"),
      h3("操作步骤"),
      p("1. 点击「积分提醒」打开工具"),
      p("2. 设置积分阈值（默认 100 分）"),
      p("3. 点击「检查达标学生」"),
      p("4. 系统显示所有积分 ≥ 阈值的学生列表"),
      pb(),

      // 第7章
      h1("第7章 排行榜"),
      p("侧边栏 → 排行榜，按积分从高到低排列所有学生。显示排名、姓名、宠物、积分和等级。"),
      p("手机端排行榜自动切换为卡片布局。"),
      pb(),

      // 第8章
      h1("第8章 积分日志"),
      p("侧边栏 → 积分日志，查看当前班级所有学生的积分变动记录。"),
      h2("8.1 功能说明"),
      p("• 分页显示积分变动记录，每页 20 条"),
      p("• 每条记录显示：学生姓名、积分变动（+/-）、原因、时间"),
      p("• 支持按时间倒序查看"),
      h2("8.2 使用场景"),
      p("• 课堂结束后回顾积分变动"),
      p("• 家长会时展示学生积分情况"),
      p("• 核对积分异常变动"),
      pb(),

      // 第9章
      h1("第9章 系统设置"),
      h2("9.1 个人信息"),
      p("可修改显示名称和头像。"),
      h2("9.2 修改密码"),
      p("输入旧密码和新密码（需满足强度要求：≥8位，含大小写和数字）→ 保存。"),
      pb(),

      // 第10章
      h1("第10章 手机端使用"),
      h2("10.1 导航"),
      p("手机端顶部显示导航栏：左侧 ☰ 汉堡菜单打开侧边栏，右侧头像可快速退出。顶部同时显示班级选择器，可快速切换班级。"),
      h2("10.2 适配说明"),
      makeTable(["页面", "手机端适配"], [
        ["班级总览", "统计卡片 2 列显示，快捷操作纵向排列"],
        ["学生管理", "自动切换为卡片列表，支持横向滚动"],
        ["排行榜", "卡片布局，排名清晰"],
        ["勋章管理", "勋章网格 3 列（超小屏 2 列）"],
        ["课堂工具", "工具卡片 2 列，弹窗全宽适配"],
        ["班级管理", "卡片布局"],
      ], [2000, 7026]),
      h2("10.3 注意事项"),
      p("• 首次加载可能较慢（约 3-5 秒），后续访问会利用浏览器缓存加速"),
      p("• 建议使用 Chrome 或 Safari 浏览器"),
      p("• 刘海屏设备已适配安全区域"),
      pb(),

      // FAQ
      h1("第11章 常见问题"),
      makeTable(["问题", "解答"], [
        ["登录时提示验证码错误", "验证码是数学计算题，如「41 - 9 = ?」填写 32。注意不要有多余空格。"],
        ["连续输错密码被锁", "等待 15 分钟自动解锁，或联系管理员重启服务。"],
        ["手机端页面加载慢", "首次加载需下载约 400KB 资源（gzip 压缩后），后续访问利用缓存会很快。"],
        ["积分抽奖消耗了积分但没中奖", "参与奖会扣除消耗积分但不额外加积分，这是正常机制。"],
        ["抽奖奖项配置丢失", "奖项配置保存在浏览器 localStorage 中，清除浏览器数据会丢失。可重新编辑。"],
        ["如何创建新用户", "联系管理员在管理后台创建，或通过 API 注册。"],
        ["忘记密码怎么办", "联系管理员在管理后台重置密码。"],
        ["Excel 导入提示列名无法识别", "确保 Excel 第一行为标题行，包含「学号」「姓名」等关键字。系统支持多种中英文列名。"],
        ["积分兑换后积分没变", "兑换会自动扣减积分，刷新页面查看最新积分。如仍有问题，检查积分日志确认。"],
        ["账号提示已过期", "联系管理员在管理后台续期或设为永久有效。"],
      ], [4000, 5026]),

      // 访问地址
      pb(),
      h1("附录：系统地址"),
      makeTable(["用途", "地址"], [
        ["教师端", "https://class-pet-v2-production.up.railway.app"],
        ["管理后台", "https://class-pet-v2-production.up.railway.app/admin-panel"],
        ["API 文档", "https://class-pet-v2-production.up.railway.app/docs"],
      ], [3000, 6026]),
    ]
  }]
});

Packer.toBuffer(doc).then(buf => {
  fs.writeFileSync("../学生积分管理系统-用户使用手册-v3.docx", buf);
  console.log("[OK] 用户使用手册已生成");
});
