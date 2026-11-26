# 05 · 「报错数 = 无效项 × 出现次数」对账表

**出处**：CK3 一次实际运行，`<用户目录>/logs/error.log`；对照脚本为 `<本地 mod>/common/on_action/<文件>`。
**用途**：支撑 `04-日志定位方法.md` §六 案例 B。

## 对账表

```
报错总数: 14

  mod 行号  innovation                        行内容
  ------------------------------------------------------------------------------
      18  innovation_baliffs_bailiffs      add_innovation = innovation_baliffs_bailiffs
      24  innovation_development           add_innovation = innovation_development
      48  innovation_baliffs_bailiffs      add_innovation = innovation_baliffs_bailiffs
      55  innovation_development           add_innovation = innovation_development
      79  innovation_baliffs_bailiffs      ...
      85  innovation_development           ...
     110  innovation_baliffs_bailiffs      ...
     117  innovation_development           ...
     141  innovation_baliffs_bailiffs      ...
     147  innovation_development           ...
     170  innovation_baliffs_bailiffs      ...
     177  innovation_development           ...
     200  innovation_baliffs_bailiffs      ...
     207  innovation_development           ...

按 innovation 汇总:
  innovation_baliffs_bailiffs            7 次
  innovation_development                 7 次

14 = 2 x 7 (2 个无效 innovation x 7 个文化块)
```

## 为什么这张表比「知道错了」值钱

它给了一个**等式**：

```
报错数  =  无效项数  x  每个无效项的出现次数
   14   =      2      x            7
```

等式成立 ⇒ 说明**只有这两处错**，改完就干净。
等式不成立 ⇒ 还有你没看见的东西（某个无效项被别的机制重复触发了）。

> **判据：能写出等式的定位才叫定位完成。**
> 只报「这里有 14 条错」的是统计，不是结论。

## 顺带一个反直觉发现

`innovation_baliffs_bailiffs` 其实是某创新的**显示名变体**（`name =` 那一行里的写法），不是 ID。
而本地化里**恰好存在这个 key** —— 所以「从本地化反抄名字」会把这个 bug 一起抄回来。

| 抄的对象 | 结果 |
|---|---|
| 从**定义文件**抄 ID | ✅ |
| 从**本地化文件**抄「看起来像 ID」的字符串 | ❌ 可能抄到显示名变体 |
