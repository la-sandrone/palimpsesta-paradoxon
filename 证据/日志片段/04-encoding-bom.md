# 04 · 编码类告警（BOM）

**出处**：CK3 1.20.x，4-mod 组合的一次运行，`<用户目录>/logs/error.log`（已轮转）。
**用途**：支撑 `06-编码与渲染.md` §六。

## 原行

```
[16:00:27][W][lexer.cpp:101]: File 'common/governments/02_theocratic_government_types.txt'
  should be in utf8-bom encoding (will try to use it anyways)
```

同一次运行里这类告警 **82 条**，其中 17 个文件来自同一个整包覆盖的 mod。

## 为什么它容易被忽略

| 原因 | 说明 |
|---|---|
| 级别是 `[W]`（警告） | 不是 `[E]`，看起来像「注意事项」 |
| 后半句很安抚 | `will try to use it anyways` —— 它确实会试，但**结果不保证** |
| 混在噪音里 | 紧邻几百条 `Invalid supported_version` |
| 症状不可定位 | 表现是「那段字没出现」，而不是报错 |

## 它真正的后果

带 BOM 才走 UTF-8 解码路径。少了 BOM，引擎按单字节表处理，
这个文件里的**中文 key 整体不成立** —— 不是乱码，是**读不到**。

⚠️ 注意区分两件事：

| 现象 | 原因 |
|---|---|
| 字变成乱码 | 编码**错**（用了 UTF-8 存 CP1252 期待的内容，或反之） |
| 字**不出现** | 文件**没被读**（BOM 缺失 / 目录不对 / 被整份遮蔽） |

## 怎么批量查

```bash
for f in $(find localisation common -name '*.txt' -o -name '*.yml'); do
  [ "$(head -c3 "$f" | xxd -p)" = "efbbbf" ] || echo "NO BOM: $f"
done
```

## 一个必须记住的坑

**很多文本工具会在保存时静默删掉 BOM。**
所以「改完看起来正常」和「BOM 还在」是两件事 —— 只有字节复查能证明。

> 实测记录：用通用文本工具改写带 BOM 的文件后，首 3 字节变成正文开头，
> 而 diff 里只显示「首行少了一个不可见字符」。
