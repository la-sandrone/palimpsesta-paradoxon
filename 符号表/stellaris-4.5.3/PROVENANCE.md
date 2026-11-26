# Stellaris 符号表基线 —— v4.5.3

> 由 `script_docs` 体系自动生成，**无 mod** 干净导出。

## 来源

| 项 | 值 |
|---|---|
| 游戏版本 | **`Cygnus v4.5.3`** |
| 构建号 | `507018f716b2543f49554de24e554e91 (Oct 30 2026 13:01:50)` |
| 分支 | `release/4.5.3/develop` |
| 导出时间 | 2026-11-09 17:27:06（游戏 17:26:06 启动，加载期自动写入） |
| mod | **无**（`dlc_load.json`：`{"enabled_mods":[]}`） |
| 来源目录 | `Stellaris/logs/script_documentation/` |
| 导出方式 | **全自动，未敲任何命令** |

版本交叉验证：`logs/game.log` 第 1 行 = `Game Version: Cygnus v4.5.3`，
与 exe 内嵌串推导结果一致。

## 内容

| 文件 | 行数 | 条目数 | 计数依据 |
|---|---|---|---|
| `triggers.log` | 4875 | **1098** | `Supported Scopes:` 出现次数 |
| `effects.log` | 6475 | **1080** | `Supported Scopes:` 出现次数 |
| `scopes.log` | 402 | **99** | `Output Scope:` 出现次数 |
| `modifiers.log` | 45606 | **45599** | `^- ` 行数 |
| `localizations.log` | 519 | — | 行是命令清单，无统一结构 |

> ⚠️ **计数别用 `grep -cE ' - '`**：文档正文里也含「空格-空格」，
> 会把 triggers 数成 1103（实际 1098）、effects 数成 1314（实际 1080）。
> 用**结构字段**计数才准。

## ⚠️ 首行是时间戳，解析前必须剥掉

每个文件第 1 行形如：

```
[17:27:06][game_application.cpp:1419]:
```

**这是唯一每次生成都会变的地方。** 实测：同版本重启一次，五个文件 `sha256` 全变，
但**剥掉首行后五个全部一致**（内容确定性）。

⇒ 解析器剥首行；跨运行 diff 忽略首行；否则每次都误报「全都变了」。

首行的 `cpp:行号` 是稳定指纹，行号变化 = 生成代码被改过，比内容 diff 更早预警：

| 文件 | 来源 |
|---|---|
| triggers.log | `game_application.cpp:1419` |
| effects.log | `game_application.cpp:1422` |
| scopes.log | `game_application.cpp:1434` |
| localizations.log | `game_application.cpp:1454` |
| modifiers.log | `modifier.cpp:2274` |

另有已验证结论：**导出是逐文件的**——删掉 `scopes.log` 后重启，它自己长回来了。

## 格式（与 CK3 **不同**，解析器不能复用）

| 项 | CK3 | 本基线 |
|---|---|---|
| 文件数 | 7 | **5**（无 `event_targets` / `on_actions`；多 `scopes` / `localizations`） |
| 块分隔 | `--------------------` | **空行**，无分隔线 |
| 首行 | 直接内容 | 带日志前缀 `[17:27:06][game_application.cpp:1419]: ` |
| 换行 | LF | **CRLF** |
| 标题行 | 无 | `== TRIGGER DOCUMENTATION ==` 等 |
| triggers/effects 字段 | Supported Scopes + **Targets** | **只有** Supported Scopes |
| scopes 独有 | — | **`Output Scope:`** |
| modifiers 格式 | `Tag:` + `Use areas:` | `- <名字>, Category: <类别>` 扁平单行 |

## 与上一份导出（v4.4.6 + 214 mod）的对比

| 文件 | v4.4.6 + mods | v4.5.3 无 mod | 差 |
|---|---|---|---|
| triggers | 1087 | 1098 | +11 |
| effects | 1056 | 1080 | +24 |
| scopes | 99 | 99 | 0 |
| **modifiers** | **102354** | **45599** | **−56755（−55%）** |
| localizations | 519 行 | 519 行 | 0 |

> **这份对比不能用来说「4.5.3 砍了 5.6 万个 modifier」**——两个变量同时变了
> （版本 + mod）。mod 加的船体组件/空间站会生成海量 modifier，
> 且**不带 mod 前缀**，所以无法从名字区分来源。

## 教训：mod 污染的检测方法

**前缀 grep 是无效检测。** 曾用 `grep -c '^- aot_' modifiers.log` 判断污染，
得 74 条，据此认为「污染很轻微」——**错**。mod 新增的组件生成的 modifier
以**组件名**命名，与 mod 名前缀无关。真实差距 5.6 万条（55%）。

⇒ 判断符号表是否被 mod 污染，**唯一可靠办法是无 mod 重跑一次再对比**，
不能靠 grep 前缀。

---

## 文件清单与校验（公开归档附注）

| 文件 | 行数 | 条目（本仓库解析器口径） | sha256（前 16 位） |
|---|---|---|---|
| `triggers.log` | 4875 | 1098 | `f986bb38a43ffe28` |
| `effects.log` | 6475 | 1080 | `27bf29601b6490d2` |
| `scopes.log` | 402 | 99 | `8d05db50e56fecb1` |
| `modifiers.log` | 45606 | 4 万5599 | `d4393dc4534a9c03` |
| `localizations.log` | 519 | 333（可解析 token；按行数是 519，口径见 05 章 §3.5） | `0fcce6278b2a3c99` |

完整 hash 用 `sha256sum *.log` 自行核对。

**这些文件是原始字节**：CRLF 保留、首行时间戳保留、未做任何清洗。
要解析就先剥首行（否则每次 diff 都会误报「全都变了」）。

## 许可

内容由 Paradox Interactive 的引擎生成，版权归其权利人；本仓库只做格式归档与索引导航，
不主张对内容的任何权利。详见 `../README.md` 的「许可与归属」。

**如权利人认为收录不妥，提 issue 即删。**
