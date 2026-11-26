# 03 · 引擎自己替换教义（CK3 `debug.log`）

**出处**：CK3 1.20.x 一次实际游戏，`<用户目录>/logs/debug.log`（已轮转）。
**用途**：支撑 `04-日志定位方法.md` §五 案例 A。

## 原行

```
[14:26:34][D][rite_effects.cpp:755] [RiteGen] Swapped out tenet 'tenet_divine_liturgy'
  for tenet 'tenet_sanctity_of_nature' while changing Rite with target divergence change 15.
```

## 这一行说明了什么

| 问题 | 答案 |
|---|---|
| 谁改的 | **引擎**（`rite_effects.cpp`，不是任何 mod 的脚本） |
| 换成什么 | 从候选池里抽的，可选项受当前「偏移度」约束 |
| 同一时刻还发生了什么 | 同一秒还有两条 doctrine 被换 |
| 为什么「合法」 | 被换上的教义确实在该信仰的 `permitted` 列表里 |

## 为什么这条比 `error.log` 有用

| | `error.log` | 这条 `debug.log` |
|---|---|---|
| 回答「有没有错」 | ✅ | ❌（这里没有错，是正常机制） |
| 回答「是谁干的」 | ❌ | ✅ |

⇒ 排查「内容莫名其妙变了」时，第一步不是找错误，而是**在 `debug.log` 里搜现象本身的动词**：
`Swapped out` / `Overriding` / `Applied` / `Generated`。

## 一个附带结论

报错/日志的来源如果是 **`.cpp` 而不是脚本文件**，那就是引擎行为。
**改 mod 不可能修掉它** —— 只能接住它（例如给玩家一个追认/驳回的交互）。

> 这类判断省下的时间最多：它把「我的代码有 bug」直接切换成「这个机制本来就是这样」。
