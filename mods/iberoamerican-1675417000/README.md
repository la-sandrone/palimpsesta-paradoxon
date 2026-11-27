# Iberoamerican

> **原始来源**：Steam 创意工坊 `1675417000` —— Iberoamerican Namelist（上游声明版本 `2.3.2`）
>
> **上游状态**：早已停止维护（声明版本停在 `2.3.2`）
>
> 本目录发布的是**兼容性修正版**，仅做编号写法与显示名的调整，**不主张对原始内容的任何权利**。
>
> **如原作者或权利人对此有异议，请提 issue，我会立即删除。**

## 改了什么

- 上游结构本身已是现代的（多段 + `sequential_name`），本目录是**逐条手改**的版本
- 编号写法与显示名做了调整
- **拼写一个字没动**

## 目录内容

```
iberoamerican-1675417000/
├── common/name_lists/Iberoamerican.txt
└── localisation/
    ├── english/iberoamerican-1675417000_l_english.yml
    ├── simp_chinese/iberoamerican-1675417000_l_simp_chinese.yml
    └── spanish/iberoamerican-1675417000_l_spanish.yml
```

## 怎么装

**不提供 `.mod` 描述文件** —— 用 Paradox Launcher 的「创建 Mod」按钮生成，把 `path` 指到本目录即可。

手写也可以，内容就四行：

```
name="Iberoamerican"
path="<本目录的绝对路径>"
supported_version="v4.6.*"
version="1.0"
```

> 注意：`path` 用**绝对路径**，反斜杠写成双反斜杠，或直接用正斜杠。

## 为什么这个目录能工作

v3.6 起编号占位符同时改了三件事，任何一条踩中都会**静默失效**（不报错，名字就是不对）：

| 项 | 3.6 之前 | 3.6 之后 |
|---|---|---|
| 语法 | `%O%` `%R%` `%C%` | `$C$` `$ORD$` `$R$` `$HEX$` |
| 载体 | 写在 `common/name_lists` 里 | **必须写在 localisation 的字符串里** |
| 字段 | 任意 | **只有 `fleet_names` / `army_names`** |

详见仓库根目录 `07-名字表与名字包.md`。
