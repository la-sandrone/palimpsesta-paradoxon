# SPQR

> **原始来源**：Steam 创意工坊 `682798125` —— SPQR Namelist（上游声明版本 `1.2.*`）
>
> **上游状态**：早已停止维护（声明版本停在 `1.2.*`，远早于当前 v4.6.0）
>
> 本目录发布的是**兼容性修正版**，仅修复命名表在 v3.6+ 的语法/装载问题，**不主张对原始内容的任何权利**。
>
> **如原作者或权利人对此有异议，请提 issue，我会立即删除。**

## 改了什么

- 从上游 zip 中取出
- 旧编号语法 `%R%` → `$R$`，并搬进 `localisation/`

**拼写一个字没动。** 只做装载与语法层的适配。

## 目录内容

```
spqr-682798125/
├── common/name_lists/SPQR.txt
└── localisation/
    ├── english/spqr-682798125_l_english.yml
    └── simp_chinese/spqr-682798125_l_simp_chinese.yml
```

## 怎么装

**不提供 `.mod` 描述文件** —— 用 Paradox Launcher 的「创建 Mod」按钮生成，把 `path` 指到本目录即可。

手写也可以，内容就四行：

```
name="SPQR"
path="<本目录的绝对路径>"
supported_version="v4.6.*"
version="1.0"
```

> ⚠️ `path` 用**绝对路径**，反斜杠要写成 `\\` 或直接用正斜杠。

## 为什么这个目录能工作

v3.6 起编号占位符同时改了三件事，任何一条踩中都会**静默失效**（不报错、名字就是不对）：

| 项 | 3.6 之前 | 3.6 之后 |
|---|---|---|
| 语法 | `%O%` `%R%` `%C%` | `$C$` `$ORD$` `$R$` `$HEX$` |
| 载体 | 写在 `common/name_lists` 里 | **必须写在 localisation 的字符串里** |
| 字段 | 任意 | **只有 `fleet_names` / `army_names`** |

正确形态：

```paradox
army_names = { generic = { sequential_name = SOME_KEY } }
```
```yaml
 SOME_KEY:0 "Palatini $R$"
```

详见仓库根目录 `07-名字表与名字包.md`。
