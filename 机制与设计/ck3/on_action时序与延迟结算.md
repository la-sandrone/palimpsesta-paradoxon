# on_action 时序：为什么社区要「1月2日 / 1月30日」结算

> **性质**：机制摸排 · **游戏**：CK3
> **归属**：CC BY-SA 4.0（见仓库 `LICENSE`）
> **适用版本**：以文中标注为准 —— 引擎改了，结论就可能过期
> **说明**：路径已占位，工坊 ID 保留（用于定位对象）；不含他人作品内容

**立档**：2026-11-10
**触发**：排查 Suiginton 与 vanilla 在 `on_game_start` 里的覆盖竞争

## 一、硬事实：`effect` 与 `on_actions` 是并发的

`common/on_action/_on_actions.info` 第 95 行原文：

> Note that it happens **concurrently** to events triggered by the on_action, **NOT before**.

含义：同一个 on_action 里，

| 槽位 | 语义 |
|---|---|
| `effect = { }` | 单槽，**独占**，多文件重复定义会被静默丢弃 |
| `events = { }` / `on_actions = { }` / `random_events` / `first_valid` | **列表，跨文件合并** |

而 `effect` 与这些列表的执行是**并发**的，**先后顺序不保证**。

> 结论：**任何「我的效果必须晚于别人的效果」的需求，都不能靠 `on_game_start` 解决。**

## 二、引擎提供的唯一可靠手段：延迟

`_on_actions.info` 第 27-30 行：

```paradox
trigger_event = {
    on_action = on_action_name
    days/months/years = X  	# Optional
}
```

本体自己就这么用（`game_start.txt`）：

```paradox
trigger_event = {
    id = bookmark.0001
    days = { 365 730 }
}
```

## 三、社区惯例：两个日子的含义

867 / 1066 开局都是 **1月1日**，所以：

| 日子 | 写法 | 含义 |
|---|---|---|
| **1月2日** | `days = 1` | 开局当天所有并发效果已结算完毕，且尚未被月度 tick 改动 |
| **1月30日** | `days = 29` | 一月的月度维护（征召、经济、控制度、faith/army monthly）都跑完了，月底再改不会被覆盖 |

### 为什么不用 1月1日

因为 1月1日正是**战场本身**：

- `on_game_start` 的 `effect` 与各 mod 的 `on_actions` 并发
- `yearly_global_pulse` 也在 **1月1日** 触发（`_on_actions.info:4` 原文 "Called every January 1st"）

在 1月1日做修正 = 和所有东西抢跑道。

### 选 2 还是选 30

| 需求 | 用 |
|---|---|
| 只是要「晚于所有 on_game_start」 | **`days = 1`（1月2日）** |
| 还要晚于一月的月度维护 / 征召 / 经济结算 | **`days = 29`（1月30日）** |

## 四、写法模板

```paradox
# 1) on_game_start 里只负责「排队」，不干活
on_game_start = {
	on_actions = { my_deferred_setup }
}

my_deferred_setup = {
	effect = {
		trigger_event = {
			on_action = my_actual_fix
			days = 1          # 1月2日
		}
	}
}

# 2) 真正干活的地方
my_actual_fix = {
	effect = {
		# 此时 on_game_start 的一切都已完成，且顺序确定
	}
}
```

## 五、本案的适用性

Suiginton 在 `on_game_start.on_actions` 里改 `byzantine_rite` 的 doctrine，
而 vanilla 在 `on_game_start.effect` 里有强制覆盖：

```paradox
# game_start.txt:2505-2522，仅 1066-1178
every_faith_rite = {
    limit = { NOT = { rite_has_doctrine = doctrine_clerical_succession_conditional } }
    change_rite_doctrine = doctrine_clerical_succession_conditional
}
```

| 开局 | 冲突? | 后果 |
|---|---|---|
| **867** | 无（该块要求 `>= 1066.1.1`） | 现状可用 |
| **1066** | **有** | 谁赢不确定 |

⇒ 只在 867 玩的话现状没问题；
  若要通吃，把改 doctrine 的部分挪到 `days = 1` 的延迟 action 里即可确定胜负。

## 六、判据

> **凡是「必须晚于别人」的逻辑，一律不在 `on_game_start` 里做。**
> `on_game_start` 只用来**排队**，不要求任何顺序。
> 这是 `effect`/`on_actions` 并发语义逼出来的唯一稳写法。