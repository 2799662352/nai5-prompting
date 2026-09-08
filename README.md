# nai5-prompting

教 AI 写 NovelAI Diffusion V5 提示词的方法包——**不是给人看的教程，是给
LLM / agent 挂载的 skill**（[Agent Skills](https://agentskills.io) 开放标准封装，
可直接被 Claude Code、Codex、Cursor 加载）。

> 本仓库 fork 自 [Miint-Sunny/nai5-prompting](https://github.com/Miint-Sunny/nai5-prompting)。
> 1.2.0 按 Agent Skills 规范与 Anthropic / OpenAI / Cursor 的 skill 编写最佳实践重整了包结构：
> 写法拆成六册按需加载、清理了指向包外文件的引用、补成品范例、评测用例与工具脚本。
> **写法规则本身与上游 v1.1-nightly-20260830 一致**，仅一处按查证结果加注
> （构思「空地」表：`harsh lighting` / `cast shadow` 不是 danbooru 词条）。

## 里面是什么

| 文件 | 管什么 | 何时读 |
|---|---|---|
| `SKILL.md` | skill 入口：阅读路线、四条铁律、本包范围 | 总是 |
| `references/通用构思.md` | **想画什么**：需求分档 A–D、把模糊想法展开成分镜的四道工序（编剧→监督→原画→摄影）、多方案硬约束、版权角色先查档案 | 需求模糊时 |
| `references/写法-字段与顺序.md` | §0–§2：字段分工与回复模板、角色栏放多少、内容顺序、迭代规则、功能块与两种笔法 | 每次落笔前 |
| `references/写法-词组与句子.md` | §3–§4.8：哪些内容必须词组（出图实测判据）、哪些必须句子 | 每次落笔时 |
| `references/写法-多人与漫画.md` | §4.9–§4.10：`source#` / `target#` / `mutual#` 绑定、第三人、Position 建议、漫画分格 | 多角色或分格时 |
| `references/写法-收尾与排查.md` | §5–§9：成品形态、质量词与 UC 两档、参数、排查表、发布前检查表 | 发出去之前 |
| `references/写法-语法与边界.md` | 开篇：NAI 语法与能力边界（权重、容量与额度、分段、文字、多语言、V5 开关） | 问语法或排查时 |
| `references/写法-实测依据.md` | §10：词组/句子判据的实测依据、证据强度与边界 | 需核实依据时 |
| `references/成品范例.md` | A / B / C 档与双人交互的完整输出（格式范例，tag 已查证存在，未经出图实测） | 想看成品长什么样 |
| `scripts/lookup_tag.py` | 查 danbooru 词条是否存在、post 数与分类（agent 可运行，需网络） | 铁律 4「能查证就查证」 |
| `scripts/build_bundle.py` | 维护者用：从 `references/` 生成单文件合订本 | 改完参考文件后 |
| `dist/NAI5_All_Prompting.md` | 上面各册的机器合订，内容一致——**只能传一个文件时用这份**，不要手改 | 单文件场合 |
| `evals/cases.json` | 9 条评测用例（A/B/C/D 档、多人、三人层次、排查、画师串、版权角色） | 改 skill 后回归 |
| `agents/openai.yaml` | Codex / ChatGPT 的展示元数据（可选） | — |

## 数据背书

结论不是经验之谈，来自一个 NAI 群的实测语料，各处数字的口径如下：

| 口径 | 数量 | 用在哪 |
|---|---|---|
| canonical 图库（带元数据可直读提示词） | 4940 张 | 结构统计的母体 |
| 真实提示词（元数据解码） | 1844 条 | 顺序、分段、权重、UC、参数等频次 |
| 全库 v7 反推 | 4663 张 | 画面层基线（单人 95% · 看镜头 76% · 大主体 92% · 高对比 24%） |
| 语法节口径 | 1918 张 | 开篇「语法与能力边界」的实测数字 |
| 角色栏分工口径 | 861 / 1010 条 | §0.1 与 §9 的字段分工数字 |
| 锁 seed 出图对照 | 每格 3 seed，共 14 + 9 张 | §3 / §4 词组 vs 句子判据（§10 逐条列证据强度） |

统计中的群成员网名已匿名化（作者A/B/…）。方法文件本身也在被压力测试：
把上百条真实需求丢给不同的模型跑，逐条审计产出，违规集中在哪里就改哪里——
多数问题不是模型不听话，是文件自己在两处说了两套话。

## 怎么用

**方式一 · 当 skill 挂**（Claude Code / Codex / Cursor 或任何支持 Agent Skills 的 agent）：
把本仓库整个目录放进 skills 目录，目录名保持 `nai5-prompting`：

| 宿主 | 项目级 | 用户级 |
|---|---|---|
| Claude Code | `.claude/skills/nai5-prompting/` | `~/.claude/skills/nai5-prompting/` |
| Codex | `.agents/skills/nai5-prompting/` | `~/.agents/skills/nai5-prompting/` |
| Cursor | `.cursor/skills/nai5-prompting/`（也读上面两处） | `~/.cursor/skills/nai5-prompting/` |

入口是 `SKILL.md`，agent 会按里面的阅读路线按需加载各册。

**方式二 · 直接发给聊天 AI**（DeepSeek / ChatGPT / Claude 网页版都行）：
把 `dist/NAI5_All_Prompting.md` 传进对话，然后说你想画什么——
说得细它照写；只给半句话（「来点夏天的图」）它会按分档给你几条不同方向。
**附件要连一句话一起发**（「附件是提示词方法，按它直接给我成品提示词」）——
只丢文件不给话，模型容易把方法文件当成待点评的资料。

## 维护

- 规则只改 `references/` 里的文件；改完运行 `python scripts/build_bundle.py` 重新生成合订本，
  `python scripts/build_bundle.py --check` 可在 CI 里校验合订本没过期。
- 改完用 `evals/cases.json` 里的用例回归一遍（用例格式与 Anthropic skill 最佳实践一致，
  需要自己的运行器）。
- 新增 tag 前先 `python scripts/lookup_tag.py <tag>` 查一下存不存在。

## 相关项目

- [nai-autocomplete](https://github.com/Miint-Sunny/nai-autocomplete)——上游作者配套的
  NovelAI 浏览器扩展（写词面板 / skill 注入 / tag 查证）。本仓库是它的方法层，
  也可以完全独立使用。

## License

[GPL-3.0](LICENSE)
