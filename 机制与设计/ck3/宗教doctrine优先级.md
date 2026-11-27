# Rite / Faith / Religion 的 doctrine 优先级

> **性质**：机制摸排 · **游戏**：CK3
> **归属**：CC BY-SA 4.0（见仓库 `LICENSE`）
> **适用版本**：以文中标注为准 —— 引擎改了，结论就可能过期
> **说明**：路径已占位，工坊 ID 保留（用于定位对象）；不含他人作品内容

**立档**：2026-11-10（排查 Suiginton 的礼教义冲突）
**依据**：本体 `.info` 文档原文 + 本体脚本，全部可复核

## 一、基本规则（官方原文）

`common/religion/rite_types/_rite_types.info` 第 78-82 行：

```
### brief: doctrines ( database keys )
# List of doctrines associated with this Rite. Rite doctrines override parent-religion
#   and faith doctrines from the same doctrine group. Faith doctrines from otherwise
#   unfilled groups are added to the instantiated main Rite.
```

翻成人话：

| 情况 | 结果 |
|---|---|
| 礼与父信仰**同一个 doctrine group** | **礼赢**（覆盖） |
| 礼**没填**的 group | 父信仰的 doctrine **加进来** |
| 礼与信仰在**不同** group | **两个都生效，不算冲突** |

再往上：`history/faiths/_faith_history.info`

```
# Main Rite at this date. Its core tenets and Rite-specific doctrines become the faith
#   effective properties; faith doctrines in otherwise unfilled doctrine groups are
#   additive to it.
```

## 二、关键：不同 group 的不算冲突

很多「看起来打架」的组合其实分属不同组，同时生效。实例：

| doctrine | doctrine_group_type |
|---|---|
| `doctrine_clerical_succession_temporal_appointment` | `doctrine_clerical_succession` |
| `special_doctrine_has_clerical_electors` | `has_clerical_electors` |

⇒ 「皇帝任命主教」和「枢机选举人」**并存**，互不覆盖。
`has_clerical_electors` 管的是枢机团 / 教宗选举那套（PAM），
消费点见 `important_actions/pam_actions.txt:931`、`on_action/title_on_actions.txt:318`、
`character_interactions/pam_interactions.txt:5477`。

## 三、按开局日期分层的额外覆盖（这才是 867 / 1066 的差异来源）

### byzantine_rite 的父信仰不同

`history/faiths/00_christianity.txt`：

| 开局 | byzantine_rite 的身份 | 父信仰 |
|---|---|---|
| **867** | `christian_faith` 的**非主礼**（`main_rite = roman_rite`，line 3） | `christian_faith` |
| **1054.7.16+** | `orthodox` 的**主礼**（line 192 `main_rite = byzantine_rite`） | `orthodox` |

### 两个信仰的 doctrines 不同

| 信仰 | doctrines |
|---|---|
| `christian_faith` | `special_doctrine_ecumenical_christian`、**`special_doctrine_has_clerical_electors`** |
| `orthodox` | 只有 `special_doctrine_ecumenical_christian` |

⇒ **`has_clerical_electors` 只有 867 路径会继承到礼上。**

## 四、vanilla 自己在 on_game_start 里的强制覆盖

`common/on_action/game_start.txt`：

### ① 1066 的「叙任权危机」覆盖（line 2505-2522）

```paradox
if = {
    limit = {
        has_pam_dlc_trigger = yes
        current_date >= 1066.1.1
        NOT = { current_date >= 1178.1.1 }
    }
    religion:christianity_religion = {
        every_faith = {
            limit = { has_doctrine_parameter = has_clerical_regions }
            change_doctrine = doctrine_clerical_succession_conditional
            every_faith_rite = {
                limit = { NOT = { rite_has_doctrine = doctrine_clerical_succession_conditional } }
                change_rite_doctrine = doctrine_clerical_succession_conditional
            }
        }
    }
}
```

注释原文：

> We put Christian faiths on conditional appointment in 1066 so the Investiture Crisis can happen.
> 867 is too early for it and by 1178 it is over.

**⇒ 玩 1066 时，礼里写什么都会被改成 `conditional`。**

### ② 1054+ 移除 electors（line 2536-2540）

```paradox
if = {
    limit = { has_global_variable = pam_great_schism_decision_taken }
    faith:christian_faith = { remove_doctrine = special_doctrine_has_clerical_electors }
    ...
}
```

`pam_great_schism_decision_taken` 在 `game_start_date >= 1054.7.16` 时设置（line 2528-2529）。

## 五、867 的结论（用户实际只玩 867）

两个强制覆盖块**都不执行**：
- conditional 要 `date >= 1066.1.1`
- remove 要 schism 已发生（`>= 1054.7.16`）

所以在 867：

```
byzantine_rite 实际拥有：
  doctrine_clerical_succession_temporal_appointment   ← 静态文件设的，组 doctrine_clerical_succession
  special_doctrine_has_clerical_electors              ← 从 christian_faith 继承，组 has_clerical_electors
  special_doctrine_is_eastern_christian_faith         ← 静态文件设的
  doctrine_clerical_marriage_disallowed               ← 静态文件设的
```

**两者不冲突，同时生效。**

## 六、执行顺序的隐患（只影响 1066+）

`common/on_action/_on_actions.info` 第 95 行原文：

> Note that it happens **concurrently** to events triggered by the on_action, **NOT before**.

⇒ `on_game_start` 的 `effect` 与 `on_actions` 列表里的 action 是**并发**的，
**先后顺序不保证**。

在 1066 路径下这意味着：mod 用 `on_actions` 追加的 `change_rite_doctrine`
与 vanilla `effect` 里的强制 `conditional` 覆盖**谁赢不确定**。
867 路径没有这个覆盖，所以碰不到。

## 七、一句话总结

> **同组礼赢，异组共存；867 没有额外覆盖，1066 有强制改写。**