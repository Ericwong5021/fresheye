# FreshEye

**面向 Codex 的用户画像驱动盲测 Skill。**

FreshEye 关注传统软件测试经常忽略的问题：

> 一个不知道源码、产品逻辑和正确操作路径的目标用户，能不能只靠界面理解软件并完成任务？

FreshEye 不是让当前开发 Agent “假装成用户”。它通过独立 subagent 启动合成用户，只允许其使用 Browser 或 Computer Use 操作可见界面；完成后，再由另一个独立 Judge subagent 根据行为轨迹和截图进行评分。

## 核心概念：认知隔离

开发 Agent 可能已经知道：

- 源代码和组件结构；
- 产品为什么这样设计；
- 正确操作入口；
- 当前版本改了什么；
- 测试希望验证什么。

这些信息都会污染“新用户视角”。FreshEye 因此要求 Runner 只能获得：

- Persona Contract；
- 普通用户能够理解的任务；
- 产品入口；
- 设备、账号、时间和安全限制；
- 当前界面能够直接看到的信息。

Runner 禁止访问源码、Git、文件、终端、DOM、Selector、控制台、网络请求、内部 API、数据库、PRD 和历史测试结果。发生任何越界，测试必须标记为 `CONTAMINATED`，不能纳入评分。

## V1 架构

```text
当前 Codex 开发会话
        │
        ▼
FreshEye Skill（编排与输入清洗）
        │
        ├── fresheye_runner subagent A
        ├── fresheye_runner subagent B
        └── fresheye_runner subagent C
        │
        ▼
行为轨迹、截图、污染记录
        │
        ▼
fresheye_judge subagent
        │
        ▼
.fresheye/runs/<run-id>/report.md
```

Runner 负责使用产品，不负责给自己评分。Judge 只看经过清洗的 Persona、任务和测试证据，不读取源码或开发上下文。

## 当前支持

- Codex CLI 与 Codex IDE；
- Browser / Computer Use；
- 单 Persona 测试；
- 多 Persona Panel；
- 同一 Persona 多次独立复现；
- 修改前后的行为回归测试；
- Persona、Manifest、Runner Result、Judge Result Schema；
- 截图、轨迹、污染和评分报告；
- AgentCompany、待办软件和 Lumi 的预设 Persona。

## 当前不支持

- 真正的容器级硬隔离；
- 云端 SaaS 测试平台；
- 原生手机自动化；
- 可靠的儿童语音对话模拟；
- 用合成用户替代真实用户研究。

所有 FreshEye 结论默认标记为 `[hypothesis]`。只有真实用户测试能够将其提升为 `[validated]`。

## 安装

让 Codex 安装：

```text
安装这个 Skill：https://github.com/Ericwong5021/fresheye
然后运行安装脚本，把 FreshEye 的两个自定义 subagent 安装到 ~/.codex/agents。
```

手动安装：

```bash
git clone https://github.com/Ericwong5021/fresheye.git
cd fresheye
python scripts/install.py --scope user
```

安装结果：

```text
~/.agents/skills/fresheye/
~/.codex/agents/fresheye-runner.toml
~/.codex/agents/fresheye-judge.toml
```

诊断：

```bash
python ~/.agents/skills/fresheye/scripts/doctor.py
```

## 使用

### 单 Persona

```text
$fresheye test http://localhost:3000
Persona: fresh-first-timer
任务：创建一个明天下午 3 点提醒的任务。
```

### 多 Persona Panel

```text
$fresheye panel http://localhost:3000
Personas: fresh-first-timer, low-digital-literacy, impatient-goal-seeker
任务：创建一个明天下午 3 点提醒的任务。
每个 Persona 独立运行 3 次，每次使用全新浏览器状态。
```

### 回归测试

```text
$fresheye regress
Baseline: .fresheye/runs/20260730-before
Current target: http://localhost:3000
保持 Persona、任务、视口、账号 Fixture 和重复次数一致。
```

## 隔离等级

| 等级 | 含义 |
|---|---|
| `L0` | 当前开发 Agent 直接模拟用户。FreshEye 不接受。 |
| `L1` | 独立 subagent 上下文，但浏览器或工具隔离不完整。 |
| `L2` | 独立 subagent + 全新浏览器状态。 |
| `L3` | Runner/Judge 分离 + 输入清洗 + 全新浏览器 + 污染审计。V1 目标。 |

Subagent 不是安全沙箱，因此 FreshEye 不会声称 V1 已经实现绝对盲测。未来独立软件版本会把 Runner 放入空工作目录、独立 Codex 进程或容器中，提升到 `L4/L5`。

## 预设 Persona

### 通用

- `fresh-first-timer`
- `impatient-goal-seeker`
- `low-digital-literacy`
- `cautious-skeptic`
- `transfer-power-user`
- `interrupted-mobile-user`

### AgentCompany

- `solo-founder-delegator`
- `skeptical-technical-operator`
- `non-agent-manager`

### 待办软件

- `wechat-casual-user`
- `busy-parent`
- `things-migrator`
- `offline-returning-user`

### Lumi

- `curious-parent-buyer`
- `safety-conscious-parent`
- `time-poor-setup-parent`
- `grandparent-caregiver`

Persona 不只描述年龄和职业，还定义心智模型、耐心、探索倾向、风险承受、信任门槛、错误恢复和放弃条件。Persona 不能包含正确操作路径或预设问题。

## 测试产物

```text
.fresheye/runs/<run-id>/
├── manifest.yaml
├── persona.yaml
├── task.yaml
├── runners/
│   └── <runner-id>/
│       ├── trace.jsonl
│       ├── result.json
│       └── evidence/
├── contamination.json
├── judge-result.json
└── report.md
```

## 评分

FreshEye 默认保留少量可解释指标：

- 任务完成：失败 / 部分完成 / 完成；
- SEQ：1–7；
- 操作信心：1–5；
- 信任：1–5；
- 问题严重度：0–4；
- 复现次数：例如 3 次独立运行中出现 2 次。

不会将这些指标合成一个不透明的“UX 总分”。

## 推荐验证顺序

1. 先在待办软件测试短流程和重复稳定性；
2. 再用 AgentCompany 测试复杂心智模型；
3. 最后用 Lumi 官网和家长端测试商业理解与信任；
4. 将 FreshEye 结果与少量真实用户测试进行校准。

## 项目状态

FreshEye v0.1.0 是方法论验证版本。目标不是证明 AI 能替代用户研究，而是验证：

- 隔离后的合成用户能否发现开发 Agent 忽略的问题；
- 相同 Persona 多次测试是否具有可接受的一致性；
- 修改前后的结果变化是否与真人感知方向一致；
- 哪些 Persona 参数真正影响测试价值。

## License

MIT
