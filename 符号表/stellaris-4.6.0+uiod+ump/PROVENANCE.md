# PROVENANCE —— Stellaris 4.6.0 + UIOD + UMP（工作基线）

> 实际工作时的那套配置：**本体 4.6.0 + 两个基准 mod**，全 DLC。
> 只归档与干净版**不同**的那个文件；其余 4 个剥掉首行后逐字节相同，用哈希对照。

## 来源

| 项 | 值 |
|---|---|
| 游戏版本 | **Corona Borealis v4.6.0**（构建 `0066127f...` 不对——见下，构建 `5d0adbc59353f1e9b085e0a2c4cb3d1a`） |
| exe 指纹 | mtime 2026-11-23 23:08:36 / sha256 `6b23d65a93d2a96b…` |
| UI 语言 | `l_simp_chinese` |
| 导出时间 | 2026-11-27 09:07:48 |
| 导出方式 | 全自动（加载期写入） |
| 导出时名册 | `dlc_load.json` 随档（两份 `mod/ugc_*.mod`） |
| 游戏版本 | **Corona Borealis v4.6.0**（构建 `5d0adbc59353f1e9b085e0a2c4cb3d1a`） |
### 两个 mod：**按订阅号记，不按版本号记**

| mod | workshop ID | 本地 `manifest`（GID） | Steam `time_updated` | 体积 |
|---|---|---|---|---|
| UI Overhaul Dynamic | **1623423360** | `5459455486775665037` | 2026-11-25 08:37:57 | 236163907 |
| !!Universal Modifier Patch | **1688887083** | `4795802625401980010` | 2026-06-15 21:32:25 | 76759 |

> **为什么不用版本号**：同一个 mod 的版本声明至少有三出处 ——
> workshop 内容里的 `descriptor.mod`、游戏目录下的 `mod/ugc_*.mod` 注册副本、启动器 DB 的元数据。
> 三者刷新时机不同：实测同一个文件在两小时内从 `4.5.*` 变成 `4.6.*`，而 Steam 的 `manifest` 一直没变。
> **版本号会骗人，GID 不会。**

## 归档范围：只有 1 个文件

| 文件 | 与干净 4.6.0 比 | 处置 |
|---|---|---|
| `triggers.log` | 仅首行不同（`70b2b30631ba6308`） | 不重复存，见 `../stellaris-4.6.0/` |
| `effects.log` | 仅首行不同（`c8b63321cff7dc3f`） | 同上 |
| `scopes.log` | 仅首行不同（`0f8aa9b0e7bf12d5`） | 同上 |
| `localizations.log` | 仅首行不同（`f0929109ca543d45`） | 同上 |
| **`modifiers.log`** | **正文不同**：47406 → 62718 行 | **本目录归档**（`007d0c8deae5eaeb`） |

⇒ 4 个文件的 raw sha256 已列在这里，剥掉首行（时间戳）后与干净版逐字节相同。

## 差异的准确内容

| 文件 | 干净 | 基准 | 名字新增 | 名字消失 | 同名内容变 |
|---|---|---|---|---|---|
| `modifiers.log` | 47400 | **62711** | **+15311** | **0** | 991 |
| 其余 4 个 | — | — | 0 | 0 | 0 |

### 为什么四个引擎符号文件一动不动

| mod | 有没有 `common/` | 结论 |
|---|---|---|
| UI Overhaul Dynamic | ❌ 没有（只有 `gfx/` `interface/` `localisation/` `unchecked_defines`） | 不碰脚本，符号层免疫 |
| UMP | ✅ 只有一个文件：`common/economic_categories/~~~modifiers_fix_categories.txt` | 只影响类别 → 修正符 |

⇒ 与 CK3 + Unop 那次的结论一致：**引擎注册的四类符号对脚本类 mod 免疫**（见 `05-符号表导出.md` §4.3）。

### 新增的 15311 个是什么

UMP 的作用机制是给类别补 `generate_add_modifiers` / `generate_mult_modifiers`；
补上之后该类别才会为每种资源生成修正符。样例：

```
country_base_energy_produces_mult             | Countries, AI Economy
country_base_minerals_produces_mult           | Countries, AI Economy
country_base_physics_research_produces_mult   | Countries, AI Economy
country_base_sr_dark_matter_produces_mult     | Countries, AI Economy
```

⇒ 命名规律是 `<类别>_<资源>_<操作>`。**这些名字在干净本体里根本不存在** ——
   任何下游 mod 引用它们，在没装 UMP 的机器上都会静默失效。这是「影子依赖」的实证。

> **归因口径**：新增条目里 **1970 个（12.9%）**直接以 UMP 那 164 个类别名开头；
> 其余推测同样由类别生成，但前缀取的是类别的 `parent` 而非类别名，**没有逐条归因**。

### 991 个「同名内容变」是什么

不是修正符本身变了，是 **`Category:` 分组被改了**。样例：

```
leader_commanders_alloys_upkeep_mult        'Economic Units, AI Economy'  ->  'Leaders, AI Economy'
leader_commanders_advanced_logic_cost_mult  'Economic Units, AI Economy'  ->  'Leaders, AI Economy'
```

⇒ UMP 把「领袖相关」的修正符从「经济单位」组挪到了「领袖」组。这类改动**只影响 UI 分组**、不影响数值，
   但它会在符号表里表现为 991 条内容差异 —— 读 diff 时容易被误判成「修正符被改了」。

## 覆盖缺口（UMP 当前的真实极限）

| 项 | 数 |
|---|---|
| 本体 4.6.0 的类别 | **289** |
| UMP 覆盖的类别 | **164** |
| **没覆盖** | **125** |

没覆盖的里包含 4.6 新增的 **`adopted_ideology`**（意识形态）。
⇒ UMP 修不到 4.6 的新系统；它现在做的是把 4.5 时代的 164 个类别补齐。
⇒ 这不报错、不告警，只表现为「某些修正符不存在」。

## 已知缺口

| 缺口 | 说明 |
|---|---|
| 15311 个新增的逐条归因 | 只验证了 12.9% 直接命中类别名前缀，其余未归因 |
| 与 小伞 等下游 mod 的覆盖重叠 | 未测（本机没装）；测法：类别名求交 + 文件名排序 |
| 这两个 mod 的下游依赖面 | 只记了「社区普遍依赖」，未量化 |
