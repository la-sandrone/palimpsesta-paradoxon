# on_action 合并模型

> **性质**：机制摸排 · **游戏**：CK3
> **归属**：CC BY-SA 4.0（见仓库 `LICENSE`）
> **适用版本**：以文中标注为准 —— 引擎改了，结论就可能过期
> **说明**：路径已占位，工坊 ID 保留（用于定位对象）；不含他人作品内容

**结论日期**：2026-11-10
**触发问题**：mod 一多，`on_game_start` 这种钩子到底是累积结算还是互相覆盖？

---

## 一、官方答案（`common/on_action/_on_actions.info`）

原文：

> You can declare data for on-actions in multiple files, however,
> **you cannot have multiple triggers or effect blocks for a given named on-action**.
> In particular, you cannot append an effect block directly to an on_action
> which already has an effect block, as this creates a conflict.

> If a modder wishes to append their own effects to an on_action without overriding a file,
> they may do it as follows:
> ```paradox
> some_vanilla_on_action = {
>     on_actions = {some_modded_on_action}
> }
> some_modded_on_action = {
>     effect = { some_fun_modding_effect = yes }
> }
> ```

### ⇒ 不是 SCM 式累积注册，是「字段槽位」

| 字段 | 语义 | 多 mod 同时定义会怎样 |
|---|---|---|
| `events` | 列表 | 可跨文件合并 |
| `on_actions` | 列表 | 可跨文件合并 |
| `random_events` / `first_valid` / `random_on_action` / `first_valid_on_action` | 列表 | 可跨文件合并 |
| **`effect`** | **单槽** | **冲突——静默丢弃其中一个** |
| **`trigger`** | **单槽** | **冲突——静默丢弃其中一个** |
| **`fallback` / `fallback_event`** | **单槽** | **冲突** |

**静默是这里最危险的地方**：不会有任何报错，游戏正常加载，
只是其中一个 mod 的那半逻辑**再也不会执行**。

---

## 二、实例：`on_game_start` 为什么没冲突

| 来源 | 声明了什么 |
|---|---|
| 本体 `game_start.txt`（2549 行） | `events = { … }` + **`effect = { … }`** |
| TAO `tao_on_game_start_actions.txt`（14 行） | **只有 `on_actions = { … }`** |

TAO **正好用了官方推荐的写法**：不碰 `effect` 槽位，只往 `on_actions` 列表里加。
所以本体的 `effect` 保留，TAO 的 10 个 setup action 被追加。

**这是「对」的写法，不是巧合——TAO 作者知道这个规矩。**

---

## 三、实扫：4-mod 组合里的真冲突

范围：本体 + Unop + TAO fork 的 `common/on_action`。
判据：**同一 on_action 的同一单槽字段，被「不同相对路径」的文件定义**。
（同名文件 = 整文件替换，不算字段冲突——这是第一版扫描的误报来源。）

结果：**只有 3 处**。

| on_action | 槽位 | 本体 | TAO | 判定 |
|---|---|---|---|---|
| `on_birthday_adulthood` | `trigger` | `birthday.txt` | `tao_birthday.txt` | ✅ **安全**——TAO 是超集，trigger 完全相同，另加 effect |
| `on_county_auto_granted_to_liege_culture` | `effect` | `culture_on_actions.txt` | `tao_override_on_actions.txt` | ⚠️ **丢了本体的一行**（见下） |
| `on_county_auto_granted_to_local_culture` | `effect` | 同上 | 同上 | ⚠️ 同上 |

### ⚠️ 发现：TAO 缺 `puppet_or_actor`

本体：

```paradox
hidden_effect = {
    scope:actor = { save_scope_as = puppet_or_actor }   ← 本体有
    scope:landed_title.holder = { save_scope_as = recipient }
```

TAO：

```paradox
hidden_effect = {
    scope:landed_title.holder = { save_scope_as = recipient }   ← 直接从这里开始
```

TAO 后加载、整个 `effect` 槽位接管 ⇒ **`scope:puppet_or_actor` 在这条链上永远不被设置**。

**实测影响：0 条报错。** `puppet_or_actor` 只在本体 `00_alliance.txt`（同盟互动）里用，
不在这条文化授予链上。

**但这是「1.19 副本丢 1.20 新增行」的又一例**，已在补丁里补回。

---

## 四、检查方法（可复用）

```
判据：同一 (on_action 名, 单槽字段) 被 >1 个「不同相对路径」的文件定义
排除：同相对路径（那是整文件替换，语义不同）
```

**这条检查应该进工具链**——因为它检测的是**静默失败**，
tiger 和 error.log 都不会报。

---

## 五、一句话

> **列表累积、槽位独占。**
> 多 mod 环境下的 `on_action` 危险不是「顺序不对」，
> 而是「你写的那半个 effect 根本没跑，还没有任何提示」。
