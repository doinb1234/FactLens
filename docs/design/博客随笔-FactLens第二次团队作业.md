# FactLens第二次团队作业——原型设计+概要设计

| 项目 | 内容 |
| --- | --- |
| 作业所属课程 | 广东工业大学计算机学院 · 计科 24 级 56 班 · [班级链接](https://edu.cnblogs.com/campus/gdgy/Class56-Grade2024-CS) |
| 作业要求 | [第二次团队作业（原型设计+概要设计）](https://edu.cnblogs.com/campus/gdgy/Class56-Grade2024-CS/homework/16784) |
| 作业的目标 | 我们理解本次作业的目标：让项目从"能跑"走向"会设计"。用专用工具把前台与后台界面做成可交互原型，把功能模块、业务流程、系统结构与数据库设计用 UML 图和规范文档固定下来，使后续编码有据可依，同时用规范的协作记录展示团队的工程化过程 |
| 团队名称 | FactLens |
| 团队成员学号－姓名 | 3224004156－刘心怡、3224004158－杨添媛、3224004157－吴纯瑶、3224004155－李晨昀、3124004111－依木拉木·阿不都苏力、3124004121－艾力夏提·艾海买提、3124004146－杨宗林 |

## 1. 项目回顾

FactLens 事实透镜是一个 **AI 多领域虚假信息鉴别智能体**：把一段拿不准真假的文字粘贴进网页，系统经过"断言拆解 → 证据检索 → 结论判定 → 报告输出"的智能体流水线，输出一份可复核的核查报告——说明系统如何判断、参考了哪些来源、哪些地方仍需核实。结论只取四种之一：**确认属实 / 确认不实 / 部分属实 / 暂无法核实**。

首版已上线并通过验收：

| 端 | 地址 | 说明 |
| --- | --- | --- |
| 前端 | https://factlens-dn7.pages.dev | Vue 3 + Vite，Cloudflare Pages 托管 |
| 后端 | https://factlens.pythonanywhere.com | Python FastAPI，POST /api/check |
| 健康检查 | https://factlens.pythonanywhere.com/api/health | 查看服务状态与模型配置 |

本次作业在首版基础上完成**设计定型**（把跑通的系统显式化为 UML 与分层架构）与**演进设计**（迭代二：服务端持久化、证据源注册表、管理后台）。

## 2. 原型设计

### 2.1 设计工具与原型入口

按要求使用专用原型工具 **墨刀** 完成原型制作，同时将同一设计实现为可在线交互的 HTML 高保真原型，双链接供评审：

- **墨刀原型（在线预览）**：https://modao.cc/proto/design/pb2mcpVbbL7mt5uEarUH （13 个画板：前台 5 页 + 后台 5 页 + 抽屉/删除确认/新增证据源 3 个弹层交互态，页面间通过墨刀页面导航切换）
- **HTML 交互原型（在线预览）**：https://doinb1234.github.io/FactLens/prototype/index.html （前台）· https://doinb1234.github.io/FactLens/prototype/admin.html （后台）

原型尺寸 1440×900，采用"青绿透镜"设计语言：主色 #0F766E→#14B8A6 渐变、白色卡片、结论四色徽章（属实绿 / 不实红 / 部分属实琥珀 / 无法核实灰），前台后台视觉一致。

### 2.2 前台应用原型

前台共 4 个页面（核查中为过渡态）。

**页面 1 · 核查页（首页）**：主标题"让真相，清晰一点。"；输入卡片支持 ≤2000 字实时计数、三个示例一键填入；"开始核查"按钮在空输入时禁用。

![前台原型-核查页](https://doinb1234.github.io/FactLens/design/assets/shots/front-home.png)

**核查中过渡态**：提交后展示四步流水线进度——1 拆解断言 → 2 检索证据 → 3 综合判定 → 4 生成报告，当前步骤呼吸高亮，配以阶段文字提示。这一步把"看不见的智能体流水线"做成了可见的过程。

**页面 2 · 核查报告页**：结论大胶囊（颜色随四值结论变化）、"模型判定/降级判定"徽章、核查时间；摘要与判断理由；支持/反驳/不确定三栏证据要点；**断言级证据链**——每条断言一张卡片，下面挂该断言检索到的来源（标题可点击、域名、摘要）；全部来源汇总（按 URL 去重）；复制报告、重新核查按钮；降级判定时显示琥珀色提示条。

![前台原型-核查报告页](https://doinb1234.github.io/FactLens/design/assets/shots/front-report.png)

**页面 3 · 历史记录页**：按关键词搜索、删除、清空；每条记录带时间、原文与结论徽章；"重新核查"回填原文并自动提交。首版存浏览器本地，迭代二迁移服务端数据库（见 3.3）。

![前台原型-历史记录页](https://doinb1234.github.io/FactLens/design/assets/shots/front-history.png)

**页面 4 · 关于页**：项目简介、六项核心功能、五条核查原则（证据说话/不足即言明/可复核/区分权威/透明告知）与首版局限的如实声明。

![前台原型-关于页](https://doinb1234.github.io/FactLens/design/assets/shots/front-about.png)

### 2.3 后台管理原型（迭代二新增）

后台共 5 个页面：管理员登录、数据概览、核查记录、证据源管理、系统配置。

**登录页**：账号密码登录，演示版提示。

![后台原型-登录页](https://doinb1234.github.io/FactLens/design/assets/shots/admin-login.png)

**数据概览**：四张统计卡（今日核查/累计核查/模型判定占比/平均耗时）；近 7 日核查量折线图；结论分布环形图；最近核查记录表。

![后台原型-数据概览](https://doinb1234.github.io/FactLens/design/assets/shots/admin-overview.png)

**核查记录**：结论筛选 + 关键词查询；详情抽屉展示完整报告；删除需二次确认。

![后台原型-核查记录](https://doinb1234.github.io/FactLens/design/assets/shots/admin-records.png)

**证据源管理**：权威域名注册表（高/中/低/黑名单四档 + 启用开关），新增/编辑弹窗。

![后台原型-证据源管理](https://doinb1234.github.io/FactLens/design/assets/shots/admin-sources.png)

**系统配置**：模型配置（密钥掩码显示）、检索参数、服务状态卡（健康检查、模型可用性、重新检查）。

![后台原型-系统配置](https://doinb1234.github.io/FactLens/design/assets/shots/admin-config.png)

### 2.4 原型中的突出特点

1. **断言级证据链（杀手级功能）**：报告不是给一个笼统结论，而是"原文 → 断言 → 证据"逐级展开，每项断言都能点开来源复核，把"系统为什么这么判"完全摊开给读者；
2. **流水线可视化**：核查中四步进度把智能体的内部过程做成可见状态，长请求不再是无反馈的等待；
3. **降级透明的设计**：无模型密钥时报告明确标注"降级判定（搜索+规则）"并展示提示条，不冒充 AI 结论；
4. **结论四色规范**：四值结论有统一颜色语义，前台报告、历史列表、后台表格同色同义；
5. **设计即开发**：HTML 原型与线上产品同源同风格（同一套 Vue 组件结构），原型页面可直接指导迭代二编码。

## 3. 概要设计

### 3.1 总体架构

系统自顶向下分为 **五层**：表现层（Vue 3 前台 + 后台 SPA）→ 接口层（FastAPI）→ 编排层（智能体流水线）→ 能力层（LLM 客户端 / 必应检索 / 规则降级引擎）→ 数据层（迭代二新增 SQLAlchemy + MySQL/SQLite）。层间单向依赖、接口解耦；模型与搜索能力可替换，无密钥时自动降级，保证**服务永远可用**。

![FactLens 分层架构图](https://doinb1234.github.io/FactLens/design/assets/architecture.png)

功能模块划分 M1～M7：输入与校验（M1）、断言拆解（M2）、证据检索（M3）、综合判定（M4）、报告生成与展示（M5）、历史记录（M6）、管理后台（M7）。思维导图如下：

![FactLens 功能模块思维导图](https://doinb1234.github.io/FactLens/design/assets/mindmap.png)

### 3.2 UML 设计

**用例图（需求分析）**：两类参与者——核查用户（访客）与管理员。"提交文本核查"包含"断言拆解、证据检索、综合判定"三个用例；"查看核查报告"扩展"复制报告"；管理员对应后台登录与四项运维用例。

![FactLens 用例图](https://doinb1234.github.io/FactLens/design/assets/usecase.png)

**活动图（业务流程）**：描述一次核查的端到端流程——前后端双重校验输入 → 拆解（模型路径/规则降级路径）→ 逐断言检索 → 判定（模型/规则双轨）→ 汇总去重 → 生成报告 → 落库与展示。图中用泳道区分用户、前端、接口层、编排层、数据层的职责。

![FactLens 核查业务流程活动图](https://doinb1234.github.io/FactLens/design/assets/activity.png)

**类图（系统结构）**：按五层给出核心类。编排层四构件（ClaimSplitter / EvidenceRetriever / Judge / ReportBuilder）对应首版 agent 模块的对象化重构；Judge 为抽象策略，ModelJudge 调用 LLM 客户端、RuleJudge 读权威域名表；数据层六类为迭代二 ORM 实体，与数据库表一一对应。

![FactLens 类图](https://doinb1234.github.io/FactLens/design/assets/class.png)

**时序图（核心算法模块）**：智能体核查流水线是系统的核心算法。时序图描述一次 POST /api/check 的控制流：双重校验 → 编排层依次调用拆解、检索、判定，两处 LLM 决策点带降级分支 → 报告组装落库 → 前端渲染与历史持久化。

![FactLens 核查流程时序图](https://doinb1234.github.io/FactLens/design/assets/sequence.png)

**协作图（对象协作）**：展示八个对象之间 15 条消息的传递方向与编号，与时序图编号一致，直观呈现"前端 → 接口层 → 编排层 → 能力层 → 报告对象"的协作关系。

![FactLens 核查流程协作图](https://doinb1234.github.io/FactLens/design/assets/collaboration.png)

### 3.3 数据库设计

首版历史记录仅存浏览器本地。迭代二引入服务端数据库 factlens（线上 MySQL 8.0 / 本地 SQLite），共六张表：核查记录 t_check_record、断言 t_claim、证据 t_evidence、证据源注册表 t_source_registry、管理员 t_admin_user、系统配置 t_app_config。

**ER 图（概念结构）**：一次核查记录拆解出 1～3 条断言，每条断言检索到多条证据；证据按域名与注册表非强制匹配（落库时保存权威等级快照）；管理员维护注册表与系统配置。

![FactLens 数据库 ER 图](https://doinb1234.github.io/FactLens/design/assets/er.png)

**关系数据模型（逻辑结构，节选）**：

| 表 | 关键字段 | 约束 |
| --- | --- | --- |
| t_check_record | id、raw_text、conclusion、conclusion_type、summary、reason、support_json、used_llm、checked_at | PK(id)，索引(checked_at)、(conclusion_type) |
| t_claim | id、record_id、seq_no、content | FK→t_check_record，UK(record_id, seq_no) |
| t_evidence | id、claim_id、record_id、title、url、url_hash、snippet、domain、authority_level | FK→t_claim/t_check_record，UK(url_hash) |
| t_source_registry | id、domain、category、authority_level、status、note | UK(domain) |
| t_admin_user | id、username、password_hash、role、status | UK(username)，口令 bcrypt 哈希 |
| t_app_config | id、config_key、config_value、description | UK(config_key) |

完整字段定义、索引策略与 MySQL 建表脚本见《FactLens_数据库设计说明书.pdf》第 3、4 章与附录 B。

**对象关系映射（ORM）**：实体类与库表的映射关系如下，数据层采用 SQLAlchemy 2.0 声明式映射：

| 实体类（Python） | 库表 | 说明 |
| --- | --- | --- |
| CheckRecord | t_check_record | 报告对象的持久化形态 |
| Claim | t_claim | 一条断言 |
| Evidence | t_evidence | 首版 searcher.Source 的落库形态 |
| SourceRegistry | t_source_registry | 证据源注册表 |
| AdminUser | t_admin_user | 管理员账号 |
| AppConfig | t_app_config | 系统配置键值 |

## 4. 团队协作记录

### 4.1 预期开发计划（迭代二，每周）

| 周次 | 时间（2026-2027） | 工作内容 | 里程碑 | 产出 |
| --- | --- | --- | --- | --- |
| 第 1 周 | 11-23 ~ 11-29 | 数据库建表与 ORM 落地；核查流程落库改造；WSGI 入口文件补录仓库 | M1 数据库上线 | 建库脚本、迁移记录、落库接口 |
| 第 2 周 | 11-30 ~ 12-06 | 后台管理 v1：登录鉴权、概览统计、核查记录管理 | M2 后台 v1 可用 | 后台 SPA、/api/admin/* 接口 |
| 第 3 周 | 12-07 ~ 12-13 | 证据源注册表接入判定加权；检索相关性过滤调优 | — | 注册表管理、加权规则与对比测试 |
| 第 4 周 | 12-14 ~ 12-20 | 断言级证据展示完善（R04）；报告导出；前端体验优化 | M3 迭代二 beta 发布 | 迭代二 beta 版本 |
| 第 5 周 | 12-21 ~ 12-27 | 缺陷修复与回归测试；超时与性能调优 | — | 测试记录、迭代二 RC |
| 第 6 周 | 12-28 ~ 01-03 | 期末验收准备：按验收标准逐项复测；部署与使用文档 | M4 验收就绪 | 验收记录、文档 |
| 第 7 周 | 01-04 ~ 01-10 | 期末交付：演示准备、项目总结博客 | M5 期末交付 | 最终版本、项目总结 |

### 4.2 分工安排

| 姓名（学号） | 角色 | 本次作业分工 | 迭代二开发分工 |
| --- | --- | --- | --- |
| 刘心怡（3224004156） | 智能体与后端 | 总体架构、时序图/协作图、系统设计说明书主笔 | 编排层重构、判定提示词调优 |
| 杨添媛（3224004158） | 前端开发与测试 | 前台原型实现与交互说明 | 核查页与报告组件 |
| 吴纯瑶（3224004157） | 产品设计与需求分析 | 原型交互稿与页面文案、需求跟踪 | 验收标准维护、文档校对 |
| 李晨昀（3224004155） | 智能体与后端 | 数据库设计、ER 图与 ORM 映射、数据库设计说明书主笔 | LLM 调用层与降级规则 |
| 依木拉木·阿不都苏力（3124004111） | 智能体与后端 | 用例图、活动图、接口设计 | 检索模块与证据源注册表后端 |
| 艾力夏提·艾海买提（3124004121） | 前端开发与测试 | 后台管理原型、历史记录页原型 | 后台前端、历史记录迁移联调 |
| 杨宗林（3124004146） | 前端开发与测试 | 原型走查与缺陷记录、博客排版 | 测试用例与回归验证 |

### 4.3 本次作业协作过程记录

| 时间 | 事项 | 参与 |
| --- | --- | --- |
| 11-09 | 领取第二次作业任务，组会拆分"原型/概要设计/数据库/协作记录"四块并认领 | 全员 |
| 11-10 ~ 11-13 | 吴纯瑶出前台与后台的页面清单与低保真线框，全组评审页面范围 | 全员 |
| 11-13 ~ 11-16 | 前端组按线框实现高保真原型（前台 4 页 + 后台 5 页）与交互规则 | 前端组 |
| 11-16 ~ 11-18 | 后端组绘制用例图/活动图/类图/时序图/协作图与 ER 图，核对代码与图纸一致性 | 后端组 |
| 11-18 ~ 11-20 | 两份设计说明书初稿互审：产品校对需求编号，前后端核对接口字段 | 全员 |
| 11-21 ~ 11-22 | 博客整合、墨刀复刻、GitHub 提交与链接复查 | 全员 |

（此处可插入组会照片 / 在线协作截图 / GitHub Issues 看板截图，建议 1～2 张。）

协作管理：任务、缺陷与评审记录使用 **GitHub Issues / Projects** 跟踪（加分项），设计文档与原型全部进入团队仓库版本管理，每位成员在仓库中均有提交记录，可通过仓库 Contributors 查看。

## 5. 附录：交付物与链接

| 交付物 | 链接 |
| --- | --- |
| GitHub 团队仓库 | https://github.com/yyue62353-lab/FactLens |
| FactLens_系统设计说明书.pdf | 在线预览/下载：https://doinb1234.github.io/FactLens/design/FactLens_系统设计说明书.pdf |
| FactLens_数据库设计说明书.pdf | 在线预览/下载：https://doinb1234.github.io/FactLens/design/FactLens_数据库设计说明书.pdf |
| 原型在线预览（墨刀） | https://modao.cc/proto/design/pb2mcpVbbL7mt5uEarUH |
| 原型在线预览（HTML） | https://doinb1234.github.io/FactLens/prototype/index.html |
| 云盘下载（备用） | 【蓝奏云链接占位-待替换，可上传两份 PDF 后补】 |

> 发布说明：文中图片与 PDF 通过团队仓库的镜像 fork（doinb1234/FactLens）开启的 GitHub Pages 提供在线预览，文件源在团队仓库 `docs/design/` 与 `docs/design/assets/`；若外链图显示异常，从团队仓库下载同名图片后用博客园编辑器重新上传即可。
