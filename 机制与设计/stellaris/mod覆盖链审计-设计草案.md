# mod 覆盖链审计 —— 设计草案

> **性质**：设计草案 · **游戏**：Stellaris
> **归属**：CC BY-SA 4.0（见仓库 `LICENSE`）
> **适用版本**：以文中标注为准 —— 引擎改了，结论就可能过期
> **说明**：路径已占位，工坊 ID 保留（用于定位对象）；不含他人作品内容

**状态**：设计，未实施
**起因**：2026-11-12 核对天体工具箱（工坊 3709855159）时，从其 `core/parser.py` 看到
可复用的 Paradox 脚本解析层与 `merge_entries()` 的归属记录模式。

---

## 一、为什么群星特别需要这个

**群星是 P 社几款里最依赖 mod 生态的，也是单存档跑 mod 最多的。**

| 证据 | 数值 |
|---|---|
| 本机订阅的 mod | **214**（`Stellaris/mod/` 下 214 个 `.mod`） |
| 使用 `replace/` 目录的 mod | **88** |
| P 社官方给的覆盖语义分档 | 5 种（LIOS / FIOS / DUPL / MERGE / NO） |
| Stellaris wiki 逐目录语义表 | 覆盖 100+ 个 `common/` 子目录 |

200 个 mod 的 playset 在这游戏里是常态，不是极端案例。而：

- **没有 `database_conflicts.log`**（CK3 有）
- 冲突日志在 EU4 / Stellaris 都不存在
- 覆盖语义**按目录不同**，`events/` 甚至是 FIOS（先加载的赢）

⇒ **一个 200 mod 的 playset，其覆盖关系目前只能靠人肉二分。**

---

## 二、三层问题，别再混为一谈

这是核对 UMP 与工具箱之后理清的分层。**三层都会静默失败，但需要完全不同的工具。**

| 层 | 问题 | 失败表现 | 现有工具 |
|---|---|---|---|
| **① 引擎符号层** | 这个 trigger/effect/scope 存在吗？作用于哪些 scope？ | 脚本报错（`Unknown trigger`） | ✅ `script_documentation/` + `symbols-stellaris.json` |
| **② 内容覆盖层** | 这个定义被哪些 mod 写过？谁赢？为什么？ | **无声**：内容不对但无报错 | ❌ **缺** ← 本文档 |
| **③ 生成层** | 这个 modifier 会不会被生成？ | **无声**：写了但完全不生效 | ⚠️ 部分（UMP 覆盖 61%） |

**关键**：第 ① 层我们已经做完了（48209 条符号）。**第 ② 层是最大的空白**，
而它恰恰是 200 mod 场景下故障最集中的地方。

---

## 三、已有资产盘点

| 资产 | 位置 | 能给我什么 |
|---|---|---|
| 引擎符号表 | `排查工具与代码/symbols-stellaris.json` | 符号是否存在、scope 约束 |
| 语义表（wiki） | `Stellaris/AGENTS.md` 官方权威节 | 每个目录属于 LIOS/FIOS/DUPL/MERGE/NO |
| 本体导出基线 | `排查工具与代码/script-docs/stellaris-4.5.3/` | 干净基线，可做 diff |
| **Paradox 脚本解析层** | 天体工具箱 `core/parser.py`（539 行） | `iter_top_level_blocks` / `extract_field` / `extract_block` / `extract_constants`（含 `@变量`） |
| **归属记录模式** | 同文件 `merge_entries()` | `merged[id] = (entry, lib_id)` —— 每个定义的赢家与来源 |

### 工具箱解析器已覆盖的 9 类内容

```
anomalies                    deposits                  archaeological_site_types
static_modifiers             gfx/models/planets        planet_classes
solar_system_initializers    star_classes              species_classes
```

⇒ 都是「天体相关」——因为工具箱只需要这些。

---

## 四、设计

### 4.1 复用解析层，不继承它的语义假设

工具箱的 `merge_entries()` 是 **uniform last-writer-wins**：

```python
for mod in mods:                      # 按 playset 顺序
    for entry in mod.get(entry_key, []):
        merged[eid] = (entry, lib_id)  # LWW，只留赢家，丢弃被压者
```

**这是我们几天前刚推翻的假设。** 真实语义按目录不同：

| 目录 | 真实语义 | LWW 会怎样错 |
|---|---|---|
| `events/` | **FIOS**（先加载赢） | 报反了 |
| `on_actions` | **MERGE**（永不整体覆盖） | 谎报冲突 |
| `technologies` / `traits` | **DUPL**（都进库） | 谎报覆盖 |
| 多数 `common/` | LIOS | ✅ 正确 |

⇒ **借用它的解析函数，语义按目录自己配。**

### 4.2 产出形态

对每个定义 id，输出一条归属链：

```
planet_foo
  ├─ vanilla:common/planet_classes/01_foo.txt:120   (defines)
  ├─ modA(id):common/planet_classes/zz_a.txt:33     (overrides)
  └─ modB(id):common/planet_classes/aaa_b.txt:7     (WINNER, LIOS)
```

关键字段：**谁定义过、加载顺序、按哪条语义规则判胜负、最终赢家**。

### 4.3 语义规则表（数据驱动，不写死在代码里）

把 wiki 那张表落成一份 `semantics.json`：

```json
{
  "events": "FIOS",
  "common/on_actions": "MERGE",
  "common/technologies": "DUPL",
  "common/planet_classes": "LIOS",
  "localisation": "LIOS_BYTE_LENGTH",
  "_default": "LIOS"
}
```

规则可改，代码不动。版本更新后审一张 diff 即可。

### 4.4 与符号表的关系

两者互补，不是替代：

| | 符号表 | 覆盖链审计 |
|---|---|---|
| 回答 | 符号**存不存在** | 定义**被谁改成什么** |
| 来源 | 游戏自己导出的官方表 | 从 mod 文件解析 |
| 失效方式 | 版本更新后过期 | playset 一变就过期（需重跑，很快） |

---

## 五、难点（按难度排序）

1. **多行/inline_script 的块边界**——Paradox 脚本允许嵌套任意深度，`iter_top_level_blocks` 已处理大部分，
   但 `inline_scripts` 引用需要展开才能算准（wiki 注明 `inline_scripts` 是 DUPL，且 *"only works when the file is fully replaced"*）
2. **`replace/` 目录**——被替换的文件**从未参与竞争**，必须单独处理，不能进同一个 LWW 表
3. **本地化的特殊规则**——普通 key 是「UTF-8 字节最短者胜」，不是加载顺序（`replace/` 内才是 LIOS）
4. **类型覆盖面**——工具箱只做了 9 类；真正的高发区 `technologies` / `ship_components` / `traits` / `pop_jobs` 全部要自己写

---

## 六、里程碑

| # | 内容 | 验收判据 |
|---|---|---|
| M1 | 抽通用解析层（借 `parser.py`），先只做 `planet_classes` 一类 | 能正确解析本体 + 214 mod 的该类定义，无漏块 |
| M2 | 加语义表，实现 LIOS/FIOS/DUPL/MERGE | 对 `events/` 判 FIOS 与本体实际行为一致 |
| M3 | 覆盖链报告 | 拿一个已知冲突的 mod 对做验证：产出里的赢家与游戏内实测一致 |
| M4 | 扩到高发类型 | 覆盖 `technologies` / `traits` / `ship_components` |
| M5 | `replace/` 与本地化规则 | 拿鸽组汉化 + 官中修正验证 replace 抢占 |

**M3 是关键验收点**：必须有「已知冲突 → 工具判定 == 游戏实测」的闭环，
否则工具只是产生了另一份不可信的输出。

---

## 七、不做的事

- ❌ 不做「自动修复」——覆盖判定只提供事实，怎么改由人决定
- ❌ 不依赖游戏运行——纯静态扫描，可离线、可进 git、可 diff
- ❌ 不重复符号表——符号存在性归 `script_documentation`，不在这里重做

---

## 八、参考

| 主题 | 位置 |
|---|---|
| 官方覆盖语义表 | `Stellaris/AGENTS.md`「官方权威：逐目录覆盖语义表」 |
| 符号表来源与解析 | `官方符号导出系统.md` |
| 可复用解析层 | `../外部参考/` 未收录；见工坊 3709855159 的 `celestial_toolbox_generator/src/celestial_toolbox/core/parser.py` |
| 经济类别层 | `机制结论/UniversalModifierPatch-适配核对.md` |
