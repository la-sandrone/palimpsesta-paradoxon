# Byzantine

> **原始来源**：Steam 创意工坊 `682721604` —— Byzantine Name List（上游声明版本 `2.2.*`）
>
> **上游状态**：早已停止维护（声明版本停在 `2.2.*`，远早于当前 v4.6.0）
>
> 本目录发布的是**兼容性修正版**，仅修复命名表在 v3.6+ 的语法/装载问题，**不主张对原始内容的任何权利**。
>
> **如原作者或权利人对此有异议，请提 issue，我会立即删除。**

## 改了什么

- **内容原本锁在 zip 里**（引擎不读 zip，所以它从未生效过）——本条目录是从 zip 中取出的
- **修复 7 处缺失右括号**（`ion_cannon`、`names1`~`names6`），按缩进结构重建括号行
- 旧编号语法 `%R%` → `$R$`，并按 3.6 起的规则搬进 `localisation/`

**拼写一个字没动。** 只做装载与语法层的适配。

### 已知遗留

- 原文件的括号与缩进互相矛盾，无法靠插补闭合修好；最终以**缩进**为结构真相重新生成括号
- 重建后 97/97 平衡，389 行内容全保留

## 目录内容

```
byzantine-682721604/
├── common/name_lists/Byzantine.txt
└── localisation/
    ├── english/byzantine-682721604_l_english.yml
    └── simp_chinese/byzantine-682721604_l_simp_chinese.yml
```

## 怎么装

**不提供 `.mod` 描述文件** —— 用 Paradox Launcher 的「创建 Mod」按钮生成，把 `path` 指到本目录即可。

手写也可以，内容就四行：

```
name="Byzantine"
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
