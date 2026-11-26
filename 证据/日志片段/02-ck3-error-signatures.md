# 02 · CK3 错误签名（归一化）

**出处**：CK3 1.20.x，含一个 1.19 世代的行政制大改 mod（workshop 3343175673）的一次运行。
**用途**：支撑 `04-日志定位方法.md` §三（先聚合后钻取）与 §四（错误来源的 `.cpp` 决定失败阶段）。

## 为什么要归一化

原始 `error.log` 里同一类错误会重复上千次，行行不同（文件名、行号、条目名都不同）。
下面这张表把**变动的部分**替换成 `X` / `N`，只留结构。

总计 899 条原始行 → **138 个签名**，涉及 113 个文件。

## 签名表（次数降序，节选）

```
   次数  来源 .cpp                 签名
   307  pdx_localize.cpp         Duplicate localization key. Key 'X' is defined in both 'X' and 'X'.
   113  jomini_effect.cpp        PostValidate of effect 'X' returned false at file: common/scripted_effects/<文件>
    82  lexer.cpp                File 'X' should be in utfN-bom encoding (will try to use it anyways)
    30  pdx_persistent_reader.cpp Error: "Unknown trigger: trait_is_criminal_in_faith_trigger, near line: N"
    24  title_links.cpp          Failed to fetch a valid landed title 'X' at location 'X'
    18  jomini_trigger.cpp       PostValidate of trigger 'X' returned false at file: common/scripted_triggers/<文件>
    12  jomini_trigger.cpp       Inconsistent trigger scopes (character vs. landed_title)
    10  pdx_persistent_reader.cpp Error: "Unknown trigger: multiply, near line: N"
     9  modifier_instance.cpp    Unknown modifier type 'X' at file: common/court_positions/types/<文件> line: N
     8  modifier_instance.cpp    Unknown modifier type 'X' at file: common/court_positions/types/<文件> line: N (})
     7  pdx_persistent_reader.cpp Error: "Unexpected token: default, near line: N" in file: common/laws/<文件>
     6  faith_links.cpp          Failed to scope to faith 'X' at file: common/council_positions/<文件> line: N
     5  pdx_gui_factory.cpp      gui/<文件>.gui:N - 'X' is not a valid widget/type/property
     4  pdx_persistent_reader.cpp Error: "Unexpected enum found: administrative, near line: N"
```

## 怎么读这张表

| 观察 | 推论 |
|---|---|
| `pdx_persistent_reader.cpp` 占多数 | 大部分错在**解析期**（名字/ token 层面），加守卫没用，要配桩或改名 |
| `jomini_*.cpp` 集中出现 | **校验期**：作用域不一致，正确做法是把块拆小（见 `02` 案例 7） |
| `lexer.cpp` 的 BOM 告警有 82 条 | **编码问题**，而且它会让整个文件失效（见 `06` §六） |
| `modifier_instance.cpp` 里出现 `(})` 这种「类型名」 | 典型的**字段拼错被当成容器**（见 `02` 案例 3） |
| `Duplicate localization key` 有 307 条 | 汉化叠用的常态噪音，胜负由编码/长度决定（见 `01` §四） |

## 一条反直觉的结论

这张表里次数最多的 307 条（本地化重复）**几乎不影响游戏**，
而次数只有 9 条的 `Unknown modifier type` 才是真问题 —— 它对应界面上的幽灵条目。

> **按次数排序只是「先看哪里」的启发式，不是优先级。**
> 真正的优先级要看：这个错是否让某个功能整体不成立。
