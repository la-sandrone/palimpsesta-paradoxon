# PROVENANCE —— Stellaris 4.6.0 符号表

> 游戏加载期**自动生成**（无 `script_docs` 命令，也不需要）。原样保存，未做任何清洗。

## 来源

| 项 | 值 |
|---|---|
| 游戏版本 | **Corona Borealis v4.6.0**（`game.log`：`Game Version: Corona Borealis v4.6.0`） |
| 构建号 | `5d0adbc59353f1e9b085e0a2c4cb3d1a`（`Nov 13 2026 07:07:46`，exe 内嵌串） |
| 分支串 | `release/4.6.0/develop` |
| exe mtime | 2026-11-23 23:08:36 +0800 |
| exe size | 47317112 |
| exe sha256（前 32 位） | `6b23d65a93d2a96b1544fed649d1f383` |
| **UI 语言** | `l_simp_chinese`（`setup.log`：`Initialized localization: l_simp_chinese`） |
| 导出时间 | 2026-11-27 08:37:21（启动 08:36:13，加载期写入） |
| 导出方式 | **全自动**，未敲任何命令 |
| **是否含 mod** | **否**（见下） |

## 「无 mod + 全 DLC」的证明

`dlc_load.json` 原文（随档保存在本目录）：

```json
{
  "enabled_mods": [],
  "disabled_dlcs": []
}
```

| 项 | 值 |
|---|---|
| `enabled_mods` | **0 个** |
| `disabled_dlcs` | **0 个**（DLC 全开，符号没被 DLC 开关截断） |

## 文件清单

| 文件 | 行数 | 条目数 | 计数依据 | sha256（前 16 位） |
|---|---|---|---|---|
| `triggers.log` | 5223 | **1171** | `Supported Scopes:` 次数 | `20b83952e0421759` |
| `effects.log` | 6921 | **1143** | `Supported Scopes:` 次数 | `48f1c386b3d8eef4` |
| `scopes.log` | 414 | **102** | `Output Scope:` 次数 | `0d6a7eaad96d7909` |
| `modifiers.log` | 47407 | **4 万7400** | `^- ` 行数 | `06d98a020849ce90` ⚠️ 顺序不稳，见下 |
| `localizations.log` | 537 | **347** | 可解析 token（行数 537；口径见 `05` 章 §3.5） | `fb3c87f57845204b` |
| **合计** | 60502 | **50163** | | |

## 格式要点（解析前必读）

| 项 | 本份的情况 |
|---|---|
| 换行 | **CRLF**（保留原样） |
| BOM | 无 |
| 首行 | **日志前缀**，如 `[08:37:21][game_application.cpp:1694]:` —— **解析前必须剥掉** |
| 块分隔 | **空行**（无 `----------` 分隔线） |
| 小节标题 | `== TRIGGER DOCUMENTATION ==` 之类 |
| 特例 | `modifiers.log` 是 `- <名字>, Category: <类别>` 扁平单行；`localizations.log` 是分节清单 |

### ⚠️ 首行的 `cpp:行号` 变了（说明生成代码被改过）

| 文件 | 4.5.3 | **4.6.0** |
|---|---|---|
| `triggers.log` | `game_application.cpp:1419` | **`game_application.cpp:1694`** |

这正是当初把「首行 cpp:行号」当**代码路径指纹**的用处：行号一变，说明 P 社动了生成代码。
**跨版本 diff 时必须忽略首行**，否则每次都会误报「全部文件都变了」。

### ✅ ~~BT~~modifiers.log~~BT~~ 的顺序**是稳定的**（实测两遍）

与 CK3 相反 —— 这一点专门测过：

| 文件 | 首行（时间戳） | 剥掉首行后 |
|---|---|---|
| `triggers.log` | 不同 | **逐字节相同** |
| `effects.log` | 不同 | **逐字节相同** |
| `scopes.log` | 不同 | **逐字节相同** |
| `modifiers.log` | 不同 | **逐字节相同（连顺序都一样）** |
| `localizations.log` | 不同 | **逐字节相同** |

两遍都是 4.6.0、无 mod、全 DLC；第二遍 08:37 → 08:47。

⇒ 结论：**Stellaris 的导出除首行时间戳外完全确定**。
⇒ 所以比对 Stellaris 可以直接剥首行后按**字节**比；CK3 不行（它的 `modifiers.log` 顺序每次可能变）。

**为什么两个游戏不同：未测定**，只记事实。

---

### ⚠️ 即便如此，仍建议按集合比

理由不是「怕顺序变」，而是：**集合比能直接告诉你「新增/消失/同名内容变」三件事**，
字节比只能告诉你「不一样」。工具：`tools/diff_symbol_docs.py`。

CK3 侧已实测：同一 build 三次导出得到三份不同字节、集合完全一致（见 `../ck3-1.21.0/PROVENANCE.md`）。
Stellaris 这一份**没有做第二次对照**，所以默认按同样口径处理：

| 做法 | 说明 |
|---|---|
| 按**集合**比，不按行 | `tools/diff_symbol_docs.py` 已这么做 |
| 不把该文件的 sha256 当内容指纹 | 同版本重导可能就变 |

## 与 4.5.3 的差异（同一工具、按集合比）

| 文件 | 4.5.3 | 4.6.0 | 名字新增 | **名字消失** | 同名内容变 |
|---|---|---|---|---|---|
| `triggers.log` | 1098 | 1171 | 73 | **0** | 10 |
| `effects.log` | 1080 | 1143 | 63 | **0** | 6 |
| `scopes.log` | 99 | 102 | 3 | **0** | 6 |
| `modifiers.log` | 4 万5599 | 4 万7400 | 1809 | **8** | 668 |
| `localizations.log` | 333 | 347 | 8 | **0** | 5 |
| **合计** | 4 万8209 | 5 万0163 | 1956 | **8** | 695 |

⇒ **triggers / effects / scopes 一个名字都没被删** —— 对 mod 来说这是好消息：
   这批 API 是**只增不改名**的。
> 「同名内容变」（695 条）不是删除：名字还在，但 scope / 文档 / 属性变了，
> 这类变化对 mod 的影响需要单独看，不能算作「消失」。

### 唯一被真删的 8 个

```
pop_ethic_fanatic_authoritarian_attraction_mult   pop_ethic_fanatic_egalitarian_attraction_mult
pop_ethic_fanatic_materialist_attraction_mult     pop_ethic_fanatic_militarist_attraction_mult
pop_ethic_fanatic_pacifist_attraction_mult        pop_ethic_fanatic_spiritualist_attraction_mult
pop_ethic_fanatic_xenophile_attraction_mult       pop_ethic_fanatic_xenophobe_attraction_mult
```

⇒ 全是「狂热派」那一档的吸引力修正符。mod 里引用这 8 个名字会**静默失效**（见 `02-静默失效案例.md` 案例 9）。

## 新增的一大批是什么（抽样，不是结论）

4.6.0 的增量集中在 **ideology（意识形态）** 这套：

```
trigger  adopted_ideology_level  any_ideology  count_adopting_country
         any_system_within_emitter_reach  combined_emitter_reach  ...
effect   adopt_ideology  create_ideology  destroy_ideology  declare_ideological_rival  ...
modifier adopted_ideology_<resource>_upkeep_mult  （一整族）
```

> 这只是名字层面的观察。**「新系统怎么运作」不在本文档的射程内** —— 那要读本体脚本 + 实测。

## 已知缺口

| 缺口 | 说明 |
|---|---|
| ~~顺序确定性~~ | 已测：两遍无 mod，剥首行后 5/5 逐字节相同，顺序也稳定 |
| DLC 清单未逐条记录 | 只记「0 个被禁用」；逐个 DLC 名与版本未入档 |
| 未做 mod 对照 | 「带 mod 的工作基线」是另一份，另存 |
