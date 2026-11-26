# PROVENANCE —— CK3 1.20.1 符号表

> 由游戏自带的 `script_docs` 控制台命令导出。原样保存，未做任何清洗。

## 来源

| 项 | 值 |
|---|---|
| 游戏版本 | **1.20.1.2（Crozier）** |
| 构建号 | `f72d1599abd31d58bb79486e0f4ef5a132b0fe60` |
| 分支 | `release/1.20.1` |
| 导出时间 | 2026-11-09 14:58 |
| 导出方式 | `-debug_mode` 启动 + 控制台 `script_docs` |
| 输出位置（当时） | `logs/{triggers,effects,event_targets,on_actions,event_scopes,modifiers,custom_localization}.log` |
| **是否含 mod** | **未记录 —— 这是本份归档的已知缺口，见下节** |

## ⚠️ 关于「含不含 mod」：我没有当时的播放集记录

导出当时启用的 mod 列表没有被记录下来（`dlc_load.json` 是启动器派生的，之后又被改过多次）。
所以**不能声称「已证明是干净基线」** —— 只能说「未发现污染迹象」。

### 判定过程（以及一次真实的误判）

**第一版检测是错的。** 用 `grep -ic 'ce_'` 扫 `triggers.log`，得到 **76 条**，
于是判断「某个 mod 的符号混进来了」。行首锚定之后是 **0 条**：

```
reactive_advice_succession     <- 'advice_' 里的 ce_
advanced_activities            <- 'advanced_'
independence_faction           <- 'independence_'
any_truce_holder               <- 'truce_'
```

`custom_localization.log` 里那 5 条「疑似 mod 键」也一样：

| 命中 | 看起来像 | 实际是 |
|---|---|---|
| `rice_wine` `rice_cake` `rice_cake_plural` | RICE 这个 mod | **米酒 / 米糕**（本体宴会食物名） |
| `tao_yuanming` | `tao_` 前缀的某个 mod | **陶渊明**（本体人物） |

```bash
# 正确的检测：行首锚定
grep -c '^ce_' triggers.log            # 0
grep -c '^tao_' triggers.log           # 0
```

### 结论

| 能力 | 状态 |
|---|---|
| 引擎符号（triggers / effects / event_targets / on_actions / event_scopes） | **mod 加不进来**（同引擎的 Stellaris 侧已实测：这几类是引擎符号） |
| 数据面（modifiers / custom_localization） | **理论上可被 mod 扩展**；本份里行首锚定后 0 条 mod 前缀，未发现污染 |
| 是否为「已证明干净」 | ❌ **不是**。要证明只能**无 mod 跑一次再对比** |

⇒ 使用建议：查「某个名字存不存在」可以放心用；
查「这个 mod 用了什么」时，别拿它当「本体全集」的证明。

---

## 文件清单

| 文件 | 行数 | 条目数 | 计数依据 | sha256（前 16 位） |
|---|---|---|---|---|
| `triggers.log` | 13380 | **1937** | 分隔线块数 | `b9a1c626d46a0cd1` |
| `effects.log` | 18492 | **2128** | 分隔线块数 | `43aedf224feb8f5c` |
| `event_targets.log` | 2409 | **328** | 分隔线块数 | `6ad56bd63ecc3766` |
| `on_actions.log` | 5593 | **932** | 独占一行的 `name:` | `d17e74c5eb5eb581` |
| `event_scopes.log` | 520 | **74** | 独占一行的 `name:` | `4dc5072cb829a9c6` |
| `modifiers.log` | 2285 | **761** | 独占一行的 `Tag:` | `363b1f33de9e5b5a` |
| `custom_localization.log` | 47384 | **2782** | 独占一行的 `name:` | `d49f6e34ff01feb1` |
| **合计** | | **8942** | | |

完整 hash 用 `sha256sum *.log` 自行核对；与上面前缀一致即为原件。

## 格式要点（解析前必读）

| 项 | 本份的情况 |
|---|---|
| 换行 | **LF**（无 CR） |
| BOM | 无 |
| 首行 | 是标题行（`Trigger Documentation:` 等），**不含时间戳** |
| 确定性 | 首行是标题而非时间戳 ⇒ 同版本重跑应得**逐字节相同**的结果（未实测，但格式上没有可变字段） |
| 块分隔 | `--------------------`（10 个以上连字符），长度不固定 |
| 特例 | `event_scopes.log` / `modifiers.log` **没有分隔线**；`modifiers.log` 用 `Tag:` 而非 `name:` |

三种块格式与解析坑见 `05-符号表导出.md` §2.3 / §2.4。

## 这份归档的价值在哪

它是**版本 diff 的基准**：下一个 CK3 版本出来之后，`comm -23` 一下就知道哪些符号消失了 ——
而那些消失的名字，就是所有 mod 会坏的地方。

```bash
python3 tools/parse_script_docs.py 符号表/ck3-1.20.1 -o /tmp/old.json
# 新版本导出后
python3 tools/parse_script_docs.py 符号表/ck3-<新版本> -o /tmp/new.json
jq -r '.symbols[].name' /tmp/old.json | sort -u > /tmp/a.txt
jq -r '.symbols[].name' /tmp/new.json | sort -u > /tmp/b.txt
comm -23 /tmp/a.txt /tmp/b.txt      # 消失的：mod 会坏的地方
```
