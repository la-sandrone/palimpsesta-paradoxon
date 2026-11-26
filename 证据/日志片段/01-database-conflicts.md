# 01 · 条目级覆盖日志（CK3 `database_conflicts.log`）

**出处**：CK3 1.20.x 一次实际运行，原始文件 `<用户目录>/logs/database_conflicts.log`（已轮转）。
**用途**：支撑 `01-覆盖语义.md` §五「只有 CK3 有这份日志，且只记赢家」。

## 真实行长什么样

```
[06:55:02][W][game_database.h:272]: Overriding entry 'byzantine_rite'
  for database 'common/religion/rite_types'
  in 'file: common/religion/rite_types/zz_<我的 mod>_byzantine_rite.txt line: 9'
```

（原始日志是**一行**，这里为阅读折行。实际字段顺序为：
`Overriding entry '<条目>' for database '<数据库>' in 'file: <覆盖者> line: <行号>'`。）

## 它说了什么、没说什么

| | 内容 |
|---|---|
| ✅ 有 | 条目名、所属数据库、**赢家**文件名与行号、发生时间 |
| ❌ 没有 | **被压的是谁**、旧值是什么、新值是什么 |
| ❌ 没有 | 文件级覆盖（同路径同名文件整份替换） |
| ❌ 没有 | **任何本地化 key 冲突** |

⇒ 所以「冲突日志干净」不等于没冲突（见 `02-静默失效案例.md` §一）。

## 版本差异（同一个文件的两种行首）

| 版本 | 行首 |
|---|---|
| 1.20.x | `[W][game_database.h:272]` |
| 1.19.x | `[W][gamedatabase.h:321]` |

> 这个差别看起来毫无意义，但它是**归一化签名的坑**：
> 如果按「源文件:行号」聚合，跨版本对比会把同一个告警算成两类。
> 跨版本比对时先把版本相关的部分折叠掉。

## 一条被覆盖条目的完整定位（三步）

```bash
# ① 从日志拿到条目名 + 赢家
grep "Overriding entry 'byzantine_rite'" "<用户目录>/logs/database_conflicts.log"

# ② 去各 mod 目录里找「还有谁定义过这个条目」
rg -l "^byzantine_rite\s*=" <各 mod 目录>/common/ 2>/dev/null

# ③ 用文件名 ASCII 序判断最终赢家（排序更晚的才是赢家）
```
