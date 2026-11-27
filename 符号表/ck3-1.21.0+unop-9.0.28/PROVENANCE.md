# PROVENANCE —— CK3 1.21.0 + Unofficial Patch 9.0.28（工作基线）

> 这份是「实际工作时那套配置」导出的符号表：**本体 + 单个 mod（Unop）**，全 DLC。
> 只归档与纯本体**不同**的 3 个文件；其余 4 个逐字节相同，用哈希对照（省 6 MB 冗余）。

## 来源

| 项 | 值 |
|---|---|
| 游戏版本 | **1.21.0.3**（构建哈希 `0066127f2f020ce83d49bd32262629f94c3031e7`，短 `0066127f2f020`，与纯本体那份同一 build） |
| exe 指纹 | mtime 2026-11-19 22:57:19 / size 114758264 / sha256 `859f0d380098adcb…` |
| mod | **Unofficial Patch** `version="9.0.28"`，workshop **2871648329**，52 MB / 533 文件 / 2330 处 `#Unop` 标记 |
| DLC | **全开**（`disabled_dlcs: []`） |
| 导出时间 | 2026-11-27 08:17:31 |
| 导出方式 | `-debug_mode` + 控制台 `script_docs` |
| **UI 语言** | `l_simp_chinese`（`pdx_settings.txt`）⚠️ 影响字节，见下 |

名册原文（`dlc_load.json`）：

```json
{
  "enabled_mods": [ "mod/ugc_2871648329.mod" ],
  "disabled_dlcs": []
}
```

## 归档范围：只有 3 个文件

| 文件 | 与纯本体比 | 处置 |
|---|---|---|
| `triggers.log` | **逐字节相同**（`fb1212b2f87ab859`） | 不重复存，见 `../ck3-1.21.0/` |
| `effects.log` | **逐字节相同**（`7e82a997da03c37b`） | 同上 |
| `event_targets.log` | **逐字节相同**（`8144af1895dff6eb`） | 同上 |
| `event_scopes.log` | **逐字节相同**（`01342efacb099f27`） | 同上 |
| `on_actions.log` | 不同（6385 行，+18） | **本目录归档**（`19636c3fd36d8c26`） |
| `modifiers.log` | 不同（2930 行，行数不变） | **本目录归档**（`f95a6ba0686acfb2`） |
| `custom_localization.log` | 不同（50065 行，+14） | **本目录归档**（`33b77ffc25927cb6`） |

⇒ 4 个相同文件的哈希与 `../ck3-1.21.0/` 里的一致，可直接核对 —— 不需要再存一份。

## 差异的准确内容

**符号层面（按名字集合比，不是按行）：**

| 类别 | 变化 |
|---|---|
| on_action | **+3** |
| custom_localization | **+1** |
| modifier | 0（集合不变） |
| 其它四类 | 0 |
| **合计** | **10056 → 10060（+4）** |

新增的 4 个名字：

```
on_action             unop_governor_fallback_succession_game_start
on_action             unop_governor_fallback_succession_update
on_action             unop_inspiration_ongoing_choice_events
custom_localization   GetClanTaxCollectorAptitude
```

### `modifiers.log` 的特殊情况

行数完全一样（2930），条目集合也一样（976 vs 976），**但字节不同 —— 因为顺序变了**。

```
纯本体:  Tag: $DISTRICT_TYPE$_district_build_speed  ...  $MEN_AT_ARMS_TYPE$_max_size_mult ...
Unop  :  Tag: $DISTRICT_TYPE$_district_build_piety_cost  ...  $GOVERNMENT_TYPE$_tax_contribution_add ...
```

⇒ **这份文件不能按行 diff 比**，必须按集合比；否则每次都报「全都变了」。

**原因已测定（2026-11-27 补跑一次无 mod）：与 Unop 无关。**
三次导出（无 mod / +Unop / 又一遍无 mod）得到三份不同字节、同一个 976 条集合 ⇒
C3 自己的条目顺序每次运行就可能变。详见 ' + BT + '../ck3-1.21.0/PROVENANCE.md' + BT + ' 同名小节。

### `custom_localization.log` 里另有 2 个键消失

| 变化 | 名字 |
|---|---|
| 增 | `not_yet_chosen`、`unop_invite_to_activity_flavor_chariot_race` |
| 减 | `alevi_house_of_worship`、`alevi_religious_text_adj` |

**这两个为什么消失：未查明，不下结论。** 已知事实：

| 观察 | 结果 |
|---|---|
| Unop 是否覆盖了同名文件 | 是，`common/customizable_localization/00_pl_custom_loc_extra.txt` |
| 两份源文件是否逐字节相同 | **不同**（`06eb4800906250d9…` vs `e8f625053286d2a8…`），行数都是 8554 |
| 该字符串在两份源文件里都出现吗 | 都出现 2 次 |

⇒ 两种可能：① Unop 改了条件分支，这两条定制文本在 1.21 下不再生成；② 导出器枚举方式差异。
**要判定只能去读 Unop 那份文件的 diff**，本次没做。

## 日志侧：这才是「工作基线」和纯本体的主要差别

| 项 | 纯本体 | +Unop |
|---|---|---|
| `error.log` | **1195** 行 | **1737** 行（+542） |
| `database_conflicts.log` | 0 条 | **0 条** |

Unop 下多出来的错误签名（前几类）：

```
  150  pdx_gui_localize.cpp:207      Unlocalized text 'EVENT_WINDOW_OPTION_AVAILABLE_*'
                                      at gui/shared/event_windows.gui:N
   66  jomini_script_system.cpp:307   Script system error!
   46  jomini_effect.cpp:139          (PostValidate)
   26  jomini_dynamicdescription.cpp:444
   21  jomini_dynamicdescription.cpp:453
   20  jomini_trigger.cpp:258
```

⇒ 这是**下一步要查的东西**，不是符号表的事：工作基线本身还带着 542 行错误，
其中 150 条是 GUI 引用了不存在的本地化 key。

## ⚠️ `database_conflicts.log` 是 0 条，这本身是个结论

Unop 覆盖了 533 个文件，冲突日志**一条都没记**。
原因见 `01-覆盖语义.md` §五：**同路径同名文件 = 整文件替换，不进冲突日志**；
冲突日志只记「不同文件定义了同一个条目」。

⇒ 「冲突日志干净」和「没有覆盖」是两件完全不同的事 —— 这次拿到了一个干净的实证。

## ⚠️ UI 语言会改变字节（实测）

导出里的列表字段用**本地化连接词**拼出来。本机 UI 语言 `l_simp_chinese`，所以：

| 文件 | 非 ASCII 行数 | 例 |
|---|---|---|
| `modifiers.log` | **198** | `Use areas: character， province，以及 county` |
| `triggers.log` | 2 | `Traits: Valid DLCs: West Slavic Attire， Tours and Tournaments，...` |

⇒ 同一版本、同一配置，**换 UI 语言导出会得到不同字节**（那 200 行变成 `, and ...,`）。
⇒ 所以跨归档比对之前，先确认两边 UI 语言一致；不一致的地方全是逗号，不是内容。

---

## 已知缺口

| 缺口 | 说明 |
|---|---|
| ~~构建哈希~~ | 已补：游戏退出后 `code_revisions.log` 写出，`0066127f2f020` / `release/1.21.0`，与纯本体那份一致 |
| 4 个相同文件未存副本 | 有意为之：哈希可核对，避免 6 MB 冗余 |
| ~~modifiers.log 顺序变化~~ | 已测定：与 Unop 无关，CK3 每次运行顺序都可能变 |
| alevi 两个键消失的原因 | 未查明，已列两种假设 |
