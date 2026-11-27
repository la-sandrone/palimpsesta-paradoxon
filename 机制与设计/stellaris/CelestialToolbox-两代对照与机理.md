# Celestial Toolbox：两代 mod 的关系与机理

> **性质**：机制摸排 · **游戏**：Stellaris
> **归属**：CC BY-SA 4.0（见仓库 `LICENSE`）
> **适用版本**：以文中标注为准 —— 引擎改了，结论就可能过期
> **说明**：路径已占位，工坊 ID 保留（用于定位对象）；不含他人作品内容

**核对日期**：2026-11-12
**游戏版本**：`Cygnus v4.5.3`

---

## 一、两个 ID 是同一个东西的两代

| | 旧版 | 新版 |
|---|---|---|
| Workshop ID | **3553991410** | **3709855159** |
| 标题 | Celestial ToolBox **[No Longer Maintained]** | Celestial Toolbox 2.0 |
| mod 名 | 天体工具箱 | 天体工具箱2.0 (Celestial Toolbox 2.0) |
| 作者 | 见工坊页 | 同一作者（与旧版） |
| 最后更新 | 2025-08-22 | 维护中 |
| 本地体积 | 48 MB | 11 MB |
| 声明版本 | `v4.*.*` | **`v4.3.*`** |
| 内部版本号 | `Beta-1.8.5` | `CGv 26.3` |

### ⚠️ 新版明确禁止与旧版同用

> **And DO NOT use with the old version of Celestial Toolbox.**

**两个都已经下载到本地**（`workshop/content/281990/` 下均有目录）。
如果 playset 里同时启用，属于作者明令禁止的组合。

---

## 二、它解决的是什么问题

Stellaris 的**脚本是静态的**：GUI 控件、`button_effects`、`gfx` 注册都必须在启动前写死，
**运行时无法枚举 mod 提供的内容**。

而这个工具箱要在界面上**列出你订阅的全部 mod 的异象 / 矿藏 / 修正 / 模型 / 星球类型**供选择。
⇒ 只能在游戏外**预先把 mod 数据编译成静态脚本**。

**这和我们做符号表的处境是同一类问题**：动态需求 → 离线预生成。

---

## 三、新版的架构

```
天体工具箱2.0/
├── Launch_Celestial_Toolbox_Generator.bat   ← 调用 PowerShell 启动生成器
├── celestial_toolbox_generator/
│   ├── main.py                              ← 入口，起 tkinter GUI
│   ├── src/celestial_toolbox/               ← 940 KB 源码
│   │   ├── core/{config,parser,template_engine}.py
│   │   ├── modules/{anomaly,deposit,modifier,entity,planet_class,
│   │   │             solar_system,star_class,pre_ftl,...}.py
│   │   └── gui/{app,home_frame,module_frame}.py
│   └── tools/windows_python_bootstrap.ps1
├── common/   ← 随包 Core 基线 + CodeGen 产物
└── interface/
```

### 随包已经带了「Core 基线」

| 类型 | 数量 |
|---|---|
| `*.txtcore` | 10 |
| `*.guicore` | 1 |
| `*.gfxcore` | 3 |
| 已生成的 `CodeGen_*.txt` | 18 |

⇒ 说明**纯原版内容不需要跑生成器**（与工坊说明一致：
*"If you only want to use the vanilla content, simply subscribe... and launch the game directly"*）。
生成器只在**要给 mod 内容做兼容库**时才需要跑。

### 旧版的架构完全不同

旧版**没有任何 .py**，用的是 `A_to_B/` 目录里的手工转换管线：

```
旧版/A_to_B/
├── conversion_log.json
├── generated_gui_controls.gui
└── planet_modifier1_inline.txt
```

⇒ 两代差别不是「修 bug」，是**手工转换 → Python 自动化转换**。

---

## 四、风险清单

| 风险 | 依据 | 严重度 |
|---|---|---|
| **两代同时启用** | 新版明令禁止 | 高 |
| **版本落后两个小版本** | 声明 `v4.3.*`，实际 4.5.3；4.5 重构了人口组/派系/组件 | 高 |
| **修改 playset 后不重跑会崩** | 工坊原文：*"If the playset, mod list, or mod order changes, you must initialize again. Otherwise opening the toolbox may crash the game."* | 高 |
| **产物写在工坊目录内** | 生成目标 `target_gui/gfx/button_effects/scripted_effects/loc` 均在 mod 根下 ⇒ **Steam 更新会覆盖，需重跑** | 中 |
| **执行第三方代码** | `.bat` → `powershell -ExecutionPolicy Bypass -File windows_python_bootstrap.ps1`；要求 Python 3.10+ | 中（信任决定） |
| **随包附带开发中间产物** | 3 个 `.bak`：`pre_solar_system_20260403`、`repair_20260405_005400` 等 | 低（不影响功能） |

---

## 五、对当前环境的判断

**不建议现在跑生成器。**

理由：生成器按 **playset 顺序扫描全部 mod** 并生成兼容库。而当前 214 个 mod
绝大部分**尚未适配 4.5.3**，跑出来的兼容库会把一堆坏的/过期的定义烤进去。
而且要改 playset 就得重跑，否则**开工具箱直接崩**。

**旧版建议退订**（已停维护 + 新版禁止同用 + 48 MB）。

---

## 六、待验证

- [ ] 新版 Core 基线（10 txtcore / 1 guicore / 3 gfxcore）在 4.5.3 上能否正常打开工具箱
- [ ] 只启用新版（旧版禁用）时，工具箱子菜单是否完整
- [ ] `planet_class` / `anomalies` 等数据结构在 4.5.3 有无变更（决定 Core 基线是否失效）
