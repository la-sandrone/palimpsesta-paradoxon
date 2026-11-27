# Universal Modifier Patch 在 v4.5.3 上的适配核对

> **性质**：机制摸排 · **游戏**：Stellaris
> **归属**：CC BY-SA 4.0（见仓库 `LICENSE`）
> **适用版本**：以文中标注为准 —— 引擎改了，结论就可能过期
> **说明**：路径已占位，工坊 ID 保留（用于定位对象）；不含他人作品内容

**对象**：`!!Universal Modifier Patch (4.4.*)`，Workshop ID **1688887083**
**核对日期**：2026-11-12
**游戏版本**：`Cygnus v4.5.3` / `507018f716b2543f49554de24e554e91`
**本体**：`common/economic_categories/`（7 个文件，270 个类别）
**mod**：单文件 `common/economic_categories/~~~modifiers_fix_categories.txt`（3388 行）

---

## 一、它到底做什么

工坊原文：

> brings the missing modifiers that existed in 2.2.0 to 2.2.5 back to life
> **(via overweight `00_common_categories.txt` load order to make them generate again)**

逐类比对后的实情，核心动作是一行注释：

```paradox
本体 : generate_mult_modifiers = { upkeep # produces }   ← P 社把 produces 注释掉了
mod  : generate_mult_modifiers = { produces upkeep }     ← 把它放出来
```

**机制**：经济类别决定「哪些 modifier 类型会被生成」。某类别没声明的类型，
即使 mod 写了也不生效、且**无任何日志**。
这个补丁靠文件名 `~~~` 抢加载顺序最后一位，按 key 覆盖本体定义，把生成列表铺满。

---

## 二、核对结果

| 检查项 | 结果 |
|---|---|
| 本体类别总数 | **270**（7 个文件） |
| mod 覆盖 | **164（61%）** |
| **过期键**（mod 有、本体已删） | **0** ✅ |
| **generate 列表真丢失** | **0** ✅ |
| `parent` / `use_for_ai_budget` | **完全一致** ✅ |
| `triggered_*` 丢失 | **0** ✅ |
| 净增 | 解放注释 **8** 项 + 纯新增 **115** 项 |

> ⚠️ 初次比对曾报 4 处「丢失」，实为 `#` 注释字符被正则误抓，**非真丢失**。

### 覆盖率按本体文件分布

| 本体文件 | 类别数 | 被覆盖 | 覆盖率 |
|---|---|---|---|
| `00_common_categories.txt` | 147 | 72 | **49%** |
| `01_job_categories.txt` | 70 | 66 | 94% |
| `02_pop_categories_categories.txt` | 19 | 18 | 95% |
| `02_wilderness_categories.txt` | 1 | 1 | 100% |
| `03_machine_age_categories.txt` | 3 | 3 | 100% |
| **`04_overlord_categories.txt`** | 25 | **0** | **0%** |
| `05_shroud_categories.txt` | 5 | 4 | 80% |

---

## 三、关键判断：它的价值已经变了

本体 4.5.3 **只剩 6 个类别**还有被注释的生成项：

```
planet_branch_offices     planet_disconnected_drones   planet_doctors
planet_engineers          planet_pop_assemblers        starbase_waystations_modules
```

**而这 6 个 mod 全都覆盖了。**

⇒ 它**不再是「修复 P 社 2.2.6 的 Oops」**（P 社基本补完了），
现在的作用是**「给 mod 扩展修正空间」**——把本体不生成、但 mod 想用的 modifier 组合提前铺出来。

这解释了为什么它仍该留着：**职业/人口类覆盖 94–95%**，是 mod 加 modifier 的主要战场。

---

## 四、残留风险

| 风险 | 说明 |
|---|---|
| **32 个类别被补 `modifier_category`** | 本体这几个类别**不指定**归属（如 `leader_commanders`、`planet_clip_maximizer`），mod 指定为 `leader` / `colony`。属**行为改变**而非纯修复，可能影响 tooltip 归类与 AI 预算归属 |
| **Overlord 25 个类别零覆盖** | 往附庸税/补贴/控股公司类别加 modifier 的 mod，这个补丁救不了 |
| **`00_common` 仅 49%** | 通用类别一半没铺到 |
| 4.5 新类别未覆盖 | `planet_zones`、`vivarium`、`planet_mind_thralls` 都不在 mod 内 |

**它只按键覆盖，未覆盖的 106 个类别保持本体原样 ⇒ 不会污染，属于「补一部分」而非「整份接管」。**

---

## 五、结论

| 项 | 判定 |
|---|---|
| 能否在 4.5.3 上用 | ✅ 结构兼容，不抹本体内容 |
| 版本警告 | `supported_version="v4.4.*"` 只是启动器提示，不影响加载 |
| 是否保留 | **保留**——职业/人口类别覆盖仍有实际价值 |
| 不能指望 | Overlord 全部、`00_common` 一半、4.5 新类别 |

---

## 六、复查方法（版本更新后重跑）

比对脚本属本地草稿工具，不进公开仓库；真正要留下的是这套判据（四支脚本各自的关注点）：

```bash
python3 cmp_cat2.py   # 键集合：交集 / mod 独有 / 本体独有
python3 cmp_gen.py    # 逐类比对 generate_add/mult，找真丢失与净增
python3 cmp_gap2.py   # 还有多少类别被注释掉
python3 cmp_cov.py    # 按本体文件统计覆盖率
```

**判据**：
- 「mod 独有」非空 ⇒ 出现过期键
- 「generate 真丢失」非空 ⇒ 开始抹本体内容

这两个一旦不为零，就该考虑停用或自己接管。
